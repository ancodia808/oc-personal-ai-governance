"""Build the bundled synthetic demo only; never reads private telemetry."""
import html
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "examples/fixtures/baseline.json"
OUTPUT = ROOT / "examples/app"


def summarize(data):
    if data.get("synthetic") is not True or data.get("schema_version") != 1:
        raise ValueError("This demo requires a version 1 synthetic fixture")
    seen = set()
    projects = defaultdict(int)
    daily = defaultdict(int)
    for turn in data["turns"]:
        if turn["id"] in seen:
            raise ValueError("Duplicate turn identifier")
        seen.add(turn["id"])
        values = [turn["input_tokens"], turn["output_tokens"]]
        if any(type(v) is not int or v < 0 for v in values):
            raise ValueError("Token values must be nonnegative integers")
        total = sum(values)
        projects[turn["project"]] += total
        daily[turn["date"]] += total
    return {"total": sum(projects.values()), "projects": dict(projects), "daily": dict(sorted(daily.items()))}


def build():
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    metrics = summarize(data)
    esc = lambda value: html.escape(str(value), quote=True)
    findings = data["findings"][:3]
    cards = "".join(f'<article><h3>{esc(f["title"])}</h3><p>{esc(f["evidence"])}</p><p><strong>Next step:</strong> {esc(f["suggestion"])}</p></article>' for f in findings)
    maximum = max(metrics["daily"].values(), default=1) or 1
    bars = "".join(f'<div class="barrow"><span>{esc(day)}</span><div class="track"><div class="bar" style="width:{value / maximum * 100:.2f}%"></div></div><strong>{value:,}</strong></div>' for day, value in metrics["daily"].items())
    rows = "".join(f'<tr><td>{esc(t["project"])}</td><td>{esc(t["task"])}</td><td>{t["input_tokens"] + t["output_tokens"]:,}</td><td>{t["active_minutes"]}</td></tr>' for t in data["turns"])
    document = f'''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Personal AI Governance - synthetic daily report</title>
<style>
:root{{font-family:system-ui,sans-serif;color:#193047;background:#f3f6fa}}body{{max-width:1080px;margin:auto;padding:36px 24px}}h1{{font-size:clamp(28px,5vw,44px);margin:14px 0}}h2{{margin-top:32px}}p{{line-height:1.65}}.tag{{color:#664900;background:#fff0bf;padding:7px 12px;border-radius:6px;font-weight:700}}.muted{{color:#526479}}.metrics{{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:16px;margin:24px 0}}article,.metric,.panel{{background:white;padding:22px;border:1px solid #d9e2ec;border-radius:12px}}.metric strong{{display:block;font-size:28px;margin-top:8px}}.findings{{display:grid;gap:12px}}h3{{margin-top:0}}.barrow{{display:grid;grid-template-columns:100px 1fr 75px;gap:14px;align-items:center;margin:18px 0;font-size:14px}}.track{{background:#edf1f6;border-radius:5px;overflow:hidden}}.bar{{height:20px;background:#236b83}}table{{width:100%;border-collapse:collapse;text-align:left}}td,th{{padding:14px 10px;border-bottom:1px solid #d9e2ec}}.tablewrap{{overflow:auto}}footer{{margin-top:30px;font-size:13px;color:#526479}}
</style>
<header><span class="tag">SYNTHETIC DEMO - No personal usage data</span><h1>Your daily usage review</h1><p class="muted">As of {esc(data["cutoff"])} - ET<br>Week starting {esc(data["week_start"])}</p></header>
<section class="panel"><strong>Coverage comes first</strong><p>{esc(data["coverage"])} These totals describe the fixture only; they are not account-wide measurements.</p></section>
<section class="metrics"><div class="metric">Observed tokens<strong>{metrics["total"]:,}</strong></div><div class="metric">Budget status<strong>Baseline first</strong></div><div class="metric">Projects represented<strong>{len(metrics["projects"])}</strong></div></section>
<p>No budget has been set. Expected pace, deviations, remaining budget, and budget warnings are unavailable. Collect a representative baseline before choosing a weekly limit.</p>
<h2>Three things to consider</h2><section class="findings">{cards}</section>
<h2>Daily observed tokens</h2><section class="panel">{bars}<p class="muted">Input plus output tokens. This demo uses per-turn counts without separate cached or reasoning subtotals.</p></section>
<h2>Activity details</h2><div class="panel tablewrap"><table><thead><tr><th>Project</th><th>Task</th><th>Tokens</th><th>Active minutes</th></tr></thead><tbody>{rows}</tbody></table></div>
<footer>Fixture: examples/fixtures/baseline.json - Schema 1 - Generator: scripts/build_demo.py<br>Coaching is authored synthetic scenario content, not automated detection. No external assets, tracking, or server.</footer></html>'''
    summary = ["# Daily usage review - SYNTHETIC DEMO", "", f"Coverage: {data['coverage']}", "", f"Observed week-to-date: **{metrics['total']:,} tokens**. Budget: **not set; baseline first**. No pace or budget warning is available.", ""]
    summary += [f"- **{f['title']}:** {f['suggestion']}" for f in findings]
    summary += ["", "[Open local details](daily-report.html)", "", "All data and coaching scenarios are invented. This is a preview of a daily chat, not an automatically delivered report."]
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "daily-report.html").write_text(document, encoding="utf-8")
    (OUTPUT / "daily-summary.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
    (OUTPUT / "expected-metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    try:
        from .render_review import render
    except ImportError:
        from render_review import render
    payload_fixture = json.loads((ROOT / 'examples/fixtures/payload-report.json').read_text(encoding='utf-8'))
    if payload_fixture.get('synthetic') is not True:
        raise ValueError('Payload preview requires a synthetic fixture')
    page, summary = render(payload_fixture, OUTPUT / 'payload-report.html', synthetic=True)
    begin = summary.index('[Open local details]')
    end = summary.index('\n', begin)
    summary = summary[:begin] + '[Open local details](payload-report.html)' + summary[end:]
    (OUTPUT / 'payload-report.html').write_text(page, encoding='utf-8')
    (OUTPUT / 'payload-summary.md').write_text(summary, encoding='utf-8')
    print("Built synthetic report, summary, and metrics in examples/app")


if __name__ == "__main__":
    build()
