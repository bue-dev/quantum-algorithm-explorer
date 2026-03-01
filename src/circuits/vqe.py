"""VQE — Variational Quantum Eigensolver for molecular simulation (simplified)."""

import math

from qiskit import QuantumCircuit


def build_circuit(params: dict) -> QuantumCircuit:
    """Build a simplified VQE ansatz circuit.

    This is a hardware-efficient ansatz (not a full VQE optimization loop).
    It demonstrates the variational circuit structure used in VQE.

    Params:
        num_qubits: Number of qubits (default 2, for H2 molecule)
        layers: Number of variational layers (default 1)
        theta: List of rotation angles (default: pre-optimized for H2)
    """
    num_qubits = params.get("num_qubits", 2)
    layers = params.get("layers", 1)
    # Pre-optimized angles for H2 ground state at bond distance ~0.735 A
    default_theta = [0.0, math.pi] + [0.0] * (num_qubits * layers * 2)
    theta = params.get("theta", default_theta)

    qc = QuantumCircuit(num_qubits, num_qubits)

    idx = 0
    # Initial state preparation
    for i in range(num_qubits):
        if idx < len(theta):
            qc.ry(theta[idx], i)
            idx += 1

    # Variational layers
    for _ in range(layers):
        # Entangling layer
        for i in range(num_qubits - 1):
            qc.cx(i, i + 1)

        # Rotation layer
        for i in range(num_qubits):
            if idx < len(theta):
                qc.ry(theta[idx], i)
                idx += 1
            if idx < len(theta):
                qc.rz(theta[idx], i)
                idx += 1

    qc.measure(range(num_qubits), range(num_qubits))
    return qc


def get_circuit_info(params: dict) -> dict:
    """Return metadata about the circuit."""
    num_qubits = params.get("num_qubits", 2)
    layers = params.get("layers", 1)

    return {
        "name": "Variational Quantum Eigensolver (VQE)",
        "num_qubits": num_qubits,
        "layers": layers,
        "description": (
            f"Hardware-efficient VQE ansatz with {num_qubits} qubits and "
            f"{layers} variational layer(s). VQE is a hybrid classical-quantum "
            f"algorithm for finding ground state energies of molecules. "
            f"This demonstrates the quantum circuit structure; a full VQE "
            f"would include a classical optimizer loop. "
            f"Classical exact diagonalization scales as O(2^{num_qubits})."
        ),
    }
