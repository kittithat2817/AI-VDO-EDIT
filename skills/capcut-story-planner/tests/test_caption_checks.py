from pathlib import Path
import importlib.util
import unittest

class CaptionChecks(unittest.TestCase):
    def test_single_line_policy_rejects_breaks_and_overwide_short_text(self):
        p=Path(__file__).resolve().parents[1]/'scripts/validate_captions.py'
        spec=importlib.util.spec_from_file_location('layout_checks',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        profile={'mode':'selective','max_lines':1,'require_layout_evidence':True}
        cue={'text':'ก่อน\nดื่ม','role':'main','start':0,'end':2,'purpose':'usage',
             'layout':{'text':'ก่อน\nดื่ม','method':'known-font shaping','estimated_lines':1,'width':40,'available_width':100}}
        self.assertFalse(m.validate([cue],profile)['valid'])
        cue.update(text='ก่อนดื่ม');cue['layout'].update(text=cue['text'],width=120)
        self.assertFalse(m.validate([cue],profile)['valid'])
        cue['layout']['width']=90
        self.assertTrue(m.validate([cue],profile)['valid'])

    def test_legacy_long_cue_fails_selective_profile(self):
        p=Path(__file__).resolve().parents[1]/'scripts/validate_captions.py'
        spec=importlib.util.spec_from_file_location('caption_checks',p)
        m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        result=m.validate([{'text':'เวลาที่พวกมึงกินเหล้าเข้าไปในร่างกายนะเนี่ย','role':'main','start':0,'end':3}],{'mode':'selective','target_words':4,'max_words':5,'terms':['แฮมแฮงค์']})
        self.assertFalse(result['valid'])

    def test_keywords_and_sop_are_distinct_from_main_caption_limit(self):
        p=Path(__file__).resolve().parents[1]/'scripts/validate_captions.py'
        spec=importlib.util.spec_from_file_location('cc2',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        policy={'mode':'selective','target_words':4,'max_words':5,'terms':['แฮมแฮงค์','อะเซทัลดีไฮด์']}
        cues=[{'text':'แฮมแฮงค์','role':'keyword','start':0,'end':1,'purpose':'brand'}, {'text':'ข้อความหมายเหตุผลิตภัณฑ์ที่ต้องรักษาครบทุกคำตาม SOP','role':'sop','start':0,'end':5}]
        self.assertTrue(m.validate(cues,policy)['valid'])
        cues[0]['text']='กินเข้าไปทั้งวันทั้งคืน'
        self.assertFalse(m.validate(cues,policy)['valid'])

    def test_closing_phrase_counts_real_thai_words(self):
        p=Path(__file__).resolve().parents[1]/'scripts/validate_captions.py'
        spec=importlib.util.spec_from_file_location('cc3',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        words=m.units('มีแฮม ไม่มีแฮงค์',['แฮม','แฮงค์'])
        self.assertEqual(words,['มี','แฮม','ไม่','มี','แฮงค์'])

    def test_sop_exemption_does_not_allow_invalid_timing(self):
        p=Path(__file__).resolve().parents[1]/'scripts/validate_captions.py'
        spec=importlib.util.spec_from_file_location('cc4',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        self.assertFalse(m.validate([{'role':'sop','text':'หมายเหตุ','start':-3,'end':-2}],{'mode':'selective'})['valid'])

if __name__=='__main__':unittest.main()
