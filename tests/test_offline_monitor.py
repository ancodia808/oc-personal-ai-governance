import json
from pathlib import Path
import tempfile
import unittest
from datetime import datetime, timezone, timedelta
from scripts.offline_monitor import scan, advisories, run, claim_queued, complete_digest, render_digest


class OfflineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        (self.home / 'sessions').mkdir()
        (self.home / 'archived_sessions').mkdir()
        self.now = datetime(2026, 10, 2, 22, tzinfo=timezone.utc)

    def write(self, folder='sessions', closed=False, account='a', broken=False):
        records = [dict(type='session_meta', timestamp='2026-10-02T19:00:00Z',
            payload=dict(id='chat', creator_account_id=account, originator='Codex Desktop')),
            dict(type='event_msg', timestamp='2026-10-02T20:00:00Z', payload=dict(type='task_started', turn_id='turn'))]
        if closed:
            records.append(dict(type='event_msg', timestamp='2026-10-02T21:00:00Z', payload=dict(type='task_complete', turn_id='turn', last_agent_message='DO NOT RETAIN')))
        (self.home / folder / 'test.jsonl').write_text('\n'.join(map(json.dumps, records)) + ('\n{' if broken else '\n'))

    def test_threshold_friday_and_completion_across_copies(self):
        self.write()
        rows, diag = scan(self.home, 'a', self.now)
        self.assertEqual(len(advisories(rows, self.now)), 1)
        self.write('archived_sessions', closed=True)
        rows, diag = scan(self.home, 'a', self.now)
        self.assertEqual(rows[0]['state'], 'closed')
        self.assertEqual(advisories(rows, self.now), [])
        self.assertNotIn('DO NOT RETAIN', json.dumps(rows))

    def test_wrong_account_and_truncated_record(self):
        self.write(account='other')
        self.assertEqual(scan(self.home, 'a', self.now)[0], [])
        self.write(broken=True)
        rows, _ = scan(self.home, 'a', self.now)
        self.assertEqual(rows[0]['state'], 'unknown')
        self.assertEqual(advisories(rows, self.now), [])

    def test_non_friday_below_threshold(self):
        self.write()
        rows, _ = scan(self.home, 'a', self.now)
        self.assertEqual(advisories(rows, self.now.replace(hour=21)), [])

    def test_queue_optout_and_completion_expiration(self):
        # Use a fixed old start; reminders are explicitly unfinished, not live status.
        self.write()
        from unittest.mock import patch
        import sqlite3
        pilot = {'delivery_enabled': True, 'alerts': {'recipient_verified': True, 'slack_user_id': 'synthetic'}}
        out = self.home / 'output'
        with patch('scripts.offline_monitor.datetime') as clock:
            clock.now.return_value = self.now
            self.assertFalse(run(self.home, {'account_id':'a'}, pilot, out)['queue_enabled'])
            result = run(self.home, {'account_id':'a'}, pilot, out, True)
            self.assertEqual(result['queue_counts'], {'queued':1})
            key = result['digest_key']
            self.assertTrue(claim_queued(out, key, self.home/'ledger.sqlite')['send_allowed'])
            run(self.home, {'account_id':'a'}, pilot, out, True)
            self.assertFalse(claim_queued(out, key, self.home/'ledger.sqlite')['send_allowed'])
            self.write(closed=True)
            self.assertEqual(run(self.home, {'account_id':'a'}, pilot, out, True)['queue_counts'], {'pending':1})

    def test_exact_cutoff_and_format(self):
        row = {'thread_id':'chat','turn_id':'turn','state':'unfinished',
               'started_at':(self.now-timedelta(hours=24)).isoformat(), 'project':'Example', 'title':'Chat'}
        notice = advisories([row], self.now)
        self.assertTrue(notice[0]['final_notice'])
        self.assertFalse(notice[0]['delayed_final'])
        self.assertFalse(advisories([row], self.now-timedelta(seconds=1))[0]['final_notice'])
        message = render_digest(notice, 'SYNTHETIC')
        self.assertIn('<@SYNTHETIC>', message)
        self.assertIn('"Example" - "Chat" - Started 24h 00m ago - **Final Notice!**', message)
        self.assertIn('final notice for some', message)
        row['started_at']=(self.now-timedelta(hours=2)).isoformat()
        self.assertNotIn('final notice for some', render_digest(advisories([row],self.now),'SYNTHETIC'))

    def test_final_once_and_repeating_active_digest(self):
        from unittest.mock import patch
        self.write()
        pilot={'delivery_enabled':True,'alerts':{'recipient_verified':True,'slack_user_id':'synthetic'}}
        out=self.home/'out'; ledger_path=self.home/'ledger.sqlite'
        with patch('scripts.offline_monitor.datetime') as clock:
            clock.now.return_value=self.now
            first=run(self.home,{'account_id':'a'},pilot,out,True)
            key=first['digest_key']
            self.assertTrue(claim_queued(out,key,ledger_path)['send_allowed'])
            complete_digest(out,key,ledger_path,'synthetic receipt')
            self.assertFalse(claim_queued(out,key,ledger_path)['send_allowed'])
            clock.now.return_value=self.now+timedelta(minutes=30)
            second=run(self.home,{'account_id':'a'},pilot,out,True)
            self.assertNotEqual(key,second['digest_key'])
            clock.now.return_value=self.now+timedelta(hours=23)
            final=run(self.home,{'account_id':'a'},pilot,out,True)
            self.assertTrue(final['advisories'][0]['delayed_final'])
            self.assertTrue(claim_queued(out,final['digest_key'],ledger_path)['send_allowed'])
            complete_digest(out,final['digest_key'],ledger_path,'synthetic final receipt')
            clock.now.return_value=self.now+timedelta(hours=24)
            self.assertEqual(run(self.home,{'account_id':'a'},pilot,out,True)['advisories'],[])

    def test_multiple_starts_and_projectless_last(self):
        self.write()
        path=self.home/'sessions/test.jsonl'
        with path.open('a') as f:
            f.write(json.dumps({'type':'event_msg','timestamp':'2026-10-02T19:00:00Z',
                               'payload':{'type':'task_started','turn_id':'second'}})+'\n')
        rows,_=scan(self.home,'a',self.now)
        self.assertEqual(len(advisories(rows,self.now)),2)
        rows[0]['project']=''; rows[1]['project']='Z project'
        self.assertEqual(advisories(rows,self.now)[-1]['project'],'')



if __name__ == '__main__':
    unittest.main()
