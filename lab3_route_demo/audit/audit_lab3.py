#!/usr/bin/env python3
"""Lab 3 option-A evidence audit (2026-11-15). Read-only over the run; writes audit/LAB3_AUDIT.json.

Checks
 A  per case R01-R08: prompt reconstructed from code == prompt sent; no outcome fields in the prompt; raw response parses
    to the stored choice/reason; receipt action == choice; receipt result_sha256 == sha of the chosen lane file and != the
    other lanes; transcript == decision file; scored counts == lane file; no format_failures (no retries); model metadata.
 B  metrics recomputed from RAW boxes (N18 build: Gold boxes of dylan_anchor_329068e889228c5c; October Qwen3-VL-32B
    raw_vlm (N17 replay) / sam_joint / sam_dino boxes) with (i) the vendored evaluator matcher and (ii) an independent
    min-cost max-flow matcher written here; for agent, always-native, always-SAM, always-DINO, post-hoc rule, oracle.
 C  IoU-sum differences vs the package's archived rows, exact float values.
 D  protocol: package files unchanged vs the downloaded zip; selection rule reproduced on the eligible set; split; timing.
Usage: python3 -I audit_lab3.py   (paths are fixed relative to this file; reads the git-ignored N18 data.js)
"""
import hashlib, importlib.util, json, os, re, sys, zipfile
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
CARD = HERE.parent
DEMO = CARD / 'lab3_demo'
N18 = CARD.parent / '20261112_n18_comparison_viewer'
ZIP = Path(os.environ.get('LAB3_ZIP', '/private/tmp/claude-501/-Users-billywelch-helios-agent/0dcb8584-889c-4c92-84a3-f2282c4f9ea1/scratchpad/lab_inputs/ME295_Lab3_Three_Demo_Options.zip'))
ROUTES = ('native', 'sam', 'dino')
LANE = {'native': 'qwen3vl32b|native', 'sam': 'qwen3vl32b|sam2', 'dino': 'qwen3vl32b|dino'}
sha = lambda b: hashlib.sha256(b).hexdigest()
load = lambda p: json.loads(Path(p).read_text(encoding='utf-8'))
out = {'generated_by': 'audit/audit_lab3.py', 'A': {}, 'B': {}, 'C': {}, 'D': {}}

