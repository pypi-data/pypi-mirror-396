from __future__ import annotations
import json
import pickle
from typing import Literal

from qiskit.providers.jobstatus import JobStatus
from qiskit_ibm_catalog import QiskitFunctionsCatalog


from ommx.adapter import SolverAdapter
from ommx.v1 import (
    Instance,
    Solution,
    DecisionVariable,
    State,
)

from .exception import OMMXKipuIskayAdapterError

type Channel = Literal["ibm_cloud", "ibm_quantum"]


class OMMXKipuIskayAdapter(SolverAdapter):
    """OMMX adapter for Iskay quantum optimizer.
    See https://quantum.cloud.ibm.com/docs/en/guides/kipu-optimization for more details regarding Iskay.
    """

    def __init__(
        self,
        ommx_instance: Instance,
        *,
        shots: int = 10000,
        num_iterations: int = 10,
        use_session: bool = True,
        seed_transpiler: int | None = None,
        direct_qubit_mapping: bool = False,
        job_tags: list[str] | None = None,
    ):
        """Initialize the OMMXKipuIskayAdapter.

        Args:
            ommx_instance (Instance): The ommx.v1.Instance to solve.
            shots (int): Number of quantum measurements per iteration.
            num_iterations (int): Number of optimization rounds to run.
            use_session (bool): Whether to keep the quantum session alive between iterations.
            seed_transpiler (int | None): Seed for the transpiler.
            direct_qubit_mapping (bool): Whether to use direct qubit mapping.
            job_tags (list[str] | None): Tags for tracking jobs in the IBM Quantum dashboard.
        """
        self.instance = ommx_instance
        self.options = {
            "shots": shots,
            "num_iterations": num_iterations,
            "use_session": use_session,
            "seed_transpiler": seed_transpiler,
            "direct_qubit_mapping": direct_qubit_mapping,
            "job_tags": job_tags,
        }
        self._check_decision_variables()
        self._set_objective()
        self._check_constraints()

    @classmethod
    def solve(
        cls,
        ommx_instance: Instance,
        token: str,
        ibm_instance: str,
        backend_name: str,
        *,
        channel: Channel = "ibm_cloud",
        shots: int = 10000,
        num_iterations: int = 10,
        use_session: bool = True,
        seed_transpiler: int | None = None,
        direct_qubit_mapping: bool = False,
        job_tags: list[str] | None = None,
        job_pkl_output_name: str | None = None,
    ) -> Solution:
        """Solve the given ommx.v1.Instance using Iskay by Kipu on Qiskit Function Catalog.

        Args:
            ommx_instance (Instance): The ommx.v1.Instance to solve.
            token (str): IBM Quantum API token for authentication.
            ibm_instance (str): The IBM Quantum instance (CRN) to use.
            backend_name (str): The name of the backend to run the optimization on.
            channel (Channel): The channel to use for IBM Quantum services. Options are "ibm_cloud" or "ibm_quantum". Default is "ibm_cloud".
            shots (int): Number of quantum measurements per iteration.
            num_iterations (int): Number of optimization rounds to run.
            use_session (bool): Whether to keep the quantum session alive between iterations.
            seed_transpiler (int | None): Seed for the transpiler.
            direct_qubit_mapping (bool): Whether to use direct qubit mapping.
            job_tags (list[str] | None): Tags for tracking jobs in the IBM Quantum dashboard.
            job_pkl_output_name (str | None): Name for the job output in pickle format. Default is None.
                If this is provided, the job result will be saved with this name. Otherwise, it won't be saved.

        Returns:
            Solution: An ommx.v1.Solution representing the solution to the optimization problem.

        Examples
        =========

        Basic QUBO Problem

        .. doctest::

            >>> from ommx.v1 import Instance, DecisionVariable
            >>> from ommx_kipu_iskay_adapter import OMMXKipuIskayAdapter

            >>> # Define binary decision variables
            >>> x = [DecisionVariable.binary(i) for i in range(3)]
            >>>
            >>> # Create an unconstrained QUBO problem: minimize x0 - 2*x1 + x2 + x0*x1
            >>> instance = Instance.from_components(
            ...     decision_variables=x,
            ...     objective=x[0] - 2*x[1] + x[2] + x[0]*x[1],
            ...     constraints=[],  # Iskay only supports unconstrained problems
            ...     sense=Instance.MINIMIZE,
            ... )
            >>>
            >>> # Solve using Iskay (requires valid IBM Quantum credentials)
            >>> solution = OMMXKipuIskayAdapter.solve(
            ...     ommx_instance=instance,
            ...     token="your_ibm_quantum_token",
            ...     ibm_instance="your_ibm_instance_crn",
            ...     backend_name="ibm_kyoto",
            ...     shots=1000,
            ...     num_iterations=5,
            ... )
            >>>
            >>> # Check the solution
            >>> solution.feasible
            True
            >>> solution.state.entries  # Variable assignments
            {0: ..., 1: ..., 2: ...}
        """
        adapter = cls(
            ommx_instance,
            shots=shots,
            num_iterations=num_iterations,
            use_session=use_session,
            seed_transpiler=seed_transpiler,
            direct_qubit_mapping=direct_qubit_mapping,
            job_tags=job_tags,
        )

        catalog = QiskitFunctionsCatalog(
            token=token, channel=channel, instance=ibm_instance
        )
        optimizer = catalog.load("kipu-quantum/iskay-quantum-optimizer")

        problem = adapter.solver_input

        # Set the arguments for Iskay.
        arguments = {
            "problem": problem,
            "problem_type": "binary",
            "instance": ibm_instance,
            "backend_name": backend_name,
            "options": adapter.options,
        }

        # Run the optimization.
        print("Submitting job to quantum backend...")
        job = optimizer.run(**arguments)
        if job_pkl_output_name is not None:
            with open(job_pkl_output_name, "wb") as pickle_file:
                pickle.dump(job, pickle_file)
            print(f"Job result saved to {job_pkl_output_name}")
        print("Waiting for results (this may take a while)...")

        # Process the job according to its status.
        if job.status() == JobStatus.ERROR:
            raise OMMXKipuIskayAdapterError(
                "An error occurred during the optimization job:"
                f"{job.error_message()}. "
                "Please check your IBM Quantum dashboard for more details."
            )

        result = job.result()

        return adapter.decode(result)

    @property
    def solver_input(self) -> dict:
        """Get HUBO/QUBO dict from OMMX instance.

        Returns:
            dict: The HUBO/QUBO as a dictionary.
        """
        return self.problem

    def decode(self, data: dict) -> Solution:
        """Convert optimized Iskay result and ommx.v1.Instance to ommx.v1.Solution.

        This method is intended to be used if you want to process Iskay results
        that were obtained separately from the solve() method.

        Args:
            data (dict): The result dictionary from Iskay optimizer containing a "solution" key
                with variable assignments.

        Returns:
            Solution: An ommx.v1.Solution representing the solution to the optimization problem.

        Raises:
            OMMXKipuIskayAdapterError: If the "solution" key is missing in the data.
            OMMXKipuIskayAdapterError: If the "solution_info" key is missing in the data.

        Examples
        =========

        .. doctest::

            >>> from ommx_kipu_iskay_adapter import OMMXKipuIskayAdapter
            >>> from ommx.v1 import Instance, DecisionVariable

            >>> # Create a simple QUBO problem
            >>> x = [DecisionVariable.binary(i) for i in range(3)]
            >>> instance = Instance.from_components(
            ...     decision_variables=x,
            ...     objective=x[0] - 2*x[1] + x[2],
            ...     constraints=[],
            ...     sense=Instance.MINIMIZE,
            ... )
            >>>
            >>> adapter = OMMXKipuIskayAdapter(instance)
            >>>
            >>> # Assume we obtained Iskay result separately
            >>> iskay_result = {"solution": {"0": 0, "1": 1, "2": 0}}
            >>>
            >>> solution = adapter.decode(iskay_result)
            >>> solution.objective
            -2.0
        """
        solution_data = data.get("solution")
        if solution_data is None:
            raise OMMXKipuIskayAdapterError(
                'The provided data does not contain a "solution" key.'
            )
        solution_info = data.get("solution_info")
        if solution_info is None:
            raise OMMXKipuIskayAdapterError(
                'The provided data does not contain a "solution_info" key.'
            )

        state = self.decode_to_state(solution_data)
        solution = self.instance.evaluate(state)

        # Attach the annotations.
        solution.solver = "Iskay Quantum Optimizer"
        solution.annotations["solution_info.seed_transpiler"] = str(
            solution_info["seed_transpiler"]
        )
        solution.annotations["solution_info.mapping"] = json.dumps(
            solution_info["mapping"]
        )

        return solution

    def decode_to_state(self, solution: dict[str, int]) -> State:
        """Create an ommx.v1.State from an Iskay solution dictionary.

        Args:
            solution (dict[str, int]): The Iskay solution as a dictionary mapping variable IDs (as strings) to values.

        Returns:
            State: An ommx.v1.State representing the variable assignments.

        Examples
        =========

        .. doctest::

            >>> from ommx_kipu_iskay_adapter import OMMXKipuIskayAdapter
            >>> from ommx.v1 import Instance, DecisionVariable

            >>> # Create a simple binary optimization problem
            >>> x0 = DecisionVariable.binary(0)
            >>> x1 = DecisionVariable.binary(1)
            >>> ommx_instance = Instance.from_components(
            ...     decision_variables=[x0, x1],
            ...     objective=x0 - 2*x1,
            ...     constraints=[],
            ...     sense=Instance.MINIMIZE,
            ... )
            >>> adapter = OMMXKipuIskayAdapter(ommx_instance)
            >>>
            >>> # Assume Iskay returned this solution
            >>> iskay_solution = {"0": 0, "1": 1}
            >>>
            >>> ommx_state = adapter.decode_to_state(iskay_solution)
            >>> ommx_state.entries
            {0: 0, 1: 1}

        """
        # In self._set_objective, we converted keys of each term to str.
        # Those keys correspond to variable IDs.
        # Thus, what we get from Iskay is a mapping from variable ID (as str) to value.
        return State(
            entries={
                var.id: solution[str(var.id)]
                for var in self.instance.used_decision_variables
            }
        )

    def _check_decision_variables(self) -> None:
        """Check the decision variables.

        Raise an error if there are any non-binary variables because Iskay accepts only binary (or spin, which is binary).

        Raises:
            OMMXKipuIskayAdapterError: If there are no decision variables.
            OMMXKipuIskayAdapterError: If there are any non-binary variables.
        """
        if len(self.instance.used_decision_variables) == 0:
            raise OMMXKipuIskayAdapterError("The instance has no decision variables.")

        for var in self.instance.used_decision_variables:
            if var.kind != DecisionVariable.BINARY:
                raise OMMXKipuIskayAdapterError(
                    f"Unsupported decision variable kind: "
                    f"id: {var.id}, kind: {var.kind}"
                )

    def _set_objective(self) -> None:
        """Set the objective function.

        Iskay only supports minimization, so if the instance is a maximization problem, the coefficients are negated.

        Raises:
            OMMXKipuIskayAdapterError: If the instance's sense is neither MAXIMIZE nor MINIMIZE.
        """
        # Iskay minimises the objective function.
        if self.instance.sense == Instance.MAXIMIZE:
            correct_phase = -1
        elif self.instance.sense == Instance.MINIMIZE:
            correct_phase = +1
        else:
            raise OMMXKipuIskayAdapterError(
                f"Sense not supported: {self.instance.sense}"
            )

        self.problem = {}
        terms = self.instance.objective.terms
        for key, coeff in terms.items():
            self.problem[str(key)] = correct_phase * float(coeff)

    def _check_constraints(self) -> None:
        """Check the constraints.

        Raise an error if there are any constraints because Iskay only supports unconstrained problem.

        Raises:
            OMMXKipuIskayAdapterError: If there are any constraints.
        """
        if len(self.instance.constraints) > 0:
            raise OMMXKipuIskayAdapterError(
                "Iskay optimizer only supports unconstrained problems."
            )
