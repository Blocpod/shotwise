import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import numpy as np

from vqa_estimator_lab.hamiltonian import compress_encoded_hamiltonian
from vqa_estimator_lab.grouping import greedy_qwc_groups
from vqa_estimator_lab.commutation import greedy_commuting_groups, validate_commuting_groups

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

def main():
    for terms in [100, 250, 500, 1000]:
        coeffs, codes = random_encoded_hamiltonian(14, terms, seed=4242 + terms)
        qwc_groups, _ = greedy_qwc_groups(coeffs, codes)
        gen_groups = greedy_commuting_groups(coeffs, codes)
        assert validate_commuting_groups(codes, gen_groups)

        term_count = sum(1 for row in codes if np.any(row != 0))
        print({
            "terms_requested": terms,
            "terms_after_compression": term_count,
            "qwc_groups": len(qwc_groups),
            "general_commuting_groups": len(gen_groups),
            "qwc_reduction": term_count / len(qwc_groups),
            "general_reduction": term_count / len(gen_groups),
        })

if __name__ == "__main__":
    main()
