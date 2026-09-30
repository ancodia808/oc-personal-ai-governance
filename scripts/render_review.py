"""Render collector JSON into private, server-free HTML and Markdown."""
import argparse
import html
import json
from pathlib import Path
try:
    from .payload_activity import external_readout
except ImportError:
    from payload_activity import external_readout
try:
    from .eastern_time import eastern as ZoneInfo
except ImportError:
    from eastern_time import eastern as ZoneInfo

try:
    from .collect_usage import output_path, timestamp, validated_usage, week_start, FIELDS
except ImportError:
    from collect_usage import output_path, timestamp, validated_usage, week_start, FIELDS


def validate(data):
    if data.get('schema_version') != 1:
        raise ValueError('Unsupported snapshot schema')
    start, cutoff = timestamp(data['start_inclusive']), timestamp(data['cutoff_exclusive'])
    zone = ZoneInfo(data['timezone'])
    if start >= cutoff:
        raise ValueError('Invalid interval')
    totals = validated_usage(data['totals'])
    for group in ('daily', 'projects'):
        for value in data[group].values():
            validated_usage(value)
        for key in FIELDS:
            if sum(v[key] for v in data[group].values()) != totals[key]:
                raise ValueError('Breakdown does not reconcile')
    for day in data['daily']:
        from datetime import date
        parsed = date.fromisoformat(day)
        if not start.astimezone(zone).date() <= parsed <= cutoff.astimezone(zone).date():
            raise ValueError('Daily bucket outside interval')
    if any(type(v) is not int or v < 0 for v in data['diagnostics'].values()):
        raise ValueError('Invalid diagnostics')
    activity = data.get('payload_activity', {})
    for direction in ('sources', 'destinations'):
        for row in activity.get(direction, []):
            if not isinstance(row['group'], str) or type(row['messages']) is not int or row['messages'] < 0:
                raise ValueError('Invalid payload activity')
    return start, cutoff, zone


