#!/usr/bin/env python3
"""Check explicit selective-caption policies; never edits media or drafts."""
import argparse,json,math,os,re,tempfile
from pathlib import Path
os.environ.setdefault('PYTHAINLP_DATA',str(Path(tempfile.gettempdir())/'capcut-planner-thai-data'))
os.environ.setdefault('PYTHAINLP_OFFLINE','1')

def units(text,terms):
    from pythainlp.tokenize import word_tokenize
    from pythainlp.corpus import thai_words
    from pythainlp.util import Trie
    dictionary=Trie(set(thai_words())|set(terms))
    return [x for x in word_tokenize(text,engine='newmm',custom_dict=dictionary,keep_whitespace=False) if any(c.isalnum() for c in x)]

def validate(cues,profile):
    errors=[];warnings=[];details=[]
    if not isinstance(cues,list) or not isinstance(profile,dict):
        return {'valid':False,'errors':['Expected cue array and profile object'],'warnings':[],'cues':[]}
    terms=profile.get('terms',[])
    limit=profile.get('max_words',5);target=profile.get('target_words',4)
    for i,c in enumerate(cues):
        if not isinstance(c,dict) or not isinstance(c.get('text'),str):
            errors.append(f'cue {i}: text required');continue
        role=c.get('role','main')
        start,end=c.get('start'),c.get('end')
        if not all(isinstance(x,(float,int)) and not isinstance(x,bool) and math.isfinite(x) for x in [start,end]) or not 0<=start<end:
            errors.append(f'cue {i}: invalid timing');continue
        if role=='sop':continue
        if profile.get('max_lines')==1:
            if any(ch in c['text'] for ch in '\n\r\u2028\u2029'):errors.append(f'cue {i}: single-line text contains a hard break')
            layout=c.get('layout',{})
            if profile.get('require_layout_evidence'):
                numbers=[layout.get('width'),layout.get('available_width')]
                if not all(isinstance(x,(float,int)) and not isinstance(x,bool) and math.isfinite(x) and x>0 for x in numbers) or layout.get('text')!=c['text'] or not layout.get('method'):
                    errors.append(f'cue {i}: current text needs measured layout evidence')
                elif layout['width']>layout['available_width'] or layout.get('estimated_lines')!=1:
                    errors.append(f'cue {i}: text exceeds measured single-line bounds')
        words=units(c['text'],terms);n=len(words)
        if profile.get('mode')=='selective':
            if role=='keyword' and n!=1:errors.append(f'cue {i}: keyword must contain one lexical term')
            if role!='keyword' and n>limit:errors.append(f'cue {i}: {n} words exceeds {limit}')
            elif role!='keyword' and n>target:warnings.append(f'cue {i}: exceptional {n}-word cue; review readability')
            if not c.get('purpose'):errors.append(f'cue {i}: selective cue needs editorial purpose')
        details.append({'index':i,'text':c['text'],'role':role,'units':words,'count':n,'duration':round(end-start,3)})
    for i,a in enumerate(cues):
        if not isinstance(a,dict):continue
        for b in cues[i+1:]:
            if not isinstance(b,dict) or a.get('role','main')=='sop' or b.get('role','main')=='sop':continue
            if all(isinstance(x,(int,float)) for x in [a.get('start'),a.get('end'),b.get('start'),b.get('end')]) and min(a['end'],b['end'])>max(a['start'],b['start']) and a.get('text')==b.get('text'):
                errors.append('Duplicate overlapping caption/keyword text')
    return {'valid':not errors,'errors':errors,'warnings':warnings,'cues':details,'counting':'PyThaiNLP newmm plus explicit named-term dictionary; whitespace and ASR subwords are not word counts'}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('cues',type=Path);p.add_argument('profile',type=Path);a=p.parse_args()
    try:result=validate(json.loads(a.cues.read_text()),json.loads(a.profile.read_text()))
    except (OSError,ValueError,ImportError) as e:result={'valid':False,'errors':[str(e)]}
    print(json.dumps(result,ensure_ascii=False,indent=2));return 0 if result['valid'] else 1
if __name__=='__main__':raise SystemExit(main())
