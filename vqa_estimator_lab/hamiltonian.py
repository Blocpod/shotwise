from __future__ import annotations

import numpy as np

PAULI_CODE = {"I": 0, "X": 1, "Y": 2, "Z": 3}
CODE_PAULI = {v: k for k, v in PAULI_CODE.items()}

def encode_hamiltonian_dense(hamiltonian: list[tuple[float, dict[int, str]]], num_qubits: int):
    coeffs = []
    codes = []

    for coeff, pstr in hamiltonian:
        row = np.zeros(num_qubits, dtype=np.int8)
        for q, p in pstr.items():
            row[int(q)] = PAULI_CODE[p]
        coeffs.append(float(coeff))
        codes.append(row)

    return np.array(coeffs, dtype=np.float64), np.vstack(codes).astype(np.int8)

def decode_pauli_code(row) -> dict[int, str]:
    return {int(q): CODE_PAULI[int(p)] for q, p in enumerate(row) if int(p) != 0}

def compress_encoded_hamiltonian(coeffs, codes, coeff_tol: float = 0.0):
    accumulator = {}

    for c, row in zip(coeffs, codes):
        key = tuple(int(x) for x in row)
        accumulator[key] = accumulator.get(key, 0.0) + float(c)

    new_coeffs = []
    new_codes = []

    for key, c in accumulator.items():
        if abs(c) > coeff_tol:
            new_coeffs.append(c)
            new_codes.append(key)

    return np.array(new_coeffs, dtype=np.float64), np.array(new_codes, dtype=np.int8)

def expectation_hamiltonian(sim, hamiltonian: list[tuple[float, dict[int, str]]]) -> float:
    energy = 0.0
    for coeff, pstr in hamiltonian:
        if pstr == {}:
            energy += coeff
        else:
            energy += coeff * sim.expectation_pauli_string(pstr)
    return float(energy)

def pauli_weight(code_row) -> int:
    return int(np.count_nonzero(code_row))

def encoded_term_expectation_from_sim(sim, code_row) -> float | None:
    pstr = decode_pauli_code(code_row)
    if not pstr:
        return None
    return sim.expectation_pauli_string(pstr)

def exact_encoded_term_expectations(sim, codes):
    out = []
    for row in codes:
        out.append(encoded_term_expectation_from_sim(sim, row))
    return out
