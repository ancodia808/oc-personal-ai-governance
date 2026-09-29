import unittest
from scripts.evaluate_activity import normalize_thread,evaluate_proxy


def sample():
    return dict(host_id='local',thread_id='synthetic',turn_id='turn1',state='working',
                status_as_of='2026-10-02T18:00:00-04:00',reported_duration_seconds=7200,duration_basis='elapsed_turn')


class ProxyTests(unittest.TestCase):
    def test_exact_threshold_and_friday(self):
        r=sample();out=evaluate_proxy(r,r['status_as_of'])
        self.assertEqual(len(out['advisories']),2)
        self.assertIsNone(out['confirmed_active_seconds'])

    def test_friday_unknown_duration(self):
        r=sample();r['reported_duration_seconds']=None
        self.assertEqual([a['trigger'] for a in evaluate_proxy(r,r['status_as_of'])['advisories']],['friday_evening'])

    def test_short_and_non_friday(self):
        r=sample();r['status_as_of']='2026-10-01T18:00:00-04:00';r['reported_duration_seconds']=7199
        self.assertFalse(evaluate_proxy(r,r['status_as_of'])['advisories'])

    def test_waiting_and_stale(self):
        r=sample();r['state']='waiting'
        self.assertFalse(evaluate_proxy(r,r['status_as_of'])['advisories'])
        r['state']='thinking'
        self.assertEqual(evaluate_proxy(r,'2026-10-02T18:06:00-04:00')['status'],'stale')

    def test_dedup_and_new_turn(self):
        r=sample();keys=[a['deduplication_key'] for a in evaluate_proxy(r,r['status_as_of'])['advisories']]
        self.assertFalse(evaluate_proxy(r,r['status_as_of'],keys)['advisories'])
        r['turn_id']='turn2'
        self.assertEqual(len(evaluate_proxy(r,r['status_as_of'],keys)['advisories']),2)

    def test_adapter_and_flags(self):
        snapshot={'thread':{'id':'test','status':{'type':'active','activeFlags':[]}},'turns':[{'id':'turn','status':'inProgress','startedAt':1790964000}]}
        run=normalize_thread(snapshot,'2026-10-02T18:00:00-04:00')
        self.assertEqual(run['state'],'working')
        self.assertEqual(run['duration_basis'],'elapsed_turn')
        snapshot['thread']['status']['activeFlags']=['waitingOnApproval']
        self.assertEqual(normalize_thread(snapshot,run['status_as_of'])['state'],'unknown')

    def test_future_and_invalid_duration(self):
        r=sample()
        with self.assertRaises(ValueError):evaluate_proxy(r,'2026-10-02T17:00:00-04:00')
        r['reported_duration_seconds']=float('nan')
        with self.assertRaises(ValueError):evaluate_proxy(r,r['status_as_of'])

    def test_completed_unloaded_chat_is_offloaded(self):
        snapshot={'thread':{'id':'test','status':{'type':'notLoaded'}},
                  'turns':[{'id':'done','status':'completed','startedAt':1790964000}]}
        run=normalize_thread(snapshot,'2026-10-02T18:00:00-04:00')
        self.assertEqual(run['state'],'offloaded')
        self.assertIsNone(run['reported_duration_seconds'])
        self.assertEqual(evaluate_proxy(run,run['status_as_of'])['advisories'],[])
        snapshot['thread']['status']={'type':'active'}
        snapshot['turns'][0]['status']='inProgress'
        self.assertEqual(normalize_thread(snapshot,run['status_as_of'])['state'],'working')

    def test_unloaded_ambiguous_turn_remains_unknown(self):
        for turns in [[],[{'status':'inProgress'}],[{'status':'interrupted'}],
                      [{'status':'completed'},{'status':'inProgress'}]]:
            snapshot={'thread':{'id':'test','status':{'type':'notLoaded'}},'turns':turns}
            self.assertEqual(normalize_thread(snapshot,'2026-10-02T18:00:00-04:00')['state'],'unknown')


if __name__=='__main__':unittest.main()
