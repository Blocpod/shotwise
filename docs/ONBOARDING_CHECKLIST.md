# External Collaborator Onboarding Checklist

## Before Running

- Confirm Python version.
- Install package in editable mode: `pip install -e .`
- Optional: install `numba` for accelerated benchmarks.
- Optional: install Qiskit only if testing Qiskit adapters.

## Validation

Run:

```bash
python -m pytest tests -q
python examples/h2_toy_corrected.py
python examples/h2_grouped_mitigation.py
python benchmarks/generate_report.py
python benchmarks/generate_dashboard.py
```

## Report Back

Please provide:

- Test output.
- Generated `reports/benchmark_report.json`.
- Generated `reports/dashboard.html`.
- Hardware/OS/Python information.
- Any dependency issues.
- Whether benchmark results match expected qualitative behavior.

## Molecular Fixtures

Do not submit external molecular Hamiltonians without:

- Geometry.
- Basis.
- Charge and multiplicity.
- Mapping.
- Active-space/tapering choices.
- Generation script.
- Dependency versions.
