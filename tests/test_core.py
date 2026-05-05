import numpy as np

from vqa_estimator_lab import (
    StateVectorSimulator,
    X,
    H,
    CZ,
    givens_01_10,
    encode_hamiltonian_dense,
    compress_encoded_hamiltonian,
    greedy_qwc_groups,
    grouped_energy_estimates,
    allocate_group_shots_uniform,
)
from vqa_estimator_lab.hamiltonian import expectation_hamiltonian

def test_bell_expectations():
    sim = StateVectorSimulator(2)
    sim.apply_gate(H, 0)
    sim.apply_controlled_gate(X, 0, 1)

    assert abs(sim.expectation_pauli_string({0: "Z", 1: "Z"}) - 1.0) < 1e-9
    assert abs(sim.expectation_pauli_string({0: "X", 1: "X"}) - 1.0) < 1e-9
    assert abs(sim.expectation_pauli_string({0: "Y", 1: "Y"}) + 1.0) < 1e-9

def test_two_qubit_gate_cz():
    sim = StateVectorSimulator(2)
    sim.apply_gate(H, 0)
    sim.apply_gate(H, 1)
    sim.apply_two_qubit_gate(CZ, 0, 1)

    expected = np.array([0.5, 0.5, 0.5, -0.5], dtype=np.complex128)
    assert np.allclose(sim.state, expected)

def test_h2_toy_givens_ground_energy():
    h2 = [
        (-1.052373245772859, {}),
        (0.39793742484318045, {0: "Z"}),
        (-0.39793742484318045, {1: "Z"}),
        (-0.01128010425623538, {0: "Z", 1: "Z"}),
        (0.18093119978423156, {0: "X", 1: "X"}),
    ]

    theta = 0.1117685
    sim = StateVectorSimulator(2)
    sim.apply_gate(X, 0)
    sim.apply_two_qubit_gate(givens_01_10(theta), 0, 1)

    energy = expectation_hamiltonian(sim, h2)
    assert abs(energy - (-1.85727503020238)) < 1e-7

def test_compression_and_qwc_grouping():
    h = [
        (1.0, {0: "Z"}),
        (2.0, {0: "Z"}),
        (3.0, {1: "Z"}),
        (4.0, {0: "X", 1: "X"}),
    ]

    coeffs, codes = encode_hamiltonian_dense(h, 2)
    coeffs2, codes2 = compress_encoded_hamiltonian(coeffs, codes)

    assert len(coeffs2) == 3
    groups, bases = greedy_qwc_groups(coeffs2, codes2)
    assert len(groups) == 2

def test_grouped_estimator_runs():
    h2 = [
        (-1.052373245772859, {}),
        (0.39793742484318045, {0: "Z"}),
        (-0.39793742484318045, {1: "Z"}),
        (-0.01128010425623538, {0: "Z", 1: "Z"}),
        (0.18093119978423156, {0: "X", 1: "X"}),
    ]

    theta = 0.1117685
    sim = StateVectorSimulator(2)
    sim.apply_gate(X, 0)
    sim.apply_two_qubit_gate(givens_01_10(theta), 0, 1)

    coeffs, codes = encode_hamiltonian_dense(h2, 2)
    coeffs, codes = compress_encoded_hamiltonian(coeffs, codes)
    groups, bases = greedy_qwc_groups(coeffs, codes)

    estimates = grouped_energy_estimates(
        sim.state,
        coeffs,
        codes,
        groups,
        bases,
        group_shots=allocate_group_shots_uniform(len(groups), 2000),
        repeats=100,
        rng=np.random.default_rng(123),
    )

    assert estimates.shape == (100,)
    assert np.isfinite(estimates).all()
