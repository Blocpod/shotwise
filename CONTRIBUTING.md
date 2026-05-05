# Contributing to VQA Estimator Lab

## Development Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install pytest
python -m pytest tests -q
```

Optional acceleration:

```bash
pip install numba
```

Optional integrations:

```bash
pip install qiskit
```

## Contribution Rules

1. Do not add molecular Hamiltonian fixtures without provenance.
2. Add or update tests for every feature.
3. Keep toy fixtures clearly labeled.
4. Keep optional dependencies optional.
5. Report benchmark hardware and environment when submitting performance claims.

## Fixture Requirements

External molecular fixtures must include:

- Geometry.
- Basis.
- Charge and multiplicity.
- Mapping.
- Active-space/tapering choices.
- Source or generation script.
- Dependency versions.

## Code Style

- Prefer clear reference implementations before optimized kernels.
- Keep dependency-heavy integrations behind optional adapters.
- Avoid claims that are not supported by tests or reproducible reports.
