# Shotwise

**Shotwise: VQA Estimator Lab** is a reproducible research framework for estimator optimization in variational quantum algorithms.

It focuses on finite-shot simulation, readout-error studies, Pauli-term grouping, shot allocation, and release-grade validation for VQA workflows.

This repository is the executable continuation of the research prototype documented in the VQA simulator findings report.

## Why Shotwise

Shotwise is not a generic replacement for production quantum simulators such as Qiskit Aer, Cirq/qsim, or cuQuantum.
Its purpose is narrower: make estimator behavior inspectable before researchers spend hardware budget or trust VQA benchmark conclusions.

The core workflow is:

```text
compress Hamiltonian terms -> group measurements -> allocate shots -> model readout error -> mitigate -> report confidence
```

## Current scope

- State-vector simulator with little-endian qubit convention.
- Single-qubit and two-qubit gate application.
- Arbitrary Pauli-string expectations.
- Encoded Pauli Hamiltonians.
- Duplicate Pauli-term compression.
- Qubit-wise commuting (QWC) grouping.
- Grouped shot-based energy estimation.
- Toy/reduced 2-qubit H2 benchmark with corrected Givens ansatz.
- Numba-accelerated expectation and gate kernels when Numba is available.
- Readout-error and mitigation utilities.

## Install

```bash
pip install -e .
```

Optional acceleration:

```bash
pip install numba
```

## Quick start

```bash
python examples/h2_toy_corrected.py
python benchmarks/benchmark_vqe_latency.py
```

## Research thesis

The project is not positioned as "another quantum simulator." Its fundable direction is:

> An estimator optimization and VQA validation layer that detects invalid ansatz behavior, reduces measurement
> overhead through compression and grouping, models finite-shot and readout-error effects, and provides reproducible
> benchmarks for near-term quantum workflows.

## Status

Release candidate v1.0.0rc1.

## Repository layout

```text
vqa_estimator_lab/        Python package
tests/                    correctness and release-candidate checks
examples/                 runnable H2, grouping, and readout demonstrations
benchmarks/               report, dashboard, scorecard, and latency scripts
fixtures/                 documented toy/reduced Hamiltonian fixture
external_reproduction/    reviewer protocol and one-command reproduction runner
reports/                  generated benchmark and readiness artifacts
docs/                     roadmap, launch notes, release notes, and review request
```


## v0.2 additions

- Grouped estimator with symmetric readout-error mitigation.
- Adaptive pilot-based group shot allocation.
- Lightweight interoperability module for exporting/importing encoded Hamiltonian JSON.
- Additional validation tests for mitigation and adaptive allocation.


## v0.3 additions

- Asymmetric readout-error channel support.
- Full confusion-matrix readout mitigation for small systems.
- Grouped estimator using general readout confusion matrices.
- Adapter helpers for simple OpenQASM-like circuit export and Hamiltonian JSON exchange.
- Additional fixtures and tests.


## v0.4 additions

- General Pauli commutation grouping beyond qubit-wise commuting (QWC).
- Greedy graph-coloring grouping for commuting observables.
- Covariance-aware group shot allocation.
- Import helpers for simple SparsePauliOp-like and OpenFermion-style Hamiltonian text.
- Benchmarks comparing QWC grouping and general commuting grouping.

## v0.5 additions

- Multiple graph-coloring heuristics for general commuting grouping.
- Best-of-heuristics commuting group selection.
- Joint-measurement planning metadata.
- Adaptive covariance-pilot group allocation.
- Documented H2 toy Hamiltonian fixture.


## v0.6 additions

- Markdown benchmark report generator.
- Built-in report data model for reproducible VQA report cards.
- Optional Qiskit adapter that activates only when Qiskit is installed.
- External fixture manifest with provenance fields.
- CLI-style benchmark report example.


## v0.7 additions

- CSV and HTML report generation.
- Optional OpenFermion/PySCF molecular Hamiltonian generation script.
- External fixture provenance template and LiH generation recipe.
- Pilot-user reproducibility guide.
- Reproducibility metadata utilities.


## v0.8 additions

- Static benchmark dashboard generation.
- Release notes and v1.0 readiness scorecard.
- External collaborator onboarding checklist.
- Launch-oriented project metadata.
- Benchmark result summarization utilities.


## v0.9 additions

- CI workflow template.
- Contributing guide.
- Security policy.
- v1.0 release-candidate checklist.
- Launch README and repository hygiene artifacts.

## v1.0 Readiness

v0.9 is the release-candidate preparation milestone. The remaining pre-v1.0 blockers are:

1. Add a verified external molecular fixture generated from a documented source.
2. Run CI on a public repository.
3. Decide license and repository governance.
4. Optional: add joint-measurement synthesis for non-QWC commuting groups.


## License

Licensed under the Apache License, Version 2.0. See `LICENSE` and `NOTICE`.

## v0.9.3 additions

- External reproduction kit.
- Reviewer protocol.
- Reviewer feedback form.
- One-command reproduction runner.
- Expected-output notes for pilot reviewers.


## v0.9.3 outside-review patch

- Fixed stale report metadata.
- Fixed reproduction runner to use the active Python interpreter.
- Fixed `pyproject.toml` table layout for package metadata.


## v1.0.0rc1 release candidate

This release candidate is intended for external technical reproduction before a stable v1.0 release.

v1.0.0rc1 includes:

- Apache-2.0 licensing.
- External reproduction kit.
- Dashboard and report generation.
- Reproducibility documentation.
- Corrected toy-H2 validation benchmark.
- Readout-error mitigation examples.

Known deferrals:

- Verified external molecular Hamiltonian fixture.
- General commuting joint-measurement circuit synthesis.
- Full public CI run on a hosted repository.
