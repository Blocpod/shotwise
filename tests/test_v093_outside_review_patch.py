from pathlib import Path
import tomllib

def test_version_093():
    from vqa_estimator_lab import __version__
    assert __version__ == "1.0.0rc1"

def test_generate_report_has_no_stale_v060_metadata():
    root = Path(__file__).resolve().parents[1]
    text = (root / "benchmarks" / "generate_report.py").read_text()
    assert "0.6.0" not in text
    assert "__version__" in text

def test_reproduction_runner_uses_active_interpreter():
    root = Path(__file__).resolve().parents[1]
    text = (root / "external_reproduction" / "run_reproduction.py").read_text()
    assert "sys.executable" in text
    assert '["python",' not in text

def test_pyproject_metadata_layout():
    root = Path(__file__).resolve().parents[1]
    data = tomllib.loads((root / "pyproject.toml").read_text())
    assert data["project"]["version"] == "1.0.0rc1"
    assert data["project"]["license"]["text"] == "Apache-2.0"
    assert "classifiers" in data["project"]
    assert "urls" in data["project"]
