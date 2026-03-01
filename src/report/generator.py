"""Markdown report builder — assembles research + simulation results."""

from src.config import Config
from src.models.schemas import AlgorithmRecommendation, SimulationResult
from src.report.templates import REPORT_TEMPLATE, build_histogram
from src.tools.algorithm_catalog import ALGORITHM_CATALOG


def build_report(
    problem: str,
    recommendation: AlgorithmRecommendation,
    sim_result: SimulationResult,
    config: Config,
) -> str:
    """Build a Markdown report from research and simulation results."""
    algo_info = ALGORITHM_CATALOG.get(recommendation.chosen_algorithm, {})
    algorithm_name = algo_info.get("name", recommendation.chosen_algorithm)

    histogram = build_histogram(sim_result.measurement_counts)

    report = REPORT_TEMPLATE.format(
        problem=problem,
        algorithm_name=algorithm_name,
        reasoning=recommendation.reasoning,
        classical_alternative=recommendation.classical_alternative,
        classical_complexity=recommendation.classical_complexity,
        quantum_complexity=recommendation.quantum_complexity,
        quantum_advantage=recommendation.quantum_advantage,
        circuit_ascii=sim_result.circuit_ascii,
        num_qubits=sim_result.num_qubits,
        circuit_depth=sim_result.circuit_depth,
        shots=config.shots,
        histogram=histogram,
        statevector_summary=sim_result.statevector_summary,
        probability_analysis=sim_result.probability_analysis,
        success_probability=sim_result.success_probability,
        model=config.model,
    )

    return report
