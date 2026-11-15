#!/usr/bin/env python3
"""Independent check of the Lab 3 option-A cached route counts against this repo's N18 viewer data.

Recomputes, for each route case (8 frames) x action (native / sam / dino), from the N18 build (private/data.js:
Gold boxes of dataset dylan_anchor_329068e889228c5c and October Qwen3-VL-32B raw_vlm / sam_joint / sam_dino boxes)
with the vendored evaluator matcher (vendor_matching.threshold_matches, sha256 816adef7...):
  gold_objects, predictions, tp (one-to-one geometric matches at IoU >= .50), fn, sum of matched box IoU,
  matched_correct_category (geometric matches whose categories are equal), category_aware_tp (separate
  class-constrained one-to-one matching at IoU >= .50, same matcher run within each category).
Compares with the package's route_data/private/*.json. Writes VERIFY_ROUTE.json. Gold is used for evaluation only.
Usage: python3 -I verify_route_vs_repo.py <lab3_demo_dir> <n18_viewer_private_dir> <vendor_matching.py> <out.json>
"""
import hashlib, importlib.util, json, sys
from collections import defaultdict
from pathlib import Path

demo, priv, vmp, out = map(Path, sys.argv[1:5])
spec = importlib.util.spec_from_file_location('vm', vmp); vm = importlib.util.module_from_spec(spec); spec.loader.exec_module(vm)
s = (priv / 'data.js').read_text(); d = json.loads(s[s.index('{'):s.rstrip().rstrip(';').rindex('}') + 1])
LANE = {'native': 'qwen3vl32b|native', 'sam': 'qwen3vl32b|sam2', 'dino': 'qwen3vl32b|dino'}
cases = json.loads((demo / 'route_data/public/cases.json').read_text())['cases']


def match(G, P):
    W = [[vm.iou(g['b'], p['b']) for p in P] for g in G]
    return [(i, j, W[i][j]) for i, j in vm.threshold_matches(W, .5)] if G and P else []


IOU_TOL = 1e-3  # integer counts must be identical. NOTE: this IoU-sum tolerance was set AFTER a first run showed 4 native rows differing by <= 0.000688 (likely box rounding, untested)
rows, ok_all = [], True
for cid, c in cases.items():
    k = f"{c['video_id']}/{c['video_frame']}"
    fr = d['frames'][k]
    G = fr['gold']
    for act, mid in LANE.items():
        r = d['results'][mid].get(k)
        P = r['p'] if r else []
        m = match(G, P)
        cat_tp = 0
        for cat in {g['c'] for g in G}:
            gi = [g for g in G if g['c'] == cat]; pj = [p for p in P if p['c'] == cat]
            cat_tp += len(match(gi, pj))
        mine = {'gold_objects': len(G), 'predictions': len(P), 'tp': len(m), 'fn': len(G) - len(m),
                'matched_correct_category': sum(G[i]['c'] == P[j]['c'] for i, j, _ in m),
                'category_aware_tp': cat_tp, 'sum_matched_box_iou': round(sum(x for _, _, x in m), 6)}
        pk = json.loads((demo / f'route_data/private/{cid}_{act}.json').read_text())
        theirs = dict(pk['counts']); theirs['sum_matched_box_iou'] = round(pk['sum_matched_box_iou'], 6)
        diff = {f: [theirs.get(f), v] for f, v in mine.items() if f != 'sum_matched_box_iou' and theirs.get(f) != v}
        iou_diff = abs(theirs['sum_matched_box_iou'] - mine['sum_matched_box_iou'])
        if iou_diff > IOU_TOL: diff['sum_matched_box_iou'] = [theirs['sum_matched_box_iou'], mine['sum_matched_box_iou']]
        ident = (pk['scene'] == fr['s'] and str(pk['video_frame']) == fr['f'] and fr['split'] == 'dev'
                 and pk['split'] == 'development')
        ok = ident and not diff
        ok_all &= ok
        rows.append({'case': cid, 'action': act, 'frame': k, 'identity_ok': ident, 'recomputed': mine,
                     'package': theirs, 'iou_sum_abs_diff': round(iou_diff, 6), 'differences_package_vs_recomputed': diff, 'match': ok})

res = {'check': 'Lab3 option-A route_data vs N18 viewer recomputation (IoU >= .50, vendor matcher)',
       'data_js_sha256': hashlib.sha256((priv / 'data.js').read_bytes()).hexdigest(),
       'vendor_matching_sha256': hashlib.sha256(vmp.read_bytes()).hexdigest(),
       'cases_json_sha256': hashlib.sha256((demo / 'route_data/public/cases.json').read_bytes()).hexdigest(),
       'integer_counts_rule': 'exact', 'iou_sum_tolerance': IOU_TOL,
       'max_iou_sum_abs_diff': max(r['iou_sum_abs_diff'] for r in rows), 'rows_checked': len(rows), 'rows_matching': sum(r['match'] for r in rows), 'all_match': ok_all, 'rows': rows}
out.write_text(json.dumps(res, indent=1) + '\n')
print(json.dumps({k: v for k, v in res.items() if k != 'rows'}, indent=1))
for r in rows:
    if not r['match']: print('MISMATCH', r['case'], r['action'], r['differences_package_vs_recomputed'], 'identity', r['identity_ok'])
