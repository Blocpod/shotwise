import numpy as np

from vqa_estimator_lab import (
    StateVectorSimulator,
    X,
    givens_01_10,
    encode_hamiltonian_dense,
    compress_encoded_hamiltonian,
    greedy_qwc_groups,
)
from vqa_estimator_lab.commutation import commute, greedy_commuting_groups, validate_commuting_groups
from vqa_estimator_lab.covariance import allocate_group_shots_covariance, qwc_group_covariance_matrix
from vqa_estimator_lab.interop import parse_sparse_pauliop_like, parse_openfermion_text

def test_general_commutation_detects_xx_yy_zz_commuting():
    coeffs, codes = encode_hamiltonian_dense([
        (1.0, {0: "X", 1: "X"}),
        (1.0, {0: "Y", 1: "Y"}),
        (1.0, {0: "Z", 1: "Z"}),
    ], 2)

    assert commute(codes[0], codes[1])
    assert commute(codes[0], codes[2])
    assert commute(codes[1], codes[2])

    groups = greedy_commuting_groups(coeffs, codes)
    assert validate_commuting_groups(codes, groups)
    assert len(groups) == 1

def test_qwc_vs_general_grouping_difference():
    coeffs, codes = encode_hamiltonian_dense([
        (1.0, {0: "X", 1: "X"}),
        (1.0, {0: "Y", 1: "Y"}),
        (1.0, {0: "Z", 1: "Z"}),
    ], 2)
    qwc, _ = greedy_qwc_groups(coeffs, codes)
    general = greedy_commuting_groups(coeffs, codes)

    assert len(qwc) == 3
    assert len(general) == 1

def test_covariance_allocation_conserves_budget():
    h2 = [
        (-1.052373245772859, {}),
        (0.39793742484318045, {0: "Z"}),
        (-0.39793742484318045, {1: "Z"}),
        (-0.01128010425623538, {0: "Z", 1: "Z"}),
        (0.18093119978423156, {0: "X", 1: "X"}),
    ]
    sim = StateVectorSimulator(2)
    sim.apply_gate(X, 0)
    sim.apply_two_qubit_gate(givens_01_10(0.1117685), 0, 1)

    coeffs, codes = encode_hamiltonian_dense(h2, 2)
    coeffs, codes = compress_encoded_hamiltonian(coeffs, codes)
    groups, bases = greedy_qwc_groups(coeffs, codes)

    alloc, diag = allocate_group_shots_covariance(sim.state, coeffs, codes, groups, bases, 1000)
    assert int(alloc.sum()) == 1000
    assert len(diag["sigmas"]) == len(groups)

    cov = qwc_group_covariance_matrix(sim.state, coeffs, codes, groups[0], bases[0])
    assert cov.shape[0] == len(groups[0])

def test_import_helpers():
    coeffs, codes = parse_sparse_pauliop_like([
        ("ZI", 0.5),
        ("XX", -0.2),
    ])
    assert codes.shape == (2, 2)

    coeffs2, codes2 = parse_openfermion_text('''
    -1.0 []
    0.5 [Z0]
    -0.2 [X0 X1]
    ''')
    assert codes2.shape == (3, 2)
    assert np.isclose(coeffs2[0], -1.0)
