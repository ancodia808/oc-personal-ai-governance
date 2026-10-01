"""Offline lifecycle reminders. No network, model calls, or automatic delivery."""
import argparse
from collections import Counter
from contextlib import closing
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sqlite3

try:
    from .collect_usage import output_path, timestamp, project_label
    from .eastern_time import eastern
    from .delivery_ledger import ledger
except ImportError:
    from collect_usage import output_path, timestamp, project_label
    from eastern_time import eastern
    from delivery_ledger import ledger

REPO = Path(__file__).resolve().parents[1]
TERMINAL = {'task_complete', 'turn_aborted', 'task_failed'}


def scan(home, account, now):
    """Merge lifecycle metadata across copies; never retain message/tool content."""
    threads = {}
    titles = {}
    index = home / 'session_index.jsonl'
    if index.exists():
        try:
            for line in index.read_text(encoding='utf-8').splitlines():
                row = json.loads(line)
                titles[row['id']] = row.get('thread_name') or row['id']
        except (OSError, ValueError, KeyError):
            pass
    diagnostics = Counter()
    for folder in ('sessions', 'archived_sessions'):
        source = home / folder
        if not source.is_dir():
            diagnostics['missing_directories'] += 1
            continue
        for path in source.rglob('*.jsonl'):
            metas, events, latest = [], [], None
            broken = False
            try:
                with path.open(encoding='utf-8') as stream:
                    for line in stream:
                        try:
                            r = json.loads(line)
                            p = r.get('payload', {})
                            if not isinstance(p, dict):
                                continue
                            if r.get('type') == 'session_meta':
                                metas.append(p)
                            stamp = timestamp(r['timestamp'])
                            if stamp > now:
                                broken = True
                                continue
                            latest = max(latest, stamp) if latest else stamp
                            if isinstance(p.get('turn_id'), str) and p['turn_id']:
                                events.append((p['turn_id'], 'activity', stamp))
                            if r.get('type') == 'event_msg' and p.get('type') in TERMINAL | {'task_started'}:
                                tid = p.get('turn_id')
                                if not isinstance(tid, str) or not tid:
                                    broken = True
                                else:
                                    events.append((tid, p['type'], stamp))
                        except (ValueError, TypeError, KeyError, AttributeError):
                            broken = True
            except (OSError, UnicodeError):
                diagnostics['read_errors'] += 1
                continue
            identities = {(m.get('id') or m.get('session_id'), m.get('creator_account_id'), m.get('originator')) for m in metas}
            if len(identities) != 1:
                diagnostics['unattributed_files'] += 1
                continue
            thread_id, owner, origin = identities.pop()
            if owner != account or origin != 'Codex Desktop' or not thread_id:
                continue
            t = threads.setdefault(thread_id, {'turns': {}, 'latest': None, 'broken': False, 'project': project_label(metas[0].get('cwd') or '')})
            t['broken'] |= broken
            if latest:
                t['latest'] = max(t['latest'], latest) if t['latest'] else latest
            for turn_id, kind, stamp in events:
                turn = t['turns'].setdefault(turn_id, {'starts': set(), 'closed': False, 'latest': stamp})
                turn['latest'] = max(turn['latest'], stamp)
                if kind == 'task_started':
                    turn['starts'].add(stamp)
                elif kind in TERMINAL:
                    turn['closed'] = True
    observations = []
    for thread_id, t in threads.items():
        project = t['project']
        if project == '<Chats without a project>':
            project = ''
        base = {'thread_id': thread_id, 'project': project, 'title': titles.get(thread_id, thread_id),
                'last_record_at': t['latest'].isoformat() if t['latest'] else None}
        if not t['turns']:
            observations.append({**base, 'turn_id': None, 'state': 'unknown', 'started_at': None})
        for turn_id, turn in t['turns'].items():
            start = next(iter(turn['starts'])) if len(turn['starts']) == 1 else None
            state = 'unknown' if t['broken'] or not start else ('closed' if turn['closed'] else 'unfinished')
            observations.append({**base, 'last_record_at': turn['latest'].isoformat(), 'turn_id': turn_id, 'state': state,
                                 'started_at': start.isoformat() if start else None})
    return observations, dict(diagnostics)


