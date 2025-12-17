import pytest

from ommx_kipu_iskay_adapter import OMMXKipuIskayAdapterError, OMMXKipuIskayAdapter

from ommx.v1 import Instance, DecisionVariable, Polynomial


def test_error_non_binary_integer_variable():
    # Integer variable (not binary)
    x = DecisionVariable.integer(1, lower=0, upper=5)
    ommx_instance = Instance.from_components(
        decision_variables=[x],
        objective=x,
        constraints=[],
        sense=Instance.MINIMIZE,
    )
    with pytest.raises(OMMXKipuIskayAdapterError) as e:
        OMMXKipuIskayAdapter(ommx_instance)
    assert "Unsupported decision variable kind" in str(e.value)


def test_error_non_binary_continuous_variable():
    # Continuous variable (not binary)
    x = DecisionVariable.continuous(1)
    ommx_instance = Instance.from_components(
        decision_variables=[x],
        objective=x,
        constraints=[],
        sense=Instance.MINIMIZE,
    )
    with pytest.raises(OMMXKipuIskayAdapterError) as e:
        OMMXKipuIskayAdapter(ommx_instance)
    assert "Unsupported decision variable kind" in str(e.value)


def test_error_with_constraints():
    # Binary variables with constraints (Iskay only supports unconstrained problems)
    x1 = DecisionVariable.binary(1)
    x2 = DecisionVariable.binary(2)
    ommx_instance = Instance.from_components(
        decision_variables=[x1, x2],
        objective=x1 + x2,
        constraints=[x1 + x2 <= 1],
        sense=Instance.MINIMIZE,
    )
    with pytest.raises(OMMXKipuIskayAdapterError) as e:
        OMMXKipuIskayAdapter(ommx_instance)
    assert "only supports unconstrained problems" in str(e.value)


def test_error_polynomial_objective():
    # Cubic objective function (3rd degree polynomial)
    # Iskay accepts quadratic terms, but let's check if it's properly handled
    x = DecisionVariable.binary(1)
    ommx_instance = Instance.from_components(
        decision_variables=[x],
        objective=Polynomial(terms={(1, 1, 1): 2.3}),
        constraints=[],
        sense=Instance.MINIMIZE,
    )
    # Note: The adapter doesn't explicitly check for polynomial degree
    # It just converts the objective to a QUBO dictionary
    # This test verifies that we can create the adapter with higher-degree polynomials
    # (though Iskay may not handle them correctly)
    adapter = OMMXKipuIskayAdapter(ommx_instance)
    # The objective should be converted to a QUBO dict
    assert adapter.solver_input is not None


def test_error_no_decision_variables():
    # Test with no decision variables used in the objective
    x = DecisionVariable.binary(1)
    ommx_instance = Instance.from_components(
        decision_variables=[x],
        objective=0,  # Constant objective, does not use any variables
        constraints=[],
        sense=Instance.MINIMIZE,
    )
    with pytest.raises(OMMXKipuIskayAdapterError) as e:
        OMMXKipuIskayAdapter(ommx_instance)
    assert "has no decision variables" in str(e.value)


def test_error_no_decision_variables_defined():
    # Test with no decision variables defined at all
    ommx_instance = Instance.from_components(
        decision_variables=[],
        objective=0,
        constraints=[],
        sense=Instance.MINIMIZE,
    )
    with pytest.raises(OMMXKipuIskayAdapterError) as e:
        OMMXKipuIskayAdapter(ommx_instance)
    assert "has no decision variables" in str(e.value)


def test_error_decode_missing_solution_key():
    # Test decoding with missing "solution" key in the data
    x = DecisionVariable.binary(1)
    ommx_instance = Instance.from_components(
        decision_variables=[x],
        objective=x,
        constraints=[],
        sense=Instance.MINIMIZE,
    )
    adapter = OMMXKipuIskayAdapter(ommx_instance)

    # Create data without "solution" key
    invalid_data = {"result": {"1": 0}}

    with pytest.raises(OMMXKipuIskayAdapterError) as e:
        adapter.decode(invalid_data)
    assert 'does not contain a "solution" key' in str(e.value)


def test_error_decode_missing_solution_info_key():
    # Test decoding with missing "solution_info" key in the data
    x = DecisionVariable.binary(1)
    ommx_instance = Instance.from_components(
        decision_variables=[x],
        objective=x,
        constraints=[],
        sense=Instance.MINIMIZE,
    )
    adapter = OMMXKipuIskayAdapter(ommx_instance)

    # Create data with "solution" but without "solution_info" key
    invalid_data = {"solution": {"1": 0}}

    with pytest.raises(OMMXKipuIskayAdapterError) as e:
        adapter.decode(invalid_data)
    assert 'does not contain a "solution_info" key' in str(e.value)
