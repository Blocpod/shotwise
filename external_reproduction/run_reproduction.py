from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "external_reproduction" / "reproduction_results.json"

FULL_COMMANDS = [
    [sys.executable, "-m", "pytest", "tests", "-q"],
    [sys.executable, "examples/h2_toy_corrected.py"],
    [sys.executable, "examples/h2_grouped_mitigation.py"],
    [sys.executable, "examples/h2_asymmetric_readout.py"],
    [sys.executable, "benchmarks/generate_report.py"],
    [sys.executable, "benchmarks/generate_dashboard.py"],
    [sys.executable, "benchmarks/generate_scorecard.py"],
]

FAST_COMMANDS = [
    [sys.executable, "-m", "pytest", "tests", "-q"],
    [sys.executable, "benchmarks/generate_report.py"],
    [sys.executable, "benchmarks/generate_dashboard.py"],
    [sys.executable, "benchmarks/generate_scorecard.py"],
]

def run_command(cmd, timeout):
    t0 = time.perf_counter()
    proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=timeout)
    return {
        "command": cmd,
        "return_code": proc.returncode,
        "elapsed_seconds": time.perf_counter() - t0,
        "stdout_tail": proc.stdout[-4000:],
        "stderr_tail": proc.stderr[-4000:],
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fast", action="store_true")
    parser.add_argument("--timeout", type=int, default=240)
    args = parser.parse_args()
    commands = FAST_COMMANDS if args.fast else FULL_COMMANDS

    results = {
        "metadata": {
            "python_version": sys.version,
            "platform": platform.platform(),
            "machine": platform.machine(),
            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "mode": "fast" if args.fast else "full",
        },
        "commands": [],
    }

    for cmd in commands:
        print("RUN:", " ".join(cmd))
        result = run_command(cmd, args.timeout)
        print("RETURN:", result["return_code"])
        print(result["stdout_tail"][-1200:])
        if result["stderr_tail"]:
            print(result["stderr_tail"][-1200:])
        results["commands"].append(result)

    results["overall_pass"] = all(x["return_code"] == 0 for x in results["commands"])
    OUT.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Wrote {OUT}")
    raise SystemExit(0 if results["overall_pass"] else 1)

if __name__ == "__main__":
    main()
