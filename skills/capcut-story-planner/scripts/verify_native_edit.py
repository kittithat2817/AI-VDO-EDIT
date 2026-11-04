#!/usr/bin/env python3
"""Read-back check against an independent plan, after native timebase is verified."""
import argparse,json
from pathlib import Path

def validate(draft,inventory,plan,timebase,fps):
    errors=[];mapping=[]
    if timebase<=0 or fps<=0:return {'valid':False,'errors':['Verified positive timebase and FPS required']}
    eps=1/fps+1/timebase
    assets={a['asset_id']:a for a in inventory['assets']}
    excluded_spans = list(plan.get('editorial_constraints',{}).get('excluded_spans',[]))
    for group in plan.get('retake_groups', []):
        selected = [c for c in group['candidates'] if c['id'] == group.get('selected_candidate')]
        if len(selected) != 1:
            errors.append('Retake group has no unique selected candidate'); continue
        chosen = selected[0]
        for candidate in group['candidates']:
            if candidate['id'] == chosen['id']: continue
            # Alternatives can overlap; reject only the portion outside the chosen take.
            for a,z in ((candidate['source_in'], min(candidate['source_out'], chosen['source_in'])),
                        (max(candidate['source_in'], chosen['source_out']), candidate['source_out'])):
                if z > a:
                    excluded_spans.append({'asset_id':group['asset_id'], 'source_in':a, 'source_out':z})
    materials={m['id']:m for arr in draft['materials'].values() if isinstance(arr,list) for m in arr if isinstance(m,dict) and 'id' in m}
    tracks=[t for t in draft['tracks'] if t.get('id')==plan.get('native_primary_track_id')]
    if len(tracks)!=1:return {'valid':False,'errors':['Primary track identity not resolved']}
    segments=tracks[0]['segments'];beats=plan['beats']
    if len(segments)!=len(beats):errors.append('Native primary segments do not match plan')
    for b,s in zip(beats,segments):
        material=materials.get(s.get('material_id'),{});expected=assets.get(b['asset_id'],{})
        if material.get('path')!=expected.get('path'):errors.append(f"{b['id']}: wrong native source identity")
        sr=s.get('source_timerange') or {};tr=s.get('target_timerange') or {}
        actual=[sr.get('start',-timebase)/timebase,(sr.get('start',0)+sr.get('duration',0))/timebase,tr.get('start',-timebase)/timebase,(tr.get('start',0)+tr.get('duration',0))/timebase]
        wanted=[b['source_in'],b['source_out'],b['timeline_in'],b['timeline_out']]
        if any(abs(a-w)>eps for a,w in zip(actual,wanted)):errors.append(f"{b['id']}: native source/target range changed from plan")
        if s.get('volume',1)<=0 or s.get('speed',1)!=1:errors.append(f"{b['id']}: primary dialogue muted or unexpectedly retimed")
        mapping.append({'beat_id':b['id'],'segment_id':s.get('id'),'asset_id':b['asset_id'],'path':material.get('path'),'source_in':actual[0],'source_out':actual[1],'timeline_in':actual[2],'timeline_out':actual[3]})
    primary_end=max((x['target_timerange']['start']+x['target_timerange']['duration'] for x in segments),default=0)/timebase
    if abs(draft.get('duration',0)/timebase-primary_end)>eps:errors.append('Draft duration extends beyond primary ending or truncates it')
    for t in draft['tracks']:
        for s in t.get('segments',[]):
            tr=s.get('target_timerange') or {};end=(tr.get('start',0)+tr.get('duration',0))/timebase
            if end>primary_end+eps:errors.append('Overlay/audio/effect extends past intended primary ending')
            if t.get('type') in ('video','audio') and s.get('volume',1)>0:
                sr=s.get('source_timerange') or {};path=materials.get(s.get('material_id'),{}).get('path')
                a=sr.get('start',0)/timebase;z=a+sr.get('duration',0)/timebase
                for excluded in excluded_spans:
                    blocked=assets.get(excluded.get('asset_id'),{}).get('path')
                    if path and path==blocked and min(z,excluded['source_out'])-max(a,excluded['source_in'])>1/timebase:
                        errors.append('Audible native source intersects excluded prompt or superseded take range')
    layout=plan.get('native_caption_layout')
    if layout:
        expected={c['segment_id']:c for c in layout['cues']}
        native=[s for t in draft['tracks'] if t['id'] in layout['track_ids'] for s in t['segments']]
        if {s.get('id') for s in native}!=set(expected):errors.append('Native caption layout coverage differs from plan')
        for s in native:
            c=expected.get(s.get('id'))
            if c is None:continue
            mat=materials.get(s['material_id'],{});content=json.loads(mat.get('content','{}'));clip=s.get('clip',{})
            if any(abs(clip.get('transform',{}).get(k,999)-layout['anchor'][k])>1e-6 for k in ('x','y')):errors.append('Native caption/keyword uses a different anchor')
            if content.get('text')!=c['text'] or any(ch in content.get('text','') for ch in '\n\r\u2028\u2029'):errors.append('Native caption text breaks single-line contract')
            if mat.get('font_size')!=c['font_size'] or mat.get('line_max_width')!=c['line_max_width'] or clip.get('scale')!=c['scale'] or any(st.get('size')!=c['font_size'] for st in content.get('styles',[])):errors.append('Native text style differs from measured layout')
            if any(mat.get(k)!=v for k,v in c.get('material_fields',{}).items()) or ('content_styles' in c and content.get('styles')!=c['content_styles']):errors.append('Native font/spacing/box/color differs from layout evidence')
            tr=s.get('target_timerange',{})
            if 'target_timerange' in c and tr!=c['target_timerange']:errors.append('Native caption timing differs from approved cue')
            if layout.get('static_anchor') and (s.get('common_keyframes') or s.get('keyframe_refs')):errors.append('Static caption anchor contains unreviewed keyframes')
            if layout.get('static_anchor') and any(ref in {x['id'] for x in draft['materials'].get('material_animations',[])} for ref in s.get('extra_material_refs',[])):errors.append('Position-sensitive captions retain unreviewed animation')
        for i,a in enumerate(native):
            ar=a['target_timerange']
            for b in native[i+1:]:
                br=b['target_timerange']
                if min(ar['start']+ar['duration'],br['start']+br['duration'])-max(ar['start'],br['start'])>1:errors.append('Captions overlap at their shared anchor')
    return {'valid':not errors,'errors':errors,'source_to_edited':mapping,'duration_seconds':primary_end,'limitations':['File read-back checks mapping and measured layout bindings, not native app playback or speaker identity. Validate editorial source and typography evidence separately.']}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('draft',type=Path);p.add_argument('inventory',type=Path);p.add_argument('plan',type=Path);p.add_argument('--timebase',type=float,required=True);p.add_argument('--fps',type=float,required=True);a=p.parse_args()
    try:result=validate(json.loads(a.draft.read_text()),json.loads(a.inventory.read_text()),json.loads(a.plan.read_text()),a.timebase,a.fps)
    except (OSError,ValueError,KeyError,TypeError) as e:result={'valid':False,'errors':[str(e)]}
    print(json.dumps(result,ensure_ascii=False,indent=2));return 0 if result['valid'] else 1
if __name__=='__main__':raise SystemExit(main())
