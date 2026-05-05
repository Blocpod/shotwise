import numpy as np

from vqa_estimator_lab import (
    StateVectorSimulator,
    X,
    givens_01_10,
    encode_hamiltonian_dense,
    compress_encoded_hamiltonian,
    greedy_qwc_groups,
    allocate_group_shots_uniform,
    allocate_group_shots_adaptive_pilot,
)
from vqa_estimator_lab.noise import grouped_energy_estimates_symmetric_readout
from vqa_estimator_lab.interop import encoded_hamiltonian_to_json, encoded_hamiltonian_from_json

H2_TOY = [
    (-1.052373245772859, {}),
    (0.39793742484318045, {0: "Z"}),
    (-0.39793742484318045, {1: "Z"}),
    (-0.01128010425623538, {0: "Z", 1: "Z"}),
    (0.18093119978423156, {0: "X", 1: "X"}),
]

def corrected_h2_state():
    sim = StateVectorSimulator(2)
    sim.apply_gate(X, 0)
    sim.apply_two_qubit_gate(givens_01_10(0.1117685), 0, 1)
    return sim

def encoded_h2():
    coeffs, codes = encode_hamiltonian_dense(H2_TOY, 2)
    return compress_encoded_hamiltonian(coeffs, codes)

def test_grouped_readout_mitigation_improves_bias():
    sim = corrected_h2_state()
    coeffs, codes = encoded_h2()
    groups, bases = greedy_qwc_groups(coeffs, codes)
    shots = allocate_group_shots_uniform(len(groups), 20000)
    truth = -1.85727503020238
    rng = np.random.default_rng(123)

    noisy = grouped_energy_estimates_symmetric_readout(
        sim.state, coeffs, codes, groups, bases, shots,
        repeats=2000, p=0.05, mitigated=False, rng=rng
    )
    mitigated = grouped_energy_estimates_symmetric_readout(
        sim.state, coeffs, codes, groups, bases, shots,
        repeats=2000, p=0.05, mitigated=True, rng=rng
    )

    assert abs(mitigated.mean() - truth) < abs(noisy.mean() - truth)

def test_adaptive_group_allocator_budget_conservation():
    sim = corrected_h2_state()
    coeffs, codes = encoded_h2()
    groups, bases = greedy_qwc_groups(coeffs, codes)
    alloc, diag = allocate_group_shots_adaptive_pilot(
        sim.state, coeffs, codes, groups, bases,
        total_shots=1000,
        pilot_fraction=0.1,
        min_pilot_shots=20,
        rng=np.random.default_rng(1),
    )

    assert int(alloc.sum()) == 1000
    assert len(alloc) == len(groups)
    assert all(x > 0 for x in alloc)
    assert "sigma_hats" in diag

def test_hamiltonian_json_roundtrip():
    coeffs, codes = encoded_h2()
    text = encoded_hamiltonian_to_json(coeffs, codes)
    coeffs2, codes2 = encoded_hamiltonian_from_json(text)

    assert np.allclose(coeffs, coeffs2)
    assert np.array_equal(codes, codes2)
