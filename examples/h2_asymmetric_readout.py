import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import numpy as np

from vqa_estimator_lab import (
    StateVectorSimulator,
    X,
    givens_01_10,
    encode_hamiltonian_dense,
    compress_encoded_hamiltonian,
    greedy_qwc_groups,
    allocate_group_shots_uniform,
    full_confusion_matrix,
)
from vqa_estimator_lab.noise import grouped_energy_estimates_confusion_readout
from vqa_estimator_lab.sampling import summarize_estimates

H2_TOY = [
    (-1.052373245772859, {}),
    (0.39793742484318045, {0: "Z"}),
    (-0.39793742484318045, {1: "Z"}),
    (-0.01128010425623538, {0: "Z", 1: "Z"}),
    (0.18093119978423156, {0: "X", 1: "X"}),
]

TRUTH = -1.85727503020238

def main():
    sim = StateVectorSimulator(2)
    sim.apply_gate(X, 0)
    sim.apply_two_qubit_gate(givens_01_10(0.1117685), 0, 1)

    coeffs, codes = encode_hamiltonian_dense(H2_TOY, 2)
    coeffs, codes = compress_encoded_hamiltonian(coeffs, codes)
    groups, bases = greedy_qwc_groups(coeffs, codes)
    group_shots = allocate_group_shots_uniform(len(groups), 65536)

    # Asymmetric readout: true 0 is misread as 1 with 3%, true 1 as 0 with 8%.
    confusion = full_confusion_matrix(num_qubits=2, p01=0.03, p10=0.08)

    rng = np.random.default_rng(789)
    noisy = grouped_energy_estimates_confusion_readout(
        sim.state, coeffs, codes, groups, bases, group_shots,
        repeats=3000, confusion_matrix=confusion, mitigated=False, rng=rng
    )
    mitigated = grouped_energy_estimates_confusion_readout(
        sim.state, coeffs, codes, groups, bases, group_shots,
        repeats=3000, confusion_matrix=confusion, mitigated=True,
        clip_mitigation=False, rng=rng
    )

    print("Asymmetric noisy summary:")
    print(summarize_estimates(noisy, TRUTH))
    print("Asymmetric mitigated summary:")
    print(summarize_estimates(mitigated, TRUTH))

if __name__ == "__main__":
    main()
