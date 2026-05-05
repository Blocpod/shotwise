from __future__ import annotations

import numpy as np

def attenuation_symmetric(pauli_code, p: float) -> float:
    weight = int(np.count_nonzero(pauli_code))
    return float((1 - 2 * p) ** weight)

def readout_attenuated_mu_symmetric(mu: float, pauli_code, p: float) -> float:
    return attenuation_symmetric(pauli_code, p) * mu

def mitigate_mu_symmetric(noisy_mu: float, pauli_code, p: float) -> float:
    a = attenuation_symmetric(pauli_code, p)
    if abs(a) < 1e-12:
        raise ValueError("Readout attenuation is too small to invert stably.")
    return noisy_mu / a

def apply_readout_error_counts(counts: dict[str, int], p01: float, p10: float, rng=None):
    '''
    Apply independent classical readout bit flips to counts.

    p01 = P(measured 1 | true 0)
    p10 = P(measured 0 | true 1)
    '''
    rng = rng if rng is not None else np.random.default_rng()
    noisy = {}

    for bitstring, count in counts.items():
        for _ in range(int(count)):
            out_bits = []
            for bit in bitstring:
                b = int(bit)
                r = rng.random()
                if b == 0:
                    out_bits.append("1" if r < p01 else "0")
                else:
                    out_bits.append("0" if r < p10 else "1")
            out = "".join(out_bits)
            noisy[out] = noisy.get(out, 0) + 1

    return noisy


def noisy_probs_symmetric_from_basis_probs(probs, num_qubits: int, p: float):
    '''
    Apply independent symmetric bit-flip readout noise to a computational-basis
    probability vector. Reference implementation, O(4^n).
    '''
    dim = 1 << num_qubits
    noisy = np.zeros(dim, dtype=np.float64)

    for true_outcome in range(dim):
        base_prob = probs[true_outcome]
        if base_prob == 0:
            continue

        for measured in range(dim):
            prob = base_prob
            for q in range(num_qubits):
                tb = (true_outcome >> q) & 1
                mb = (measured >> q) & 1
                prob *= (1 - p) if tb == mb else p
            noisy[measured] += prob

    return noisy / noisy.sum()

def grouped_energy_estimates_symmetric_readout(
    state,
    coeffs,
    codes,
    groups,
    bases,
    group_shots,
    repeats: int,
    p: float,
    mitigated: bool = False,
    rng=None,
):
    '''
    Grouped QWC energy estimates under symmetric independent readout error.

    If mitigated=True, each term expectation is corrected by dividing by
    attenuation (1 - 2p)^weight.
    '''
    from .sampling import (
        basis_rotated_probabilities_from_state,
        term_eigenvalues_for_basis_measurement,
    )
    from .hamiltonian import pauli_weight

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

        ideal_probs = basis_rotated_probabilities_from_state(state, bases[group_idx], num_qubits)
        noisy_probs = noisy_probs_symmetric_from_basis_probs(ideal_probs, num_qubits, p)
        sampled_counts = rng.multinomial(shots, noisy_probs, size=repeats)

        for term_idx in term_indices:
            coeff = coeffs[term_idx]
            code = codes[term_idx]
            eigvals = term_eigenvalues_for_basis_measurement(code, num_qubits)
            means = sampled_counts @ eigvals / shots

            if mitigated:
                a = (1 - 2 * p) ** pauli_weight(code)
                if abs(a) < 1e-12:
                    raise ValueError("Readout attenuation too small to invert.")
                means = means / a

            energies += coeff * means

    return energies


def grouped_energy_estimates_confusion_readout(
    state,
    coeffs,
    codes,
    groups,
    bases,
    group_shots,
    repeats: int,
    confusion_matrix,
    mitigated: bool = False,
    clip_mitigation: bool = False,
    rng=None,
):
    '''
    Grouped QWC energy estimates under an arbitrary classical readout confusion matrix.

    This is a reference implementation intended for small-to-moderate grouped validation.
    If mitigated=True, the observed probability vector for each repeated shot batch is
    multiplied by confusion_matrix^{-1} before term expectations are computed.

    clip_mitigation=False preserves unbiased quasi-probability mitigation but can produce
    negative entries. clip_mitigation=True projects back to a probability simplex, which is
    more stable but biased.
    '''
    from .sampling import (
        basis_rotated_probabilities_from_state,
    )
    from .readout import apply_confusion_matrix, mitigate_probability_vector, expectation_from_probs

    rng = rng if rng is not None else np.random.default_rng()
    num_qubits = int(np.log2(state.shape[0]))
    dim = 1 << num_qubits

    confusion_matrix = np.asarray(confusion_matrix, dtype=np.float64)
    if confusion_matrix.shape != (dim, dim):
        raise ValueError(f"Confusion matrix must have shape {(dim, dim)}.")

    energies = np.zeros(repeats, dtype=np.float64)

    for coeff, code in zip(coeffs, codes):
        if not np.any(code):
            energies += coeff

    for group_idx, term_indices in enumerate(groups):
        shots = int(group_shots[group_idx])
        if shots <= 0:
            raise ValueError("Every group must receive positive shots.")

        ideal_probs = basis_rotated_probabilities_from_state(state, bases[group_idx], num_qubits)
        observed_probs = apply_confusion_matrix(ideal_probs, confusion_matrix)
        sampled_counts = rng.multinomial(shots, observed_probs, size=repeats)

        for r in range(repeats):
            p_obs = sampled_counts[r] / shots
            if mitigated:
                p_use = mitigate_probability_vector(
                    p_obs,
                    confusion_matrix,
                    clip=clip_mitigation,
                )
            else:
                p_use = p_obs

            for term_idx in term_indices:
                energies[r] += coeffs[term_idx] * expectation_from_probs(p_use, codes[term_idx])

    return energies
