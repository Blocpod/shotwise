from __future__ import annotations

import numpy as np

from .simulator import StateVectorSimulator
from .gates import H, S_DAG

def basis_rotated_probabilities_from_state(state, basis_codes, num_qubits: int):
    '''
    Rotate QWC measurement basis into computational/Z basis and return probabilities.

    basis code:
        0/I or 3/Z: no rotation
        1/X: H
        2/Y: S† then H
    '''
    sim = StateVectorSimulator(num_qubits)
    sim.state = state.copy()

    for q, p in enumerate(basis_codes):
        if p == 1:
            sim.apply_gate(H, q)
        elif p == 2:
            sim.apply_gate(S_DAG, q)
            sim.apply_gate(H, q)
        elif p in (0, 3):
            pass
        else:
            raise ValueError(f"Invalid basis code: {p}")

    probs = np.abs(sim.state) ** 2
    return probs / probs.sum()

def term_eigenvalues_for_basis_measurement(pauli_code, num_qubits: int):
    dim = 1 << num_qubits
    vals = np.ones(dim, dtype=np.float64)

    for outcome in range(dim):
        ev = 1
        for q, p in enumerate(pauli_code):
            if p != 0:
                bit = (outcome >> q) & 1
                ev *= 1 if bit == 0 else -1
        vals[outcome] = ev

    return vals

def grouped_energy_estimates(state, coeffs, codes, groups, bases, group_shots, repeats: int, rng=None):
    rng = rng if rng is not None else np.random.default_rng()
    num_qubits = int(np.log2(state.shape[0]))
    energies = np.zeros(repeats, dtype=np.float64)

    for coeff, code in zip(coeffs, codes):
        if not np.any(code):
            energies += coeff

    for group_idx, term_indices in enumerate(groups):
        shots = int(group_shots[group_idx])
        if shots <= 0:
            raise ValueError("Every group must receive positive shots.")

        probs = basis_rotated_probabilities_from_state(state, bases[group_idx], num_qubits)
        sampled_counts = rng.multinomial(shots, probs, size=repeats)

        for term_idx in term_indices:
            coeff = coeffs[term_idx]
            eigvals = term_eigenvalues_for_basis_measurement(codes[term_idx], num_qubits)
            means = sampled_counts @ eigvals / shots
            energies += coeff * means

    return energies

def allocate_group_shots_uniform(num_groups: int, total_shots: int):
    base = total_shots // num_groups
    leftover = total_shots - base * num_groups
    return np.array([base + (1 if i < leftover else 0) for i in range(num_groups)], dtype=int)

def group_variance_proxy(state, coeffs, codes, group, basis, num_qubits: int):
    probs = basis_rotated_probabilities_from_state(state, basis, num_qubits)
    dim = len(probs)

    values = np.zeros(dim, dtype=np.float64)
    for term_idx in group:
        eigvals = term_eigenvalues_for_basis_measurement(codes[term_idx], num_qubits)
        values += coeffs[term_idx] * eigvals

    mean = np.dot(probs, values)
    second = np.dot(probs, values * values)
    return max(0.0, second - mean * mean)

def allocate_group_shots_variance(state, coeffs, codes, groups, bases, total_shots: int, min_shots_per_group: int = 1):
    num_qubits = int(np.log2(state.shape[0]))
    num_groups = len(groups)

    if total_shots < min_shots_per_group * num_groups:
        min_shots_per_group = 0

    remaining = total_shots - min_shots_per_group * num_groups
    sigmas = np.array([
        np.sqrt(group_variance_proxy(state, coeffs, codes, g, b, num_qubits))
        for g, b in zip(groups, bases)
    ], dtype=np.float64)

    if sigmas.sum() <= 0:
        return allocate_group_shots_uniform(num_groups, total_shots)

    raw = remaining * sigmas / sigmas.sum()
    base = np.floor(raw).astype(int)
    leftover = remaining - base.sum()
    order = np.argsort(-(raw - base))

    for k in range(leftover):
        base[order[k % num_groups]] += 1

    return base + min_shots_per_group

def summarize_estimates(estimates, truth, chemical_accuracy: float = 1.6e-3):
    abs_err = np.abs(estimates - truth)
    return {
        "mean_energy": float(estimates.mean()),
        "std_energy": float(estimates.std(ddof=1)),
        "bias": float(estimates.mean() - truth),
        "median_abs_error": float(np.median(abs_err)),
        "within_chemical_accuracy_rate": float(np.mean(abs_err <= chemical_accuracy)),
    }
