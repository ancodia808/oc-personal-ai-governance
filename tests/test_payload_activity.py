import json
import unittest
from scripts.payload_activity import summarize_request, aggregate_requests
from scripts.render_review import render
from tests.test_renderer import fixture


class PayloadTests(unittest.TestCase):
    def test_wrapper_groups_once_and_redacts_url(self):
        call = {'name': 'exec', 'input': 'await tools.web__run({open:[{ref_id:"https://docs.example.org/private/file?secret=abc"},{ref_id:"https://docs.example.org/other"}]}); await tools.mcp__codex_apps__slack_slack_send_message({channel_id:"SECRET",message:"SECRET"});'}
        groups = summarize_request(call, '/work/demo')
        self.assertEqual(groups, {('sources', 'Website: docs.example.org'), ('destinations', 'Slack')})
        result = aggregate_requests({'id': groups}, set())
        self.assertNotIn('SECRET', json.dumps(result))
        self.assertNotIn('private/file', json.dumps(result))
        self.assertEqual(result['sources'][0]['messages'], 1)

    def test_local_and_unsupported(self):
        call = {'name':'exec_command','arguments':json.dumps({'cmd':'Get-Content docs/guide.md','workdir':'/work/demo'})}
        self.assertEqual(summarize_request(call,'/other'), {('sources','Local project directory: demo')})
        call['arguments']=json.dumps({'cmd':'Get-Content ../secret.txt'})
        self.assertEqual(summarize_request(call,'/work/demo'),set())
        self.assertEqual(summarize_request({'name':'exec','input':'await tools.web__run(dynamicArgs);'},'/work/demo'),set())

    def test_sort_conflict_unknown_and_render_escape(self):
        r=aggregate_requests({'a':{('sources','Zulu')},'b':{('sources','Zulu')},'c':{('sources','<script>')},'d':set(),'e':{('sources','Excluded')}},{'e'})
        self.assertEqual([x['messages'] for x in r['sources']],[2,1])
        self.assertEqual(r['unclassified_request_messages'],1)
        d=fixture();d['payload_activity']=r
        page,summary=render(d,'private/test.html')
        self.assertNotIn('<script>',page)
        self.assertIn('&lt;script&gt;',page)
        self.assertLess(summary.index('Zulu: 2'),summary.index('&lt;script&gt;: 1'))

    def test_old_snapshot_unavailable(self):
        self.assertIn('Unavailable in this snapshot',render(fixture(),'private/test.html')[0])

    def test_legacy_website_destinations_without_post_evidence_filtered(self):
        d=fixture()
        d['payload_activity']=aggregate_requests({'a':{('sources','Website: example.org'),('destinations','Website: example.org')},'b':{('destinations','Slack')}},set())
        page,summary=render(d,'private/test.html')
        for output in (page,summary):
            self.assertIn('External Sources (requested)',output)
            self.assertIn('External Destinations (posted)',output)
            self.assertEqual(output.count('Website: example.org'),1)
            self.assertIn('Slack',output)

    def test_external_readout_and_unknown_search_provider(self):
        groups=summarize_request({'name':'exec','input':'await tools.web__run({search_query:[{q:"test",domains:["filter.example.org"]}]});'},'/work/demo')
        self.assertFalse(any('filter.example.org' in label for _,label in groups))
        r=aggregate_requests({'a':groups,'b':{('sources','Codex app'),('destinations','Local project directory: PRIVATE_FOLDER')},'c':{('sources','Slack')}},set())
        d=fixture();d['payload_activity']=r
        page,summary=render(d,'private/test.html')
        for output in (page,summary):
            self.assertNotIn('PRIVATE_FOLDER',output)
            self.assertNotIn('Web search service (queries)',output)
            self.assertIn('unidentified provider hostname: 1',output)
            self.assertIn('Slack',output)


if __name__=='__main__': unittest.main()
