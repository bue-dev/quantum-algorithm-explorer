"""Research Agent — analyzes problems and recommends quantum algorithms."""

import json
import logging

import anthropic

from src.config import Config
from src.models.schemas import AlgorithmRecommendation
from src.tools.algorithm_catalog import lookup_algorithms
from src.tools.complexity_compare import compare_complexity

logger = logging.getLogger(__name__)

TOOLS = [
    {
        "name": "lookup_algorithm_catalog",
        "description": (
            "Look up quantum algorithms matching a problem category. "
            "Returns a list of algorithms with descriptions, complexity info, "
            "and suitability details. Categories include: search, optimization, "
            "database, decision, oracle, function_analysis, hidden_information, "
            "cryptography."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "problem_category": {
                    "type": "string",
                    "description": "The problem category to search for (e.g., 'search', 'optimization', 'factoring')",
                }
            },
            "required": ["problem_category"],
        },
    },
    {
        "name": "compare_complexity",
        "description": (
            "Compare classical and quantum complexity for a specific algorithm "
            "at a given problem size. Returns step counts, speedup factor, "
            "and a human-readable explanation."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "algorithm_name": {
                    "type": "string",
                    "description": "Algorithm key (e.g., 'grovers_search', 'deutsch_jozsa', 'bernstein_vazirani')",
                },
                "problem_size": {
                    "type": "integer",
                    "description": "Size of the problem (e.g., number of items to search, number of bits)",
                },
            },
            "required": ["algorithm_name", "problem_size"],
        },
    },
]

SYSTEM_PROMPT = """\
You are a quantum computing research specialist. Given a problem description, \
you must analyze it and recommend the most suitable quantum algorithm.

You MUST use the tools provided to look up algorithms and compare complexities — \
do not rely solely on your own knowledge, as the catalog reflects what is actually \
implemented and runnable.

Available algorithm keys: grovers_search, deutsch_jozsa, bernstein_vazirani, qft, qaoa, vqe

After using the tools, respond with a JSON object (no markdown, no code fences) \
with exactly these fields:
- chosen_algorithm: string, must be one of the algorithm keys from the catalog
- algorithm_params: object, parameters for the circuit (must match the algorithm's expected params)
- reasoning: string, 2-3 sentences explaining why this algorithm fits
- classical_alternative: string, the best classical algorithm for this problem
- classical_complexity: string, Big-O notation
- quantum_complexity: string, Big-O notation
- quantum_advantage: string, 2-3 sentences explaining the quantum speedup
"""


def _execute_tool(name: str, input_data: dict) -> str:
    """Execute a tool and return the result as a JSON string."""
    if name == "lookup_algorithm_catalog":
        result = lookup_algorithms(input_data["problem_category"])
    elif name == "compare_complexity":
        result = compare_complexity(
            input_data["algorithm_name"], input_data["problem_size"]
        )
    else:
        result = {"error": f"Unknown tool: {name}"}
    return json.dumps(result, default=str)


def analyze(problem: str, config: Config) -> AlgorithmRecommendation:
    """Analyze a problem and return an algorithm recommendation."""
    client = anthropic.Anthropic(api_key=config.anthropic_api_key)

    messages = [
        {
            "role": "user",
            "content": f"Analyze this problem and recommend the best quantum algorithm: {problem}",
        }
    ]

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
            logger.info("Research Agent response (stop_reason=%s)", response.stop_reason)

        # If Claude is done (no more tool calls), extract the final text
        if response.stop_reason == "end_turn":
            break

        # Extract tool use blocks
        tool_use_blocks = [b for b in response.content if b.type == "tool_use"]

        if not tool_use_blocks:
            break

        # Append assistant's response (preserves tool_use blocks)
        messages.append({"role": "assistant", "content": response.content})

        # Execute each tool and collect results
        tool_results = []
        for tool_block in tool_use_blocks:
            if config.verbose:
                logger.info(
                    "  Tool call: %s(%s)", tool_block.name, tool_block.input
                )
            result = _execute_tool(tool_block.name, tool_block.input)
            if config.verbose:
                logger.info("  Tool result: %s", result[:200])
            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": tool_block.id,
                    "content": result,
                }
            )

        # Send tool results back
        messages.append({"role": "user", "content": tool_results})

    # Parse the final text response into our Pydantic model
    final_text = ""
    for block in response.content:
        if block.type == "text":
            final_text += block.text

    # Clean up potential markdown code fences
    text = final_text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    data = json.loads(text)
    return AlgorithmRecommendation(**data)