# ---------------- A. decision → execution → receipt chain ----------------
sys.path.insert(0, str(DEMO))
import route, run_demo  # the package's own code: used only to rebuild prompts and digests
cases = load(DEMO / 'route_data/public/cases.json')['cases']
FORBIDDEN = re.compile(r'"(tp|fn|gold_objects|category_aware_tp|matched_correct_category|sum_matched_box_iou|counts|layer|coverage|gold)"')
transcript = {e['case']: e for e in load(DEMO / 'evidence/route/transcript.json')}
comp = load(DEMO / 'evidence/route/comparison.json')
runj = load(DEMO / 'evidence/route/run.json')
A = []
for cid, case in cases.items():
    d = load(DEMO / f'evidence/route/decisions/{cid}.json')
    lanes = {a: load(DEMO / f'route_data/private/{cid}_{a}.json') for a in ROUTES}
    digests = {a: route.digest(lanes[a]) for a in ROUTES}
    rebuilt = run_demo.public_prompt('route', cid, case, list(ROUTES))
    try:
        ch, rs = run_demo.parse_action(d['raw_response'], cid, list(ROUTES)); parsed_ok = (ch == d['choice'] and rs == d['reason'])
    except Exception as e:
        parsed_ok = False
    ra = load(DEMO / f'runs/route/agent/{cid}.json'); rf = load(DEMO / f'runs/route/fixed/{cid}.json')
    mu = d['model_metadata'].get('modelUsage') or {}
    row = {'case': cid, 'observation_seen': case['initial_native'], 'choice': d['choice'], 'reason': d['reason'],
           'prompt_equals_code_rebuild_from_public_case': d['prompt'] == rebuilt,
           'prompt_observation_keys': sorted(json.loads(d['prompt'][d['prompt'].index('\n{'):])['observation']),
           'prompt_contains_outcome_fields': bool(FORBIDDEN.search(d['prompt'])),
           'raw_response_parses_to_stored_choice_and_reason': parsed_ok,
           'transcript_event_equals_decision_file': all(transcript[cid][k] == d[k] for k in d),
           'receipt_action_equals_choice': ra['action'] == d['choice'], 'receipt_reason_equals_reason': ra['reason'] == d['reason'],
           'receipt_observation_equals_case': ra['observation'] == case,
           'receipt_sha_equals_chosen_lane': ra['result_sha256'] == digests[d['choice']],
           'receipt_sha_differs_from_other_lanes': all(ra['result_sha256'] != digests[a] for a in ROUTES if a != d['choice']),
           'receipt_sha256': ra['result_sha256'], 'receipt_committed_utc': ra['committed_utc'], 'agent_stop_state': ra['stop_state'],
           'fixed_action': rf['action'], 'fixed_sha_equals_native_lane': rf['result_sha256'] == digests['native'], 'fixed_stop_state': rf['stop_state'],
           'scored_counts_equal_chosen_lane': comp['agent']['cases'][cid]['counts'] == lanes[d['choice']]['counts'],
           'baseline_scored_counts_equal_native_lane': comp['baseline']['cases'][cid]['counts'] == lanes['native']['counts'],
           'agent_tp_over_gold': [lanes[d['choice']]['counts']['tp'], lanes[d['choice']]['counts']['gold_objects']],
           'baseline_tp_over_gold': [lanes['native']['counts']['tp'], lanes['native']['counts']['gold_objects']],
           'model_ids': sorted(mu), 'cost_usd': d['model_metadata'].get('total_cost_usd'), 'duration_ms': d['model_metadata'].get('duration_ms')}
    row['chain_pass'] = all(row[k] for k in row if k.startswith(('prompt_equals', 'raw_response', 'transcript_', 'receipt_', 'fixed_sha', 'scored_', 'baseline_scored'))
                            and isinstance(row[k], bool)) and not row['prompt_contains_outcome_fields']
    A.append(row)
out['A'] = {'cases': A, 'format_failures_dir_exists': (DEMO / 'evidence/route/format_failures').exists(),
            'run_json': runj, 'total_cost_usd': round(sum(r['cost_usd'] for r in A), 6), 'model_calls_recorded': len(A),
            'all_model_ids': sorted({m for r in A for m in r['model_ids']}), 'all_chains_pass': all(r['chain_pass'] for r in A)}

# ---------------- B. recompute from raw boxes ----------------
spec = importlib.util.spec_from_file_location('vm', N18 / 'portable/vendor_matching.py'); vm = importlib.util.module_from_spec(spec); spec.loader.exec_module(vm)
s = (N18 / 'viewer/private/data.js').read_text(); data = json.loads(s[s.index('{'):s.rstrip().rstrip(';').rindex('}') + 1])


def iou(a, b):  # written independently of vendor_matching.iou (same definition: area of intersection / area of union)
    ix = max(0.0, min(a[2], b[2]) - max(a[0], b[0])); iy = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
    inter = ix * iy; union = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / union if union > 0 else 0.0


