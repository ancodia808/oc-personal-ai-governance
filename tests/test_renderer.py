import unittest
from scripts.render_review import render


def fixture():
    usage = dict(input_tokens=100,output_tokens=10,total_tokens=110,cached_input_tokens=80,reasoning_output_tokens=2)
    return dict(schema_version=1,collector_version='1.0',start_inclusive='2026-09-28T04:00:00Z',cutoff_exclusive='2026-09-29T16:00:00Z',timezone='America/New_York',totals=usage,daily={'2026-09-28':usage},projects={'Synthetic workshop':usage},unique_responses=1,diagnostics={},limitations=['Partial local observations.'])


class RendererTests(unittest.TestCase):
    def test_reconciled_report_and_no_observation_day(self):
        page, summary=render(fixture(),'private/daily-review.html')
        self.assertIn('Week to date',summary)
        self.assertIn('No observations',summary)
        self.assertIn('110',summary)
        self.assertIn('(ET)',summary)
        self.assertIn('ET',page)
        self.assertEqual(summary.count('\n- '),3)
        self.assertNotIn('<script',page)

    def test_injection_escaped(self):
        d=fixture();d['projects']={'<script>alert(1)</script>':d['totals']}
        page,summary=render(d,'private/daily-review.html')
        self.assertNotIn('<script>',page)
        self.assertIn('&lt;script&gt;',page)

    def test_mismatch_rejected(self):
        d=fixture();d['projects']={}
        with self.assertRaises(ValueError):render(d,'private/daily-review.html')

    def test_custom_interval_not_week(self):
        d=fixture();d['start_inclusive']='2026-09-28T05:00:00Z'
        self.assertIn('Reporting interval',render(d,'private/daily-review.html')[1])

    def test_diagnostics_prioritized(self):
        d=fixture();d['diagnostics']={'invalid_usage_records':2}
        page,summary=render(d,'private/daily-review.html')
        self.assertIn('Coverage needs review',summary)
        self.assertIn('invalid usage records: 2',summary)

    def test_unknown_cached_not_zero(self):
        d=fixture();d['totals']['cached_input_tokens']=None
        page,summary=render(d,'private/daily-review.html')
        self.assertIn('Unavailable',page)
        self.assertNotIn('0.0% of input',summary)


if __name__=='__main__':unittest.main()
