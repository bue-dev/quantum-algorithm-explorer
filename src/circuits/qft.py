"""Quantum Fourier Transform — fundamental building block of quantum algorithms."""

import math

from qiskit import QuantumCircuit


def build_circuit(params: dict) -> QuantumCircuit:
    """Build a QFT circuit.

    Params:
        num_qubits: Number of qubits (default 3)
        input_state: Binary string for initial state (default "101")
    """
    num_qubits = params.get("num_qubits", 3)
    input_state = params.get("input_state", "101")

    if len(input_state) != num_qubits:
        input_state = input_state.zfill(num_qubits)[:num_qubits]

    qc = QuantumCircuit(num_qubits, num_qubits)

    # Prepare input state
    for i, bit in enumerate(reversed(input_state)):
        if bit == "1":
            qc.x(i)

    qc.barrier()

    # QFT
    for i in range(num_qubits - 1, -1, -1):
        qc.h(i)
        for j in range(i - 1, -1, -1):
            angle = math.pi / (2 ** (i - j))
            qc.cp(angle, j, i)

    # Swap qubits for correct ordering
    for i in range(num_qubits // 2):
        qc.swap(i, num_qubits - 1 - i)

    qc.barrier()
    qc.measure(range(num_qubits), range(num_qubits))
    return qc


def get_circuit_info(params: dict) -> dict:
    """Return metadata about the circuit."""
    num_qubits = params.get("num_qubits", 3)
    input_state = params.get("input_state", "101")

    return {
        "name": "Quantum Fourier Transform",
        "num_qubits": num_qubits,
        "input_state": input_state,
        "description": (
            f"Applies the Quantum Fourier Transform to the {num_qubits}-qubit "
            f"state |{input_state}>. QFT maps computational basis states to "
            f"frequency domain, analogous to the classical Discrete Fourier Transform "
            f"but exponentially faster: O(n log n) vs O(n 2^n) classically."
        ),
    }
