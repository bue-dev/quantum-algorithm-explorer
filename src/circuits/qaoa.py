"""QAOA — Quantum Approximate Optimization Algorithm for combinatorial problems."""

import math

from qiskit import QuantumCircuit


def build_circuit(params: dict) -> QuantumCircuit:
    """Build a QAOA circuit for MaxCut.

    Params:
        num_qubits: Number of qubits / graph nodes (default 4)
        p_layers: Number of QAOA layers (default 1)
        graph_edges: List of [i, j] edges (default: cycle graph)
        gamma: Cost unitary angle (default pi/4)
        beta: Mixer unitary angle (default pi/8)
    """
    num_qubits = params.get("num_qubits", 4)
    p_layers = params.get("p_layers", 1)
    graph_edges = params.get(
        "graph_edges",
        [[i, (i + 1) % num_qubits] for i in range(num_qubits)],
    )
    gamma = params.get("gamma", math.pi / 4)
    beta = params.get("beta", math.pi / 8)

    qc = QuantumCircuit(num_qubits, num_qubits)

    # Initial superposition
    qc.h(range(num_qubits))

    for _ in range(p_layers):
        # Cost unitary: ZZ interaction for each edge
        qc.barrier()
        for edge in graph_edges:
            i, j = edge[0], edge[1]
            qc.cx(i, j)
            qc.rz(2 * gamma, j)
            qc.cx(i, j)

        # Mixer unitary: X rotations
        qc.barrier()
        for i in range(num_qubits):
            qc.rx(2 * beta, i)

    qc.measure(range(num_qubits), range(num_qubits))
    return qc


def get_circuit_info(params: dict) -> dict:
    """Return metadata about the circuit."""
    num_qubits = params.get("num_qubits", 4)
    p_layers = params.get("p_layers", 1)
    graph_edges = params.get(
        "graph_edges",
        [[i, (i + 1) % num_qubits] for i in range(num_qubits)],
    )

    return {
        "name": "Quantum Approximate Optimization Algorithm (QAOA)",
        "num_qubits": num_qubits,
        "p_layers": p_layers,
        "num_edges": len(graph_edges),
        "description": (
            f"QAOA for MaxCut on a {num_qubits}-node graph with "
            f"{len(graph_edges)} edges using {p_layers} layer(s). "
            f"Finds approximate solutions to combinatorial optimization problems. "
            f"Classical exact solution requires O(2^{num_qubits}) time; "
            f"QAOA provides a heuristic quantum approach."
        ),
    }
