from __future__ import annotations

import json

from .hamiltonian import CODE_PAULI, encode_hamiltonian_dense

def encoded_hamiltonian_to_jsonable(coeffs, codes):
    return {
        "format": "vqa_estimator_lab.encoded_hamiltonian.v1",
        "num_terms": int(len(coeffs)),
        "num_qubits": int(codes.shape[1]) if len(codes) else 0,
        "terms": [
            {
                "coefficient": float(c),
                "pauli": {str(q): CODE_PAULI[int(p)] for q, p in enumerate(row) if int(p) != 0}
            }
            for c, row in zip(coeffs, codes)
        ],
    }

def encoded_hamiltonian_to_json(coeffs, codes, path=None, indent: int = 2):
    data = encoded_hamiltonian_to_jsonable(coeffs, codes)
    text = json.dumps(data, indent=indent)
    if path is not None:
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
    return text

def encoded_hamiltonian_from_jsonable(data):
    if data.get("format") != "vqa_estimator_lab.encoded_hamiltonian.v1":
        raise ValueError("Unsupported Hamiltonian JSON format.")

    num_qubits = int(data["num_qubits"])
    hamiltonian = []
    for term in data["terms"]:
        coeff = float(term["coefficient"])
        pstr = {int(q): str(p) for q, p in term["pauli"].items()}
        hamiltonian.append((coeff, pstr))

    return encode_hamiltonian_dense(hamiltonian, num_qubits)

def encoded_hamiltonian_from_json(path_or_text):
    if isinstance(path_or_text, str) and path_or_text.strip().startswith("{"):
        data = json.loads(path_or_text)
    else:
        with open(path_or_text, "r", encoding="utf-8") as f:
            data = json.load(f)
    return encoded_hamiltonian_from_jsonable(data)


def parse_sparse_pauliop_like(terms, little_endian: bool = False):
    """
    Parse a simple SparsePauliOp-like representation.

    Input:
        terms = [
            ("ZI", 0.5),
            ("XX", -0.2),
        ]

    By default, the leftmost character is the highest qubit index, matching common
    printed Pauli-string conventions. Set little_endian=True if the first character
    should map to qubit 0.
    """
    if not terms:
        raise ValueError("No terms provided.")

    num_qubits = len(terms[0][0])
    hamiltonian = []

    for pauli_label, coeff in terms:
        if len(pauli_label) != num_qubits:
            raise ValueError("All Pauli labels must have the same length.")

        pstr = {}
        for pos, p in enumerate(pauli_label.upper()):
            if p == "I":
                continue
            if p not in ("X", "Y", "Z"):
                raise ValueError(f"Unsupported Pauli character: {p}")

            q = pos if little_endian else num_qubits - 1 - pos
            pstr[q] = p

        hamiltonian.append((float(coeff), pstr))

    return encode_hamiltonian_dense(hamiltonian, num_qubits)

def parse_openfermion_text(text: str):
    """
    Parse a small OpenFermion-style qubit Hamiltonian text format.

    Supported line examples:
        -1.052373 []
        0.397937 [Z0]
        -0.01128 [Z0 Z1]
        0.18093 [X0 X1]

    This is intentionally minimal and dependency-free.
    """
    hamiltonian = []
    max_q = -1

    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue

        if "[" not in line or "]" not in line:
            raise ValueError(f"Invalid line: {line}")

        coeff_text = line.split("[", 1)[0].strip()
        body = line.split("[", 1)[1].split("]", 1)[0].strip()

        coeff = float(coeff_text)
        pstr = {}

        if body:
            for tok in body.split():
                p = tok[0].upper()
                q = int(tok[1:])
                if p not in ("X", "Y", "Z"):
                    raise ValueError(f"Unsupported Pauli: {tok}")
                pstr[q] = p
                max_q = max(max_q, q)

        hamiltonian.append((coeff, pstr))

    num_qubits = max_q + 1 if max_q >= 0 else 1
    return encode_hamiltonian_dense(hamiltonian, num_qubits)
