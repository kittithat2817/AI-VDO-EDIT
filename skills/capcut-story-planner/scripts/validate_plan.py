#!/usr/bin/env python3
"""Check a story plan's source mappings. Read-only; no editor or network calls."""
import argparse
import json
import math
from pathlib import Path
import subprocess

PROFILES = Path(__file__).resolve().parents[1] / 'references' / 'profiles.json'


def number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def validate(inventory, plan, check_media=False):
    errors, warnings = [], []
    def need(condition, message):
        if not condition:
            errors.append(message)
    if not isinstance(inventory, dict) or not isinstance(plan, dict):
        return {'valid': False, 'handoff_ready': False, 'sop_complete': False,
                'errors': ['Inventory and plan must be JSON objects'], 'warnings': []}
    need(inventory.get('version') == 1 and plan.get('version') == 1, 'Expected version 1')
    need(bool(inventory.get('project_id')) and inventory.get('project_id') == plan.get('project_id'), 'Project identity mismatch')
    need(bool(inventory.get('timeline_id')), 'Active timeline identity required')
    need(isinstance(plan.get('goal'), str) and bool(plan['goal'].strip()), 'Content goal required')
    need(plan.get('status') in ('ready', 'needs_core_clarification'), 'Invalid plan status')
    profiles = json.loads(PROFILES.read_text(encoding='utf-8'))
    profile = plan.get('profile')
    need(isinstance(profile, str) and profile in profiles, 'Unknown SOP profile')
    assets = {}
    timeline_unknown = set()
    raw_assets = inventory.get('assets', [])
    if not isinstance(raw_assets, list):
        errors.append('assets must be an array')
        raw_assets = []
    for asset in raw_assets:
        if not isinstance(asset, dict):
            errors.append('Asset must be an object')
            continue
        aid = asset.get('asset_id')
        if not isinstance(aid, str) or not aid or aid in assets:
            errors.append('Asset IDs must be nonempty and unique')
            continue
        assets[aid] = asset
        path = asset.get('path')
        need(isinstance(path, str) and Path(path).is_absolute(), f'{aid}: absolute source path required')
        need(asset.get('kind') in ('video', 'audio', 'image'), f'{aid}: invalid kind')
        if asset.get('kind') != 'image':
            need(number(asset.get('duration_seconds')) and asset['duration_seconds'] > 0, f'{aid}: invalid duration')
        origins = asset.get('origins')
        need(isinstance(origins, list) and bool(origins) and all(x in ['media', 'timeline'] for x in origins), f'{aid}: project origin required')
        if isinstance(origins, list) and 'timeline' in origins:
            uses = asset.get('timeline_uses')
            if asset.get('timeline_uses_unknown') is True:
                timeline_unknown.add(aid)
                warnings.append(f'{aid}: original timeline coordinates unresolved')
            elif not isinstance(uses, list) or not uses:
                errors.append(f'{aid}: timeline provenance required or mark timeline_uses_unknown')
            else:
                for use in uses:
                    fields = ['source_in', 'source_out', 'original_timeline_in', 'original_timeline_out']
                    if not isinstance(use, dict) or not all(number(use.get(k)) for k in fields):
                        errors.append(f'{aid}: invalid original timeline coordinates')
                    else:
                        need(0 <= use['source_in'] < use['source_out'] and 0 <= use['original_timeline_in'] < use['original_timeline_out'], f'{aid}: invalid original timeline ranges')
        mids = asset.get('material_ids')
        need(isinstance(mids, list) and bool(mids) and all(isinstance(x, str) and x for x in mids), f'{aid}: material identity required')
    beats = plan.get('beats', [])
    if not isinstance(beats, list):
        errors.append('beats must be an array')
        beats = []
    need(bool(beats), 'At least one primary beat required')
    end, ids, used = 0.0, set(), set()
    for beat in beats:
        if not isinstance(beat, dict):
            errors.append('Beat must be an object')
            continue
        bid = beat.get('id')
        if not isinstance(bid, str) or not bid or bid in ids:
            errors.append('Beat IDs must be nonempty and unique')
        else:
            ids.add(bid)
        label = str(bid)
        for field in ['role', 'summary', 'evidence', 'why_here', 'connects_to_next']:
            need(isinstance(beat.get(field), str) and bool(beat[field].strip()), f'{label}: {field} required')
        aid = beat.get('asset_id')
        asset = assets.get(aid) if isinstance(aid, str) else None
        need(asset is not None, f'{label}: source is outside selected project inventory')
        if asset:
            need(asset.get('kind') == 'video', f'{label}: primary beat requires a source video')
            used.add(aid)
        times = [beat.get(x) for x in ['source_in', 'source_out', 'timeline_in', 'timeline_out']]
        if not all(number(x) for x in times):
            errors.append(f'{label}: finite source and edited times required')
            continue
        si, so, ti, to = times
        need(0 <= si < so, f'{label}: invalid source range')
        need(0 <= ti < to, f'{label}: invalid edited range')
        need(abs(ti - end) <= .001, f'{label}: gap or overlap on edited timeline')
        need(abs((so-si) - (to-ti)) <= .001, f'{label}: mapping must be 1x before downstream retiming')
        if asset and number(asset.get('duration_seconds')):
            need(so <= asset['duration_seconds'] + .001, f'{label}: range exceeds source duration')
        end = to
    constraints = plan.get('editorial_constraints', {})
    if not isinstance(constraints, dict):
        errors.append('editorial_constraints must be an object')
        constraints = {}
    excluded = constraints.get('excluded_spans', [])
    if not isinstance(excluded, list):
        errors.append('excluded_spans must be an array')
        excluded = []
    for span in excluded:
        if not isinstance(span, dict) or not isinstance(span.get('asset_id'), str) or not all(number(span.get(k)) for k in ['source_in','source_out']):
            errors.append('Excluded span requires asset identity and finite source range')
            continue
        need(span['asset_id'] in assets and 0 <= span['source_in'] < span['source_out'], 'Invalid excluded source span')
        need(bool(span.get('reason')) and bool(span.get('evidence')), 'Excluded span requires reason and evidence')
        for beat in beats:
            if isinstance(beat, dict) and beat.get('asset_id') == span['asset_id'] and all(number(beat.get(k)) for k in ['source_in','source_out']):
                need(min(beat['source_out'],span['source_out']) - max(beat['source_in'],span['source_in']) <= .000001, f"{beat.get('id')}: selected range intersects excluded source")
    ending = constraints.get('protected_ending')
    if ending is not None:
        if not isinstance(ending, dict) or not all(number(ending.get(k)) for k in ['source_in','source_out']):
            errors.append('Protected ending requires finite source range')
        else:
            need(isinstance(ending.get('asset_id'), str) and ending['asset_id'] in assets and 0 <= ending['source_in'] < ending['source_out'], 'Invalid protected ending identity or range')
            need(bool(ending.get('required_text')) and bool(ending.get('evidence')), 'Protected ending requires expected text and evidence')
            last = beats[-1] if beats and isinstance(beats[-1], dict) else {}
            need(last.get('asset_id') == ending.get('asset_id') and number(last.get('source_in')) and number(last.get('source_out')) and last['source_in'] <= ending['source_in']+.001 and last['source_out'] >= ending['source_out']-.001, 'Protected ending must be covered by the last primary beat')
    if constraints.get('require_speaker_review') is True:
        reviews = plan.get('speaker_review', [])
        if not isinstance(reviews, list):
            reviews = []
        for beat in beats:
            if not isinstance(beat, dict) or not all(number(beat.get(k)) for k in ['source_in','source_out']):
                continue
            safe = [r for r in reviews if isinstance(r, dict) and r.get('asset_id') == beat.get('asset_id') and r.get('role') in ('presenter','content_guest') and bool(r.get('evidence')) and all(number(r.get(k)) for k in ['source_in','source_out']) and r['source_in'] <= beat['source_in']+.001 and r['source_out'] >= beat['source_out']-.001]
            need(bool(safe), f"{beat.get('id')}: selected speech needs presenter/content-guest review evidence")
    linked = {r.get('asset_id') for r in plan.get('requirements', []) if isinstance(r, dict) and isinstance(r.get('asset_id'), str)} if isinstance(plan.get('requirements'), list) else set()
    groups = plan.get('retake_groups', [])
    if not isinstance(groups, list):
        errors.append('retake_groups must be an array'); groups = []
    group_ids = set()
    for group in groups:
        if not isinstance(group, dict) or not all(number(group.get(k)) for k in ['source_in','source_out']):
            errors.append('Retake group requires finite source bounds'); continue
        gid = group.get('id')
        need(isinstance(gid, str) and bool(gid) and gid not in group_ids, 'Retake group IDs must be nonempty and unique')
        if isinstance(gid, str): group_ids.add(gid)
        aid = group.get('asset_id')
        candidates = group.get('candidates', [])
        if not isinstance(candidates, list) or not candidates:
            errors.append('Retake candidates required'); continue
        good = [c for c in candidates if isinstance(c,dict) and all(number(c.get(k)) for k in ['source_in','source_out']) and group['source_in'] <= c['source_in'] < c['source_out'] <= group['source_out'] and c.get('evidence') and c.get('status') in ['restart','complete','intentional_repetition']]
        need(aid in assets and len(good)==len(candidates), 'Invalid retake candidate identity, bounds or evidence')
        need(len({c.get('id') for c in good})==len(good), 'Retake candidate IDs must be unique')
        chosen = [c for c in good if c.get('id')==group.get('selected_candidate') and c['status'] in ['complete','intentional_repetition']]
        if len(chosen)!=1:
            errors.append('Select one reviewed complete retake candidate'); continue
        selected=chosen[0]
        need(bool(group.get('selection_reason')), 'Retake selection reason required')
        complete=[c for c in good if c['status']=='complete']
        if group.get('policy')=='last_complete' and complete:
            last=max(complete,key=lambda c:c['source_in'])
            need(selected['id']==last['id'] or bool(group.get('override_reason')), 'Earlier complete take requires a meaning/continuity override reason')
        overlaps=[b for b in beats if isinstance(b,dict) and b.get('asset_id')==aid and all(number(b.get(k)) for k in ['source_in','source_out']) and min(b['source_out'],group['source_out'])-max(b['source_in'],group['source_in'])>1e-6]
        need(bool(overlaps), 'Selected retake must appear in the story')
        for b in overlaps:
            need(max(b['source_in'],group['source_in'])>=selected['source_in']-1e-6 and min(b['source_out'],group['source_out'])<=selected['source_out']+1e-6, 'Selected range includes a superseded retake attempt')
        cursor=selected['source_in']
        for b in sorted(overlaps,key=lambda b:b['source_in']):
            if b['source_in']>cursor+1e-6:break
            cursor=max(cursor,b['source_out'])
        need(cursor>=selected['source_out']-1e-6,'Complete retake candidate is truncated or has an internal gap')
    if constraints.get('require_content_review') is True:
        reviews = plan.get('content_review', [])
        if not isinstance(reviews, list):
            errors.append('content_review must be an array'); reviews = []
        reviewed = {}
        for review in reviews:
            if not isinstance(review, dict) or not isinstance(review.get('beat_id'), str):
                errors.append('Content review requires beat identity'); continue
            bid = review['beat_id']
            need(bid in ids and bid not in reviewed, 'Content review beat IDs must be current and unique')
            reviewed[bid] = review
        for i, beat in enumerate(beats):
            if not isinstance(beat, dict): continue
            bid = beat.get('id'); review = reviewed.get(bid, {})
            need(bool(review), f'{bid}: selected beat needs content review')
            need(review.get('asset_id') == beat.get('asset_id') and all(
                number(review.get(k)) and number(beat.get(k)) and abs(review[k]-beat[k]) <= 1e-6
                for k in ('source_in', 'source_out')), f'{bid}: content review source binding is stale')
            need(review.get('decision') in ('keep_distinct', 'selected_take', 'intentional_repetition', 'non_speech'),
                 f'{bid}: selected content decision must be resolved')
            for field in ('meaning', 'evidence', 'reason', 'join_reason'):
                need(isinstance(review.get(field), str) and bool(review[field].strip()), f'{bid}: content review {field} required')
            following = beats[i+1].get('id') if i+1 < len(beats) and isinstance(beats[i+1], dict) else None
            need('next_beat_id' in review and review['next_beat_id'] == following, f'{bid}: content review join is stale')
            matching = {g['id'] for g in groups if isinstance(g, dict) and isinstance(g.get('id'), str)
                        and g.get('asset_id') == beat.get('asset_id')
                        and all(number(obj.get(k)) for obj in (g, beat) for k in ('source_in', 'source_out'))
                        and min(g['source_out'], beat['source_out'])-max(g['source_in'], beat['source_in']) > 1e-6}
            refs = review.get('retake_group_ids', [])
            refs_valid = isinstance(refs, list) and all(isinstance(x, str) for x in refs)
            need(refs_valid and len(refs) == len(set(refs)) and set(refs) == matching,
                 f'{bid}: content review must link exactly its retake groups')
            need((review.get('decision') == 'selected_take') == bool(matching),
                 f'{bid}: selected_take decision must match reviewed alternatives')
    if check_media:
        for aid, asset in assets.items():
            path = asset.get('path')
            if not isinstance(path, str) or not Path(path).is_file():
                (errors if aid in used or aid in linked else warnings).append(f'{aid}: source file unavailable')
                continue
            if aid not in used:
                continue
            try:
                output = subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration:stream=codec_type', '-of', 'json', path], stderr=subprocess.DEVNULL)
                media = json.loads(output)
                duration = float(media['format']['duration'])
                need(any(x.get('codec_type') == 'video' for x in media.get('streams', [])), f'{aid}: primary source has no video stream')
                need(number(duration) and duration > 0, f'{aid}: nonfinite actual media duration')
                for beat in beats:
                    if isinstance(beat, dict) and beat.get('asset_id') == aid and number(beat.get('source_out')):
                        need(beat['source_out'] <= duration + .05, f'{aid}: range exceeds actual media duration')
            except (OSError, subprocess.CalledProcessError, ValueError, KeyError, TypeError):
                errors.append(f'{aid}: ffprobe could not verify duration')
    else:
        warnings.append('Actual files not checked; run --check-media before editing')
    requirements_error_start = len(errors)
    requirements = plan.get('requirements', [])
    if not isinstance(requirements, list):
        errors.append('requirements must be an array')
        requirements = []
    reqs, complete = {}, True
    for req in requirements:
        if not isinstance(req, dict):
            errors.append('Requirement must be an object')
            continue
        rid = req.get('id')
        if not isinstance(rid, str) or not rid or rid in reqs:
            errors.append('Requirement IDs must be unique')
            continue
        reqs[rid] = req
        status, delivery = req.get('status'), req.get('delivery')
        need(status in ('satisfied', 'scheduled', 'missing', 'not_applicable'), f'{rid}: invalid requirement status')
        need(delivery in ('text', 'media', 'spoken', 'none'), f'{rid}: invalid delivery')
        if status in ('scheduled', 'missing'):
            complete = False
            warnings.append(f'{rid}: {status}; keep on editor checklist')
        if status in ('scheduled', 'satisfied'):
            need(delivery != 'none', f'{rid}: actionable delivery required')
            if delivery == 'text':
                need(isinstance(req.get('content'), str) and bool(req['content'].strip()), f'{rid}: text content required')
                need(isinstance(req.get('source_note'), str) and bool(req['source_note'].strip()), f'{rid}: text provenance required')
            elif delivery in ('media', 'spoken'):
                need(isinstance(req.get('asset_id'), str) and req['asset_id'] in assets, f'{rid}: project source required')
        if status == 'missing':
            need(bool(req.get('source_note')), f'{rid}: missing reason required')
    if isinstance(profile, str) and profile in profiles:
        for rid in profiles[profile]['required']:
            need(rid in reqs, f'{rid}: mandatory SOP item omitted')
            need(reqs.get(rid, {}).get('status') != 'not_applicable', f'{rid}: mandatory SOP item cannot be skipped')
    requirements_valid = len(errors) == requirements_error_start and isinstance(profile, str) and profile in profiles
    uncertainties = plan.get('uncertainties', [])
    if not isinstance(uncertainties, list):
        errors.append('uncertainties must be an array')
        uncertainties = []
    core = False
    for item in uncertainties:
        if not isinstance(item, dict):
            errors.append('Uncertainty must be an object')
            continue
        need(item.get('impact') in ('local', 'core') and bool(item.get('description')), 'Uncertainty requires impact and description')
        core = core or item.get('impact') == 'core'
    coverage = inventory.get('coverage', {})
    covered = isinstance(coverage, dict) and coverage.get('media') is True and coverage.get('timeline') is True
    if not covered:
        warnings.append('Media and active timeline discovery must both be complete before handoff')
    handoff = plan.get('handoff', {})
    need(isinstance(handoff, dict) and handoff.get('recipient') == 'capcut-script-edit' and handoff.get('mode') in ('automatic', 'plan_only'), 'Expected capcut-script-edit handoff mode automatic or plan_only')
    timeline_resolved = not (used & timeline_unknown)
    valid = not errors
    return {'valid': valid, 'handoff_ready': valid and check_media and covered and timeline_resolved and not core and plan.get('status') == 'ready' and handoff.get('mode') == 'automatic',
            'sop_complete': requirements_valid and complete, 'duration_seconds': end, 'errors': errors, 'warnings': warnings}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('inventory', type=Path)
    parser.add_argument('plan', type=Path)
    parser.add_argument('--check-media', action='store_true')
    args = parser.parse_args()
    try:
        report = validate(json.loads(args.inventory.read_text(encoding='utf-8')), json.loads(args.plan.read_text(encoding='utf-8')), args.check_media)
    except (OSError, ValueError) as exc:
        report = {'valid': False, 'handoff_ready': False, 'sop_complete': False, 'errors': [str(exc)], 'warnings': []}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report['valid'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
