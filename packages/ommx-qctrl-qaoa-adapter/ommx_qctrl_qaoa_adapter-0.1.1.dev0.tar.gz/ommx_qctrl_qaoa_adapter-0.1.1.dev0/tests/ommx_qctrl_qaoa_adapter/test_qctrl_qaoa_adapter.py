from types import SimpleNamespace
import sys

import pytest
import sympy as sp

from ommx_qctrl_qaoa_adapter import OMMXQctrlQAOAAdapter, OMMXQctrlQAOAAdapterError
from ommx.v1 import DecisionVariable, Instance


class FakeJob:
    def __init__(
        self, *, status_name: str, result: dict | None = None, error_message: str = ""
    ):
        self._status = SimpleNamespace(name=status_name)
        self._result = result
        self._error_message = error_message

    def status(self):
        return self._status

    def result(self):
        return self._result

    def error_message(self):
        return self._error_message


def _sample_instance():
    x = [DecisionVariable.binary(i) for i in range(3)]
    edges = [(0, 1), (1, 2)]
    objective = 0
    for i, j in edges:
        objective += x[i] + x[j] - 2 * x[i] * x[j]
    instance = Instance.from_components(
        decision_variables=x,
        objective=objective,
        constraints=[],
        sense=Instance.MAXIMIZE,
    )
    return x, instance


def _sample_result(bitstring: str) -> dict:
    bit_length = len(bitstring)
    return {
        "solution_bitstring": bitstring,
        "solution_bitstring_cost": 0.0,
        "variables_to_bitstring_index_map": {
            f"x_{index}": index for index in range(bit_length)
        },
        "best_parameters": [0.1, 0.2],
        "iteration_count": 4,
        "provider_job_ids": ["job-1"],
        "final_bitstring_distribution": {bitstring: 16},
    }


def _fireopal_stub(mocker, job):
    credentials = SimpleNamespace(
        make_credentials_for_ibm_cloud=mocker.Mock(return_value="cred-cloud"),
    )
    return SimpleNamespace(
        credentials=credentials, solve_qaoa=mocker.Mock(return_value=job)
    )


def test_decode_success():
    variables, instance = _sample_instance()
    adapter = OMMXQctrlQAOAAdapter(instance)
    result = _sample_result("101")

    solution = adapter.decode(result)

    assert solution.state.entries[variables[0].id] == 1
    assert solution.state.entries[variables[1].id] == 0
    assert solution.state.entries[variables[2].id] == 1
    assert solution.objective == pytest.approx(2.0)
    assert solution.annotations["result.best_parameters"] == "[0.1, 0.2]"
    assert solution.annotations["result.provider_job_ids"] == '["job-1"]'


def test_decode_missing_bitstring():
    _, instance = _sample_instance()
    adapter = OMMXQctrlQAOAAdapter(instance)
    invalid = _sample_result("000")
    invalid.pop("solution_bitstring")

    with pytest.raises(OMMXQctrlQAOAAdapterError):
        adapter.decode(invalid)


def test_decode_missing_mapping_entry():
    _, instance = _sample_instance()
    adapter = OMMXQctrlQAOAAdapter(instance)
    result = _sample_result("000")
    # Remove one mapping to trigger failure.
    result["variables_to_bitstring_index_map"].pop("x_2")

    with pytest.raises(OMMXQctrlQAOAAdapterError):
        adapter.decode(result)


def test_solver_input_contains_expected_terms():
    variables, instance = _sample_instance()
    adapter = OMMXQctrlQAOAAdapter(instance)
    poly = adapter.solver_input

    assert isinstance(poly, sp.Poly)
    symbol_names = {str(symbol) for symbol in poly.gens}
    for var in variables:
        assert f"x_{var.id}" in symbol_names

    expr = poly.as_expr()
    sym_a = sp.symbols(f"x_{variables[0].id}")
    sym_b = sp.symbols(f"x_{variables[1].id}")
    assert expr.has(sym_a * sym_b)


def test_solve_with_mock(tmp_path, mocker):
    variables, instance = _sample_instance()

    job = FakeJob(status_name="DONE", result=_sample_result("101"))
    fireopal = _fireopal_stub(mocker, job)
    run_options = object()

    mocker.patch.dict(sys.modules, {"fireopal": fireopal})

    job_file = tmp_path / "job.pkl"
    solution = OMMXQctrlQAOAAdapter.solve(
        ommx_instance=instance,
        backend_name="fake_backend",
        ibm_token="fake_token",
        ibm_instance="fake_instance",
        run_options=run_options,
        job_pkl_output_name=str(job_file),
    )

    assert job_file.exists()
    assert solution.state.entries[variables[0].id] == 1
    assert solution.objective == pytest.approx(2.0)

    fireopal.credentials.make_credentials_for_ibm_cloud.assert_called_once_with(
        token="fake_token",
        instance="fake_instance",
    )
    fireopal.solve_qaoa.assert_called_once()
    call_args = fireopal.solve_qaoa.call_args
    assert call_args.args[2] == "fake_backend"
    assert call_args.kwargs["run_options"] is run_options


def test_solve_job_error(mocker):
    _, instance = _sample_instance()

    job = FakeJob(status_name="ERROR", error_message="boom")
    fireopal = _fireopal_stub(mocker, job)

    mocker.patch.dict(sys.modules, {"fireopal": fireopal})

    with pytest.raises(OMMXQctrlQAOAAdapterError):
        OMMXQctrlQAOAAdapter.solve(
            ommx_instance=instance,
            backend_name="fake_backend",
            ibm_token="fake",
            ibm_instance="fake_instance",
        )
