"""Static knowledge base of quantum algorithms and their properties."""

ALGORITHM_CATALOG: dict = {
    "grovers_search": {
        "name": "Grover's Search Algorithm",
        "categories": ["search", "optimization", "database"],
        "description": (
            "Provides a quadratic speedup for unstructured search problems. "
            "Given a search space of N items, finds a marked item in O(√N) "
            "evaluations instead of O(N) classically."
        ),
        "classical_complexity": "O(N)",
        "quantum_complexity": "O(√N)",
        "speedup_type": "quadratic",
        "best_for": [
            "unstructured database search",
            "satisfiability problems (SAT)",
            "constraint satisfaction",
            "finding specific items in unsorted data",
        ],
        "limitations": [
            "Requires construction of a quantum oracle",
            "Speedup is quadratic, not exponential",
            "Not efficient for structured/sorted data (use classical binary search)",
        ],
        "default_params": {
            "num_qubits": 3,
            "marked_state": "101",
        },
    },
    "deutsch_jozsa": {
        "name": "Deutsch-Jozsa Algorithm",
        "categories": ["decision", "oracle", "function_analysis"],
        "description": (
            "Determines with certainty whether a Boolean function is constant "
            "(same output for all inputs) or balanced (returns 0 for half the inputs "
            "and 1 for the other half) using a single function evaluation."
        ),
        "classical_complexity": "O(2^(n-1) + 1)",
        "quantum_complexity": "O(1)",
        "speedup_type": "exponential",
        "best_for": [
            "testing function properties",
            "determining if a function is constant or balanced",
            "demonstrating quantum advantage",
            "educational examples of quantum computing",
        ],
        "limitations": [
            "Only works for the specific promise problem (constant vs balanced)",
            "The promise must be satisfied (function must be either constant or balanced)",
            "Limited practical applications but strong theoretical significance",
        ],
        "default_params": {
            "num_qubits": 3,
            "oracle_type": "balanced",
            "pattern": "101",
        },
    },
    "bernstein_vazirani": {
        "name": "Bernstein-Vazirani Algorithm",
        "categories": ["hidden_information", "oracle", "cryptography"],
        "description": (
            "Finds a hidden bit string s encoded in an oracle function "
            "f(x) = s·x mod 2 using a single query. Classically, finding each bit "
            "requires a separate query, so n queries are needed for an n-bit string."
        ),
        "classical_complexity": "O(n)",
        "quantum_complexity": "O(1)",
        "speedup_type": "linear_to_constant",
        "best_for": [
            "extracting hidden information from oracles",
            "reverse-engineering linear Boolean functions",
            "educational demonstration of quantum parallelism",
            "cryptographic analysis scenarios",
        ],
        "limitations": [
            "Only works for linear functions (inner product with secret string)",
            "Requires the specific oracle structure",
            "The speedup is from n queries to 1, not exponential in problem size",
        ],
        "default_params": {
            "num_qubits": 3,
            "secret": "101",
        },
    },
    "qft": {
        "name": "Quantum Fourier Transform",
        "categories": ["transform", "signal_processing", "subroutine"],
        "description": (
            "The quantum analog of the Discrete Fourier Transform. Maps "
            "computational basis states to the frequency domain exponentially "
            "faster than classical FFT. A key subroutine in Shor's algorithm "
            "and quantum phase estimation."
        ),
        "classical_complexity": "O(n * 2^n)",
        "quantum_complexity": "O(n^2)",
        "speedup_type": "exponential",
        "best_for": [
            "frequency analysis",
            "period finding",
            "phase estimation",
            "subroutine for factoring algorithms",
        ],
        "limitations": [
            "Output is in the frequency domain (not directly readable as classical bits)",
            "Useful primarily as a subroutine rather than standalone",
            "Requires high-fidelity controlled rotations",
        ],
        "default_params": {
            "num_qubits": 3,
            "input_state": "101",
        },
    },
    "qaoa": {
        "name": "Quantum Approximate Optimization Algorithm (QAOA)",
        "categories": ["optimization", "combinatorial", "graph"],
        "description": (
            "Hybrid classical-quantum algorithm for combinatorial optimization. "
            "Uses alternating cost and mixer unitaries to approximately solve "
            "problems like MaxCut, TSP, and graph coloring."
        ),
        "classical_complexity": "O(2^N) for exact solution",
        "quantum_complexity": "Heuristic (not provably faster, but empirically promising)",
        "speedup_type": "heuristic",
        "best_for": [
            "MaxCut problems",
            "traveling salesman problem (TSP)",
            "graph coloring",
            "scheduling and resource allocation",
            "combinatorial optimization",
        ],
        "limitations": [
            "Heuristic — no proven exponential speedup",
            "Solution quality depends on circuit depth (p parameter)",
            "Requires classical optimizer for parameter tuning",
        ],
        "default_params": {
            "num_qubits": 4,
            "p_layers": 1,
        },
    },
    "vqe": {
        "name": "Variational Quantum Eigensolver (VQE)",
        "categories": ["simulation", "chemistry", "molecular"],
        "description": (
            "Hybrid classical-quantum algorithm for finding ground state energies "
            "of molecular Hamiltonians. Uses a parameterized quantum circuit "
            "(ansatz) optimized by a classical optimizer."
        ),
        "classical_complexity": "O(2^N) for exact diagonalization",
        "quantum_complexity": "Heuristic (polynomial circuit, classical optimization loop)",
        "speedup_type": "heuristic",
        "best_for": [
            "molecular ground state energy calculation",
            "quantum chemistry simulation",
            "materials science",
            "drug discovery molecular modeling",
        ],
        "limitations": [
            "Requires a classical optimization loop (not shown in simplified demo)",
            "Ansatz design significantly impacts results",
            "Noise on real hardware limits accuracy",
        ],
        "default_params": {
            "num_qubits": 2,
            "layers": 1,
        },
    },
}


def lookup_algorithms(problem_category: str) -> list[dict]:
    """Look up algorithms matching a problem category.

    Args:
        problem_category: Category to search for (e.g., "search", "optimization")

    Returns:
        List of matching algorithm entries.
    """
    category = problem_category.lower().strip()
    results = []
    for key, algo in ALGORITHM_CATALOG.items():
        categories = [c.lower() for c in algo["categories"]]
        best_for = " ".join(algo["best_for"]).lower()
        description = algo["description"].lower()

        if (
            category in categories
            or category in best_for
            or category in description
        ):
            results.append({"key": key, **algo})

    # If no exact match, return all algorithms for the agent to decide
    if not results:
        results = [{"key": key, **algo} for key, algo in ALGORITHM_CATALOG.items()]

    return results
