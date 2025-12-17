import pytest

from ommx_kipu_iskay_adapter import OMMXKipuIskayAdapter, OMMXKipuIskayAdapterError

from ommx.v1 import Instance, DecisionVariable, Quadratic
from qiskit.providers.jobstatus import JobStatus


def test_integration_binary_minimize():
    # Objective function: x1 - 2*x2 (Minimize)
    # x1, x2: binary
    # Optimal solution: x1 = 0, x2 = 1 (objective = -2)
    x1 = DecisionVariable.binary(1)
    x2 = DecisionVariable.binary(2)
    instance = Instance.from_components(
        decision_variables=[x1, x2],
        objective=x1 - 2 * x2,
        constraints=[],
        sense=Instance.MINIMIZE,
    )

    adapter = OMMXKipuIskayAdapter(instance)

    # Test decode with mock solution
    mock_solution = {str(x1.id): 0, str(x2.id): 1}
    mock_solution_info = {
        "seed_transpiler": 42,
        "mapping": {str(x1.id): 0, str(x2.id): 1},
    }
    mock_result = {"solution": mock_solution, "solution_info": mock_solution_info}

    solution = adapter.decode(mock_result)

    assert solution.state.entries[x1.id] == 0
    assert solution.state.entries[x2.id] == 1
    assert solution.objective == pytest.approx(-2.0)


def test_integration_binary_maximize():
    # Objective function: -x1 + x2 (Maximize)
    # x1, x2: binary
    # Optimal solution: x1 = 0, x2 = 1 (objective = 1)
    x1 = DecisionVariable.binary(1)
    x2 = DecisionVariable.binary(2)
    instance = Instance.from_components(
        decision_variables=[x1, x2],
        objective=-x1 + x2,
        constraints=[],
        sense=Instance.MAXIMIZE,
    )

    adapter = OMMXKipuIskayAdapter(instance)

    # Test decode with mock solution
    mock_solution = {str(x1.id): 0, str(x2.id): 1}
    mock_solution_info = {
        "seed_transpiler": 42,
        "mapping": {str(x1.id): 0, str(x2.id): 1},
    }
    mock_result = {"solution": mock_solution, "solution_info": mock_solution_info}

    solution = adapter.decode(mock_result)

    assert solution.state.entries[x1.id] == 0
    assert solution.state.entries[x2.id] == 1
    assert solution.objective == pytest.approx(1.0)


def test_integration_quadratic_objective():
    # Objective function: x1 + x2 + 2*x1*x2 (QUBO)
    # x1, x2: binary
    x1 = DecisionVariable.binary(1)
    x2 = DecisionVariable.binary(2)

    # Create quadratic objective: x1 + x2 + 2*x1*x2
    objective = Quadratic(
        rows=[1, 2],
        columns=[1, 2],
        values=[2, 2],  # 2*x1*x2 represented as off-diagonal terms
        linear=x1 + x2,
    )

    instance = Instance.from_components(
        decision_variables=[x1, x2],
        objective=objective,
        constraints=[],
        sense=Instance.MINIMIZE,
    )

    adapter = OMMXKipuIskayAdapter(instance)

    # Test decode with mock solution
    # If x1=0, x2=0: objective = 0
    mock_solution = {str(x1.id): 0, str(x2.id): 0}
    mock_solution_info = {
        "seed_transpiler": 42,
        "mapping": {str(x1.id): 0, str(x2.id): 1},
    }
    mock_result = {"solution": mock_solution, "solution_info": mock_solution_info}

    solution = adapter.decode(mock_result)

    assert solution.state.entries[x1.id] == 0
    assert solution.state.entries[x2.id] == 0
    assert solution.objective == pytest.approx(0.0)


def test_integration_three_variables():
    # Objective function: x0 + x1 + x2 (Minimize)
    # x0, x1, x2: binary
    # Optimal solution: all zeros (objective = 0)
    x = [DecisionVariable.binary(i) for i in range(3)]
    instance = Instance.from_components(
        decision_variables=x,
        objective=x[0] + x[1] + x[2],
        constraints=[],
        sense=Instance.MINIMIZE,
    )

    adapter = OMMXKipuIskayAdapter(instance)

    # Test decode with mock solution
    mock_solution = {str(x[0].id): 0, str(x[1].id): 0, str(x[2].id): 0}
    mock_solution_info = {
        "seed_transpiler": 42,
        "mapping": {str(x[0].id): 0, str(x[1].id): 1, str(x[2].id): 2},
    }
    mock_result = {"solution": mock_solution, "solution_info": mock_solution_info}

    solution = adapter.decode(mock_result)

    assert solution.state.entries[x[0].id] == 0
    assert solution.state.entries[x[1].id] == 0
    assert solution.state.entries[x[2].id] == 0
    assert solution.objective == pytest.approx(0.0)