def mcmf_match(G, P, thr=0.5):
    """Independent matcher: min-cost max-flow (successive shortest paths, Bellman-Ford) on edges with IoU >= thr,
    cost = -IoU. Max flow = max number of one-to-one matches; min cost among max flows = max summed IoU."""
    nG, nP = len(G), len(P); S, T = nG + nP, nG + nP + 1; graph = defaultdict(list); E = []
    def add(u, v, c):
        graph[u].append(len(E)); E.append([u, v, 1, c]); graph[v].append(len(E)); E.append([v, u, 0, -c])
    for i in range(nG): add(S, i, 0.0)
    for j in range(nP): add(nG + j, T, 0.0)
    for i in range(nG):
        for j in range(nP):
            w = iou(G[i]['b'], P[j]['b'])
            if w >= thr: add(i, nG + j, -w)
    while True:
        dist = {S: 0.0}; prev = {}; changed = True; n = nG + nP + 2
        for _ in range(n):
            if not changed: break
            changed = False
            for k, (u, v, cap, c) in enumerate(E):
                if cap > 0 and u in dist and dist[u] + c < dist.get(v, float('inf')) - 1e-12:
                    dist[v] = dist[u] + c; prev[v] = k; changed = True
        if T not in dist: break
        v = T
        while v != S:
            k = prev[v]; E[k][2] -= 1; E[k ^ 1][2] += 1; v = E[k][0]
    return sorted((u, v - nG, -c) for (u, v, cap, c) in E[::2] if u < nG and nG <= v < nG + nP and cap == 0 and c <= 0 and (u, v) != (S, T))


def vendor_match(G, P):
    if not G or not P: return []
    W = [[vm.iou(g['b'], p['b']) for p in P] for g in G]
    return sorted((i, j, W[i][j]) for i, j in vm.threshold_matches(W, .5))


def frame_stats(G, P, matcher):
    m = matcher(G, P)
    cat_tp = sum(len(matcher([g for g in G if g['c'] == c], [p for p in P if p['c'] == c])) for c in {g['c'] for g in G})
    return {'gold': len(G), 'pred': len(P), 'tp': len(m), 'iou_sum': sum(x for _, _, x in m),
            'cat_agree': sum(G[i]['c'] == P[j]['c'] for i, j, _ in m), 'cat_aware_tp': cat_tp,
            'pairs': [[i, j, round(x, 6), G[i]['c'], P[j]['c']] for i, j, x in m]}


key = {cid: f"{c['video_id']}/{c['video_frame']}" for cid, c in cases.items()}
per = {}
for cid in cases:
    G = data['frames'][key[cid]]['gold']
    per[cid] = {}
    for a in ROUTES:
        r = data['results'][LANE[a]].get(key[cid]); P = r['p'] if r else []
        v, f = frame_stats(G, P, vendor_match), frame_stats(G, P, mcmf_match)
        same = {k: v[k] == f[k] for k in ('gold', 'pred', 'tp', 'cat_agree', 'cat_aware_tp')}
        same['iou_sum_absdiff'] = abs(v['iou_sum'] - f['iou_sum'])
        per[cid][a] = {'vendor': v, 'independent': f, 'agreement': same}
agent_choice = {r['case']: r['choice'] for r in A}
rule = {cid: ('dino' if cases[cid]['initial_native']['emitted_boxes'] == 0 else 'sam') for cid in cases}
policies = {'agent (Claude)': agent_choice, 'always native (pre-registered baseline)': {c: 'native' for c in cases},
            'always SAM (exploratory)': {c: 'sam' for c in cases}, 'always DINO (exploratory)': {c: 'dino' for c in cases},
            'rule: SAM unless native empty, then DINO (post-hoc)': rule}


def agg(choice, which):
    t = Counter()
    for cid, a in choice.items():
        st = per[cid][a][which]
        for k in ('gold', 'pred', 'tp', 'cat_agree', 'cat_aware_tp'): t[k] += st[k]
        t['iou_sum'] += st['iou_sum']; t['min_evidence'] += int(st['cat_aware_tp'] > 0)
    return {'gold_localization_recall': [t['tp'], t['gold']], 'category_aware_recall': [t['cat_aware_tp'], t['gold']],
            'gold_support_yield': [t['tp'], t['pred']], 'conditional_iou': [round(t['iou_sum'], 6), t['tp']],
            'matched_category_agreement': [t['cat_agree'], t['tp']], 'frames_min_evidence': [t['min_evidence'], len(choice)]}


