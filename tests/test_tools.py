"""Tests for the tools (catalog lookup, complexity comparison, circuit runner)."""

from src.tools.algorithm_catalog import ALGORITHM_CATALOG, lookup_algorithms
from src.tools.circuit_runner import (
    CIRCUIT_REGISTRY,
    get_probability_distribution,
    get_statevector,
    run_circuit,
)
from src.tools.complexity_compare import compare_complexity


class TestAlgorithmCatalog:
    def test_catalog_has_all_algorithms(self):
        expected = {
            "grovers_search",
            "deutsch_jozsa",
            "bernstein_vazirani",
            "qft",
            "qaoa",
            "vqe",
        }
        assert set(ALGORITHM_CATALOG.keys()) == expected

    def test_lookup_search(self):
        results = lookup_algorithms("search")
        keys = [r["key"] for r in results]
        assert "grovers_search" in keys

    def test_lookup_optimization(self):
        results = lookup_algorithms("optimization")
        keys = [r["key"] for r in results]
        assert "qaoa" in keys

    def test_lookup_unknown_returns_all(self):
        results = lookup_algorithms("nonexistent_category")
        assert len(results) == len(ALGORITHM_CATALOG)


class TestComplexityCompare:
    def test_grover_complexity(self):
        result = compare_complexity("grovers_search", 1000)
        assert result["classical_steps"] == 1000
        assert result["quantum_steps"] < 1000
        assert result["speedup_factor"] > 1

    def test_deutsch_jozsa_complexity(self):
        result = compare_complexity("deutsch_jozsa", 3)
        assert result["quantum_steps"] == 1
        assert result["classical_steps"] > 1

    def test_bernstein_vazirani_complexity(self):
        result = compare_complexity("bernstein_vazirani", 5)
        assert result["quantum_steps"] == 1
        assert result["classical_steps"] == 5

    def test_unknown_algorithm(self):
        result = compare_complexity("unknown", 10)
        assert "error" in result


class TestCircuitRunner:
    def test_registry_matches_catalog(self):
        assert set(CIRCUIT_REGISTRY.keys()) == set(ALGORITHM_CATALOG.keys())

    def test_run_grover(self):
        result = run_circuit(
            "grovers_search", {"num_qubits": 3, "marked_state": "101"}, shots=100
        )
        assert "counts" in result
        assert "circuit_ascii" in result
        assert "info" in result

    def test_get_statevector(self):
        result = get_statevector(
            "bernstein_vazirani", {"num_qubits": 3, "secret": "101"}
        )
        assert "amplitudes" in result
        assert "probabilities" in result

    def test_get_probability_distribution(self):
        result = get_probability_distribution(
            "bernstein_vazirani", {"num_qubits": 3, "secret": "101"}
        )
        assert "probabilities" in result
        assert result["max_probability_state"] == "101"
        assert result["max_probability"] > 0.99

    def test_unknown_algorithm_raises(self):
        try:
            run_circuit("nonexistent", {})
            assert False, "Should have raised ValueError"
        except ValueError:
            pass
