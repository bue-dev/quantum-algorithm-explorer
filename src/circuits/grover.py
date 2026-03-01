"""Grover's search algorithm — quadratic speedup for unstructured search."""

import math

from qiskit import QuantumCircuit


def _apply_oracle(qc: QuantumCircuit, marked_state: str) -> None:
    """Flip the sign of the marked state using a multi-controlled Z gate."""
    n = qc.num_qubits
    # Flip qubits where the marked state has a '0'
    for i, bit in enumerate(reversed(marked_state)):
        if bit == "0":
            qc.x(i)
    # Multi-controlled Z = H on last qubit, MCX, H on last qubit
    qc.h(n - 1)
    qc.mcx(list(range(n - 1)), n - 1)
    qc.h(n - 1)
    # Undo the flips
    for i, bit in enumerate(reversed(marked_state)):
        if bit == "0":
            qc.x(i)


def _apply_diffuser(qc: QuantumCircuit, n: int) -> None:
    """Grover diffusion operator (inversion about the mean)."""
    qc.h(range(n))
    qc.x(range(n))
    qc.h(n - 1)
    qc.mcx(list(range(n - 1)), n - 1)
    qc.h(n - 1)
    qc.x(range(n))
    qc.h(range(n))


def build_circuit(params: dict) -> QuantumCircuit:
    """Build a Grover's search circuit.

    Params:
        num_qubits: Number of qubits (default 3)
        marked_state: Binary string of the state to find (default "101")
        iterations: Number of Grover iterations (auto-calculated if not set)
    """
    num_qubits = params.get("num_qubits", 3)
    marked_state = params.get("marked_state", "101")
    iterations = params.get("iterations", None)

    if len(marked_state) != num_qubits:
        marked_state = marked_state.zfill(num_qubits)[:num_qubits]

    if iterations is None:
        iterations = max(1, int(math.pi / 4 * math.sqrt(2**num_qubits)))

    qc = QuantumCircuit(num_qubits, num_qubits)

    # Initialize uniform superposition
    qc.h(range(num_qubits))

    # Grover iterations
    for _ in range(iterations):
        _apply_oracle(qc, marked_state)
        _apply_diffuser(qc, num_qubits)

    # Measure
    qc.measure(range(num_qubits), range(num_qubits))
    return qc


def get_circuit_info(params: dict) -> dict:
    """Return metadata about the circuit."""
    num_qubits = params.get("num_qubits", 3)
    marked_state = params.get("marked_state", "101")
    iterations = params.get("iterations", None)
    if iterations is None:
        iterations = max(1, int(math.pi / 4 * math.sqrt(2**num_qubits)))

    return {
        "name": "Grover's Search Algorithm",
        "num_qubits": num_qubits,
        "iterations": iterations,
        "marked_state": marked_state,
        "description": (
            f"Searches for state |{marked_state}⟩ among {2**num_qubits} states "
            f"using {iterations} Grover iteration(s). "
            f"Classical requires O({2**num_qubits}) queries; "
            f"Grover's requires O(√{2**num_qubits}) ≈ {iterations} queries."
        ),
    }