oracle = {cid: max(ROUTES, key=lambda a: (per[cid][a]['vendor']['tp'], -ROUTES.index(a))) for cid in cases}
out['B'] = {'per_case_route': per, 'policies': {n: {'choices': ch, 'vendor': agg(ch, 'vendor'), 'independent': agg(ch, 'independent')}
                                                 for n, ch in list(policies.items()) + [('per-frame best (ORACLE, Gold-based)', oracle)]},
            'matchers_agree_all_rows': all(all(v for k, v in per[c][a]['agreement'].items() if k != 'iou_sum_absdiff') and per[c][a]['agreement']['iou_sum_absdiff'] < 1e-9
                                           for c in per for a in ROUTES),
            'max_matcher_iou_sum_absdiff': max(per[c][a]['agreement']['iou_sum_absdiff'] for c in per for a in ROUTES)}
# categories involved in agent's matches
cats = Counter(); special = []
for cid, a in agent_choice.items():
    for i, j, x, gc, pc in per[cid][a]['vendor']['pairs']:
        cats[(gc, pc)] += 1
        if gc in ('other', 'unknown', 'unlabeled') or pc in ('other', 'unknown', 'unlabeled', 'unmapped'): special.append([cid, a, gc, pc])
out['B']['agent_match_category_pairs'] = {f'{g} -> {p}': n for (g, p), n in sorted(cats.items())}
out['B']['agent_matches_involving_other_unknown_unmapped'] = special
# 13 vs 12: frames where class-constrained matching differs from category agreement of the geometric assignment
diff = []
for cid, a in agent_choice.items():
    v = per[cid][a]['vendor']
    if v['cat_aware_tp'] != v['cat_agree']:
        G = data['frames'][key[cid]]['gold']; P = data['results'][LANE[a]][key[cid]]['p']
        cm = []
        for c in {g['c'] for g in G}:
            gi = [k for k, g in enumerate(G) if g['c'] == c]; pj = [k for k, p in enumerate(P) if p['c'] == c]
            for i, j, x in vendor_match([G[k] for k in gi], [P[k] for k in pj]): cm.append([gi[i], pj[j], round(x, 6), c])
        diff.append({'case': cid, 'route': a, 'geometric_pairs': v['pairs'], 'class_constrained_pairs': sorted(cm),
                     'cat_agree_in_geometric': v['cat_agree'], 'class_constrained_tp': v['cat_aware_tp']})
out['B']['category_aware_vs_agreement_cases'] = diff

# ---------------- C. archived package rows vs raw-box recomputation ----------------
C = []
for cid in cases:
    for a in ROUTES:
        pk = load(DEMO / f'route_data/private/{cid}_{a}.json'); v = per[cid][a]['vendor']
        ints = {'gold_objects': v['gold'], 'predictions': v['pred'], 'tp': v['tp'], 'fn': v['gold'] - v['tp'],
                'matched_correct_category': v['cat_agree'], 'category_aware_tp': v['cat_aware_tp']}
        C.append({'case': cid, 'route': a, 'integer_counts_identical': all(pk['counts'][k] == ints[k] for k in ints),
                  'iou_sum_package': pk['sum_matched_box_iou'], 'iou_sum_recomputed': v['iou_sum'],
                  'iou_sum_exactly_equal': pk['sum_matched_box_iou'] == v['iou_sum'],
                  'iou_sum_absdiff': abs(pk['sum_matched_box_iou'] - v['iou_sum'])})
out['C'] = {'rows': C, 'rows_integer_identical': sum(r['integer_counts_identical'] for r in C),
            'rows_iou_sum_bitwise_equal': sum(r['iou_sum_exactly_equal'] for r in C),
            'rows_iou_sum_absdiff_below_1e-6': sum(r['iou_sum_absdiff'] < 1e-6 for r in C),
            'rows_iou_sum_absdiff_ge_1e-6': [[r['case'], r['route'], r['iou_sum_absdiff']] for r in C if r['iou_sum_absdiff'] >= 1e-6]}

