"""Read-only local Codex Desktop collector. No prompts, network, or delivery."""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import sys
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

VERSION = '1.0'
FIELDS = ('input_tokens', 'output_tokens', 'total_tokens')
SUBSETS = ('cached_input_tokens', 'reasoning_output_tokens')


def timestamp(value):
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if result.tzinfo is None:
        raise ValueError('Timestamp requires an offset')
    return result.astimezone(timezone.utc)


def week_start(cutoff, zone):
    local = cutoff.astimezone(zone)
    return (local.replace(hour=0, minute=0, second=0, microsecond=0)
            - timedelta(days=local.weekday())).astimezone(timezone.utc)


def validated_usage(value):
    if not isinstance(value, dict):
        raise ValueError('Missing usage')
    result = {}
    for key in FIELDS + SUBSETS:
        item = value.get(key)
        if item is None and key in SUBSETS:
            result[key] = None
            continue
        if type(item) is not int or item < 0:
            raise ValueError('Invalid token count')
        result[key] = item
    if result['total_tokens'] != result['input_tokens'] + result['output_tokens']:
        raise ValueError('Token total does not reconcile')
    for sub, parent in [('cached_input_tokens', 'input_tokens'), ('reasoning_output_tokens', 'output_tokens')]:
        if result[sub] is not None and result[sub] > result[parent]:
            raise ValueError('Invalid subset')
    return result


def collect(home, account, start, cutoff, zone):
    if not account or start >= cutoff:
        raise ValueError('Account and a positive reporting interval are required')
    diagnostics = Counter()
    records, conflicts = {}, set()
    for folder in ('sessions', 'archived_sessions'):
        source = home / folder
        if not source.is_dir():
            diagnostics['missing_source_directories'] += 1
            continue
        for path in sorted(source.rglob('*.jsonl')):
            # Scan content: timestamps/mtime of the filename are not usage dates.
            diagnostics['files_scanned'] += 1
            metas, pending, models = [], [], {}
            try:
                with path.open(encoding='utf-8') as stream:
                    for line in stream:
                        try:
                            row = json.loads(line)
                            payload = row.get('payload', {})
                            if not isinstance(payload, dict):
                                raise ValueError()
                            kind = row.get('type')
                            if kind == 'session_meta':
                                metas.append({k: payload.get(k) for k in ('originator', 'creator_account_id', 'cwd')})
                            elif kind == 'turn_context':
                                models[payload.get('turn_id')] = payload.get('model')
                            elif kind == 'token_usage_record':
                                pending.append((row.get('timestamp'), {k: payload.get(k) for k in ('response_id', 'thread_id', 'turn_id', 'usage')}))
                            elif kind == 'event_msg' and payload.get('type') == 'token_count':
                                diagnostics['cumulative_snapshots_not_added'] += 1
                        except (ValueError, AttributeError, TypeError):
                            diagnostics['malformed_lines'] += 1
            except (OSError, UnicodeError):
                diagnostics['unreadable_files'] += 1
                continue
            origins = {m['originator'] for m in metas if m['originator']}
            accounts = {m['creator_account_id'] for m in metas if m['creator_account_id']}
            if origins != {'Codex Desktop'} or accounts != {account}:
                diagnostics['excluded_identity_or_origin_files'] += 1
                continue
            project = next((m['cwd'] for m in reversed(metas) if m['cwd']), 'Unknown')
            project = project.replace('\\', '/').rstrip('/').split('/')[-1]
            for raw_time, payload in pending:
                rid = payload['response_id']
                try:
                    when = timestamp(raw_time)
                    if not start <= when < cutoff:
                        continue
                    if not all(isinstance(payload[k], str) and payload[k] for k in ('response_id', 'thread_id', 'turn_id')):
                        raise ValueError('Missing identifier')
                    usage = validated_usage(payload['usage'])
                    record = {'timestamp': when.isoformat(), 'thread_id': payload['thread_id'],
                              'turn_id': payload['turn_id'], 'usage': usage,
                              'project': project, 'model': models.get(payload['turn_id']) or 'Unknown'}
                except (ValueError, TypeError, AttributeError):
                    diagnostics['invalid_usage_records'] += 1
                    if isinstance(rid, str) and rid:
                        conflicts.add(rid)
                    continue
                if rid in records:
                    if record != records[rid]:
                        conflicts.add(rid)
                    else:
                        diagnostics['duplicate_records_removed'] += 1
                else:
                    records[rid] = record
    for rid in conflicts:
        records.pop(rid, None)
    diagnostics['conflicting_response_ids_excluded'] = len(conflicts)
    def aggregate(rows):
        rows = list(rows)
        return {key: (None if any(r['usage'][key] is None for r in rows)
                      else sum(r['usage'][key] for r in rows)) for key in FIELDS + SUBSETS}
    daily, projects = defaultdict(list), defaultdict(list)
    for record in records.values():
        daily[timestamp(record['timestamp']).astimezone(zone).date().isoformat()].append(record)
        projects[record['project']].append(record)
    return {'schema_version': 1, 'collector_version': VERSION,
            'scope': 'Local Codex Desktop; selected account; partial coverage',
            'start_inclusive': start.isoformat(), 'cutoff_exclusive': cutoff.isoformat(),
            'timezone': str(zone), 'totals': aggregate(records.values()),
            'daily': {k: aggregate(v) for k, v in sorted(daily.items())},
            'projects': {k: aggregate(v) for k, v in sorted(projects.items())},
            'unique_responses': len(records), 'diagnostics': dict(diagnostics),
            'active_processing_seconds': None, 'ongoing_runs': None,
            'limitations': ['Local logs are an undocumented, version-dependent source.',
                           'No records means no observed usage, not proof of zero usage.',
                           'Elapsed or missing completion events do not prove active processing.',
                           'Project folder labels can combine folders with identical names.']}