def advisories(observations, now):
    local = now.astimezone(eastern())
    result = []
    for row in observations:
        if row['state'] != 'unfinished':
            continue
        elapsed = (now - timestamp(row['started_at'])).total_seconds()
        final = elapsed >= 86400
        friday = local.weekday() == 4 and local.hour >= 18
        if not final and elapsed < 7200 and not friday:
            continue
        trigger = 'final_notice' if final else 'possibly_running'
        key = json.dumps(['local', row['thread_id'], row['turn_id'], trigger], separators=(',', ':'))
        result.append({**row, 'deduplication_key': key, 'trigger': trigger, 'final_notice': final,
            'delayed_final': final and elapsed >= 88200,
            'observed_at': now.isoformat(), 'elapsed_seconds': elapsed,
            'verified_processing': False, 'duration_basis': 'time_since_recorded_start'})
    return sorted(result, key=lambda r: (not bool(r.get('project')), r.get('project', '').casefold(),
                                        r.get('title', r['thread_id']).casefold(), r['started_at'], r['turn_id']))


def safe_label(value):
    # Labels are data: prevent new bullets, markup or mention injection.
    import re
    return re.sub(r'[<>@*_`~"\r\n]', ' ', value).strip()


def render_digest(rows, recipient):
    text = ['**PAIGe - Possibly still running**', '',
            f'<@{recipient}>, you have chats that may still be running (see below).'
            + (' This is the final notice for some of them.' if any(r['final_notice'] for r in rows) else ''), '']
    for row in rows:
        minutes = int(row['elapsed_seconds'] // 60)
        project = f'"{safe_label(row["project"])}" - ' if row.get('project') else ''
        title = safe_label(row.get('title') or row['thread_id'])
        suffix = ' - **Final Notice!**' if row['final_notice'] else ''
        if row.get('delayed_final'):
            suffix += ' (delayed)'
        text.append(f'- {project}"{title}" - Started {minutes // 60}h {minutes % 60:02d}m ago{suffix}')
    text.extend(['', 'Unmatched starts do not confirm ongoing processing.'])
    if any(r['final_notice'] for r in rows):
        text.append('Final notices leave the active list; current status remains unknown.')
    return '\n'.join(text)


def run(home, config, pilot, destination, queue=False):
    destination = output_path(str(destination))
    destination.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(output_path(str(destination / 'runner-lock.sqlite')), timeout=10)) as lock:
        lock.execute('BEGIN IMMEDIATE')
        return _run(home, config, pilot, destination, queue)


