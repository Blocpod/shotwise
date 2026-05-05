import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import time
import numpy as np

from vqa_estimator_lab.gates import RY, CZ
from vqa_estimator_lab.numba_kernels import (
    NUMBA_AVAILABLE,
    apply_single_qubit_gate_kernel,
    apply_two_qubit_gate_kernel,
    expectation_hamiltonian_encoded_parallel,
)
from vqa_estimator_lab.hamiltonian import compress_encoded_hamiltonian

if NUMBA_AVAILABLE:
    from numba import set_num_threads, get_num_threads

def random_encoded_hamiltonian(num_qubits, num_terms, max_weight=4, seed=123):
    rng = np.random.default_rng(seed)
    coeffs = np.empty(num_terms + 1, dtype=np.float64)
    codes = np.zeros((num_terms + 1, num_qubits), dtype=np.int8)

    coeffs[0] = rng.normal(scale=0.1)

    for t in range(1, num_terms + 1):
        coeffs[t] = rng.normal(scale=0.1)
        weight = int(rng.integers(1, min(max_weight, num_qubits) + 1))
        qubits = rng.choice(num_qubits, size=weight, replace=False)
        paulis = rng.integers(1, 4, size=weight)
        for q, p in zip(qubits, paulis):
            codes[t, int(q)] = int(p)

    return compress_encoded_hamiltonian(coeffs, codes)

def line_edges(num_qubits):
    return [(q, q + 1) for q in range(num_qubits - 1)]

def prepare_ansatz_state(num_qubits, depth, params, edges):
    state = np.zeros(1 << num_qubits, dtype=np.complex128)
    state[0] = 1.0 + 0.0j

    for layer in range(depth):
        for q in range(num_qubits):
            apply_single_qubit_gate_kernel(state, RY(params[layer, q]), q)

        for q0, q1 in edges:
            apply_two_qubit_gate_kernel(state, CZ, q0, q1)

    return state

def main():
    if not NUMBA_AVAILABLE:
        raise SystemExit("Numba is required for this benchmark.")

    set_num_threads(4)

    num_qubits = 14
    depth = 2
    num_terms = 500
    repeats = 10

    rng = np.random.default_rng(123)
    params = rng.normal(scale=0.5, size=(depth, num_qubits)).astype(np.float64)
    edges = line_edges(num_qubits)
    coeffs, codes = random_encoded_hamiltonian(num_qubits, num_terms, seed=999)

    # warm
    state = prepare_ansatz_state(num_qubits, depth, params, edges)
    energy = expectation_hamiltonian_encoded_parallel(state, coeffs, codes)

    times = []
    for r in range(repeats):
        t0 = time.perf_counter()
        state = prepare_ansatz_state(num_qubits, depth, params + 1e-5 * r, edges)
        energy = expectation_hamiltonian_encoded_parallel(state, coeffs, codes)
        t1 = time.perf_counter()
        times.append(t1 - t0)

    print("threads:", get_num_threads())
    print("num_qubits:", num_qubits)
    print("num_terms_after_compression:", len(coeffs) - 1)
    print("best_total_seconds:", min(times))
    print("median_total_seconds:", float(np.median(times)))
    print("energy:", energy)

if __name__ == "__main__":
    main()
