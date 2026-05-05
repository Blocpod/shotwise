from __future__ import annotations

import numpy as np

def single_qubit_confusion_matrix(p01: float, p10: float) -> np.ndarray:
    '''
    Classical readout confusion matrix A where rows are measured outcomes and
    columns are true outcomes:

        A = [[P(m=0|t=0), P(m=0|t=1)],
             [P(m=1|t=0), P(m=1|t=1)]]

    p01 = P(measured 1 | true 0)
    p10 = P(measured 0 | true 1)
    '''
    if not (0 <= p01 < 1 and 0 <= p10 < 1):
        raise ValueError("p01 and p10 must be in [0, 1).")
    return np.array([
        [1 - p01, p10],
        [p01, 1 - p10],
    ], dtype=np.float64)

def kron_n_matrices(mats):
    if not mats:
        raise ValueError("Need at least one matrix.")
    out = mats[0]
    for m in mats[1:]:
        out = np.kron(out, m)
    return out

def full_confusion_matrix(num_qubits: int, p01, p10) -> np.ndarray:
    '''
    Build the full 2^n x 2^n confusion matrix.

    p01 and p10 can be scalars or arrays of length num_qubits.

    Qubit convention:
        qubit 0 is least significant bit. The Kronecker product is built MSB-to-LSB
        so it matches integer/binary probability-vector indexing.
    '''
    p01_arr = np.full(num_qubits, float(p01)) if np.isscalar(p01) else np.asarray(p01, dtype=float)
    p10_arr = np.full(num_qubits, float(p10)) if np.isscalar(p10) else np.asarray(p10, dtype=float)

    if len(p01_arr) != num_qubits or len(p10_arr) != num_qubits:
        raise ValueError("p01 and p10 arrays must have length num_qubits.")

    mats = [
        single_qubit_confusion_matrix(float(p01_arr[q]), float(p10_arr[q]))
        for q in reversed(range(num_qubits))
    ]
    return kron_n_matrices(mats)

def apply_confusion_matrix(probs: np.ndarray, confusion: np.ndarray) -> np.ndarray:
    noisy = confusion @ probs
    return noisy / noisy.sum()

def mitigate_probability_vector(observed_probs: np.ndarray, confusion: np.ndarray, clip: bool = True) -> np.ndarray:
    '''
    Matrix-inversion readout mitigation.

    If clip=True, negative quasi-probabilities are clipped and renormalized.
    For unbiased expectation estimates, clipping may introduce bias; it is useful for
    probability-vector display and robust downstream sampling diagnostics.
    '''
    mitigated = np.linalg.solve(confusion, observed_probs)

    if clip:
        mitigated = np.maximum(mitigated, 0.0)
        s = mitigated.sum()
        if s <= 0:
            raise ValueError("Mitigated probabilities collapsed to zero after clipping.")
        mitigated = mitigated / s

    return mitigated

def expectation_from_probs(probs: np.ndarray, pauli_code) -> float:
    '''
    Estimate Z-basis Pauli expectation from computational-basis probabilities.
    Intended after a group's basis rotations.
    '''
    dim = len(probs)
    val = 0.0
    for outcome in range(dim):
        ev = 1
        for q, p in enumerate(pauli_code):
            if p != 0:
                bit = (outcome >> q) & 1
                ev *= 1 if bit == 0 else -1
        val += ev * probs[outcome]
    return float(val)

def counts_to_probs(counts: dict[str, int], num_qubits: int) -> np.ndarray:
    dim = 1 << num_qubits
    probs = np.zeros(dim, dtype=np.float64)
    total = sum(counts.values())
    if total <= 0:
        raise ValueError("Empty counts.")
    for bitstring, count in counts.items():
        probs[int(bitstring, 2)] += count / total
    return probs
