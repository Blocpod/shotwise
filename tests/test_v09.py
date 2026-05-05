from pathlib import Path

def test_ci_workflow_exists():
    root = Path(__file__).resolve().parents[1]
    ci = root / ".github" / "workflows" / "ci.yml"
    assert ci.exists()
    text = ci.read_text()
    assert "pytest" in text
    assert "generate_report.py" in text

def test_release_docs_exist():
    root = Path(__file__).resolve().parents[1]
    for name in [
        "CONTRIBUTING.md",
        "SECURITY.md",
        "LICENSE",
        "CITATION.cff",
        "docs/LAUNCH_README.md",
        "docs/V1_RELEASE_CANDIDATE_CHECKLIST.md",
    ]:
        assert (root / name).exists()

def test_version_module():
    from vqa_estimator_lab import __version__
    assert __version__ == "1.0.0rc1"
