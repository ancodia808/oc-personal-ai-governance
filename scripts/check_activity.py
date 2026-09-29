"""Evaluate a private read_thread snapshot; does not send notifications."""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
try:
    from .evaluate_activity import normalize_thread, evaluate_proxy
    from .collect_usage import output_path
except ImportError:
    from evaluate_activity import normalize_thread, evaluate_proxy
    from collect_usage import output_path


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',required=True,type=Path,help='Envelope with observed_at and snapshot from read_thread')
    parser.add_argument('--output',required=True)
    parser.add_argument('--cutoff',help='Evaluation timestamp; defaults to now')
    parser.add_argument('--timezone',default='America/New_York')
    args=parser.parse_args()
    envelope=json.loads(args.input.read_text(encoding='utf-8'))
    run=normalize_thread(envelope['snapshot'],envelope['observed_at'])
    result=evaluate_proxy(run,args.cutoff or datetime.now(timezone.utc).isoformat(),timezone=args.timezone,
                          delivered=envelope.get('delivered_keys',[]))
    path=output_path(args.output)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps({'observation':run,'evaluation':result},indent=2)+'\n',encoding='utf-8')
    print('Private activity advisory evaluation written; nothing sent.')


if __name__=='__main__':main()
