"""Private durable send claims. Ambiguous sends are never retried automatically."""
import argparse
import json
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
try:
    from .collect_usage import output_path
except ImportError:
    from collect_usage import output_path


def ledger(path, action, key, receipt=None):
    path=output_path(str(path))
    path.parent.mkdir(parents=True,exist_ok=True)
    with closing(sqlite3.connect(path,timeout=10)) as db, db:
        db.execute('CREATE TABLE IF NOT EXISTS deliveries (key TEXT PRIMARY KEY, status TEXT NOT NULL, updated TEXT NOT NULL, receipt TEXT)')
        now=datetime.now(timezone.utc).isoformat()
        if action=='claim':
            cursor=db.execute('INSERT OR IGNORE INTO deliveries VALUES (?, ?, ?, ?)',(key,'pending',now,None))
            claimed=cursor.rowcount==1
        else:
            claimed=False
            if action=='complete':
                if not receipt:raise ValueError('Successful delivery receipt required')
                cursor=db.execute("UPDATE deliveries SET status='sent', updated=?, receipt=? WHERE key=? AND status='pending'",(now,receipt,key))
                if cursor.rowcount!=1:raise ValueError('Pending claim required')
        row=db.execute('SELECT status, updated, receipt FROM deliveries WHERE key=?',(key,)).fetchone()
        return {'send_allowed':claimed,'status':row[0] if row else 'absent','updated':row[1] if row else None,'receipt':row[2] if row else None}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['claim','complete','status'])
    parser.add_argument('--key',required=True)
    parser.add_argument('--receipt')
    parser.add_argument('--db',default='private/delivery-ledger.sqlite')
    args=parser.parse_args()
    print(json.dumps(ledger(args.db,args.action,args.key,args.receipt)))
