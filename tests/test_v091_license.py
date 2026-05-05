from pathlib import Path

def test_license_is_apache_2():
    root = Path(__file__).resolve().parents[1]
    license_text = (root / "LICENSE").read_text()
    assert "Apache License" in license_text
    assert "Version 2.0" in license_text
    assert "Grant of Patent License" in license_text

def test_notice_exists():
    root = Path(__file__).resolve().parents[1]
    assert (root / "NOTICE").exists()

def test_version_091():
    from vqa_estimator_lab import __version__
    assert __version__ == "1.0.0rc1"

def test_pyproject_license_metadata():
    root = Path(__file__).resolve().parents[1]
    text = (root / "pyproject.toml").read_text()
    assert "Apache-2.0" in text