def render(data, details_path, synthetic=False):
    start, cutoff, zone = validate(data)
    e = lambda value: html.escape(str(value), quote=True)
    number = lambda value: 'Unavailable' if value is None else f'{value:,}'
    total = data['totals']['total_tokens']
    today = data['daily'].get(cutoff.astimezone(zone).date().isoformat())
    today_text = number(today['total_tokens']) if today else 'No observations'
    period = 'Week to date' if start == week_start(cutoff, zone) else 'Reporting interval'
    issues = {k:v for k,v in data['diagnostics'].items() if v and k in (
        'malformed_lines','unreadable_files','invalid_usage_records',
        'conflicting_response_ids_excluded','missing_source_directories')}
    findings = []
    if issues:
        findings.append('Coverage needs review: ' + '; '.join(f'{k.replace("_", " ")}: {v}' for k,v in sorted(issues.items())) + '. Excluded or unreadable data can understate usage.')
    if total and data['projects']:
        project, usage = max(sorted(data['projects'].items()), key=lambda item:item[1]['total_tokens'])
        findings.append(f'{project} represents {usage["total_tokens"]/total:.1%} of observed tokens. Review this workflow first; volume alone does not establish waste or justify switching models.')
    cached, inputs = data['totals']['cached_input_tokens'], data['totals']['input_tokens']
    if cached is not None and inputs:
        findings.append(f'{cached/inputs:.1%} of input tokens were cached and are already included in totals. Token volume is not a dollar-cost estimate.')
    findings.append('Active processing and ongoing-run status are unavailable. No two-hour or Friday alert can be established from this snapshot.')
    findings = findings[:3]
    label = 'SYNTHETIC EXAMPLE' if synthetic else 'PRIVATE - Actual local observations'
    coverage = 'Local Codex Desktop only; selected account; partial coverage. Other devices and cloud-only activity are not established as covered.'
    budget = 'Budget not set: baseline first. Pace, remaining budget, and budget warnings are unavailable.'
    rows = ''.join(f'<tr><td>{e(k)}</td><td>{number(v["total_tokens"])}</td><td>{number(v["cached_input_tokens"])}</td></tr>' for k,v in sorted(data['projects'].items(), key=lambda item:(-item[1]['total_tokens'],item[0])))
    peak = max((v['total_tokens'] for v in data['daily'].values()), default=1) or 1
    bars = ''.join(f'<div class="barrow"><span>{e(k)}</span><div class="track"><div class="bar" style="width:{100*v["total_tokens"]/peak:.2f}%"></div></div><strong>{number(v["total_tokens"])}</strong></div>' for k,v in sorted(data['daily'].items()))
    diagnostic_labels = {
        'cumulative_snapshots_not_added': 'Running totals skipped to prevent double counting',
        'files_skipped_by_filters': 'Files skipped by account and app filters',
        'unattributed_files': 'Files that could not be attributed',
        'excluded_identity_or_origin_files': 'Files skipped by scope or attribution filters (legacy combined count)',
    }
    diagnostics = ''.join(f'<tr><td>{e(diagnostic_labels.get(k, k.replace("_"," ")))}</td><td>{v:,}</td></tr>' for k,v in sorted(data['diagnostics'].items()) if k != 'unattributed_files' or v)
    cards = ''.join(f'<article><p>{e(f)}</p></article>' for f in findings)
    limitations = ''.join(f'<li>{e(v)}</li>' for v in data['limitations'])
    activity = data.get('payload_activity')
    direction_titles = {'sources': 'External Sources (requested)',
                        'destinations': 'External Destinations (posted)'}
    if activity is not None:
        activity = external_readout(activity)
    traffic_html = ''
    if activity is None:
        traffic_html += '<p>Unavailable in this snapshot; collect again to obtain request metadata.</p>'
    else:
        for direction in ('sources', 'destinations'):
            entries = sorted(activity[direction], key=lambda r: (-r['messages'], r['group']))
            traffic_rows = ''.join(f'<tr><td>{e(r["group"])}</td><td>{r["messages"]:,}</td></tr>' for r in entries)
            count_label = '# of requests' if direction == 'sources' else '# of posts'
            traffic_html += f'<h2>{direction_titles[direction]}</h2><div class="panel scroll"><table><tr><th>Group</th><th>{count_label}</th></tr>{traffic_rows}</table>'
            if not entries:
                traffic_html += '<p>No attributable requests observed; this does not establish zero traffic.</p>'
            traffic_html += '</div>'
        traffic_html += f'<p>Unclassified request messages: {activity["unclassified_request_messages"]:,}. Conflicting request IDs excluded: {activity["conflicting_request_ids_excluded"]:,}.</p>'
        traffic_html += f'<p>Search request messages with unidentified provider hostname: {activity["unattributed_search_messages"]:,}. These are excluded from the website rankings. Unclassified messages may include internal activity.</p>'
    document = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Daily usage review</title>
