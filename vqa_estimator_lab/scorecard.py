from __future__ import annotations

def v1_readiness_scorecard():
    '''
    Static readiness scorecard for launch planning.
    '''
    items = [
        ("Correctness tests", True, "Core simulator, grouping, mitigation, reporting tests are present."),
        ("Toy benchmark fixture", True, "Documented toy/reduced H2 fixture included."),
        ("External molecular fixture", False, "Generator script exists; verified generated fixture is deferred from v1.0."),
        ("Performance benchmark", True, "14-qubit benchmark script included."),
        ("Report generator", True, "Markdown/JSON/CSV/HTML reporting supported."),
        ("Optional framework adapter", True, "Qiskit adapter included, dependency-gated."),
        ("Pilot-user guide", True, "Reproducibility guide included."),
        ("External reproduction kit", True, "Reviewer protocol and reproduction runner included."),
        ("Apache-2.0 licensing", True, "LICENSE and NOTICE included."),
        ("Joint-measurement synthesis", False, "Planner flags requirement; synthesis not implemented."),
        ("Hosted CI run", False, "CI workflow template exists, but hosted run still pending."),
    ]
    complete = sum(1 for _, done, _ in items if done)
    return {
        "complete": complete,
        "total": len(items),
        "score": complete / len(items),
        "items": [
            {"name": name, "complete": done, "notes": notes}
            for name, done, notes in items
        ],
    }

def render_scorecard_markdown(scorecard=None):
    if scorecard is None:
        scorecard = v1_readiness_scorecard()
    lines = [
        "# VQA Estimator Lab v1.0 Readiness Scorecard",
        "",
        f"**Score:** {scorecard['complete']} / {scorecard['total']} ({scorecard['score']:.1%})",
        "",
        "| Item | Complete | Notes |",
        "|---|---:|---|",
    ]
    for item in scorecard["items"]:
        lines.append(f"| {item['name']} | {'yes' if item['complete'] else 'no'} | {item['notes']} |")
    return "\n".join(lines)
