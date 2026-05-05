from pathlib import Path

def test_external_reproduction_files_exist():
    root = Path(__file__).resolve().parents[1]
    required = [
        "external_reproduction/README.md",
        "external_reproduction/REPRODUCTION_PROTOCOL.md",
        "external_reproduction/run_reproduction.py",
        "external_reproduction/reviewer_feedback_form.md",
        "external_reproduction/requirements.txt",
        "external_reproduction/environment.yml",
        "external_reproduction/expected_outputs/EXPECTED_BEHAVIOR.md",
    ]
    for rel in required:
        assert (root / rel).exists()

def test_version_092():
    from vqa_estimator_lab import __version__
    assert __version__ == "1.0.0rc1"
