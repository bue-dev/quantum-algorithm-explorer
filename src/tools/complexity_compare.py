"""Classical vs quantum complexity comparison utilities."""

import math

from src.tools.algorithm_catalog import ALGORITHM_CATALOG

MAX_EXPONENT = 64  # Prevent overflow in 2**n calculations


def _safe_speedup(classical: int, quantum: int) -> float:
    """Compute speedup factor without float overflow."""
    if quantum <= 0:
        return float("inf")
    try:
        return round(classical / quantum, 2)
    except OverflowError:
        return float("inf")


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
    speedup = _safe_speedup(classical_steps, quantum_steps)
    return {
        "classical_steps": classical_steps,
        "quantum_steps": quantum_steps,
        "speedup_factor": speedup,
        "explanation": (
            f"For {n} items: classical linear search needs up to {classical_steps} "
            f"queries. Grover's algorithm needs ~{quantum_steps} iterations, "
            f"a ~{speedup}x speedup."
        ),
    }


def _compare_deutsch_jozsa(n: int) -> dict:
    # n here is the number of input bits
    n_clamped = min(n, MAX_EXPONENT)
    classical_steps = 2 ** (n_clamped - 1) + 1 if n_clamped > 0 else 1
    quantum_steps = 1
    speedup = _safe_speedup(classical_steps, quantum_steps)
    return {
        "classical_steps": classical_steps,
        "quantum_steps": quantum_steps,
        "speedup_factor": speedup,
        "explanation": (
            f"For a {n}-bit function: classical worst case needs {classical_steps} "
            f"evaluations to distinguish constant from balanced. "
            f"Deutsch-Jozsa needs exactly 1 evaluation — "
            f"an exponential speedup ({speedup}x)."
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
    n_clamped = min(n, MAX_EXPONENT)
    classical_steps = n_clamped * (2**n_clamped)
    quantum_steps = n_clamped * n_clamped
    speedup = _safe_speedup(classical_steps, quantum_steps)
    return {
        "classical_steps": classical_steps,
        "quantum_steps": quantum_steps,
        "speedup_factor": speedup,
        "explanation": (
            f"For {n} qubits: classical DFT on 2^{n}={2**n_clamped} points needs "
            f"O({classical_steps}) operations. QFT needs O({quantum_steps}) gates — "
            f"an exponential speedup ({speedup}x)."
        ),
    }


def _compare_qaoa(n: int) -> dict:
    # n is the number of graph nodes
    n_clamped = min(n, MAX_EXPONENT)
    classical_steps = 2**n_clamped
    quantum_steps = n * 10  # rough estimate for p=1 QAOA circuit
    speedup = _safe_speedup(classical_steps, quantum_steps)
    return {
        "classical_steps": classical_steps,
        "quantum_steps": quantum_steps,
        "speedup_factor": speedup,
        "explanation": (
            f"For a {n}-node graph: exact classical MaxCut needs O(2^{n})={2**n_clamped} "
            f"evaluations. QAOA is heuristic with ~{quantum_steps} gate operations "
            f"for p=1. Speedup is not guaranteed but empirically promising."
        ),
    }


def _compare_vqe(n: int) -> dict:
    # n is the number of qubits (representing molecular orbitals)
    n_clamped = min(n, MAX_EXPONENT)
    classical_steps = 2**n_clamped
    quantum_steps = n * 5  # rough: gates per VQE iteration
    speedup = _safe_speedup(classical_steps, quantum_steps)
    return {
        "classical_steps": classical_steps,
        "quantum_steps": quantum_steps,
        "speedup_factor": speedup,
        "explanation": (
            f"For {n} molecular orbitals: classical exact diagonalization needs "
            f"O(2^{n})={2**n_clamped} operations. VQE circuit uses ~{quantum_steps} gates "
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
