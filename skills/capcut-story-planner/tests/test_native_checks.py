import importlib.util
from pathlib import Path
import unittest

class NativeChecks(unittest.TestCase):
    def test_superseded_take_cannot_return_on_audio_even_without_copied_exclusion(self):
        p=Path(__file__).resolve().parents[1]/'scripts/verify_native_edit.py'
        spec=importlib.util.spec_from_file_location('retake_native',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        inv={'assets':[{'asset_id':'a','path':'/source/a.mov'}]}
        plan={'native_primary_track_id':'main', 'beats':[{'id':'b','asset_id':'a','source_in':10,'source_out':12,'timeline_in':0,'timeline_out':2}],
              'retake_groups':[{'id':'cta','asset_id':'a','source_in':1,'source_out':12,
                  'candidates':[{'id':'trial','source_in':1,'source_out':3,'status':'restart'},
                                {'id':'final','source_in':10,'source_out':12,'status':'complete'}],
                  'selected_candidate':'final'}]}
        draft={'duration':2000000,'materials':{'videos':[{'id':'v','path':'/source/a.mov'}]},'tracks':[
            {'id':'main','type':'video','segments':[{'material_id':'v','source_timerange':{'start':10000000,'duration':2000000},'target_timerange':{'start':0,'duration':2000000},'volume':1}]},
            {'id':'linked','type':'audio','segments':[{'material_id':'v','source_timerange':{'start':1000000,'duration':2000000},'target_timerange':{'start':0,'duration':2000000},'volume':1}]}]}
        self.assertFalse(m.validate(draft,inv,plan,1000000,60)['valid'])
        draft['tracks'].pop()
        self.assertTrue(m.validate(draft,inv,plan,1000000,60)['valid'])

    def test_native_keyword_must_share_anchor_and_preserve_measured_style(self):
        p=Path(__file__).resolve().parents[1]/'scripts/verify_native_edit.py'
        spec=importlib.util.spec_from_file_location('nlayout',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        import json
        inv={'assets':[{'asset_id':'a','path':'/source/a.mov'}]}
        text={'id':'text','content':json.dumps({'text':'keyword','styles':[{'size':15}]}),'font_size':15,'line_max_width':.82}
        seg={'id':'caption','material_id':'text','target_timerange':{'start':0,'duration':1000000},'clip':{'transform':{'x':0,'y':.58},'scale':{'x':1,'y':1}}}
        plan={'native_primary_track_id':'main','beats':[{'id':'b','asset_id':'a','source_in':0,'source_out':2,'timeline_in':0,'timeline_out':2}],
              'native_caption_layout':{'anchor':{'x':0,'y':-.17},'track_ids':['captions'],'cues':[{'segment_id':'caption','text':'keyword','font_size':15,'scale':{'x':1,'y':1},'line_max_width':.82}]}}
        draft={'duration':2000000,'materials':{'videos':[{'id':'v','path':'/source/a.mov'}],'texts':[text]},'tracks':[{'id':'main','type':'video','segments':[{'material_id':'v','source_timerange':{'start':0,'duration':2000000},'target_timerange':{'start':0,'duration':2000000}}]},{'id':'captions','type':'text','segments':[seg]}]}
        self.assertFalse(m.validate(draft,inv,plan,1000000,60)['valid'])
        seg['clip']['transform']['y']=-.17
        self.assertTrue(m.validate(draft,inv,plan,1000000,60)['valid'])
        text['font_size']=25
        self.assertFalse(m.validate(draft,inv,plan,1000000,60)['valid'])
        text['font_size']=15
        expected=plan['native_caption_layout']['cues'][0]
        expected['material_fields']={'font_path':'/measured.ttf','letter_spacing':0}
        text.update(font_path='/wrong.ttf',letter_spacing=0)
        self.assertFalse(m.validate(draft,inv,plan,1000000,60)['valid'])
        text['font_path']='/measured.ttf'
        plan['native_caption_layout']['static_anchor']=True
        seg['common_keyframes']=[{'property_type':'position'}]
        self.assertFalse(m.validate(draft,inv,plan,1000000,60)['valid'])

    def test_written_native_must_preserve_source_identity_and_ending(self):
        p=Path(__file__).resolve().parents[1]/'scripts/verify_native_edit.py'
        spec=importlib.util.spec_from_file_location('native_checks',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        inv={'assets':[{'asset_id':'a','path':'/source/a.mov'}]}
        plan={'native_primary_track_id':'main','beats':[{'id':'b1','asset_id':'a','source_in':3,'source_out':5,'timeline_in':0,'timeline_out':2}]}
        draft={'duration':2000000,'materials':{'videos':[{'id':'v','path':'/wrong.mov'}]},'tracks':[{'id':'main','segments':[{'material_id':'v','source_timerange':{'start':3000000,'duration':2000000},'target_timerange':{'start':0,'duration':2000000},'volume':1}]}]}
        self.assertFalse(m.validate(draft,inv,plan,1000000,60)['valid'])
        draft['materials']['videos'][0]['path']='/source/a.mov'
        self.assertTrue(m.validate(draft,inv,plan,1000000,60)['valid'])
        draft['duration']=3000000
        self.assertFalse(m.validate(draft,inv,plan,1000000,60)['valid'])

    def test_excluded_prompt_on_additional_audio_track_is_rejected(self):
        p=Path(__file__).resolve().parents[1]/'scripts/verify_native_edit.py'
        spec=importlib.util.spec_from_file_location('nc2',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        inv={'assets':[{'asset_id':'a','path':'/source/a.mov'},{'asset_id':'crew','path':'/source/crew.mov'}]}
        plan={'native_primary_track_id':'main','beats':[{'id':'b1','asset_id':'a','source_in':3,'source_out':5,'timeline_in':0,'timeline_out':2}], 'editorial_constraints':{'excluded_spans':[{'asset_id':'crew','source_in':10,'source_out':12}]}}
        draft={'duration':2000000,'materials':{'videos':[{'id':'v','path':'/source/a.mov'}],'audios':[{'id':'voice','path':'/source/crew.mov'}]},'tracks':[{'id':'main','type':'video','segments':[{'material_id':'v','source_timerange':{'start':3000000,'duration':2000000},'target_timerange':{'start':0,'duration':2000000},'volume':1}]},{'id':'extra','type':'audio','segments':[{'material_id':'voice','source_timerange':{'start':10000000,'duration':2000000},'target_timerange':{'start':0,'duration':2000000},'volume':1}]}]}
        self.assertFalse(m.validate(draft,inv,plan,1000000,60)['valid'])

if __name__=='__main__':unittest.main()
