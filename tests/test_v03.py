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
    Circuit,
)
from vqa_estimator_lab.noise import grouped_energy_estimates_confusion_readout
from vqa_estimator_lab.readout import single_qubit_confusion_matrix, mitigate_probability_vector
from vqa_estimator_lab.adapters import circuit_to_openqasm2_like, hamiltonian_to_pennylane_like_terms

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

def test_confusion_matrix_shapes_and_inverse():
    A = single_qubit_confusion_matrix(0.03, 0.08)
    assert A.shape == (2, 2)
    assert np.allclose(A.sum(axis=0), 1.0)

    C = full_confusion_matrix(2, 0.03, 0.08)
    assert C.shape == (4, 4)
    assert np.allclose(C.sum(axis=0), 1.0)

    p = np.array([0.7, 0.1, 0.1, 0.1])
    obs = C @ p
    mit = mitigate_probability_vector(obs, C, clip=False)
    assert np.allclose(p, mit)

def test_asymmetric_readout_mitigation_improves_bias():
    sim = corrected_h2_state()
    coeffs, codes = encoded_h2()
    groups, bases = greedy_qwc_groups(coeffs, codes)
    truth = -1.85727503020238
    shots = allocate_group_shots_uniform(len(groups), 30000)
    confusion = full_confusion_matrix(2, p01=0.03, p10=0.08)
    rng = np.random.default_rng(42)

    noisy = grouped_energy_estimates_confusion_readout(
        sim.state, coeffs, codes, groups, bases, shots,
        repeats=1500, confusion_matrix=confusion, mitigated=False, rng=rng
    )
    mitigated = grouped_energy_estimates_confusion_readout(
        sim.state, coeffs, codes, groups, bases, shots,
        repeats=1500, confusion_matrix=confusion, mitigated=True,
        clip_mitigation=False, rng=rng
    )

    assert abs(mitigated.mean() - truth) < abs(noisy.mean() - truth)

def test_adapter_exports():
    c = Circuit(2).x(0).ry(0.12, 1).cz(0, 1)
    qasm = circuit_to_openqasm2_like(c)
    assert "OPENQASM 2.0" in qasm
    assert "cz q[0],q[1];" in qasm

    coeffs, codes = encoded_h2()
    terms = hamiltonian_to_pennylane_like_terms(coeffs, codes)
    assert len(terms) == len(coeffs)
    assert any("X(0) @ X(1)" in t[1] for t in terms)
