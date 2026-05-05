# Reproduction Protocol

## Recommended Environment

- Python 3.10, 3.11, or 3.12.
- Fresh virtual environment.
- No Qiskit required.
- Numba optional.

## Commands

```bash
pip install -e .
pip install pytest
python external_reproduction/run_reproduction.py
```

## Pass Criteria

- Test suite exits with return code 0.
- Report generation exits with return code 0.
- Dashboard generation exits with return code 0.
- Scorecard generation exits with return code 0.
- Corrected H2 example reports energy near -1.857275.
- Grouped/asymmetric readout examples show mitigation reduces bias.