def _run(home, config, pilot, destination, queue=False):
    destination = output_path(str(destination))
    destination.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    observations, diagnostics = scan(home, config['account_id'], now)
    candidates = advisories(observations, now)
    enabled = pilot.get('delivery_enabled') is True
    alerts = pilot.get('alerts', {})
    recipient = alerts.get('slack_user_id')
    queue_enabled = queue and enabled and alerts.get('slack_enabled', True) and alerts.get('recipient_verified') is True and bool(recipient)
    with closing(sqlite3.connect(output_path(str(destination / 'queue.sqlite')), timeout=10)) as db, db:
        db.execute('CREATE TABLE IF NOT EXISTS queue (key TEXT PRIMARY KEY, payload TEXT NOT NULL, status TEXT NOT NULL)')
        db.execute('CREATE TABLE IF NOT EXISTS final_notices (key TEXT PRIMARY KEY, digest_key TEXT NOT NULL, status TEXT NOT NULL)')
        candidates = [c for c in candidates if not c['final_notice'] or not db.execute('SELECT 1 FROM final_notices WHERE key=?', (c['deduplication_key'] + '|' + str(recipient),)).fetchone()]
        digest_key = None
        # Pending/claimed sends are never released automatically.
        db.execute("UPDATE queue SET status='expired' WHERE status='queued'")
        if queue_enabled and not diagnostics.get('read_errors') and not diagnostics.get('missing_directories'):
            if candidates:
                digest_key = 'offline-digest|' + str(int(now.timestamp()) // 1800) + '|' + recipient
                payload = json.dumps({'recipient': recipient, 'rows': candidates,
                                      'message': render_digest(candidates, recipient), 'observed_at': now.isoformat()})
                db.execute("INSERT INTO queue VALUES (?,?,'queued') ON CONFLICT(key) DO UPDATE SET payload=excluded.payload, status='queued' WHERE queue.status IN ('queued','expired')", (digest_key, payload))
        queue_counts = dict(db.execute('SELECT status, COUNT(*) FROM queue GROUP BY status'))
    previous = destination / 'latest.json'
    gap = None
    if previous.exists():
        gap = (now - timestamp(json.loads(previous.read_text(encoding='utf-8'))['observed_at'])).total_seconds()
    result = {'observed_at': now.isoformat(), 'policy': 'offline_digest_24h_v2',
        'scope': 'All attributable local Desktop lifecycle records; no live or pinned-chat discovery',
        'counts': dict(Counter(r['state'] for r in observations)), 'diagnostics': diagnostics,
        'monitoring_interruption_seconds': gap if gap is not None and gap > 2700 else None,
        'count_unit': 'turns', 'advisories': candidates, 'digest_key': digest_key, 'queue_enabled': bool(queue_enabled), 'queue_counts': queue_counts}
    tmp = output_path(str(destination / 'latest.tmp'))
    tmp.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    tmp.replace(previous)
    return result


def claim_queued(destination, key, ledger_path):
    with closing(sqlite3.connect(output_path(str(destination / 'queue.sqlite')))) as db, db:
        db.execute('BEGIN IMMEDIATE')
        row = db.execute("SELECT payload FROM queue WHERE key=? AND status='queued'", (key,)).fetchone()
        if not row or not key.startswith('offline-digest|'):
            return {'send_allowed': False, 'reason': 'No currently eligible digest'}
        payload = json.loads(row[0])
        if (datetime.now(timezone.utc) - timestamp(payload['observed_at'])).total_seconds() > 300:
            return {'send_allowed': False, 'reason': 'Digest must be revalidated'}
        finals = [r['deduplication_key'] + '|' + payload['recipient'] for r in payload['rows'] if r['final_notice']]
        if any(db.execute('SELECT 1 FROM final_notices WHERE key=?', (k,)).fetchone() for k in finals):
            return {'send_allowed': False, 'reason': 'Final notice already reserved; regenerate digest'}
        claim = ledger(ledger_path, 'claim', key)
        if claim['send_allowed']:
            db.execute("UPDATE queue SET status='pending' WHERE key=?", (key,))
            db.executemany("INSERT INTO final_notices VALUES (?,?,'pending')", [(k, key) for k in finals])
        return {**claim, 'payload': payload if claim['send_allowed'] else None}


def complete_digest(destination, key, ledger_path, receipt):
    result = ledger(ledger_path, 'complete', key, receipt)
    with closing(sqlite3.connect(output_path(str(destination / 'queue.sqlite')))) as db, db:
        db.execute("UPDATE queue SET status='sent' WHERE key=? AND status='pending'", (key,))
        db.execute("UPDATE final_notices SET status='sent' WHERE digest_key=?", (key,))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--queue', action='store_true', help='Queue reminders for the verified private Slack recipient; never sends')
    parser.add_argument('--claim', help='Revalidate and claim one queued key for an authorized delivery agent')
    parser.add_argument('--complete', help='Complete a previously claimed key after confirmed delivery')
    parser.add_argument('--receipt', help='Immediate successful send response; required with --complete')
    parser.add_argument('--codex-home', type=Path, default=Path(os.environ.get('CODEX_HOME', Path.home() / '.codex')))
    parser.add_argument('--output-dir', type=Path, default=REPO / 'private/offline-monitor')
    args = parser.parse_args()
    if args.claim and args.complete:
        parser.error('Choose claim or complete')
    if args.complete:
        if not args.receipt:
            parser.error('--complete requires --receipt')
        print(json.dumps(complete_digest(args.output_dir, args.complete, REPO / 'private/delivery-ledger.sqlite', args.receipt)))
        return
    config = json.loads((REPO / 'private/collector.local.json').read_text(encoding='utf-8'))
    pilot = json.loads((REPO / 'private/pilot.local.json').read_text(encoding='utf-8'))
    if pilot.get('delivery_enabled') is not True:
        print('PAIGe - Monitoring disabled by private configuration.')
        return
    result = run(args.codex_home, config, pilot, args.output_dir, args.queue or bool(args.claim))
    if args.claim:
        print(json.dumps(claim_queued(args.output_dir, args.claim, REPO / 'private/delivery-ledger.sqlite')))
        return
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
