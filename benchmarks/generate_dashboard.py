import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from vqa_estimator_lab.dashboard import write_dashboard_from_report

def main():
    report_json = REPO_ROOT / "reports" / "benchmark_report.json"
    if not report_json.exists():
        import subprocess
        subprocess.run([sys.executable, "benchmarks/generate_report.py"], cwd=str(REPO_ROOT), check=True)

    output = REPO_ROOT / "reports" / "dashboard.html"
    write_dashboard_from_report(report_json, output)
    print(f"Wrote {output}")

if __name__ == "__main__":
    main()
