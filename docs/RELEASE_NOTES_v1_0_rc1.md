# VQA Estimator Lab v1.0.0rc1 Release Notes

## Purpose

v1.0.0rc1 is the first release candidate intended for external technical reproduction.

## Included

- Apache-2.0 license and NOTICE.
- Corrected toy-H2 benchmark.
- State-vector simulator core.
- Pauli expectation evaluation.
- Duplicate Pauli compression.
- QWC and general commuting grouping.
- Readout-error simulation and mitigation.
- Adaptive and covariance-aware shot allocation.
- Optional Qiskit adapter.
- Optional LiH generation script with dependency-gated provenance.
- Benchmark report, dashboard, and scorecard generation.
- External reproduction kit.

## Known Deferrals

The following are intentionally deferred beyond this release candidate:

- Verified external molecular Hamiltonian fixture.
- General commuting joint-measurement circuit synthesis.
- GPU acceleration.
- Density-matrix noise simulation.
- Hosted public CI result.

## Release Gate

The stable v1.0 release should be cut only after at least one external reviewer completes
`external_reproduction/run_reproduction.py` and returns the reproduction results and feedback form.
