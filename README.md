# Quantum Algorithm Explorer

AI-powered quantum algorithm analysis using Claude agents and Qiskit simulation.

Given a computational problem in natural language, this tool:
1. **Research Agent** — Analyzes the problem and recommends the best quantum algorithm
2. **Simulation Agent** — Runs the quantum circuit on a simulator and interprets results
3. **Report Generator** — Produces a comparison report (classical vs quantum)

## Quick Start

### Prerequisites

- Python 3.10+
- An [Anthropic API key](https://console.anthropic.com/)

### Setup

```bash
# Clone
git clone https://github.com/bue-dev/quantum-algorithm-explorer.git
cd quantum-algorithm-explorer

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -e ".[dev]"

# Configure API key
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### Usage

```bash
# Basic usage
python -m src.cli "find element 42 in a database of 1000 items"

# Save report to file
python -m src.cli "determine if a function is constant or balanced" -o report.md

# Verbose mode (see agent tool calls)
python -m src.cli "find a hidden 5-bit string" --verbose

# Custom settings
python -m src.cli "optimize a traveling salesman route" --shots 2048
```

## Supported Algorithms

| Algorithm | Best For | Quantum Speedup |
|-----------|----------|-----------------|
| Grover's Search | Unstructured search, SAT | Quadratic O(√N) |
| Deutsch-Jozsa | Constant vs balanced functions | Exponential O(1) |
| Bernstein-Vazirani | Hidden bit string extraction | Linear → constant |
| QFT | Fourier transform, period finding | Exponential O(n²) |
| QAOA | Combinatorial optimization (MaxCut, TSP) | Heuristic |
| VQE | Molecular simulation, chemistry | Heuristic |

## Architecture

```
User Input (problem description)
       |
  [Orchestrator]  (sequential Python pipeline)
       |
       +-- Research Agent (Claude + algorithm catalog tools)
       |       -> AlgorithmRecommendation
       |
       +-- Simulation Agent (Claude + Qiskit execution tools)
       |       -> SimulationResult
       |
       +-- Report Generator (pure Python, no AI)
                -> Markdown report
```

## Running Tests

```bash
pytest tests/ -v
```

## Cost

Each run makes ~2 Claude API calls using Sonnet (~$0.02 per run). Use `--model claude-haiku-4-5` for cheaper runs.

## License

MIT
