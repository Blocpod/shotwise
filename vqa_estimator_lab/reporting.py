from __future__ import annotations
import platform
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path
import json

@dataclass
class BenchmarkRecord:
    name: str
    status: str
    metrics: dict
    notes: str = ""

@dataclass
class Report:
    title: str
    summary: str
    records: list[BenchmarkRecord]
    metadata: dict
    def to_dict(self):
        return {
            "title": self.title,
            "summary": self.summary,
            "records": [asdict(r) for r in self.records],
            "metadata": self.metadata,
        }

def default_metadata():
    return {
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
    }

def render_markdown(report: Report) -> str:
    lines = [f"# {report.title}", "", report.summary.strip(), "", "## Metadata", ""]
    for k, v in report.metadata.items():
        lines.append(f"- **{k}:** {v}")
    lines += ["", "## Benchmark Records", ""]
    for i, record in enumerate(report.records, 1):
        lines += [f"### {i}. {record.name}", "", f"**Status:** {record.status}", ""]
        if record.notes:
            lines += [record.notes.strip(), ""]
        lines += ["| Metric | Value |", "|---|---:|"]
        for k, v in record.metrics.items():
            lines.append(f"| {k} | {v} |")
        lines.append("")
    return "\n".join(lines)

def write_report(report: Report, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.suffix.lower() == ".json":
        output_path.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")
    else:
        output_path.write_text(render_markdown(report), encoding="utf-8")
    return output_path

def make_report(title: str, summary: str, records: list[BenchmarkRecord], metadata: dict | None = None):
    md = default_metadata()
    if metadata:
        md.update(metadata)
    return Report(title=title, summary=summary, records=records, metadata=md)


def render_csv(report: Report) -> str:
    import csv
    import io
    buf = io.StringIO()
    fieldnames = ["record_name", "status", "metric", "value", "notes"]
    writer = csv.DictWriter(buf, fieldnames=fieldnames)
    writer.writeheader()
    for record in report.records:
        for k, v in record.metrics.items():
            writer.writerow({
                "record_name": record.name,
                "status": record.status,
                "metric": k,
                "value": v,
                "notes": record.notes,
            })
    return buf.getvalue()

def render_html(report: Report) -> str:
    def esc(x):
        import html
        return html.escape(str(x))
    parts = [
        "<!doctype html>",
        "<html><head><meta charset='utf-8'>",
        f"<title>{esc(report.title)}</title>",
        "<style>body{font-family:system-ui,Arial,sans-serif;max-width:960px;margin:40px auto;line-height:1.5}"
        "table{border-collapse:collapse;width:100%;margin:1rem 0}td,th{border:1px solid #ddd;padding:6px}"
        "th{background:#f6f6f6;text-align:left}.pass{color:green}.fail{color:#b00020}</style>",
        "</head><body>",
        f"<h1>{esc(report.title)}</h1>",
        f"<p>{esc(report.summary)}</p>",
        "<h2>Metadata</h2><table><tbody>",
    ]
    for k, v in report.metadata.items():
        parts.append(f"<tr><th>{esc(k)}</th><td>{esc(v)}</td></tr>")
    parts.append("</tbody></table><h2>Benchmark Records</h2>")
    for idx, record in enumerate(report.records, 1):
        cls = "pass" if record.status.lower() in ("pass", "implemented") else "fail"
        parts.append(f"<h3>{idx}. {esc(record.name)}</h3>")
        parts.append(f"<p><strong>Status:</strong> <span class='{cls}'>{esc(record.status)}</span></p>")
        if record.notes:
            parts.append(f"<p>{esc(record.notes)}</p>")
        parts.append("<table><thead><tr><th>Metric</th><th>Value</th></tr></thead><tbody>")
        for k, v in record.metrics.items():
            parts.append(f"<tr><td>{esc(k)}</td><td>{esc(v)}</td></tr>")
        parts.append("</tbody></table>")
    parts.append("</body></html>")
    return "\n".join(parts)

def write_report_all_formats(report: Report, output_stem):
    output_stem = Path(output_stem)
    write_report(report, output_stem.with_suffix(".md"))
    write_report(report, output_stem.with_suffix(".json"))
    output_stem.with_suffix(".csv").write_text(render_csv(report), encoding="utf-8")
    output_stem.with_suffix(".html").write_text(render_html(report), encoding="utf-8")
    return {
        "markdown": str(output_stem.with_suffix(".md")),
        "json": str(output_stem.with_suffix(".json")),
        "csv": str(output_stem.with_suffix(".csv")),
        "html": str(output_stem.with_suffix(".html")),
    }
