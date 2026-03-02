"""Simulation Agent — runs quantum circuits and interprets results."""

import json
import logging
import re

import anthropic

from src.config import Config
from src.models.schemas import AlgorithmRecommendation, SimulationResult
from src.tools.circuit_runner import (
    get_probability_distribution,
    get_statevector,
    run_circuit,
)

logger = logging.getLogger(__name__)

TOOLS = [
    {
        "name": "run_qiskit_circuit",
        "description": (
            "Run a quantum circuit simulation and return measurement counts. "
            "The circuit is pre-built from the algorithm name and parameters."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "algorithm": {
                    "type": "string",
                    "description": "Algorithm key (e.g., 'grovers_search', 'deutsch_jozsa', 'bernstein_vazirani')",
                },
                "params": {
                    "type": "object",
                    "description": "Parameters for the circuit (e.g., num_qubits, marked_state, secret)",
                },
                "shots": {
                    "type": "integer",
                    "description": "Number of measurement shots (default 1024)",
                },
            },
            "required": ["algorithm", "params"],
        },
    },
    {
        "name": "get_statevector",
        "description": (
            "Run the circuit without measurement and return the quantum statevector. "
            "Shows the amplitudes and probabilities for each basis state."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "algorithm": {
                    "type": "string",
                    "description": "Algorithm key",
                },
                "params": {
                    "type": "object",
                    "description": "Parameters for the circuit",
                },
            },
            "required": ["algorithm", "params"],
        },
    },
    {
        "name": "get_probability_distribution",
        "description": (
            "Get the probability distribution over computational basis states. "
            "Shows which states are most likely to be measured and their probabilities."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "algorithm": {
                    "type": "string",
                    "description": "Algorithm key",
                },
                "params": {
                    "type": "object",
                    "description": "Parameters for the circuit",
                },
            },
            "required": ["algorithm", "params"],
        },
    },
]

SYSTEM_PROMPT = """\
You are a quantum circuit simulation specialist. You receive a recommended \
quantum algorithm and its parameters, and your job is to run the simulation \
and interpret the results.

You MUST call all three tools in sequence:
1. run_qiskit_circuit — to get measurement results
2. get_statevector — to get the quantum state
3. get_probability_distribution — to analyze probabilities

Then respond with a JSON object (no markdown, no code fences) with exactly these fields:
- circuit_description: string, human-readable description of what the circuit does
- circuit_ascii: string, the circuit diagram text from the run_qiskit_circuit result
- num_qubits: integer
- circuit_depth: integer (from the circuit info)
- measurement_counts: object, the raw measurement counts from run_qiskit_circuit
- statevector_summary: string, explain the key amplitudes and what they mean
- probability_analysis: string, interpret the probability distribution in context
- success_probability: float, probability of measuring the correct/desired state

Focus on making the analysis accessible. Explain what the results mean \
in the context of the original problem.
"""


def _execute_tool(name: str, input_data: dict, config: Config) -> str:
    """Execute a tool and return the result as a JSON string."""
    algorithm = input_data["algorithm"]
    params = input_data.get("params", {})

    if name == "run_qiskit_circuit":
        shots = input_data.get("shots", config.shots)
        result = run_circuit(algorithm, params, shots=shots)
    elif name == "get_statevector":
        result = get_statevector(algorithm, params)
    elif name == "get_probability_distribution":
        result = get_probability_distribution(algorithm, params)
    else:
        result = {"error": f"Unknown tool: {name}"}

    return json.dumps(result, default=str)


def simulate(
    recommendation: AlgorithmRecommendation, config: Config
) -> SimulationResult:
    """Run a quantum simulation based on the research recommendation."""
    client = anthropic.Anthropic(api_key=config.anthropic_api_key)

    user_message = (
        f"Run a quantum simulation for the following algorithm:\n"
        f"Algorithm: {recommendation.chosen_algorithm}\n"
        f"Parameters: {json.dumps(recommendation.algorithm_params)}\n"
        f"Reasoning: {recommendation.reasoning}\n"
        f"Use {config.shots} shots for the measurement simulation."
    )

    messages = [{"role": "user", "content": user_message}]

    # Agentic loop
    while True:
        response = client.messages.create(
            model=config.model,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        if config.verbose:
            logger.info(
                "Simulation Agent response (stop_reason=%s)", response.stop_reason
            )

        if response.stop_reason == "end_turn":
            break

        tool_use_blocks = [b for b in response.content if b.type == "tool_use"]

        if not tool_use_blocks:
            break

        messages.append({"role": "assistant", "content": response.content})

        tool_results = []
        for tool_block in tool_use_blocks:
            if config.verbose:
                logger.info(
                    "  Tool call: %s(%s)", tool_block.name, tool_block.input
                )
            result = _execute_tool(tool_block.name, tool_block.input, config)
            if config.verbose:
                logger.info("  Tool result: %s", result[:200])
            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": tool_block.id,
                    "content": result,
                }
            )

        messages.append({"role": "user", "content": tool_results})

    # Parse the final text response
    final_text = ""
    for block in response.content:
        if block.type == "text":
            final_text += block.text

    text = final_text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    if not text:
        raise ValueError("Simulation Agent returned empty response.")

    # Try direct parse first; if that fails, extract the first JSON object
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise ValueError(
                f"No JSON object found in Simulation Agent response.\n"
                f"Raw response: {text[:500]}"
            )
        try:
            data = json.loads(match.group())
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Failed to parse Simulation Agent JSON: {e}\n"
                f"Raw response: {text[:500]}"
            ) from e

    return SimulationResult(**data)
