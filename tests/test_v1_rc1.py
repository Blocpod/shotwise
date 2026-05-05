from pathlib import Path

def test_version_rc1():
    from vqa_estimator_lab import __version__
    assert __version__ == "1.0.0rc1"

def test_rc1_docs_exist():
    root = Path(__file__).resolve().parents[1]
    required = [
        "docs/RELEASE_NOTES_v1_0_rc1.md",
        "docs/V1_0_RC1_EXTERNAL_REVIEW_REQUEST.md",
        "docs/V1_RELEASE_CANDIDATE_CHECKLIST.md",
    ]
    for rel in required:
        assert (root / rel).exists()

def test_release_notes_are_honest_about_deferrals():
    root = Path(__file__).resolve().parents[1]
    text = (root / "docs" / "RELEASE_NOTES_v1_0_rc1.md").read_text()
    assert "Known Deferrals" in text
    assert "Verified external molecular Hamiltonian fixture" in text
    assert "joint-measurement" in text.lower()
