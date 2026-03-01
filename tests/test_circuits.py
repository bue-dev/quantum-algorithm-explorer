"""Tests for the quantum circuit implementations."""

from src.circuits import bernstein_vazirani, deutsch_jozsa, grover, qaoa, qft, vqe
from src.tools.circuit_runner import run_circuit


class TestGrover:
    def test_build_circuit(self):
        qc = grover.build_circuit({"num_qubits": 3, "marked_state": "101"})
        assert qc.num_qubits == 3
        assert qc.num_clbits == 3

    def test_finds_marked_state(self):
        result = run_circuit(
            "grovers_search",
            {"num_qubits": 3, "marked_state": "101"},
            shots=1024,
        )
        counts = result["counts"]
        # The marked state should have the highest count
        max_state = max(counts, key=counts.get)
        assert max_state == "101"

    def test_circuit_info(self):
        info = grover.get_circuit_info({"num_qubits": 3, "marked_state": "101"})
        assert info["name"] == "Grover's Search Algorithm"
        assert info["num_qubits"] == 3


class TestDeutschJozsa:
    def test_balanced_oracle(self):
        result = run_circuit(
            "deutsch_jozsa",
            {"num_qubits": 3, "oracle_type": "balanced", "pattern": "101"},
            shots=1024,
        )
        counts = result["counts"]
        # For balanced oracle, all-zeros should NOT be the result
        assert counts.get("000", 0) < 100

    def test_constant_oracle(self):
        result = run_circuit(
            "deutsch_jozsa",
            {"num_qubits": 3, "oracle_type": "constant", "constant_value": 0},
            shots=1024,
        )
        counts = result["counts"]
        # For constant oracle, all-zeros should be the result
        assert counts.get("000", 0) == 1024

    def test_circuit_info(self):
        info = deutsch_jozsa.get_circuit_info({"num_qubits": 3})
        assert info["name"] == "Deutsch-Jozsa Algorithm"
        assert info["num_qubits"] == 4  # 3 input + 1 ancilla


class TestBernsteinVazirani:
    def test_finds_secret(self):
        result = run_circuit(
            "bernstein_vazirani",
            {"num_qubits": 3, "secret": "110"},
            shots=1024,
        )
        counts = result["counts"]
        # Should find the secret string with certainty
        assert counts.get("110", 0) == 1024

    def test_circuit_info(self):
        info = bernstein_vazirani.get_circuit_info({"num_qubits": 3, "secret": "110"})
        assert info["name"] == "Bernstein-Vazirani Algorithm"
        assert info["secret"] == "110"


class TestQFT:
    def test_build_circuit(self):
        qc = qft.build_circuit({"num_qubits": 3, "input_state": "101"})
        assert qc.num_qubits == 3

    def test_circuit_info(self):
        info = qft.get_circuit_info({"num_qubits": 3})
        assert info["name"] == "Quantum Fourier Transform"


class TestQAOA:
    def test_build_circuit(self):
        qc = qaoa.build_circuit({"num_qubits": 4, "p_layers": 1})
        assert qc.num_qubits == 4

    def test_circuit_info(self):
        info = qaoa.get_circuit_info({"num_qubits": 4})
        assert "QAOA" in info["name"]


class TestVQE:
    def test_build_circuit(self):
        qc = vqe.build_circuit({"num_qubits": 2, "layers": 1})
        assert qc.num_qubits == 2

    def test_circuit_info(self):
        info = vqe.get_circuit_info({"num_qubits": 2})
        assert "VQE" in info["name"]
