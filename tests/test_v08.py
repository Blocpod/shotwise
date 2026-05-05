import json
from pathlib import Path

from vqa_estimator_lab.reporting import BenchmarkRecord, make_report, write_report
from vqa_estimator_lab.dashboard import dashboard_html_from_report
from vqa_estimator_lab.scorecard import v1_readiness_scorecard, render_scorecard_markdown

def test_dashboard_html_generation():
    report = make_report(
        "Dash",
        "Summary",
        [BenchmarkRecord("A", "pass", {"x": 1}, "note")],
        {"package_version": "test"},
    )
    html = dashboard_html_from_report(report.to_dict())
    assert "<html>" in html
    assert "Dash" in html
    assert "A" in html

def test_scorecard_shape():
    sc = v1_readiness_scorecard()
    assert sc["complete"] <= sc["total"]
    assert 0 <= sc["score"] <= 1
    md = render_scorecard_markdown(sc)
    assert "v1.0 Readiness" in md

def test_release_docs_exist():
    root = Path(__file__).resolve().parents[1]
    assert (root / "docs" / "RELEASE_NOTES_v0_8.md").exists()
    assert (root / "docs" / "ONBOARDING_CHECKLIST.md").exists()