<style>body{{font:16px system-ui;color:#193047;background:#f3f6fa;max-width:1080px;margin:auto;padding:32px 20px}}h1{{font-size:clamp(28px,5vw,42px)}}p,li{{line-height:1.6}}article,.panel,.metric{{background:white;border:1px solid #d9e2ec;border-radius:12px;padding:20px;margin:12px 0}}.metrics{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:16px}}.metric strong{{display:block;font-size:28px;margin-top:8px}}table{{border-collapse:collapse;width:100%}}th,td{{padding:12px;text-align:left;border-bottom:1px solid #d9e2ec}}.scroll{{overflow:auto}}.barrow{{display:grid;grid-template-columns:100px 1fr 110px;gap:12px;align-items:center;margin:16px 0}}.track{{background:#edf1f6}}.bar{{height:20px;background:#236b83}}small{{color:#526479}}@media(max-width:500px){{.barrow{{grid-template-columns:90px 1fr}}.barrow strong{{grid-column:2}}}}</style></head><body>
<header><strong>{label}</strong><h1>Daily usage review</h1><p>Through {e(cutoff.astimezone(zone).isoformat())} - ET<br>Interval begins {e(start.astimezone(zone).isoformat())}; ET; cutoff is exclusive.</p></header>
<section class="panel"><b>Coverage</b><p>{coverage}</p><p>{data['unique_responses']:,} unique responses observed. No observations does not establish zero usage.</p></section>
<section class="metrics"><div class="metric">Today within this interval<strong>{today_text}</strong></div><div class="metric">{period}<strong>{number(total)}</strong>observed tokens</div><div class="metric">Weekly budget<strong>Not set</strong></div></section><p>{budget}</p>
<h2>Findings</h2>{cards}<h2>Daily observed tokens</h2><section class="panel">{bars or '<p>No observations in this interval.</p>'}</section>
<h2>Project activity</h2><div class="panel scroll"><table><thead><tr><th>Project folder</th><th>Total tokens</th><th>Cached input subset</th></tr></thead><tbody>{rows}</tbody></table></div>
{traffic_html}
<h2>Measurement diagnostics</h2><div class="panel scroll"><table><tr><th>Check</th><th>Count</th></tr>{diagnostics}</table></div>
<p>Input plus output equals total. Cached input and reasoning output are subsets, not additional tokens. Active processing: unavailable. Ongoing runs: unavailable.</p><ul>{limitations}</ul>
<footer><small>Generated locally by PAIGe. Self-contained HTML with no tracking.</small></footer></body></html>'''
    # HTML entities prevent Markdown link/format injection from project labels.
    def md(value):
        text = html.escape(str(value))
        for char in '\\`*_{}[]()#+!|':
            text = text.replace(char, '\\'+char)
        return text.replace('\n', ' ').replace('\r', ' ')
    target = str(Path(details_path).resolve()).replace('\\','/').replace(' ', '%20').replace('<','%3C').replace('>','%3E')
    summary = f'# Daily usage review - {label}\n\nThrough {cutoff.astimezone(zone).isoformat()} (ET).\n\n{coverage}\n\n**{period}: {number(total)} tokens.** Today within this interval: {today_text}.\n\n{budget}\n\n'
    summary += '\n'.join('- '+md(f) for f in findings)
    if activity is not None:
        for direction in ('sources', 'destinations'):
            summary += '\n\n## ' + direction_titles[direction] + '\n\nTop 5:\n\n'
            entries = sorted(activity[direction], key=lambda r: (-r['messages'], r['group']))[:5]
            summary += '\n'.join(f'{i}. {md(r["group"])}: {r["messages"]:,} request messages' for i, r in enumerate(entries, 1)) or 'No attributable requests observed.'
            summary += '\n'
        summary += f'\nUnclassified request messages: {activity["unclassified_request_messages"]:,}. Full rankings are in the HTML report.\n'
        summary += f'\nSearch requests with unidentified provider hostname: {activity["unattributed_search_messages"]:,}; excluded from website rankings. Unclassified messages may include internal activity.\n'
    summary += f'\n\n[Open local details](<{target}>)\n\nActive-processing duration and ongoing-run status are unavailable.\n'
    return document, summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output-dir', required=True)
    args = parser.parse_args()
    try:
        html_path = output_path(str(Path(args.output_dir)/'daily-review.html'))
        md_path = output_path(str(Path(args.output_dir)/'daily-summary.md'))
        data = json.loads(args.input.read_text(encoding='utf-8'))
        document, summary = render(data, html_path)
        for path, content in [(html_path, document),(md_path, summary)]:
            path.parent.mkdir(parents=True, exist_ok=True)
            temp = output_path(str(path)+'.tmp')
            temp.write_text(content,encoding='utf-8')
            temp.replace(path)
        print('Private HTML report and daily summary written. No notifications sent.')
    except (ValueError, KeyError, TypeError, OSError):
        parser.exit(2, 'Rendering failed: check snapshot schema, reconciliation, timezone dependencies, and private output paths.\n')


if __name__ == '__main__':
    main()
