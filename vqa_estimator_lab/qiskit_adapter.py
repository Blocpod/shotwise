from __future__ import annotations
import importlib.util

def qiskit_available() -> bool:
    return importlib.util.find_spec("qiskit") is not None

def from_qiskit_sparse_pauli_op(op, little_endian: bool = False):
    from .interop import parse_sparse_pauliop_like
    terms = []
    for pauli, coeff in zip(op.paulis, op.coeffs):
        label = pauli.to_label() if hasattr(pauli, "to_label") else str(pauli)
        c = complex(coeff)
        if abs(c.imag) > 1e-12:
            raise ValueError("Complex Hamiltonian coefficients are not supported.")
        terms.append((label, float(c.real)))
    return parse_sparse_pauliop_like(terms, little_endian=little_endian)

def to_qiskit_sparse_pauli_op(coeffs, codes):
    if not qiskit_available():
        raise ImportError("Qiskit is not installed.")
    from qiskit.quantum_info import SparsePauliOp
    char = {0: "I", 1: "X", 2: "Y", 3: "Z"}
    labels = ["".join(char[int(p)] for p in reversed(row)) for row in codes]
    return SparsePauliOp(labels, coeffs=[float(c) for c in coeffs])
