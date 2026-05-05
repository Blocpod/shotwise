from __future__ import annotations

import numpy as np

from .sampling import basis_rotated_probabilities_from_state, term_eigenvalues_for_basis_measurement

def group_value_distribution(state, coeffs, codes, group, basis):
    '''
    For a QWC group, compute the full distribution of grouped contribution:
        G(x) = sum_i c_i eig_i(x)
    over measurement outcomes after the group's basis rotation.

    Returns:
        probs, values
    '''
    num_qubits = int(np.log2(state.shape[0]))
    probs = basis_rotated_probabilities_from_state(state, basis, num_qubits)
    values = np.zeros(1 << num_qubits, dtype=np.float64)

    for term_idx in group:
        eigvals = term_eigenvalues_for_basis_measurement(codes[term_idx], num_qubits)
        values += coeffs[term_idx] * eigvals

    return probs, values

def group_mean_variance(state, coeffs, codes, group, basis):
    probs, values = group_value_distribution(state, coeffs, codes, group, basis)
    mean = float(np.dot(probs, values))
    second = float(np.dot(probs, values * values))
    return mean, max(0.0, second - mean * mean)

def qwc_group_covariance_matrix(state, coeffs, codes, group, basis):
    '''
    Compute covariance matrix between term-level contributions c_i P_i within a QWC group.
    Useful for diagnostics and covariance-aware shot allocation.
    '''
    num_qubits = int(np.log2(state.shape[0]))
    probs = basis_rotated_probabilities_from_state(state, basis, num_qubits)
    m = len(group)

    samples_by_term = np.zeros((m, 1 << num_qubits), dtype=np.float64)

    for row, term_idx in enumerate(group):
        eigvals = term_eigenvalues_for_basis_measurement(codes[term_idx], num_qubits)
        samples_by_term[row] = coeffs[term_idx] * eigvals

    means = samples_by_term @ probs
    cov = np.zeros((m, m), dtype=np.float64)

    for i in range(m):
        for j in range(m):
            cov[i, j] = float(np.dot(probs, samples_by_term[i] * samples_by_term[j]) - means[i] * means[j])

    return cov

def allocate_group_shots_covariance(state, coeffs, codes, groups, bases, total_shots: int, min_shots_per_group: int = 1):
    '''
    Allocate shots proportional to sqrt(Var(G_g)), where G_g is the full grouped
    contribution. This is covariance-aware because Var(G_g) includes all cross-term
    covariance inside the QWC group.
    '''
    num_groups = len(groups)

    if total_shots < min_shots_per_group * num_groups:
        min_shots_per_group = 0

    remaining = total_shots - min_shots_per_group * num_groups

    sigmas = np.array([
        np.sqrt(group_mean_variance(state, coeffs, codes, g, b)[1])
        for g, b in zip(groups, bases)
    ], dtype=np.float64)

    if sigmas.sum() <= 0:
        base = np.full(num_groups, remaining // max(num_groups, 1), dtype=int)
        for i in range(remaining - base.sum()):
            base[i % num_groups] += 1
        return base + min_shots_per_group, {"sigmas": sigmas.tolist()}

    raw = remaining * sigmas / sigmas.sum()
    base = np.floor(raw).astype(int)
    leftover = remaining - base.sum()
    order = np.argsort(-(raw - base))

    for k in range(leftover):
        base[order[k % num_groups]] += 1

    return base + min_shots_per_group, {"sigmas": sigmas.tolist()}

def allocate_group_shots_covariance_pilot(state, coeffs, codes, groups, bases, total_shots:int, pilot_fraction:float=0.1, min_pilot_shots:int=50, variance_floor:float=1e-12, rng=None):
    from .adaptive import sample_group_values
    from .sampling import allocate_group_shots_uniform
    rng = rng if rng is not None else np.random.default_rng()
    n=len(groups)
    if n == 0: return np.array([], dtype=int), {"sigma_hats":[]}
    pilot_total = min(total_shots, max(int(total_shots*pilot_fraction), min_pilot_shots*n))
    pilot_per = max(1, pilot_total//n); remaining=max(0,total_shots-pilot_per*n)
    sig=[]
    for g,b in zip(groups,bases):
        samples=sample_group_values(state, coeffs, codes, g, b, pilot_per, rng=rng)
        var=float(np.var(samples, ddof=1)) if pilot_per>1 else float(np.var(samples))
        sig.append(np.sqrt(max(var, variance_floor)))
    sig=np.array(sig,dtype=np.float64)
    if sig.sum() <= 0: main=allocate_group_shots_uniform(n, remaining)
    else:
        raw=remaining*sig/sig.sum(); main=np.floor(raw).astype(int); left=remaining-main.sum(); order=np.argsort(-(raw-main))
        for k in range(left): main[order[k % n]] += 1
    return (main+pilot_per).astype(int), {"pilot_shots_per_group":int(pilot_per),"remaining_shots":int(remaining),"sigma_hats":sig.tolist(),"main_alloc":main.astype(int).tolist()}
