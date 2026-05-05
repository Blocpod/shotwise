from __future__ import annotations

import json
from pathlib import Path

def load_report_json(path):
    path = Path(path)
    return json.loads(path.read_text(encoding="utf-8"))

def dashboard_html_from_report(report: dict) -> str:
    def esc(x):
        import html
        return html.escape(str(x))

    records = report.get("records", [])
    metadata = report.get("metadata", {})

    cards = []
    for rec in records:
        status = rec.get("status", "")
        cls = "ok" if status.lower() in ("pass", "implemented") else "warn"
        metrics = rec.get("metrics", {})
        metric_html = "".join(
            f"<tr><td>{esc(k)}</td><td>{esc(v)}</td></tr>"
            for k, v in metrics.items()
        )
        cards.append(
            f"<section class='card {cls}'>"
            f"<h2>{esc(rec.get('name',''))}</h2>"
            f"<p><strong>Status:</strong> {esc(status)}</p>"
            f"<p>{esc(rec.get('notes',''))}</p>"
            f"<table>{metric_html}</table>"
            f"</section>"
        )

    meta_html = "".join(
        f"<tr><td>{esc(k)}</td><td>{esc(v)}</td></tr>"
        for k, v in metadata.items()
    )

    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>{esc(report.get("title", "VQA Dashboard"))}</title>
<style>
body {{ font-family: system-ui, Arial, sans-serif; margin: 0; background: #f7f7fb; color: #222; }}
header {{ background: #111827; color: white; padding: 32px 48px; }}
main {{ max-width: 1100px; margin: 32px auto; padding: 0 24px; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 18px; }}
.card {{ background: white; border-radius: 12px; padding: 20px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); border-top: 5px solid #64748b; }}
.card.ok {{ border-top-color: #16a34a; }}
.card.warn {{ border-top-color: #dc2626; }}
table {{ width: 100%; border-collapse: collapse; margin-top: 12px; }}
td {{ border-bottom: 1px solid #e5e7eb; padding: 6px; }}
.meta {{ background: white; border-radius: 12px; padding: 20px; margin-bottom: 24px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); }}
</style>
</head>
<body>
<header>
<h1>{esc(report.get("title", "VQA Estimator Lab Dashboard"))}</h1>
<p>{esc(report.get("summary", ""))}</p>
</header>
<main>
<section class="meta">
<h2>Metadata</h2>
<table>{meta_html}</table>
</section>
<section class="grid">
{''.join(cards)}
</section>
</main>
</body>
</html>"""

def write_dashboard_from_report(report_json_path, output_html_path):
    report = load_report_json(report_json_path)
    html = dashboard_html_from_report(report)
    output_html_path = Path(output_html_path)
    output_html_path.parent.mkdir(parents=True, exist_ok=True)
    output_html_path.write_text(html, encoding="utf-8")
    return output_html_path
