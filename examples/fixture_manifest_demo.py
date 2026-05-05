import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main():
    manifest = json.loads((ROOT / "fixtures" / "manifest.json").read_text())
    print(json.dumps(manifest, indent=2))

if __name__ == "__main__":
    main()
