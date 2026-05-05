# Pilot User Reproducibility Guide

This guide is intended for collaborators evaluating VQA Estimator Lab.

## Quick Validation

```bash
pip install -e .
python -m pytest tests -q
python examples/h2_toy_corrected.py
python examples/h2_grouped_mitigation.py
python benchmarks/generate_report.py
```

## What to Report

For every benchmark or molecular fixture, include:

- Package version.
- Python version and platform.
- Hamiltonian source.
- Molecular geometry, basis, charge, multiplicity.
- Fermion-to-qubit mapping.
- Active-space or tapering reductions, if any.
- Number of qubits and Pauli terms before/after compression.
- Grouping method and number of measurement groups.
- Shot budget and allocation rule.
- Noise model and mitigation method.

## Fixture Policy

Toy fixtures are allowed for validation if clearly labeled as toy/reduced fixtures.

External molecular fixtures must include:

- Generation script.
- Dependency versions.
- Geometry.
- Basis set.
- Mapping.
- Active-space/tapering choices.
- Source or reproducibility command.

Do not publish a molecular benchmark without this metadata.
