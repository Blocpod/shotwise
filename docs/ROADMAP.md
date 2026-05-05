# Technical Roadmap

## v0.1 Completed

- Corrected toy/reduced H2 benchmark.
- State-vector core.
- Pauli expectation evaluator.
- Encoded Hamiltonian representation.
- Duplicate Pauli compression.
- QWC grouping.
- Grouped shot estimator.
- Numba kernels for gates and Hamiltonian expectations.
- 14-qubit / 500-term VQE loop target demonstrated under tuned threading.

## v0.2 Goals

- Add command-line benchmark runner.
- Add grouped estimator with readout-error mitigation.
- Add asymmetric readout-error model.
- Add adaptive group shot allocation using pilot samples rather than oracle variance.
- Add Qiskit/Cirq/PennyLane import/export adapters.
- Add real small molecular Hamiltonian fixtures with documented provenance.

## v0.3 Goals

- Pauli grouping beyond QWC: general commutation graph coloring.
- Grouped covariance-aware shot allocation.
- Numba-accelerated grouped sampling post-processing.
- Automated ansatz expressibility diagnostics.
- Benchmark dashboard.

## Fundability Milestones

- Public repository with CI.
- Reproducible benchmark notebook.
- External comparison against Qiskit Aer / PennyLane / Cirq workflows.
- Pilot user feedback from at least 2 quantum researchers.
- Grant proposal package.


## v0.3 Completed

- Added asymmetric readout-error support via full confusion matrices.
- Added matrix-inversion readout mitigation for small grouped estimators.
- Added lightweight Circuit abstraction and OpenQASM-like export.
- Added PennyLane-like Hamiltonian term export helper.
- Added tests for asymmetric mitigation and adapter export.

## v0.4 Goals

- General commutation grouping beyond QWC.
- Covariance-aware grouped shot allocation.
- Import adapters for Qiskit SparsePauliOp and OpenFermion-style text/JSON.
- Benchmark dashboard artifacts.


## v0.4 Completed

- Added general Pauli commutation grouping via anticommutation graph coloring.
- Added validation that general commuting groups are valid.
- Added covariance-aware QWC group shot allocation.
- Added simple SparsePauliOp-like and OpenFermion-style import helpers.
- Added grouping comparison benchmark.

## v0.5 Goals

- General commuting joint-measurement compilation.
- Covariance-aware adaptive pilot allocation using sampled covariances.
- Real external Hamiltonian fixtures with provenance.
- CI-ready benchmark reports.

## v0.5 Completed

- Added multiple coloring heuristics and best-of-heuristics selection.
- Added joint-measurement planning metadata.
- Added adaptive covariance-pilot group allocation.
- Added documented H2 toy fixture.
- Added grouping heuristic benchmark.


## v0.6 Completed

- Added benchmark report generator.
- Added report model and Markdown/JSON report export.
- Added optional Qiskit adapter.
- Added fixture manifest with provenance policy.
- Added tests for reporting, manifest, and optional adapter behavior.

## v0.7 Goals

- Verified real molecular Hamiltonian fixture with generation script.
- CSV/HTML benchmark dashboard.
- General commuting joint-measurement circuit synthesis.
- Pilot-user reproducibility guide.


## v0.7 Completed

- Added CSV and HTML report rendering.
- Added reproducibility metadata utilities.
- Added optional LiH OpenFermion/PySCF generation script.
- Added pilot-user reproducibility guide.
- Added fixture generator metadata to manifest.

## v0.8 Goals

- Run fixture generation in an environment with OpenFermion/PySCF installed.
- Add generated LiH fixture after provenance verification.
- Add benchmark dashboard with plots.
- Add external collaborator onboarding checklist.


## v0.8 Completed

- Added static dashboard generation.
- Added v1.0 readiness scorecard.
- Added release notes and external collaborator onboarding checklist.
- Added launch-oriented reporting artifacts.

## v0.9 Goals

- CI workflow files.
- Packaging polish.
- Final launch README.
- v1.0 release candidate checklist.


## v0.9 Completed

- Added CI workflow template.
- Added CONTRIBUTING, SECURITY, LICENSE, and CITATION metadata.
- Added launch README and v1.0 release-candidate checklist.
- Added version module and release hygiene tests.

## v1.0 Goals

- Public repository CI run.
- Final license decision.
- External pilot reproduction.
- Verified external molecular fixture or explicit deferral.
- Release announcement and fundraising package.
