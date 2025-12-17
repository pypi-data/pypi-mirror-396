from __future__ import annotations

import json
import pickle
from collections.abc import Mapping
from typing import Any

import sympy as sp

from ommx.adapter import SolverAdapter
from ommx.v1 import DecisionVariable, Instance, Solution, State

from .exception import OMMXQctrlQAOAAdapterError


class OMMXQctrlQAOAAdapter(SolverAdapter):
    """OMMX adapter for the Q-CTRL QAOA solver."""

    SOLVER_NAME = "Q-CTRL QAOA Solver"

    def __init__(
        self,
        ommx_instance: Instance,
    ):
        """Initializes the adapter.

        Args:
            ommx_instance (Instance): The OMMX model to encode for Fire Opal.
        """
        self.instance = ommx_instance
        self._symbol_map: dict[int, sp.Symbol] = {}
        self.cost_polynomial: sp.Poly | None = None
        self._check_decision_variables()
        self._set_objective()
        self._check_constraints()

    @property
    def solver_input(self) -> sp.Poly:
        """Return the SymPy polynomial representing the HUBO/QUBO objective.

        Note:
            This returns the raw SymPy polynomial.
        """
        return self.cost_polynomial

    @classmethod
    def solve(
        cls,
        ommx_instance: Instance,
        backend_name: str,
        *,
        credentials: Any | None = None,
        ibm_token: str | None = None,
        ibm_instance: str | None = None,
        run_options: Any | None = None,
        job_pkl_output_name: str | None = None,
    ) -> Solution:
        """Solves the provided instance using the Q-CTRL QAOA solver.

        Args:
            ommx_instance (Instance): Instance to solve.
            backend_name (str): Target backend within the IBM instance.
            credentials (Any | None): Pre-built Fire Opal credentials. If omitted,
                ``ibm_token`` and ``ibm_instance`` must be provided and will be wrapped
                using Fire Opal's IBM Cloud helper.
            ibm_token (str | None): IBM Quantum API token used when ``credentials`` is not provided.
            ibm_instance (str | None): IBM Quantum instance CRN used when ``credentials`` is not provided.
            run_options (Any | None): Optional provider-specific run options passed to ``fireopal.solve_qaoa``.
            job_pkl_output_name (str | None): Optional path to store the raw job object.

        Returns:
            Solution: Evaluated solution produced by Fire Opal.

        Raises:
            OMMXQctrlQAOAAdapterError: If the cost polynomial cannot be built or Fire Opal is unavailable.
        """
        adapter = cls(ommx_instance)
        if adapter.cost_polynomial is None:
            raise OMMXQctrlQAOAAdapterError(
                "Unable to build the Fire Opal cost polynomial from the provided instance."
            )

        try:
            import fireopal as fireopal_module
        except ImportError as exc:
            raise OMMXQctrlQAOAAdapterError(
                "fireopal is required to submit jobs to Q-CTRL."
            ) from exc

        credential_bundle = cls._resolve_credentials(
            credentials=credentials,
            ibm_token=ibm_token,
            ibm_instance=ibm_instance,
            fireopal_module=fireopal_module,
        )

        print("Submitting job to Quantum backend via Fire Opal...")
        job = fireopal_module.solve_qaoa(
            adapter.solver_input,
            credential_bundle,
            backend_name,
            run_options=run_options,
        )
        if job_pkl_output_name:
            with open(job_pkl_output_name, "wb") as fp:
                pickle.dump(job, fp)
            print(f"Job result saved to {job_pkl_output_name}")
        print("Waiting for results (this may take a while)...")

        cls._ensure_job_succeeded(job)
        return adapter.decode(job.result())

    def decode(self, data: Mapping[str, Any]) -> Solution:
        """Converts a QAOA solver result to an OMMX solution.

        Args:
            data (Mapping[str, Any]): Raw payload returned by ``fireopal.solve_qaoa``.

        Returns:
            Solution: Evaluated solution including annotations.

        Raises:
            OMMXQctrlQAOAAdapterError: If the payload misses required fields.
        """
        bitstring = data.get("solution_bitstring")
        if not isinstance(bitstring, str):
            raise OMMXQctrlQAOAAdapterError(
                'The provided data must contain a "solution_bitstring" string.'
            )

        mapping = data.get("variables_to_bitstring_index_map")
        if not isinstance(mapping, Mapping):
            raise OMMXQctrlQAOAAdapterError(
                'The provided data must contain a "variables_to_bitstring_index_map" mapping.'
            )

        try:
            normalized_mapping = {
                str(key): int(value) for key, value in mapping.items()
            }
        except (TypeError, ValueError) as exc:
            raise OMMXQctrlQAOAAdapterError(
                '"variables_to_bitstring_index_map" values must be integers.'
            ) from exc

        state = self.decode_to_state(bitstring, normalized_mapping)
        solution = self.instance.evaluate(state)
        solution.solver = self.SOLVER_NAME
        self._attach_annotations(solution, data)
        return solution

    def decode_to_state(
        self,
        bitstring: str,
        variables_to_bitstring_index_map: Mapping[str, int],
    ) -> State:
        """Converts a QAOA bitstring into an :class:`ommx.v1.State`.

        Args:
            bitstring (str): Bitstring reported by Fire Opal.
            variables_to_bitstring_index_map (Mapping[str, int]): Mapping from symbol to bit index.

        Returns:
            State: Reconstructed OMMX state.

        Raises:
            OMMXQctrlQAOAAdapterError: If the mapping is inconsistent or indices are invalid.
        """
        entries: dict[Any, int] = {}
        size = len(bitstring)
        for var in self.instance.used_decision_variables:
            label = self._variable_label(var)
            if label not in variables_to_bitstring_index_map:
                raise OMMXQctrlQAOAAdapterError(
                    f"Variable {label} not found in variables_to_bitstring_index_map."
                )
            index = variables_to_bitstring_index_map[label]
            if index < 0 or index >= size:
                raise OMMXQctrlQAOAAdapterError(
                    f"Bitstring index {index} for variable {label} is out of bounds."
                )
            bit_value = bitstring[index]
            if bit_value not in {"0", "1"}:
                raise OMMXQctrlQAOAAdapterError(
                    f"Unexpected bit value '{bit_value}' for variable {label}."
                )
            entries[var.id] = int(bit_value)
        return State(entries=entries)

    def _variable_label(self, var: DecisionVariable) -> str:
        """Provides the symbolic label used for a decision variable.

        Args:
            var (DecisionVariable): Variable to describe.

        Returns:
            str: Symbol name used inside the polynomial.
        """
        symbol = self._symbol_map.get(var.id)
        if symbol is None:
            return str(var.id)
        return str(symbol)

    def _attach_annotations(
        self,
        solution: Solution,
        data: Mapping[str, Any],
    ) -> None:
        """Stores relevant Fire Opal fields inside the solution annotations.

        Args:
            solution (Solution): Solution being enriched.
            data (Mapping[str, Any]): Raw Fire Opal payload.
        """
        annotation_serializers: dict[str, Any] = {
            "best_parameters": json.dumps,
            "iteration_count": lambda value: str(value),
            "provider_job_ids": json.dumps,
            "solution_bitstring_cost": lambda value: str(value),
            "final_bitstring_distribution": json.dumps,
            "variables_to_bitstring_index_map": json.dumps,
        }
        for key, serializer in annotation_serializers.items():
            if key in data and data[key] is not None:
                solution.annotations[f"result.{key}"] = serializer(data[key])

    def _check_decision_variables(self) -> None:
        """Validates that the instance has binary decision variables."""
        if len(self.instance.used_decision_variables) == 0:
            raise OMMXQctrlQAOAAdapterError("The instance has no decision variables.")

        for var in self.instance.used_decision_variables:
            if var.kind != DecisionVariable.BINARY:
                raise OMMXQctrlQAOAAdapterError(
                    f"Unsupported decision variable kind: "
                    f"id: {var.id}, kind: {var.kind}"
                )

    def _set_objective(self) -> None:
        """Builds the polynomial objective understood by Fire Opal."""
        if self.instance.sense == Instance.MAXIMIZE:
            correct_phase = -1
        elif self.instance.sense == Instance.MINIMIZE:
            correct_phase = +1
        else:
            raise OMMXQctrlQAOAAdapterError(
                f"Sense not supported: {self.instance.sense}"
            )

        symbol_ids = sorted(var.id for var in self.instance.used_decision_variables)
        self._symbol_map = {var_id: sp.symbols(f"x_{var_id}") for var_id in symbol_ids}

        polynomial_expr = 0.0
        for key, coeff in self.instance.objective.terms.items():
            normalized_key = self._normalize_term_key(key)
            factor = correct_phase * float(coeff)
            monomial = 1
            for var_id in normalized_key:
                try:
                    monomial *= self._symbol_map[var_id]
                except KeyError as exc:
                    raise OMMXQctrlQAOAAdapterError(
                        f"Objective term references unknown variable id {var_id}."
                    ) from exc
            polynomial_expr += factor * monomial

        symbols = [self._symbol_map[var_id] for var_id in symbol_ids]
        self.cost_polynomial = (
            sp.Poly(polynomial_expr, *symbols) if symbols else sp.Poly(polynomial_expr)
        )

    def _check_constraints(self) -> None:
        """Ensures the instance is unconstrained."""
        if len(self.instance.constraints) > 0:
            raise OMMXQctrlQAOAAdapterError(
                "QAOA solver only supports unconstrained problems."
            )

    @staticmethod
    def _normalize_term_key(key: Any) -> tuple[int, ...]:
        """Normalizes objective term keys into tuples.

        Args:
            key (Any): Original key from the objective dictionary.

        Returns:
            tuple[int, ...]: Canonicalized key used internally.

        Raises:
            OMMXQctrlQAOAAdapterError: If the key type is unsupported.
        """
        if key in (None, ()):
            return tuple()
        if isinstance(key, int):
            return (key,)
        if isinstance(key, (list, tuple)):
            return tuple(int(k) for k in key)
        if isinstance(key, (set, frozenset)):
            return tuple(int(k) for k in sorted(key))
        raise OMMXQctrlQAOAAdapterError(
            f"Unsupported objective term key type: {type(key)!r}"
        )

    @staticmethod
    def _ensure_job_succeeded(job: Any) -> None:
        """Raises when the Fire Opal job reports an error status.

        Args:
            job (Any): Fire Opal job object whose status should be inspected.

        Raises:
            OMMXQctrlQAOAAdapterError: If the job reports an error or failure status.
        """
        status_callable = getattr(job, "status", None)
        if not callable(status_callable):
            return
        status = status_callable()
        status_str = None
        if hasattr(status, "name"):
            status_str = status.name
        elif hasattr(status, "value"):
            status_str = status.value
        elif status is not None:
            status_str = str(status)

        if status_str and status_str.upper() in {"ERROR", "FAILED"}:
            error_message = (
                job.error_message()
                if hasattr(job, "error_message") and callable(job.error_message)
                else "Unknown error."
            )
            raise OMMXQctrlQAOAAdapterError(
                "An error occurred during the optimization job:"
                f" {error_message} "
                "Please check your IBM Quantum dashboard for more details."
            )

    @staticmethod
    def _resolve_credentials(
        *,
        credentials: Any | None,
        ibm_token: str | None,
        ibm_instance: str | None,
        fireopal_module: Any,
    ) -> Any:
        """Constructs the credential bundle accepted by Fire Opal.

        Args:
            credentials (Any | None): Pre-built credentials provided by the caller.
            ibm_token (str | None): IBM Quantum token when building credentials locally.
            ibm_instance (str | None): IBM Quantum instance CRN when building credentials.
            fireopal_module (Any): Imported Fire Opal module to source helpers from.

        Returns:
            Any: Credential object passed to ``fireopal.solve_qaoa``.

        Raises:
            OMMXQctrlQAOAAdapterError: If inputs are missing or helpers are unavailable.
        """
        if credentials is not None:
            return credentials
        if not ibm_token or not ibm_instance:
            raise OMMXQctrlQAOAAdapterError(
                "Either a credentials object or both ibm_token and ibm_instance must be provided."
            )
        credentials_module = getattr(fireopal_module, "credentials", None)
        if credentials_module is None:
            raise OMMXQctrlQAOAAdapterError(
                "fireopal.credentials is not available; unable to build credentials bundle."
            )

        builder = getattr(
            credentials_module,
            "make_credentials_for_ibm_cloud",
            None,
        )
        if builder is None:
            raise OMMXQctrlQAOAAdapterError(
                "fireopal.credentials.make_credentials_for_ibm_cloud is unavailable."
            )
        return builder(
            token=ibm_token,
            instance=ibm_instance,
        )
