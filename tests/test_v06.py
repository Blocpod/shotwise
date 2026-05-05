import json
from pathlib import Path
from vqa_estimator_lab.reporting import BenchmarkRecord, make_report, render_markdown
from vqa_estimator_lab.qiskit_adapter import qiskit_available
from vqa_estimator_lab import encode_hamiltonian_dense, compress_encoded_hamiltonian

def test_report_markdown_rendering():
    report = make_report("Test Report", "A test summary.", [BenchmarkRecord("Unit", "pass", {"x": 1}, "ok")], {"package_version": "test"})
    md = render_markdown(report)
    assert "# Test Report" in md
    assert "| x | 1 |" in md

def test_fixture_manifest_exists():
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root / "fixtures" / "manifest.json").read_text())
    assert manifest["fixtures"][0]["name"] == "h2_toy_reduced_openfermion"
    assert "policy" in manifest

def test_qiskit_adapter_availability_check_is_boolean():
    assert isinstance(qiskit_available(), bool)

def test_qiskit_export_failure_without_dependency_or_roundtrip_if_available():
    from vqa_estimator_lab.qiskit_adapter import to_qiskit_sparse_pauli_op
    coeffs, codes = encode_hamiltonian_dense([(1.0, {0: "Z"})], 1)
    coeffs, codes = compress_encoded_hamiltonian(coeffs, codes)
    if qiskit_available():
        assert to_qiskit_sparse_pauli_op(coeffs, codes) is not None
    else:
        try:
            to_qiskit_sparse_pauli_op(coeffs, codes)
        except ImportError:
            assert True
        else:
            assert False
