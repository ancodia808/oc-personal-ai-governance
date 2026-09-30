import json
from pathlib import Path
import tempfile
import unittest
from scripts.eastern_time import eastern as ZoneInfo
from scripts.collect_usage import collect, timestamp, week_start, output_path


class CollectorTests(unittest.TestCase):
    def setUp(self):
        test_root = Path(__file__).resolve().parents[1]/'private'
        test_root.mkdir(exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=test_root)
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.start = timestamp('2026-09-28T00:00:00-04:00')
        self.end = timestamp('2026-09-30T00:00:00-04:00')
        self.zone = ZoneInfo('America/New_York')

    def write(self, name, records, origin='Codex Desktop', account='synthetic-account'):
        p = self.home/name
        p.parent.mkdir(parents=True, exist_ok=True)
        meta = {'type':'session_meta','payload':{'originator':origin,'creator_account_id':account,'cwd':'/synthetic/demo'}}
        p.write_text('\n'.join(json.dumps(r) for r in [meta]+records)+'\n',encoding='utf-8')
        return p

    def row(self, rid='r1', when='2026-09-29T12:00:00Z', total=110):
        return {'type':'token_usage_record','timestamp':when,'payload':{'response_id':rid,'thread_id':'t','turn_id':'u','usage':{'input_tokens':100,'output_tokens':total-100,'total_tokens':total,'cached_input_tokens':80,'reasoning_output_tokens':2}}}

    def run_collect(self):
        return collect(self.home,'synthetic-account',self.start,self.end,self.zone)

    def test_deduplicates_archive_and_ignores_cumulative(self):
        self.write('sessions/a.jsonl',[self.row(),{'type':'event_msg','payload':{'type':'token_count','info':{'total_token_usage':{'total_tokens':99999}}}}])
        self.write('archived_sessions/a.jsonl',[self.row()])
        r=self.run_collect()
        self.assertEqual(r['totals']['total_tokens'],110)
        self.assertEqual(r['totals']['cached_input_tokens'],80)
        self.assertEqual(r['diagnostics']['duplicate_records_removed'],1)

    def test_conflict_excludes_both(self):
        self.write('sessions/a.jsonl',[self.row()])
        self.write('archived_sessions/a.jsonl',[self.row(total=120)])
        self.assertEqual(self.run_collect()['unique_responses'],0)

    def test_filters_identity_and_extension(self):
        self.write('sessions/a.jsonl',[self.row()],account=None)
        self.write('sessions/b.jsonl',[self.row('b')],origin='codex_vscode')
        self.write('sessions/c.jsonl',[self.row('c')],account='other')
        result=self.run_collect()
        self.assertEqual(result['unique_responses'],0)
        self.assertEqual(result['diagnostics']['files_skipped_by_filters'],2)
        self.assertEqual(result['diagnostics']['unattributed_files'],1)

    def test_half_open_boundaries_and_local_day(self):
        self.write('sessions/old-name.jsonl',[self.row('a',self.start.isoformat()),self.row('b',self.end.isoformat()),self.row('c','2026-09-29T02:00:00Z')])
        r=self.run_collect()
        self.assertEqual(r['totals']['total_tokens'],220)
        self.assertEqual(list(r['daily']),['2026-09-28'])

    def test_invalid_and_truncated_records(self):
        bad=self.row('bad');bad['payload']['usage']['cached_input_tokens']=101
        p=self.write('sessions/a.jsonl',[self.row(),bad])
        with p.open('a') as f:f.write('{')
        r=self.run_collect()
        self.assertEqual(r['unique_responses'],1)
        self.assertEqual(r['diagnostics']['malformed_lines'],1)
        self.assertIsNone(r['active_processing_seconds'])

    def test_missing_subset_is_unknown(self):
        row=self.row();del row['payload']['usage']['cached_input_tokens']
        self.write('sessions/a.jsonl',[row])
        self.assertIsNone(self.run_collect()['totals']['cached_input_tokens'])

    def test_dst_week_boundary(self):
        cutoff=timestamp('2026-11-02T00:00:00-05:00')
        beginning=week_start(timestamp('2026-11-01T12:00:00-05:00'),self.zone)
        self.assertEqual((cutoff-beginning).total_seconds()/3600,169)

    def test_rejects_shareable_output(self):
        with self.assertRaises(ValueError):output_path('examples/collected.json')

    def test_empty_coverage_explicit(self):
        r=self.run_collect()
        self.assertEqual(r['diagnostics']['missing_source_directories'],2)
        self.assertIsNone(r['ongoing_runs'])

    def test_payload_requests_identity_interval_and_duplicate(self):
        def call(key, when='2026-09-29T12:00:00Z'):
            return {'type':'response_item','timestamp':when,'payload':{'type':'function_call','call_id':key,'name':'mcp__codex_apps__slack_slack_search_public','arguments':'{"query":"PRIVATE BODY"}'}}
        self.write('sessions/a.jsonl',[call('a'),call('old','2026-09-20T12:00:00Z'),call('end',self.end.isoformat())])
        self.write('archived_sessions/a.jsonl',[call('a')])
        self.write('sessions/b.jsonl',[call('wrong')],account='another')
        r=self.run_collect()['payload_activity']
        self.assertEqual(r['sources'],[{'group':'Slack','messages':1}])
        self.assertEqual(r['observed_request_messages'],1)
        self.assertNotIn('PRIVATE BODY',json.dumps(r))


if __name__=='__main__':unittest.main()
