"""Bernstein-Vazirani algorithm — finds a hidden bit string in one query."""

from qiskit import QuantumCircuit


def _apply_oracle(qc: QuantumCircuit, n: int, secret: str) -> None:
    """Apply the inner-product oracle for the secret string.

    The oracle computes f(x) = s·x (mod 2), where s is the secret string.
    """
    for i, bit in enumerate(reversed(secret)):
        if bit == "1":
            qc.cx(i, n)


def build_circuit(params: dict) -> QuantumCircuit:
    """Build a Bernstein-Vazirani circuit.

    Params:
        num_qubits: Number of input qubits (default 3), total = num_qubits + 1 ancilla
        secret: Hidden bit string to find (default "101")
    """
    num_qubits = params.get("num_qubits", 3)
    secret = params.get("secret", "101")

    if len(secret) != num_qubits:
        secret = secret.zfill(num_qubits)[:num_qubits]

    total_qubits = num_qubits + 1  # +1 for ancilla
    qc = QuantumCircuit(total_qubits, num_qubits)

    # Initialize ancilla in |1⟩
    qc.x(num_qubits)

    # Apply Hadamard to all qubits
    qc.h(range(total_qubits))

    # Apply oracle
    qc.barrier()
    _apply_oracle(qc, num_qubits, secret)
    qc.barrier()

    # Apply Hadamard to input qubits
    qc.h(range(num_qubits))

    # Measure input qubits
    qc.measure(range(num_qubits), range(num_qubits))
    return qc


def get_circuit_info(params: dict) -> dict:
    """Return metadata about the circuit."""
    num_qubits = params.get("num_qubits", 3)
    secret = params.get("secret", "101")

    return {
        "name": "Bernstein-Vazirani Algorithm",
        "num_qubits": num_qubits + 1,
        "secret": secret,
        "description": (
            f"Finds the hidden {num_qubits}-bit string s={secret} using a single query. "
            f"The oracle computes f(x) = s·x mod 2. "
            f"Classical requires {num_qubits} queries; "
            f"Bernstein-Vazirani requires exactly 1."
        ),
    }
