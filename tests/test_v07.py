import json
from pathlib import Path

from vqa_estimator_lab.reporting import BenchmarkRecord, make_report, render_csv, render_html
from vqa_estimator_lab.reproducibility import environment_snapshot, fixture_metadata

def test_csv_and_html_report_rendering():
    report = make_report(
        "Report",
        "Summary",
        [BenchmarkRecord("A", "pass", {"m": 1}, "note")],
        {"package_version": "test"},
    )
    csv_text = render_csv(report)
    html_text = render_html(report)
    assert "record_name,status,metric,value,notes" in csv_text
    assert "<html>" in html_text
    assert "Report" in html_text

def test_environment_snapshot_has_python():
    snap = environment_snapshot()
    assert "python_version" in snap
    assert "platform" in snap

def test_fixture_metadata_shape():
    meta = fixture_metadata(
        name="x",
        path="fixtures/x.txt",
        fixture_type="toy",
        num_qubits=2,
        term_count=3,
    )
    assert meta["name"] == "x"
    assert meta["num_qubits"] == 2

def test_lih_generator_script_exists_and_is_dependency_gated():
    root = Path(__file__).resolve().parents[1]
    script = root / "scripts" / "generate_lih_openfermion.py"
    assert script.exists()
    text = script.read_text()
    assert "openfermion" in text.lower()
    assert "not installed" in text.lower()

def test_manifest_mentions_generator_policy():
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root / "fixtures" / "manifest.json").read_text())
    assert "generators" in manifest
    assert "external_molecular_fixtures" in manifest["policy"]