def output_path(value):
    path = Path(value).expanduser().resolve()
    repo = Path(__file__).resolve().parents[1]
    if path.is_relative_to(repo):
        # Only the designated ignored private folder is allowed within this checkout.
        import subprocess
        if not path.is_relative_to(repo / 'private'):
            raise ValueError('Collected output must be outside the repository or in ignored private/')
        rel = path.relative_to(repo).as_posix()
        ignored = subprocess.run(['git', 'check-ignore', '-q', '--', rel], cwd=repo).returncode == 0
        tracked = subprocess.check_output(['git', 'ls-files', '--', rel], cwd=repo).strip()
        if not ignored or tracked:
            raise ValueError('Output must be ignored and untracked')
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', required=True, type=Path, help='Private JSON with account_id and timezone')
    parser.add_argument('--codex-home', type=Path, default=Path(os.environ.get('CODEX_HOME', Path.home()/'.codex')))
    parser.add_argument('--cutoff', help='ISO timestamp with offset; defaults to now')
    parser.add_argument('--start', help='ISO timestamp with offset; defaults to local Monday midnight')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    try:
        config = json.loads(args.config.read_text(encoding='utf-8'))
        zone = ZoneInfo(config.get('timezone', 'America/New_York'))
        cutoff = timestamp(args.cutoff) if args.cutoff else datetime.now(timezone.utc)
        start = timestamp(args.start) if args.start else week_start(cutoff, zone)
        destination = output_path(args.output)
        result = collect(args.codex_home.expanduser(), config['account_id'], start, cutoff, zone)
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_suffix(destination.suffix+'.tmp')
        temporary.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
        temporary.replace(destination)
        print('Private usage snapshot written. Review diagnostics before interpreting totals.')
    except ZoneInfoNotFoundError:
        parser.exit(2, 'Timezone database missing: install requirements.txt in your Python environment.\n')
    except (ValueError, KeyError, OSError):
        parser.exit(2, 'Collection failed: check private configuration, timestamps, source and output permissions.\n')


if __name__ == '__main__':
    main()
