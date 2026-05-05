from __future__ import annotations

import hashlib
import json
import platform
import sys
import time
from pathlib import Path

def sha256_file(path) -> str:
    path = Path(path)
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def environment_snapshot(extra: dict | None = None) -> dict:
    data = {
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "python_version": sys.version,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
    }
    if extra:
        data.update(extra)
    return data

def write_json(data: dict, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return path

def fixture_metadata(
    name: str,
    path: str,
    fixture_type: str,
    num_qubits: int | None = None,
    term_count: int | None = None,
    provenance: str = "",
    generation_script: str | None = None,
    chemistry: dict | None = None,
    notes: str = "",
):
    return {
        "name": name,
        "path": path,
        "type": fixture_type,
        "num_qubits": num_qubits,
        "term_count": term_count,
        "provenance": provenance,
        "generation_script": generation_script,
        "chemistry": chemistry or {},
        "notes": notes,
    }
