from __future__ import annotations

def circuit_to_openqasm2_like(circuit) -> str:
    '''
    Export a lightweight OpenQASM 2-like text representation.

    This is not a full QASM implementation; it is a dependency-free interchange aid
    for common gates used in the examples.
    '''
    lines = [
        "OPENQASM 2.0;",
        'include "qelib1.inc";',
        f"qreg q[{circuit.num_qubits}];",
    ]

    for op in circuit.operations:
        name = op["name"]
        qs = op["qubits"]
        params = op.get("params", [])

        if name in ("rx", "ry", "rz"):
            lines.append(f"{name}({params[0]:.17g}) q[{qs[0]}];")
        elif name in ("x", "h"):
            lines.append(f"{name} q[{qs[0]}];")
        elif name == "cz":
            lines.append(f"cz q[{qs[0]}],q[{qs[1]}];")
        else:
            raise ValueError(f"Unsupported gate for QASM-like export: {name}")

    return "\n".join(lines) + "\n"

def hamiltonian_to_pennylane_like_terms(coeffs, codes):
    '''
    Return a dependency-free list of PennyLane-like term strings.

    Example:
        [(0.5, "Z(0) @ X(2)")]
    '''
    labels = {1: "X", 2: "Y", 3: "Z"}
    terms = []
    for c, row in zip(coeffs, codes):
        factors = [f"{labels[int(p)]}({q})" for q, p in enumerate(row) if int(p) != 0]
        terms.append((float(c), " @ ".join(factors) if factors else "I"))
    return terms