# ---------------- D. protocol ----------------
D = {}
if ZIP.exists():
    z = zipfile.ZipFile(ZIP); same = {}; extra = []
    for n in z.namelist():
        if n.endswith('/'): continue
        rel = n.split('/', 1)[1]; p = DEMO / rel
        same[rel] = p.exists() and sha(p.read_bytes()) == sha(z.read(n))
    D['package_zip_sha256'] = sha(ZIP.read_bytes())
    D['package_files_unchanged'] = all(same.values()); D['package_files_changed'] = [k for k, v in same.items() if not v]
else:
    D['package_files_unchanged'] = 'UNVERIFIED (zip not found)'
# selection rule: development frames with all three Qwen32B lanes present (DONE) in the October export
lanes_done = defaultdict(set)
for l in open(N18 / 'viewer/private/export/anchor_lane_predictions.jsonl'):
    r = json.loads(l)
    if r['method'] in ('sam_joint:qwen3vl32b', 'sam_dino:qwen3vl32b') and r['state'] == 'DONE': lanes_done[r['method']].add(f"{r['video_id']}/{r['frame_id']}")
native_present = set(data['results'][LANE['native']])
elig = sorted(k for k, f in data['frames'].items() if f['split'] == 'dev' and k in lanes_done['sam_joint:qwen3vl32b']
              and k in lanes_done['sam_dino:qwen3vl32b'] and k in native_present)
by_scene = defaultdict(list)
for k in elig: by_scene[data['frames'][k]['s']].append(int(data['frames'][k]['f']))
order = {s: sorted(v) for s, v in sorted(by_scene.items())}
sel = []; idx = {s: 0 for s in order}
while len(sel) < 8 and any(idx[s] < len(order[s]) for s in order):
    for s in order:
        if len(sel) < 8 and idx[s] < len(order[s]): sel.append((s, order[s][idx[s]])); idx[s] += 1
D['eligible_dev_frames_all_three_lanes'] = len(elig); D['eligible_scenes'] = len(order)
D['round_robin_selection_reproduced'] = [list(x) for x in sel]
D['package_cases'] = [[c['scene'], c['video_frame']] for c in cases.values()]
D['selection_matches_package'] = D['round_robin_selection_reproduced'] == D['package_cases']
D['all_cases_dev_split'] = all(data['frames'][key[c]]['split'] == 'dev' for c in cases)
D['decision_times_utc'] = [r['receipt_committed_utc'] for r in A]
D['route_py_reads_only_json'] = 'no subprocess/network/GPU imports in route.py' if not re.search(r'import (subprocess|socket|urllib|requests|torch)', (DEMO / 'route.py').read_text()) else 'CHECK'
out['D'] = D

(HERE / 'LAB3_AUDIT.json').write_text(json.dumps(out, indent=1, default=str) + '\n')
print(json.dumps({'A_all_chains_pass': out['A']['all_chains_pass'], 'format_failures': out['A']['format_failures_dir_exists'],
                  'cost': out['A']['total_cost_usd'], 'models': out['A']['all_model_ids'],
                  'B_matchers_agree': out['B']['matchers_agree_all_rows'], 'B_max_matcher_diff': out['B']['max_matcher_iou_sum_absdiff'],
                  'policies': {n: v['independent'] for n, v in out['B']['policies'].items()},
                  'special_category_matches': special, 'cat_diff_cases': [(d['case'], d['cat_agree_in_geometric'], d['class_constrained_tp']) for d in diff],
                  'C': {k: v for k, v in out['C'].items() if k != 'rows'}, 'D': {k: v for k, v in D.items() if k not in ('decision_times_utc',)}}, indent=1))