def test_decode_to_state():
    # Test decode_to_state method
    x1 = DecisionVariable.binary(1)
    x2 = DecisionVariable.binary(2)
    instance = Instance.from_components(
        decision_variables=[x1, x2],
        objective=x1 + x2,
        constraints=[],
        sense=Instance.MINIMIZE,
    )

    adapter = OMMXKipuIskayAdapter(instance)

    # Test decode_to_state
    mock_solution = {str(x1.id): 1, str(x2.id): 0}
    state = adapter.decode_to_state(mock_solution)

    assert state.entries[x1.id] == 1
    assert state.entries[x2.id] == 0


def test_solver_input():
    # Test that solver_input returns a proper QUBO dictionary
    x1 = DecisionVariable.binary(1)
    x2 = DecisionVariable.binary(2)
    instance = Instance.from_components(
        decision_variables=[x1, x2],
        objective=2 * x1 - 3 * x2,
        constraints=[],
        sense=Instance.MINIMIZE,
    )

    adapter = OMMXKipuIskayAdapter(instance)
    qubo = adapter.solver_input

    # Check that QUBO is a dictionary with string keys
    assert isinstance(qubo, dict)
    assert str((x1.id,)) in qubo
    assert str((x2.id,)) in qubo


def test_solve_with_mock(mocker):
    # Test the full solve() method with mocked Qiskit components
    x1 = DecisionVariable.binary(1)
    x2 = DecisionVariable.binary(2)
    instance = Instance.from_components(
        decision_variables=[x1, x2],
        objective=x1 - 2 * x2,
        constraints=[],
        sense=Instance.MINIMIZE,
    )

    # Create mock job that returns a solution
    mock_job = mocker.Mock()
    mock_job.status.return_value = JobStatus.DONE
    mock_job.result.return_value = {
        "solution": {str(x1.id): 0, str(x2.id): 1},
        "solution_info": {
            "seed_transpiler": 42,
            "mapping": {str(x1.id): 0, str(x2.id): 1},
        },
    }

    # Create mock optimizer
    mock_optimizer = mocker.Mock()
    mock_optimizer.run.return_value = mock_job

    # Create mock catalog
    mock_catalog = mocker.Mock()
    mock_catalog.load.return_value = mock_optimizer

    # Patch QiskitFunctionsCatalog
    mock_catalog_class = mocker.patch(
        "ommx_kipu_iskay_adapter.adapter.QiskitFunctionsCatalog",
        return_value=mock_catalog,
    )

    # Call solve
    solution = OMMXKipuIskayAdapter.solve(
        ommx_instance=instance,
        token="fake_token",
        ibm_instance="fake_instance",
        backend_name="fake_backend",
        shots=100,
        num_iterations=1,
    )

    # Verify the solution
    assert solution.state.entries[x1.id] == 0
    assert solution.state.entries[x2.id] == 1
    assert solution.objective == pytest.approx(-2.0)

    # Verify that catalog was created with correct parameters
    mock_catalog_class.assert_called_once_with(
        token="fake_token",
        channel="ibm_cloud",
        instance="fake_instance",
    )

    # Verify that optimizer was loaded
    mock_catalog.load.assert_called_once_with("kipu-quantum/iskay-quantum-optimizer")

    # Verify that optimizer.run was called
    assert mock_optimizer.run.called


def test_solve_with_job_error(mocker):
    # Test that job errors are properly handled
    x1 = DecisionVariable.binary(1)
    x2 = DecisionVariable.binary(2)
    instance = Instance.from_components(
        decision_variables=[x1, x2],
        objective=x1 + x2,
        constraints=[],
        sense=Instance.MINIMIZE,
    )

    # Create mock job that returns an error
    mock_job = mocker.Mock()
    mock_job.status.return_value = JobStatus.ERROR
    mock_job.error_message.return_value = "Mock error message"

    # Create mock optimizer
    mock_optimizer = mocker.Mock()
    mock_optimizer.run.return_value = mock_job

    # Create mock catalog
    mock_catalog = mocker.Mock()
    mock_catalog.load.return_value = mock_optimizer

    # Patch QiskitFunctionsCatalog
    mocker.patch(
        "ommx_kipu_iskay_adapter.adapter.QiskitFunctionsCatalog",
        return_value=mock_catalog,
    )

    # Call solve and expect an error
    with pytest.raises(OMMXKipuIskayAdapterError) as e:
        OMMXKipuIskayAdapter.solve(
            ommx_instance=instance,
            token="fake_token",
            ibm_instance="fake_instance",
            backend_name="fake_backend",
        )

    assert "error occurred during the optimization job" in str(e.value)
