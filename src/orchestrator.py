"""Orchestrator — sequential pipeline: Research Agent -> Simulation Agent -> Report."""

import logging

from src.agents import research_agent, simulation_agent
from src.config import Config
from src.report.generator import build_report

logger = logging.getLogger(__name__)


def run_pipeline(problem: str, config: Config) -> str:
    """Run the full research -> simulate -> report pipeline.

    Returns the Markdown report as a string.
    """
    # Step 1: Research
    logger.info("Step 1/3: Research Agent analyzing problem...")
    recommendation = research_agent.analyze(problem, config)
    logger.info(
        "  Recommended: %s (%s)",
        recommendation.chosen_algorithm,
        recommendation.quantum_complexity,
    )

    # Step 2: Simulate
    logger.info("Step 2/3: Simulation Agent running quantum circuit...")
    sim_result = simulation_agent.simulate(recommendation, config)
    logger.info(
        "  Circuit: %d qubits, depth %d, success %.1f%%",
        sim_result.num_qubits,
        sim_result.circuit_depth,
        sim_result.success_probability * 100,
    )

    # Step 3: Report
    logger.info("Step 3/3: Generating report...")
    report = build_report(problem, recommendation, sim_result, config)

    return report
