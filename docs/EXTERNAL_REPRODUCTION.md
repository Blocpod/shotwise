# External Reproduction

The external reproduction kit lives in `external_reproduction/`.

Recommended reviewer workflow:

```bash
python external_reproduction/run_reproduction.py
```

Fast validation mode:

```bash
python external_reproduction/run_reproduction.py --fast
```

The reviewer should return:

- `external_reproduction/reproduction_results.json`
- `reports/benchmark_report.json`
- `reports/dashboard.html`
- `reports/v1_readiness_scorecard.json`
- completed `external_reproduction/reviewer_feedback_form.md`

A successful external reproduction is the main gate for v1.0-rc1.
