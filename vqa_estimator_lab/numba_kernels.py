from __future__ import annotations

import numpy as np

try:
    from numba import njit, prange
    NUMBA_AVAILABLE = True
except Exception:
    NUMBA_AVAILABLE = False
    njit = None
    prange = range

if NUMBA_AVAILABLE:
    @njit(cache=False)
    def apply_single_qubit_gate_kernel(state, gate, target):
        dim = state.shape[0]
        mask = 1 << target

        for i0 in range(dim):
            if i0 & mask:
                continue

            i1 = i0 | mask
            v0 = state[i0]
            v1 = state[i1]

            state[i0] = gate[0, 0] * v0 + gate[0, 1] * v1
            state[i1] = gate[1, 0] * v0 + gate[1, 1] * v1

    @njit(cache=False)
    def apply_two_qubit_gate_kernel(state, gate, q0, q1):
        dim = state.shape[0]
        mask0 = 1 << q0
        mask1 = 1 << q1

        for base in range(dim):
            if (base & mask0) or (base & mask1):
                continue

            idx00 = base
            idx01 = base | mask1
            idx10 = base | mask0
            idx11 = base | mask0 | mask1

            v00 = state[idx00]
            v01 = state[idx01]
            v10 = state[idx10]
            v11 = state[idx11]

            state[idx00] = gate[0, 0] * v00 + gate[0, 1] * v01 + gate[0, 2] * v10 + gate[0, 3] * v11
            state[idx01] = gate[1, 0] * v00 + gate[1, 1] * v01 + gate[1, 2] * v10 + gate[1, 3] * v11
            state[idx10] = gate[2, 0] * v00 + gate[2, 1] * v01 + gate[2, 2] * v10 + gate[2, 3] * v11
            state[idx11] = gate[3, 0] * v00 + gate[3, 1] * v01 + gate[3, 2] * v10 + gate[3, 3] * v11

    @njit(cache=False)
    def expectation_hamiltonian_encoded_serial(state, coeffs, pauli_codes):
        dim = state.shape[0]
        num_terms = pauli_codes.shape[0]
        num_qubits = pauli_codes.shape[1]
        total_real = 0.0

        for t in range(num_terms):
            coeff = coeffs[t]
            any_nonidentity = False
            for q in range(num_qubits):
                if pauli_codes[t, q] != 0:
                    any_nonidentity = True
                    break

            if not any_nonidentity:
                total_real += coeff
                continue

            term_real = 0.0

            for i in range(dim):
                j = i
                phase_real = 1.0
                phase_imag = 0.0

                for q in range(num_qubits):
                    p = pauli_codes[t, q]
                    if p == 0:
                        continue

                    bit = (i >> q) & 1
                    mask = 1 << q

                    if p == 1:
                        j = j ^ mask
                    elif p == 2:
                        j = j ^ mask
                        old_real = phase_real
                        if bit == 0:
                            phase_real = -phase_imag
                            phase_imag = old_real
                        else:
                            phase_real = phase_imag
                            phase_imag = -old_real
                    elif p == 3:
                        if bit == 1:
                            phase_real = -phase_real
                            phase_imag = -phase_imag

                ai_real = state[i].real
                ai_imag = -state[i].imag
                sj_real = state[j].real
                sj_imag = state[j].imag

                ps_real = phase_real * sj_real - phase_imag * sj_imag
                ps_imag = phase_real * sj_imag + phase_imag * sj_real

                prod_real = ai_real * ps_real - ai_imag * ps_imag
                term_real += prod_real

            total_real += coeff * term_real

        return total_real

    @njit(cache=False, parallel=True)
    def expectation_hamiltonian_encoded_parallel(state, coeffs, pauli_codes):
        dim = state.shape[0]
        num_terms = pauli_codes.shape[0]
        num_qubits = pauli_codes.shape[1]
        contributions = np.zeros(num_terms, dtype=np.float64)

        for t in prange(num_terms):
            coeff = coeffs[t]
            any_nonidentity = False
            for q in range(num_qubits):
                if pauli_codes[t, q] != 0:
                    any_nonidentity = True
                    break

            if not any_nonidentity:
                contributions[t] = coeff
                continue

            term_real = 0.0

            for i in range(dim):
                j = i
                phase_real = 1.0
                phase_imag = 0.0

                for q in range(num_qubits):
                    p = pauli_codes[t, q]
                    if p == 0:
                        continue

                    bit = (i >> q) & 1
                    mask = 1 << q

                    if p == 1:
                        j = j ^ mask
                    elif p == 2:
                        j = j ^ mask
                        old_real = phase_real
                        if bit == 0:
                            phase_real = -phase_imag
                            phase_imag = old_real
                        else:
                            phase_real = phase_imag
                            phase_imag = -old_real
                    elif p == 3:
                        if bit == 1:
                            phase_real = -phase_real
                            phase_imag = -phase_imag

                ai_real = state[i].real
                ai_imag = -state[i].imag
                sj_real = state[j].real
                sj_imag = state[j].imag

                ps_real = phase_real * sj_real - phase_imag * sj_imag
                ps_imag = phase_real * sj_imag + phase_imag * sj_real

                prod_real = ai_real * ps_real - ai_imag * ps_imag
                term_real += prod_real

            contributions[t] = coeff * term_real

        total = 0.0
        for t in range(num_terms):
            total += contributions[t]

        return total
