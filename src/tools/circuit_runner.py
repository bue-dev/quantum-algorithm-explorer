"""Central Qiskit execution wrapper — dispatches to pre-built circuits."""

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

from src.circuits import bernstein_vazirani, deutsch_jozsa, grover, qaoa, qft, vqe

CIRCUIT_REGISTRY: dict = {
    "grovers_search": grover,
    "deutsch_jozsa": deutsch_jozsa,
    "bernstein_vazirani": bernstein_vazirani,
    "qft": qft,
    "qaoa": qaoa,
    "vqe": vqe,
}


def _get_circuit_module(algorithm: str):
    if algorithm not in CIRCUIT_REGISTRY:
        raise ValueError(
            f"Unknown algorithm: {algorithm}. "
            f"Must be one of {list(CIRCUIT_REGISTRY.keys())}"
        )
    return CIRCUIT_REGISTRY[algorithm]


def run_circuit(algorithm: str, params: dict, shots: int = 1024) -> dict:
    """Run a pre-built circuit and return measurement counts."""
    module = _get_circuit_module(algorithm)
    qc = module.build_circuit(params)
    info = module.get_circuit_info(params)

    simulator = AerSimulator()
    transpiled = transpile(qc, simulator)
    result = simulator.run(transpiled, shots=shots).result()
    counts = result.get_counts()

    return {
        "counts": dict(counts),
        "circuit_ascii": qc.draw(output="text").single_string(),
        "info": info,
    }


def get_statevector(algorithm: str, params: dict) -> dict:
    """Run circuit without measurement and return statevector."""
    module = _get_circuit_module(algorithm)
    qc = module.build_circuit(params)

    # Record which qubits are measured before removing measurements
    measured_qubits = list(range(qc.num_clbits))

    # Remove measurements for statevector simulation
    qc.remove_final_measurements()
    qc.save_statevector()

    simulator = AerSimulator(method="statevector")
    transpiled = transpile(qc, simulator)
    result = simulator.run(transpiled).result()
    sv = result.get_statevector()

    # Trace out ancilla qubits — only keep probabilities for measured qubits
    probs = sv.probabilities_dict(qargs=measured_qubits)

    sv_array = np.asarray(sv)
    amplitudes = {}
    for i, amp in enumerate(sv_array):
        label = format(i, f"0{qc.num_qubits}b")
        if abs(amp) > 1e-10:
            amplitudes[label] = {"real": round(float(amp.real), 6), "imag": round(float(amp.imag), 6)}

    return {
        "amplitudes": amplitudes,
        "probabilities": {k: round(v, 6) for k, v in probs.items() if v > 1e-10},
    }


def get_probability_distribution(algorithm: str, params: dict) -> dict:
    """Get probability distribution over computational basis states."""
    sv_result = get_statevector(algorithm, params)
    probs = sv_result["probabilities"]

    sorted_probs = dict(sorted(probs.items(), key=lambda x: x[1], reverse=True))

    return {
        "probabilities": sorted_probs,
        "num_states": len(sorted_probs),
        "max_probability_state": next(iter(sorted_probs)),
        "max_probability": next(iter(sorted_probs.values())),
    }
