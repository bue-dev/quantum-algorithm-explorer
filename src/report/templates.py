"""Report section templates."""

REPORT_TEMPLATE = """\
# Quantum Algorithm Explorer Report

## Problem Statement

{problem}

---

## Research Analysis

### Recommended Algorithm: {algorithm_name}

{reasoning}

### Classical vs Quantum Comparison

| Aspect | Classical | Quantum |
|--------|-----------|---------|
| Algorithm | {classical_alternative} | {algorithm_name} |
| Time Complexity | {classical_complexity} | {quantum_complexity} |

### Quantum Advantage

{quantum_advantage}

---

## Simulation Results

### Circuit Diagram

```
{circuit_ascii}
```

### Circuit Properties

- **Qubits**: {num_qubits}
- **Circuit Depth**: {circuit_depth}
- **Shots**: {shots}

### Measurement Results

{histogram}

### State Vector Analysis

{statevector_summary}

### Probability Distribution Analysis

{probability_analysis}

### Success Probability: {success_probability:.1%}

---

## Configuration

- **Model**: {model}
- **Shots**: {shots}
"""


def build_histogram(counts: dict[str, int], width: int = 40) -> str:
    """Build an ASCII histogram from measurement counts."""
    if not counts:
        return "(no measurements)"

    total = sum(counts.values())
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    max_count = sorted_counts[0][1]

    lines = []
    for state, count in sorted_counts:
        bar_len = int(count / max_count * width) if max_count > 0 else 0
        bar = "#" * bar_len
        pct = count / total * 100
        lines.append(f"  |{state}> : {bar:<{width}} {count:>5} ({pct:5.1f}%)")

    return "\n".join(lines)
