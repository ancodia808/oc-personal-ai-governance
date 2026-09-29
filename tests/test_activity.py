import unittest
from scripts.evaluate_activity import evaluate


def run():
    return dict(evidence='verified_execution_intervals_v1',account_id='synthetic',thread_id='t',turn_id='u',
                run_started_at='2026-10-02T16:00:00-04:00',status_as_of='2026-10-02T18:01:00-04:00',state='processing',
                processing_intervals=[dict(start='2026-10-02T16:00:00-04:00',end='2026-10-02T18:01:00-04:00')])


class ActivityTests(unittest.TestCase):
    def test_two_triggers(self):
        r=run();out=evaluate(r,r['status_as_of'])
        self.assertEqual({x['trigger'] for x in out['advisories']},{'two_hour','friday_evening'})

    def test_duplicate_overlap_not_double_counted(self):
        r=run();r['processing_intervals']*=2
        self.assertEqual(evaluate(r,r['status_as_of'])['confirmed_active_seconds'],7260)

    def test_waiting_and_stale_never_alert(self):
        r=run();r['state']='waiting'
        self.assertFalse(evaluate(r,r['status_as_of'])['advisories'])
        r['state']='processing'
        self.assertEqual(evaluate(r,'2026-10-03T12:00:00-04:00')['status'],'stale')

    def test_unverified_and_future(self):
        self.assertIsNone(evaluate({},'2026-10-02T18:01:00-04:00')['confirmed_active_seconds'])
        with self.assertRaises(ValueError):evaluate(run(),'2026-10-02T17:00:00-04:00')

    def test_friday_under_two_hours(self):
        r=run();r['processing_intervals'][0]['start']='2026-10-02T17:55:00-04:00'
        self.assertEqual([a['trigger'] for a in evaluate(r,r['status_as_of'])['advisories']],['friday_evening'])

    def test_exact_threshold_and_wait_gap(self):
        r=run();r['status_as_of']='2026-10-02T18:00:00-04:00';r['processing_intervals'][0]['end']=r['status_as_of']
        self.assertIn('two_hour',[a['trigger'] for a in evaluate(r,r['status_as_of'])['advisories']])
        self.assertIn('friday_evening',[a['trigger'] for a in evaluate(r,r['status_as_of'])['advisories']])
        r['processing_intervals'][0]['start']='2026-10-02T16:00:01-04:00'
        self.assertNotIn('two_hour',[a['trigger'] for a in evaluate(r,r['status_as_of'])['advisories']])

    def test_delivery_receipt_dedup_and_retry(self):
        r=run();first=evaluate(r,r['status_as_of'])
        receipts=[a['deduplication_key'] for a in first['advisories']]
        self.assertFalse(evaluate(r,r['status_as_of'],receipts)['advisories'])
        self.assertEqual(len(evaluate(r,r['status_as_of'])['advisories']),2)

    def test_completed_no_alert(self):
        r=run();r['state']='completed'
        self.assertFalse(evaluate(r,r['status_as_of'])['advisories'])


if __name__=='__main__':unittest.main()
