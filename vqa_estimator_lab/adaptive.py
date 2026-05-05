from __future__ import annotations

import numpy as np

from .sampling import (
    basis_rotated_probabilities_from_state,
    term_eigenvalues_for_basis_measurement,
    allocate_group_shots_uniform,
)

def sample_group_values(state, coeffs, codes, group, basis, shots: int, rng=None):
    rng = rng if rng is not None else np.random.default_rng()
    num_qubits = int(np.log2(state.shape[0]))
    probs = basis_rotated_probabilities_from_state(state, basis, num_qubits)
    outcomes = rng.choice(1 << num_qubits, size=int(shots), p=probs)

    values = np.zeros(1 << num_qubits, dtype=np.float64)
    for term_idx in group:
        eigvals = term_eigenvalues_for_basis_measurement(codes[term_idx], num_qubits)
        values += coeffs[term_idx] * eigvals

    return values[outcomes]

def estimate_group_sigma_pilot(state, coeffs, codes, group, basis, pilot_shots: int, rng=None, variance_floor: float = 1e-12):
    samples = sample_group_values(state, coeffs, codes, group, basis, pilot_shots, rng=rng)
    if pilot_shots <= 1:
        return float(np.sqrt(max(float(np.var(samples)), variance_floor)))
    return float(np.sqrt(max(float(np.var(samples, ddof=1)), variance_floor)))

def allocate_group_shots_adaptive_pilot(
    state,
    coeffs,
    codes,
    groups,
    bases,
    total_shots: int,
    pilot_fraction: float = 0.1,
    min_pilot_shots: int = 50,
    variance_floor: float = 1e-12,
    rng=None,
):
    '''
    Adaptive two-stage shot allocation for QWC groups.

    The grouped contribution already includes coefficients, so priority is sigma(G),
    not |c| sigma for individual terms.
    '''
    rng = rng if rng is not None else np.random.default_rng()
    num_groups = len(groups)

    if num_groups == 0:
        return np.array([], dtype=int), {"pilot_shots_per_group": 0, "sigma_hats": []}

    pilot_total = max(int(total_shots * pilot_fraction), num_groups * min_pilot_shots)
    pilot_total = min(int(total_shots), pilot_total)

    pilot_per_group = max(1, pilot_total // num_groups)
    actual_pilot_total = pilot_per_group * num_groups
    remaining = max(0, int(total_shots) - actual_pilot_total)

    sigma_hats = np.array([
        estimate_group_sigma_pilot(
            state,
            coeffs,
            codes,
            group,
            basis,
            pilot_per_group,
            rng=rng,
            variance_floor=variance_floor,
        )
        for group, basis in zip(groups, bases)
    ], dtype=np.float64)

    if sigma_hats.sum() <= 0:
        main_alloc = allocate_group_shots_uniform(num_groups, remaining)
    else:
        raw = remaining * sigma_hats / sigma_hats.sum()
        main_alloc = np.floor(raw).astype(int)
        leftover = remaining - main_alloc.sum()
        order = np.argsort(-(raw - main_alloc))
        for k in range(leftover):
            main_alloc[order[k % num_groups]] += 1

    total_alloc = main_alloc + pilot_per_group

    diagnostics = {
        "pilot_shots_per_group": int(pilot_per_group),
        "actual_pilot_total": int(actual_pilot_total),
        "remaining_shots": int(remaining),
        "sigma_hats": sigma_hats.tolist(),
        "main_alloc": main_alloc.astype(int).tolist(),
    }
    return total_alloc.astype(int), diagnostics
