"""Classical vs quantum complexity comparison utilities."""

import math

from src.tools.algorithm_catalog import ALGORITHM_CATALOG


def compare_complexity(algorithm_name: str, problem_size: int) -> dict:
    """Compare classical and quantum complexity for a given algorithm and problem size.

    Args:
        algorithm_name: Key from the algorithm catalog.
        problem_size: Size of the problem (e.g., number of items to search).

    Returns:
        Dictionary with classical/quantum step counts and comparison.
    """
    if algorithm_name not in ALGORITHM_CATALOG:
        return {"error": f"Unknown algorithm: {algorithm_name}"}

    algo = ALGORITHM_CATALOG[algorithm_name]

    comparisons = {
        "grovers_search": _compare_grover(problem_size),
        "deutsch_jozsa": _compare_deutsch_jozsa(problem_size),
        "bernstein_vazirani": _compare_bernstein_vazirani(problem_size),
        "qft": _compare_qft(problem_size),
        "qaoa": _compare_qaoa(problem_size),
        "vqe": _compare_vqe(problem_size),
    }

    comparison = comparisons.get(algorithm_name, _default_comparison(algo))

    return {
        "algorithm": algo["name"],
        "problem_size": problem_size,
        "classical_complexity": algo["classical_complexity"],
        "quantum_complexity": algo["quantum_complexity"],
        "speedup_type": algo["speedup_type"],
        **comparison,
    }


def _compare_grover(n: int) -> dict:
    classical_steps = n
    quantum_steps = max(1, int(math.pi / 4 * math.sqrt(n)))
    speedup = classical_steps / quantum_steps if quantum_steps > 0 else float("inf")
    return {
        "classical_steps": classical_steps,
        "quantum_steps": quantum_steps,
        "speedup_factor": round(speedup, 2),
        "explanation": (
            f"For {n} items: classical linear search needs up to {classical_steps} "
            f"queries. Grover's algorithm needs ~{quantum_steps} iterations, "
            f"a {speedup:.1f}x speedup."
        ),
    }


def _compare_deutsch_jozsa(n: int) -> dict:
    # n here is the number of input bits
    classical_steps = 2 ** (n - 1) + 1 if n > 0 else 1
    quantum_steps = 1
    speedup = classical_steps / quantum_steps
    return {
        "classical_steps": classical_steps,
        "quantum_steps": quantum_steps,
        "speedup_factor": round(speedup, 2),
        "explanation": (
            f"For a {n}-bit function: classical worst case needs {classical_steps} "
            f"evaluations to distinguish constant from balanced. "
            f"Deutsch-Jozsa needs exactly 1 evaluation — "
            f"an exponential speedup ({speedup:.0f}x)."
        ),
    }


def _compare_bernstein_vazirani(n: int) -> dict:
    # n is the number of bits in the secret string
    classical_steps = n
    quantum_steps = 1
    speedup = n if n > 0 else 1
    return {
        "classical_steps": classical_steps,
        "quantum_steps": quantum_steps,
        "speedup_factor": round(speedup, 2),
        "explanation": (
            f"For a {n}-bit secret string: classically need {classical_steps} "
            f"queries (one per bit). Bernstein-Vazirani finds all {n} bits "
            f"in a single query — a {speedup}x speedup."
        ),
    }


def _compare_qft(n: int) -> dict:
    # n is the number of qubits
    classical_steps = n * (2**n)
    quantum_steps = n * n
    speedup = classical_steps / quantum_steps if quantum_steps > 0 else float("inf")
    return {
        "classical_steps": classical_steps,
        "quantum_steps": quantum_steps,
        "speedup_factor": round(speedup, 2),
        "explanation": (
            f"For {n} qubits: classical DFT on 2^{n}={2**n} points needs "
            f"O({classical_steps}) operations. QFT needs O({quantum_steps}) gates — "
            f"an exponential speedup ({speedup:.1f}x)."
        ),
    }


def _compare_qaoa(n: int) -> dict:
    # n is the number of graph nodes
    classical_steps = 2**n
    quantum_steps = n * 10  # rough estimate for p=1 QAOA circuit
    speedup = classical_steps / quantum_steps if quantum_steps > 0 else float("inf")
    return {
        "classical_steps": classical_steps,
        "quantum_steps": quantum_steps,
        "speedup_factor": round(speedup, 2),
        "explanation": (
            f"For a {n}-node graph: exact classical MaxCut needs O(2^{n})={2**n} "
            f"evaluations. QAOA is heuristic with ~{quantum_steps} gate operations "
            f"for p=1. Speedup is not guaranteed but empirically promising."
        ),
    }


def _compare_vqe(n: int) -> dict:
    # n is the number of qubits (representing molecular orbitals)
    classical_steps = 2**n
    quantum_steps = n * 5  # rough: gates per VQE iteration
    speedup = classical_steps / quantum_steps if quantum_steps > 0 else float("inf")
    return {
        "classical_steps": classical_steps,
        "quantum_steps": quantum_steps,
        "speedup_factor": round(speedup, 2),
        "explanation": (
            f"For {n} molecular orbitals: classical exact diagonalization needs "
            f"O(2^{n})={2**n} operations. VQE circuit uses ~{quantum_steps} gates "
            f"per iteration, but requires many classical optimization iterations."
        ),
    }


def _default_comparison(algo: dict) -> dict:
    return {
        "classical_steps": "varies",
        "quantum_steps": "varies",
        "speedup_factor": "see description",
        "explanation": (
            f"Classical: {algo['classical_complexity']}, "
            f"Quantum: {algo['quantum_complexity']}. "
            f"Speedup type: {algo['speedup_type']}."
        ),
    }
