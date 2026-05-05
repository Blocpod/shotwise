
from __future__ import annotations
import numpy as np
from .grouping import qwc_compatible
from .commutation import validate_commuting_groups

def is_qwc_group(codes, group) -> bool:
    for i,a in enumerate(group):
        for b in group[i+1:]:
            if not qwc_compatible(codes[a], codes[b]): return False
    return True

def qwc_basis_for_group(codes, group):
    basis = np.zeros(codes.shape[1], dtype=np.int8)
    for idx in group:
        for q,p in enumerate(codes[idx]):
            if p != 0:
                if basis[q] == 0: basis[q] = p
                elif basis[q] != p: raise ValueError("Group is not QWC.")
    return basis

def joint_measurement_plan(coeffs, codes, groups):
    if not validate_commuting_groups(codes, groups): raise ValueError("Groups are not mutually commuting.")
    plan = []
    for gid, group in enumerate(groups):
        qwc = is_qwc_group(codes, group)
        plan.append({
            "group_id": gid,
            "term_indices": [int(x) for x in group],
            "num_terms": len(group),
            "qwc": bool(qwc),
            "measurement_type": "single_qubit_basis" if qwc else "joint_commuting_measurement",
            "requires_joint_measurement_compiler": not qwc,
            "coefficient_l1": float(sum(abs(coeffs[i]) for i in group)),
            "max_pauli_weight": int(max(np.count_nonzero(codes[i]) for i in group)) if group else 0,
            "basis": qwc_basis_for_group(codes, group).astype(int).tolist() if qwc else None,
        })
    return plan

def summarize_measurement_plan(plan):
    total=len(plan); qwc=sum(1 for x in plan if x["qwc"]); terms=sum(x["num_terms"] for x in plan)
    return {"groups":total,"terms":terms,"qwc_groups":qwc,"joint_groups":total-qwc,"qwc_fraction":qwc/total if total else 0.0,"average_terms_per_group":terms/total if total else 0.0}
