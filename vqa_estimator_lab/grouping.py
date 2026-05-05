from __future__ import annotations

import numpy as np

def qwc_compatible(code_a, code_b) -> bool:
    for a, b in zip(code_a, code_b):
        if a != 0 and b != 0 and a != b:
            return False
    return True

def qwc_group_basis(group_codes):
    basis = np.zeros(group_codes.shape[1], dtype=np.int8)

    for row in group_codes:
        for q, p in enumerate(row):
            if p != 0:
                if basis[q] == 0:
                    basis[q] = p
                elif basis[q] != p:
                    raise ValueError("Group is not QWC-compatible.")

    return basis

def greedy_qwc_groups(coeffs, codes, include_identity: bool = False):
    '''
    Greedy first-fit grouping by qubit-wise commuting compatibility.
    Returns:
        groups: list[list[int]]
        bases:  list[np.ndarray]
    '''
    indices = list(range(len(coeffs)))

    if not include_identity:
        indices = [i for i in indices if np.any(codes[i] != 0)]

    indices.sort(key=lambda i: int(np.count_nonzero(codes[i])), reverse=True)

    groups = []
    bases = []

    for idx in indices:
        row = codes[idx]
        placed = False

        for gidx, basis in enumerate(bases):
            compatible = True
            for q, p in enumerate(row):
                if p != 0 and basis[q] != 0 and basis[q] != p:
                    compatible = False
                    break

            if compatible:
                groups[gidx].append(idx)
                for q, p in enumerate(row):
                    if p != 0 and basis[q] == 0:
                        basis[q] = p
                placed = True
                break

        if not placed:
            groups.append([idx])
            bases.append(row.copy())

    return groups, bases

def grouping_stats(coeffs, codes) -> dict:
    groups, bases = greedy_qwc_groups(coeffs, codes)
    group_sizes = np.array([len(g) for g in groups], dtype=int)
    basis_weights = np.array([np.count_nonzero(b) for b in bases], dtype=int)

    term_count = int(np.sum(np.any(codes != 0, axis=1)))

    return {
        "terms_excluding_identity": term_count,
        "qwc_groups": len(groups),
        "average_terms_per_group": float(group_sizes.mean()) if len(group_sizes) else 0.0,
        "max_terms_in_group": int(group_sizes.max()) if len(group_sizes) else 0,
        "median_terms_per_group": float(np.median(group_sizes)) if len(group_sizes) else 0.0,
        "average_basis_weight": float(basis_weights.mean()) if len(basis_weights) else 0.0,
        "max_basis_weight": int(basis_weights.max()) if len(basis_weights) else 0,
        "measurement_setting_reduction": term_count / len(groups) if len(groups) else float("inf"),
    }
