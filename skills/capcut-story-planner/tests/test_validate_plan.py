import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'validate_plan.py'
spec = importlib.util.spec_from_file_location('validator', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class StoryPlanChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name)
        for name, color in [('a', 'red'), ('b', 'green'), ('c', 'blue')]:
            subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', f'color=c={color}:s=16x16:r=10:d=1', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', str(cls.root / f'{name}.mp4')], check=True)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def setUp(self):
        self.inventory = {'version': 1, 'project_id': 'test-project', 'timeline_id': 'timeline-1', 'coverage': {'media': True, 'timeline': True},
            'assets': [{'asset_id': name, 'path': str(self.root / f'{name}.mp4'), 'kind': 'video', 'duration_seconds': 1., 'material_ids': [name+'-material'], 'origins': ['media']} for name in ['a','b','c']]}
        self.plan = {'version': 1, 'project_id': 'test-project', 'profile': 'general', 'goal': 'Explain one idea through evidence to a conclusion', 'status': 'ready', 'beats': [], 'requirements': [], 'uncertainties': [], 'omissions': [], 'handoff': {'recipient': 'capcut-script-edit', 'mode': 'automatic'}}
        for i, (name, role) in enumerate([('b','hook'),('c','evidence'),('a','conclusion')]):
            self.plan['beats'].append({'id': str(i), 'asset_id': name, 'role': role, 'source_in': .1, 'source_out': .3, 'timeline_in': i*.2, 'timeline_out': (i+1)*.2, 'summary': 'test source segment', 'evidence': 'synthetic fixture', 'why_here': 'supports sequence', 'connects_to_next': 'reasoned continuation or closure'})

    def check(self, media=True):
        return module.validate(self.inventory, self.plan, media)

    def test_three_sources_work_in_story_order_without_sorting(self):
        before = copy.deepcopy(self.plan)
        result = self.check()
        self.assertTrue(result['valid'], result)
        self.assertTrue(result['handoff_ready'], result)
        self.assertAlmostEqual(result['duration_seconds'], .6)
        self.assertEqual(self.plan, before)
        self.assertEqual([x['asset_id'] for x in self.plan['beats']], ['b','c','a'])

    def test_file_and_source_range_must_match_actual_media(self):
        self.inventory['assets'][1]['duration_seconds'] = 100
        self.plan['beats'] = [dict(self.plan['beats'][0], source_out=5., timeline_out=4.9)]
        self.assertFalse(self.check()['valid'])
        self.inventory['assets'][1]['path'] = str(self.root/'missing.mp4')
        self.assertFalse(self.check()['handoff_ready'])

    def test_foreign_source_and_wrong_project_are_rejected(self):
        self.plan['beats'][0]['asset_id'] = 'outside-project'
        self.assertFalse(self.check()['valid'])
        self.plan['project_id'] = 'different-project'
        self.assertFalse(self.check()['valid'])

    def test_edited_overlap_is_rejected(self):
        self.plan['beats'][1]['timeline_in'] = .1
        self.plan['beats'][1]['timeline_out'] = .3
        self.assertFalse(self.check()['valid'])

    def test_core_uncertainty_blocks_handoff_but_local_does_not(self):
        self.plan['uncertainties'] = [{'impact': 'local', 'description': 'Unused take has an unclear word'}]
        self.assertTrue(self.check()['handoff_ready'])
        self.plan['uncertainties'][0]['impact'] = 'core'
        self.assertTrue(self.check()['valid'])
        self.assertFalse(self.check()['handoff_ready'])

    def test_incomplete_discovery_or_unchecked_media_not_ready(self):
        self.assertFalse(self.check(False)['handoff_ready'])
        self.inventory['coverage']['media'] = False
        self.assertFalse(self.check()['handoff_ready'])

    def test_missing_sop_stays_on_checklist_without_blocking_assembly(self):
        self.plan['profile'] = 'hamhang-experiment'
        self.assertFalse(self.check()['valid'])
        for rid in ['non_drinking', 'approval_notice', 'product_mark', 'product_note']:
            self.plan['requirements'].append({'id': rid, 'status': 'missing', 'delivery': 'none', 'source_note': 'Not yet present in current project'})
        result = self.check()
        self.assertTrue(result['handoff_ready'], result)
        self.assertFalse(result['sop_complete'])
        self.plan['requirements'][0]['status'] = 'not_applicable'
        self.assertFalse(self.check()['valid'])

    def test_broken_unused_asset_does_not_block_clear_content(self):
        self.inventory['assets'].append({'asset_id': 'unused', 'path': str(self.root/'missing.mp4'), 'kind': 'video', 'duration_seconds': 1., 'material_ids': ['unused-material'], 'origins': ['timeline'], 'timeline_uses_unknown': True})
        result = self.check()
        self.assertTrue(result['handoff_ready'], result)
        self.assertTrue(result['warnings'])

    def test_invalid_json_shapes_are_reported_without_crashing(self):
        self.plan['beats'] = {'invalid': True}
        self.assertFalse(self.check()['valid'])
        self.plan['status'] = []
        self.assertFalse(self.check()['valid'])

    def test_confirmed_excluded_source_is_never_selected(self):
        self.plan['editorial_constraints'] = {'excluded_spans': [{'asset_id': 'b', 'source_in': .2, 'source_out': .25, 'reason': 'production prompt', 'evidence': 'user-confirmed fixture'}]}
        self.assertFalse(self.check()['valid'])

    def test_retake_selection_cannot_drag_in_a_superseded_attempt(self):
        self.plan['beats'] = [self.plan['beats'][0]]
        self.plan['retake_groups'] = [{'id':'restart','asset_id':'b','source_in':.1,'source_out':.3,
            'candidates':[{'id':'first','source_in':.1,'source_out':.2,'status':'restart','evidence':'reviewed source'},
                          {'id':'last','source_in':.2,'source_out':.3,'status':'complete','evidence':'reviewed full final delivery'}],
            'selected_candidate':'last','selection_reason':'last complete rendition','policy':'last_complete'}]
        self.assertFalse(self.check(False)['valid'])
        self.plan['beats'][0].update(source_in=.2,timeline_out=.1)
        self.assertTrue(self.check(False)['valid'])
        self.plan['beats'][0].update(source_in=.21,timeline_out=.09)
        self.assertFalse(self.check(False)['valid'])

    def test_protected_ending_must_be_kept_as_last_source(self):
        self.plan['editorial_constraints'] = {'protected_ending': {'asset_id': 'c', 'source_in': .1, 'source_out': .3, 'required_text': 'closing line', 'evidence': 'confirmed source'}}
        self.assertFalse(self.check()['valid'])

    def test_semantic_qc_requires_current_review_of_every_selected_beat_and_join(self):
        self.plan['editorial_constraints'] = {'require_content_review': True}
        self.assertFalse(self.check(False)['valid'])
        self.plan['content_review'] = [
            {'beat_id': b['id'], 'asset_id': b['asset_id'],
             'source_in': b['source_in'], 'source_out': b['source_out'],
             'decision': 'keep_distinct', 'meaning': 'Different contribution to the argument',
             'evidence': 'Reviewed original context and adjacent rendition',
             'reason': 'Adds information rather than repeating a trial delivery',
             'next_beat_id': self.plan['beats'][i+1]['id'] if i+1 < len(self.plan['beats']) else None,
             'join_reason': 'Continues the argument or closes it without restarting the same thought'}
            for i,b in enumerate(self.plan['beats'])]
        self.assertTrue(self.check(False)['valid'])
        self.plan['content_review'][1]['source_in'] = .15
        self.assertFalse(self.check(False)['valid'])
        self.plan['content_review'][1]['source_in'] = .1
        self.plan['content_review'][0]['next_beat_id'] = '2'
        self.assertFalse(self.check(False)['valid'])

    def test_content_review_must_link_the_selected_complete_alternative(self):
        self.plan['beats'] = [dict(self.plan['beats'][0], source_in=.2, timeline_out=.1)]
        self.plan['editorial_constraints'] = {'require_content_review': True}
        self.plan['retake_groups'] = [{'id':'thought','asset_id':'b','source_in':.1,'source_out':.3,
            'candidates':[{'id':'trial','source_in':.1,'source_out':.2,'status':'restart','evidence':'QC'},
                          {'id':'complete','source_in':.2,'source_out':.3,'status':'complete','evidence':'QC'}],
            'selected_candidate':'complete','selection_reason':'Complete thought and clean continuation','policy':'last_complete'}]
        review = {'beat_id':'0','asset_id':'b','source_in':.2,'source_out':.3,
                  'decision':'selected_take','meaning':'One complete thought','evidence':'User QC and source context',
                  'reason':'Trial and final are alternatives, not question and answer',
                  'next_beat_id':None,'join_reason':'Closes the thought'}
        self.plan['content_review'] = [review]
        self.assertFalse(self.check(False)['valid'])
        review['retake_group_ids'] = ['thought']
        self.assertTrue(self.check(False)['valid'])
        review['decision'] = 'keep_distinct'
        self.assertFalse(self.check(False)['valid'])

    def test_speech_selection_requires_evidence_for_presenter_role(self):
        self.plan['editorial_constraints'] = {'require_speaker_review': True}
        self.assertFalse(self.check()['valid'])

    def test_previous_editor_recipient_is_rejected(self):
        self.plan['handoff']['recipient'] = 'capcut-director'
        self.assertFalse(self.check()['valid'])

    def test_plan_only_never_invokes_automatic_handoff(self):
        self.plan['handoff']['mode'] = 'plan_only'
        result = self.check()
        self.assertTrue(result['valid'], result)
        self.assertFalse(result['handoff_ready'])

    def test_timeline_provenance_cannot_be_silently_omitted(self):
        self.inventory['assets'][1]['origins'] = ['media', 'timeline']
        self.assertFalse(self.check()['valid'])
        self.inventory['assets'][1]['timeline_uses_unknown'] = True
        self.assertTrue(self.check()['valid'])
        self.assertFalse(self.check()['handoff_ready'])
        del self.inventory['assets'][1]['timeline_uses_unknown']
        self.inventory['assets'][1]['timeline_uses'] = [{'source_in': 0., 'source_out': 1., 'original_timeline_in': 5., 'original_timeline_out': 6.}]
        self.assertTrue(self.check()['handoff_ready'])

    def test_media_failure_does_not_reclassify_sop_completeness(self):
        self.inventory['assets'][0]['path'] = str(self.root/'absent.mp4')
        result = self.check()
        self.assertFalse(result['valid'])
        self.assertFalse(result['handoff_ready'])
        self.assertTrue(result['sop_complete'])

    def test_cli_reads_files_and_returns_machine_result(self):
        ip, pp = self.root/'inventory.json', self.root/'plan.json'
        ip.write_text(json.dumps(self.inventory))
        pp.write_text(json.dumps(self.plan))
        proc = subprocess.run(['python3', str(SCRIPT), str(ip), str(pp), '--check-media'], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(json.loads(proc.stdout)['handoff_ready'])


if __name__ == '__main__':
    unittest.main()
