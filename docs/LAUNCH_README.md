# Shotwise Launch README

## Positioning

Shotwise is an estimator-optimization and validation framework for variational quantum algorithms.

It is not positioned as a generic replacement for Qiskit Aer, Cirq/qsim, or cuQuantum. Its differentiator is the combination of:

- Ansätze validation.
- Finite-shot estimation.
- Pauli compression.
- QWC and general commuting grouping.
- Readout-error modeling and mitigation.
- Covariance-aware shot allocation.
- Reproducible report generation.

## Launch Claims

Supported by the current package:

- Corrected toy-H2 benchmark validates ansatz failure detection.
- Grouped measurement improves finite-shot estimation.
- Symmetric and asymmetric readout-error mitigation reduce bias.
- Numba-backed benchmark scripts demonstrate medium-scale simulator feasibility.
- Reporting and dashboard artifacts support external reproducibility.

Not yet claimed:

- Verified LiH performance.
- Superiority over mature production simulators.
- Full chemistry stack replacement.
- Joint-measurement synthesis for all general commuting groups.

## Recommended v1.0 Gate

Release v1.0 only after:

1. CI passes in a public repository.
2. License is finalized.
3. External fixture provenance policy is enforced.
4. At least one external collaborator reproduces the report.
