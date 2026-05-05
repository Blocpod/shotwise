import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import numpy as np
from scipy.optimize import minimize

from vqa_estimator_lab import (
    StateVectorSimulator,
    X,
    givens_01_10,
    expectation_hamiltonian,
    encode_hamiltonian_dense,
    compress_encoded_hamiltonian,
    greedy_qwc_groups,
    grouped_energy_estimates,
    allocate_group_shots_uniform,
)
from vqa_estimator_lab.sampling import summarize_estimates

H2_TOY = [
    (-1.052373245772859, {}),
    (0.39793742484318045, {0: "Z"}),
    (-0.39793742484318045, {1: "Z"}),
    (-0.01128010425623538, {0: "Z", 1: "Z"}),
    (0.18093119978423156, {0: "X", 1: "X"}),
]

def prepare_state(theta):
    sim = StateVectorSimulator(2)
    sim.apply_gate(X, 0)  # prepare |01>
    sim.apply_two_qubit_gate(givens_01_10(theta), 0, 1)
    return sim

def energy(theta):
    return expectation_hamiltonian(prepare_state(float(theta)), H2_TOY)

def main():
    result = minimize(lambda x: energy(x[0]), x0=np.array([0.1]), method="COBYLA")
    theta = float(result.x[0])
    sim = prepare_state(theta)

    print("theta:", theta)
    print("energy:", result.fun)
    sim.print_state()

    coeffs, codes = encode_hamiltonian_dense(H2_TOY, 2)
    coeffs, codes = compress_encoded_hamiltonian(coeffs, codes)
    groups, bases = greedy_qwc_groups(coeffs, codes)

    print("QWC groups:", groups)
    print("QWC bases:", [b.tolist() for b in bases])

    rng = np.random.default_rng(123)
    shots = 65536
    group_shots = allocate_group_shots_uniform(len(groups), shots)
    estimates = grouped_energy_estimates(
        sim.state, coeffs, codes, groups, bases,
        group_shots=group_shots,
        repeats=2000,
        rng=rng,
    )

    print("grouped sampling summary:")
    print(summarize_estimates(estimates, result.fun))

if __name__ == "__main__":
    main()
