"""List Desktop-origin thread IDs for the configured account, without prompts."""
import argparse
import json
import os
from pathlib import Path
try:
    from .collect_usage import output_path
except ImportError:
    from collect_usage import output_path


def inventory(home, account):
    candidates={};errors=0
    for folder in ('sessions','archived_sessions'):
        for path in (home/folder).rglob('*.jsonl'):
            metas=[]
            try:
                for line in path.open(encoding='utf-8'):
                    # Parse metadata only; no message content is retained.
                    if '"session_meta"' not in line:continue
                    r=json.loads(line)
                    if r.get('type')=='session_meta':metas.append(r['payload'])
            except (OSError,ValueError,UnicodeError):errors+=1;continue
            if {m.get('originator') for m in metas}!={'Codex Desktop'}:continue
            accounts={m.get('creator_account_id') for m in metas if m.get('creator_account_id')}
            if accounts!={account}:continue
            for m in metas:
                tid=m.get('id') or m.get('session_id')
                if tid:candidates[tid]=True
    return {'eligible_thread_ids':sorted(candidates),'read_errors':errors,'scope':'Local Desktop metadata; not a live status source'}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config',default='private/collector.local.json',type=Path)
    p.add_argument('--output',default='private/monitor-inventory.json')
    args=p.parse_args()
    config=json.loads(args.config.read_text(encoding='utf-8'))
    result=inventory(Path(os.environ.get('CODEX_HOME',Path.home()/'.codex')),config['account_id'])
    destination=output_path(args.output);destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('Private Desktop inventory written.')
