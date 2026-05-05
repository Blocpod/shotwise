import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from vqa_estimator_lab.scorecard import v1_readiness_scorecard, render_scorecard_markdown
import json

def main():
    out_md = REPO_ROOT / "reports" / "v1_readiness_scorecard.md"
    out_json = REPO_ROOT / "reports" / "v1_readiness_scorecard.json"
    out_md.parent.mkdir(exist_ok=True)

    scorecard = v1_readiness_scorecard()
    out_md.write_text(render_scorecard_markdown(scorecard), encoding="utf-8")
    out_json.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
    print(f"Wrote {out_md}")
    print(f"Wrote {out_json}")

if __name__ == "__main__":
    main()
