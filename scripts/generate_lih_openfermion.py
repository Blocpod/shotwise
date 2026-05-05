#!/usr/bin/env python
'''
Generate a LiH qubit Hamiltonian fixture using OpenFermion and PySCF.

This script is intentionally optional and dependency-gated. It does not ship a fabricated
LiH Hamiltonian. To use it, install compatible versions of openfermion and openfermionpyscf.

Example:
    pip install openfermion openfermionpyscf pyscf
    python scripts/generate_lih_openfermion.py

Output:
    fixtures/lih_sto3g_jw_openfermion.txt
    fixtures/lih_sto3g_jw_manifest.json

Default chemistry:
    LiH linear molecule
    geometry: Li at (0, 0, 0), H at (0, 0, 1.45 Angstrom)
    basis: STO-3G
    multiplicity: 1
    charge: 0
    mapping: Jordan-Wigner
'''
from __future__ import annotations

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "fixtures"

def main():
    try:
        from openfermion import MolecularData, jordan_wigner, get_fermion_operator
        from openfermionpyscf import run_pyscf
    except Exception as exc:
        raise SystemExit(
            "OpenFermion/OpenFermion-PySCF dependencies are not installed. "
            "Install with: pip install openfermion openfermionpyscf pyscf\n"
            f"Original error: {exc}"
        )

    geometry = [("Li", (0.0, 0.0, 0.0)), ("H", (0.0, 0.0, 1.45))]
    basis = "sto-3g"
    multiplicity = 1
    charge = 0

    molecule = MolecularData(
        geometry=geometry,
        basis=basis,
        multiplicity=multiplicity,
        charge=charge,
        description="lih_1p45_sto3g",
    )
    molecule = run_pyscf(molecule, run_scf=True, run_fci=False)

    fermion_hamiltonian = get_fermion_operator(molecule.get_molecular_hamiltonian())
    qubit_hamiltonian = jordan_wigner(fermion_hamiltonian)
    qubit_hamiltonian.compress()

    OUT.mkdir(exist_ok=True)
    txt_path = OUT / "lih_sto3g_jw_openfermion.txt"

    lines = []
    for term, coeff in sorted(qubit_hamiltonian.terms.items(), key=lambda kv: str(kv[0])):
        coeff = complex(coeff)
        if abs(coeff.imag) > 1e-10:
            raise ValueError(f"Unexpected complex coefficient: {coeff}")
        if len(term) == 0:
            body = ""
        else:
            body = " ".join(f"{p}{q}" for q, p in term)
        lines.append(f"{coeff.real:.17g} [{body}]")

    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    max_q = 0
    for term in qubit_hamiltonian.terms:
        for q, _ in term:
            max_q = max(max_q, q)

    manifest = {
        "name": "lih_sto3g_jw_openfermion",
        "path": str(txt_path.relative_to(ROOT)),
        "type": "external_generated_molecular_qubit_hamiltonian",
        "num_qubits": max_q + 1,
        "term_count": len(qubit_hamiltonian.terms),
        "provenance": "Generated locally using OpenFermion + OpenFermion-PySCF + PySCF.",
        "generation_script": "scripts/generate_lih_openfermion.py",
        "chemistry": {
            "molecule": "LiH",
            "geometry_angstrom": geometry,
            "basis": basis,
            "multiplicity": multiplicity,
            "charge": charge,
            "mapping": "Jordan-Wigner",
            "bond_length_angstrom": 1.45,
        },
        "notes": "Generated fixture; verify dependency versions and quantum-chemistry conventions before publication.",
    }

    (OUT / "lih_sto3g_jw_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Wrote {txt_path}")
    print(json.dumps(manifest, indent=2))

if __name__ == "__main__":
    main()
