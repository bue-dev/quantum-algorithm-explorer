from pydantic import BaseModel


class AlgorithmRecommendation(BaseModel):
    """Output of the Research Agent."""

    chosen_algorithm: str
    algorithm_params: dict
    reasoning: str
    classical_alternative: str
    classical_complexity: str
    quantum_complexity: str
    quantum_advantage: str


class SimulationResult(BaseModel):
    """Output of the Simulation Agent."""

    circuit_description: str
    circuit_ascii: str
    num_qubits: int
    circuit_depth: int
    measurement_counts: dict[str, int]
    statevector_summary: str
    probability_analysis: str
    success_probability: float
