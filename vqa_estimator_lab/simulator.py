from __future__ import annotations

import numpy as np
from collections import Counter

class StateVectorSimulator:
    '''
    Minimal state-vector simulator.

    Convention:
        - Qubit 0 is the least significant bit.
        - Printed bitstrings show qubit 0 on the right.
        - Two-qubit local basis follows argument order: |q0 q1> = |00>, |01>, |10>, |11>.
    '''

    def __init__(self, num_qubits: int, rng=None):
        if num_qubits < 1:
            raise ValueError("num_qubits must be at least 1.")
        self.num_qubits = int(num_qubits)
        self.dim = 1 << self.num_qubits
        self.state = np.zeros(self.dim, dtype=np.complex128)
        self.state[0] = 1.0 + 0.0j
        self.rng = rng if rng is not None else np.random.default_rng()

    def copy(self) -> "StateVectorSimulator":
        sim = StateVectorSimulator(self.num_qubits, rng=self.rng)
        sim.state = self.state.copy()
        return sim

    def reset(self) -> None:
        self.state[:] = 0.0
        self.state[0] = 1.0 + 0.0j

    def normalize(self) -> None:
        norm = np.linalg.norm(self.state)
        if norm == 0:
            raise ValueError("State norm is zero.")
        self.state /= norm

    def _validate_qubit(self, qubit: int) -> None:
        if not 0 <= qubit < self.num_qubits:
            raise ValueError(f"Invalid qubit {qubit}.")

    def _validate_gate(self, gate, shape):
        gate = np.asarray(gate, dtype=np.complex128)
        if gate.shape != shape:
            raise ValueError(f"Gate must have shape {shape}.")
        return gate

    def apply_gate(self, gate, target: int) -> None:
        self._validate_qubit(target)
        gate = self._validate_gate(gate, (2, 2))
        mask = 1 << target
        new_state = self.state.copy()

        for idx0 in range(self.dim):
            if idx0 & mask:
                continue

            idx1 = idx0 | mask
            v0 = self.state[idx0]
            v1 = self.state[idx1]

            new_state[idx0] = gate[0, 0] * v0 + gate[0, 1] * v1
            new_state[idx1] = gate[1, 0] * v0 + gate[1, 1] * v1

        self.state = new_state

    def apply_controlled_gate(self, gate, control: int, target: int) -> None:
        self._validate_qubit(control)
        self._validate_qubit(target)
        if control == target:
            raise ValueError("Control and target must be different.")

        gate = self._validate_gate(gate, (2, 2))
        control_mask = 1 << control
        target_mask = 1 << target
        new_state = self.state.copy()

        for idx0 in range(self.dim):
            if not (idx0 & control_mask) or (idx0 & target_mask):
                continue

            idx1 = idx0 | target_mask
            v0 = self.state[idx0]
            v1 = self.state[idx1]

            new_state[idx0] = gate[0, 0] * v0 + gate[0, 1] * v1
            new_state[idx1] = gate[1, 0] * v0 + gate[1, 1] * v1

        self.state = new_state

    def apply_two_qubit_gate(self, gate, q0: int, q1: int) -> None:
        self._validate_qubit(q0)
        self._validate_qubit(q1)
        if q0 == q1:
            raise ValueError("q0 and q1 must be different.")

        gate = self._validate_gate(gate, (4, 4))
        mask0 = 1 << q0
        mask1 = 1 << q1
        new_state = self.state.copy()

        for base in range(self.dim):
            if (base & mask0) or (base & mask1):
                continue

            idx00 = base
            idx01 = base | mask1
            idx10 = base | mask0
            idx11 = base | mask0 | mask1

            local_v = np.array([
                self.state[idx00],
                self.state[idx01],
                self.state[idx10],
                self.state[idx11],
            ], dtype=np.complex128)

            transformed = gate @ local_v

            new_state[idx00] = transformed[0]
            new_state[idx01] = transformed[1]
            new_state[idx10] = transformed[2]
            new_state[idx11] = transformed[3]

        self.state = new_state

    def probabilities(self) -> np.ndarray:
        probs = np.abs(self.state) ** 2
        return probs / probs.sum()

    def sample_counts(self, shots: int = 1024) -> dict[str, int]:
        probs = self.probabilities()
        outcomes = self.rng.choice(self.dim, size=int(shots), p=probs)
        labels = [format(int(x), f"0{self.num_qubits}b") for x in outcomes]
        return dict(Counter(labels))

    def expectation_pauli_string(self, pauli_string: dict[int, str]) -> float:
        '''
        Compute <psi|P|psi> for a Pauli string.

        Example:
            {0: "X", 2: "Z"} means X_0 Z_2.
        '''
        for q, p in pauli_string.items():
            self._validate_qubit(q)
            if p not in ("I", "X", "Y", "Z"):
                raise ValueError(f"Invalid Pauli operator {p} on qubit {q}.")

        result = 0.0 + 0.0j

        for i, amp_i in enumerate(self.state):
            j = i
            phase = 1.0 + 0.0j

            for q, p in pauli_string.items():
                bit = (i >> q) & 1
                mask = 1 << q

                if p == "I":
                    pass
                elif p == "X":
                    j ^= mask
                elif p == "Y":
                    j ^= mask
                    phase *= 1j if bit == 0 else -1j
                elif p == "Z":
                    phase *= 1 if bit == 0 else -1

            result += np.conj(amp_i) * phase * self.state[j]

        return float(np.real_if_close(result))

    def print_state(self, threshold: float = 1e-9) -> None:
        for i, amp in enumerate(self.state):
            prob = abs(amp) ** 2
            if prob > threshold:
                print(f"|{format(i, f'0{self.num_qubits}b')}>: {amp:.6f}  Prob: {prob:.6%}")
