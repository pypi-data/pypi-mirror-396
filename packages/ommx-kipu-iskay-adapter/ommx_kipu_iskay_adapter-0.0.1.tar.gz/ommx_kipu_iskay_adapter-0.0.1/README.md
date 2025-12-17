# ommx-kipu-iskay-adapter
This package provides an adapter for [Kipu Iskay quantum optimiser through IBM's Qiskit Functions Catalog](https://quantum.cloud.ibm.com/docs/en/guides/kipu-optimization) from OMMX.

[OMMX](https://github.com/Jij-Inc/OMMX) (Open Mathematical programming Modeling eXtension) is an open standard for representing mathematical optimisation problems. It provides a unified interface for defining and solving optimisation problems across different solvers. This means that OMMX makes it easy to compare quantum and classical solvers. For instance, you can use this library to solve problems in OMMX format with quantum algorithms. There are also several other adapters such as for PySCIPOpt (classical) and D-Wave (quantum annealing):

* [ommx-pyscipopt-adapter](https://github.com/Jij-Inc/ommx/tree/main/python/ommx-pyscipopt-adapter)
* [ommx-dwave-adapter](https://github.com/Jij-Inc/ommx-dwave-adapter)
* [and more](https://ommx-en-book.readthedocs.io/en/latest/user_guide/supported_ommx_adapters.html)

Furthermore, it has rich functionalities such as converting constrained problems into unconstrained ones ([to_qubo](https://jij-inc.github.io/ommx/python/ommx/autoapi/ommx/v1/index.html#ommx.v1.Instance.to_qubo)/[to_hubo](https://jij-inc.github.io/ommx/python/ommx/autoapi/ommx/v1/index.html#ommx.v1.Instance.to_hubo)). All you have got to do is define your original problems in OMMX format. OMMX enables you to convert those problems into QUBO/HUBO ones when needed. For more information, see the [OMMX tutorial](https://jij-inc.github.io/ommx/en/).

## Prerequisites
Before using the Kipu Iskay adapter, you need:

* IBM Quantum Account: Sign up at IBM Quantum
* API Token: Obtain your API token from the IBM Quantum dashboard
* Instance CRN: Get your IBM Quantum instance CRN (Cloud Resource Name)
* Access to Iskay: Ensure you have access to the Kipu Iskay function in the [IBM Quantum Functions Catalog](https://quantum.cloud.ibm.com/functions)

> **Warning**: Running quantum optimisation jobs incurs costs on IBM Quantum. Make sure you understand the pricing before running jobs.

## Installation
`ommx-kipu-iskay-adapter` can be installed from PyPI:

```bash
pip install ommx-kipu-iskay-adapter
```

## Understanding Iskay Quantum Optimiser
Iskay is a quantum optimisation solver developed by [Kipu Quantum](https://kipu-quantum.com/), available on the IBM Quantum Functions Catalog. It is designed to solve unconstrained binary optimisation problems (QUBO/HUBO) using quantum hardware.

> **Tip**: If you have a constrained optimisation problem, you can convert it to an unconstrained QUBO/HUBO formulation using OMMX's `to_qubo` or `to_hubo` methods, which means you don't need to manually convert the problem into QUBO/HUBO.

## Usage
### Starting with OMMX problem
Here is a simple example of how to use the adapter directly.

#### 1. Define your problem in OMMX format
First, define your optimisation problem using OMMX. If you have got constrained problems, no worries! `ommx.v1.Instance` provides `to_qubo`/`to_hubo` methods that convert the instance itself into QUBO/HUBO format as you will see below.

```python
from ommx.v1 import Instance, DecisionVariable

# Create binary decision variables
x0 = DecisionVariable.binary(0)
x1 = DecisionVariable.binary(1)
x2 = DecisionVariable.binary(2)

# Define the objective function
# Example: Minimize x0 + x1 - 2*x2 + x0*x1
objective = x0 + x1 - 2*x2 + x0*x1

# Create the OMMX instance with constraint
instance = Instance.from_components(
    decision_variables=[x0, x1, x2],
    objective=objective,
    constraints=[x0 + x1 + x2 == 1],  # Only one variable can be 1
    sense=Instance.MINIMIZE,
)

# Convert to QUBO/HUBO (unconstrained)
instance.to_qubo(uniform_penalty_weight=2.0)
```

#### 2. Solve with Iskay
Solve your problems with Kipu Iskay quantum optimiser. Note that you must provide credentials to the adapter to connect to the Qiskit Functions Catalog.

* `token`: IBM Quantum API token for authentication.
* `ibm_instance`: The IBM Quantum instance (CRN) to use.
* `backend_name`: The name of the backend to run the optimisation on.
* `channel`: The channel to use for IBM Quantum services. Options are "ibm_cloud" or "ibm_quantum". Default is "ibm_cloud".

```python
from ommx_kipu_iskay_adapter import OMMXKipuIskayAdapter

# Your IBM Quantum credentials
IBM_TOKEN = "your_ibm_quantum_token"
IBM_INSTANCE = "your_ibm_instance_crn"
BACKEND_NAME = "your_favourite_backend"
CHANNEL = "ibm_cloud"

# Solve the QUBO problem
solution = OMMXKipuIskayAdapter.solve(
    ommx_instance=instance,
    token=IBM_TOKEN,
    ibm_instance=IBM_INSTANCE,
    backend_name=BACKEND_NAME,
    channel=CHANNEL,
    shots=1000,
    num_iterations=5,
)
```

#### 3. Analyse the result
You will have `ommx.v1.Solution` instance as the returned value. You can do whatever you want with it such as follows.

```python
# Get the objective value
print(f"Objective value: {solution.objective}")
# Access solver metadata
print(f"Solver: {solution.solver}")
```

### Advanced options
The `solve` method accepts several optional parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `shots` | int | 10000 | Number of quantum measurements per iteration |
| `num_iterations` | int | 10 | Number of optimisation rounds |
| `use_session` | bool | True | Keep quantum session alive between iterations |
| `seed_transpiler` | int | None | Seed for transpiler reproducibility |
| `direct_qubit_mapping` | bool | False | Use direct qubit mapping |
| `job_tags` | list[str] | None | Tags for job tracking |
| `job_pkl_output_name` | str | None | Path to save job object |

### Working with Results Separately
If you have results from a previous Iskay job, you can decode them separately. For more information about results of Iskay, see [Output section of the Iskay quantum optimiser document](https://quantum.cloud.ibm.com/docs/en/guides/kipu-optimization#output).

```python
from ommx_kipu_iskay_adapter import OMMXKipuIskayAdapter

# Create the adapter with your QUBO instance
adapter = OMMXKipuIskayAdapter(instance)

# Decode results from Iskay
iskay_result = {
    "solution": {"0": 0, "1": 1, "2": 1},
    "solution_info": {
        "seed_transpiler": 42,
        "mapping": {"0": 0, "1": 1, "2": 2}
    }
}

solution = adapter.decode(iskay_result)
print(f"Objective: {solution.objective}")
```

## Error Handling
The adapter raises `OMMXKipuIskayAdapterError` for various error conditions:

- **No decision variables**: The instance has no decision variables
- **Non-binary variables**: Iskay only supports binary variables
- **Constraints present**: Iskay only supports unconstrained problems
- **Job error**: Check the IBM Quantum dashboard for details

## Contribution
The packages required for development can be installed by `uv`:

```bash
uv sync --all-extras
```

Use the following commands to test, lint and format.

```bash
uv run pytest
uv run black ./
```

## References
- [Iskay Documentation](https://quantum.cloud.ibm.com/docs/en/guides/kipu-optimization)
- [IBM Quantum Function Catalog](https://quantum.ibm.com/functions)
- [OMMX Documentation](https://jij-inc.github.io/ommx/en/)