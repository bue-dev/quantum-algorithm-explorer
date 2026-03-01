"""Deutsch-Jozsa algorithm — determines if a function is constant or balanced in one query."""

from qiskit import QuantumCircuit


def _apply_balanced_oracle(qc: QuantumCircuit, n: int, pattern: str) -> None:
    """Apply a balanced oracle that flips the ancilla for states matching the pattern.

    The pattern determines which input qubits control the ancilla flip.
    A balanced oracle returns 0 for half the inputs and 1 for the other half.
    """
    for i, bit in enumerate(reversed(pattern)):
        if bit == "1":
            qc.cx(i, n)


def _apply_constant_oracle(qc: QuantumCircuit, n: int, value: int) -> None:
    """Apply a constant oracle (returns same value for all inputs)."""
    if value == 1:
        qc.x(n)


def build_circuit(params: dict) -> QuantumCircuit:
    """Build a Deutsch-Jozsa circuit.

    Params:
        num_qubits: Number of input qubits (default 3), total = num_qubits + 1 ancilla
        oracle_type: "balanced" or "constant" (default "balanced")
        pattern: For balanced oracle, which qubits control flip (default "101")
        constant_value: For constant oracle, 0 or 1 (default 0)
    """
    num_qubits = params.get("num_qubits", 3)
    oracle_type = params.get("oracle_type", "balanced")
    pattern = params.get("pattern", "101")
    constant_value = params.get("constant_value", 0)

    if len(pattern) != num_qubits:
        pattern = pattern.zfill(num_qubits)[:num_qubits]

    total_qubits = num_qubits + 1  # +1 for ancilla
    qc = QuantumCircuit(total_qubits, num_qubits)

    # Initialize ancilla in |1⟩
    qc.x(num_qubits)

    # Apply Hadamard to all qubits
    qc.h(range(total_qubits))

    # Apply oracle
    qc.barrier()
    if oracle_type == "balanced":
        _apply_balanced_oracle(qc, num_qubits, pattern)
    else:
        _apply_constant_oracle(qc, num_qubits, constant_value)
    qc.barrier()

    # Apply Hadamard to input qubits
    qc.h(range(num_qubits))

    # Measure input qubits only
    qc.measure(range(num_qubits), range(num_qubits))
    return qc


def get_circuit_info(params: dict) -> dict:
    """Return metadata about the circuit."""
    num_qubits = params.get("num_qubits", 3)
    oracle_type = params.get("oracle_type", "balanced")

    return {
        "name": "Deutsch-Jozsa Algorithm",
        "num_qubits": num_qubits + 1,
        "oracle_type": oracle_type,
        "description": (
            f"Determines if a {num_qubits}-bit function is constant or balanced "
            f"using a single query. Oracle type: {oracle_type}. "
            f"Classical requires up to {2**(num_qubits-1) + 1} queries; "
            f"Deutsch-Jozsa requires exactly 1."
        ),
    }
