#!/usr/bin/env python3
"""Replay the recorded Lab 3 run in a clean temporary copy and check the key metrics. No model is called:
the `claude` CLI is removed from PATH, so run_demo.py would stop if any decision were missing.
Usage (from inside lab3_route_demo/):  python3 verify_replay.py
Exit code 0 = all checks pass."""
import json, os, shutil, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPECT = {'agent': {'gold_localization_recall': (23, 132), 'category_aware_grounding_recall': (13, 132), 'gold_support_yield': (23, 200),
                    'matched_category_agreement': (12, 23)},
          'baseline': {'gold_localization_recall': (19, 132), 'category_aware_grounding_recall': (11, 132), 'gold_support_yield': (19, 196),
                       'matched_category_agreement': (11, 19)}}
CHOICES = {'R01': 'native', 'R02': 'native', 'R03': 'dino', 'R04': 'sam', 'R05': 'native', 'R06': 'native', 'R07': 'sam', 'R08': 'sam'}

base = Path(tempfile.gettempdir()).resolve()
if base == HERE or HERE in base.parents:  # never create the work copy inside this folder
    base = HERE.parent
with tempfile.TemporaryDirectory(prefix='lab3_replay_', dir=base) as tmp:
    work = Path(tmp) / 'lab3_route_demo'
    shutil.copytree(HERE, work, ignore=shutil.ignore_patterns('.lock', '.claude', '__pycache__'))
    env = dict(os.environ)
    env['PATH'] = os.pathsep.join(p for p in env.get('PATH', '').split(os.pathsep) if not (Path(p) / 'claude').exists())
    proc = subprocess.run([sys.executable, 'run_demo.py', 'route', '--model', 'claude-opus-5-5'], cwd=work, env=env, capture_output=True, text=True)
    print(proc.stdout.strip()); print(proc.stderr.strip(), file=sys.stderr)
    checks = {'replay exit code 0 without claude on PATH': proc.returncode == 0}
    if proc.returncode == 0:
        comp = json.loads((work / 'evidence/route/comparison.json').read_text())
        tr = json.loads((work / 'evidence/route/transcript.json').read_text())
        checks['8 committed decisions reused'] = {e['case']: e['choice'] for e in tr} == CHOICES
        checks['8 agent receipts'] = len(list((work / 'runs/route/agent').glob('R0*.json'))) == 8
        checks['8 baseline receipts (all native)'] = all(json.loads(p.read_text())['action'] == 'native' for p in (work / 'runs/route/fixed').glob('R0*.json')) and len(list((work / 'runs/route/fixed').glob('R0*.json'))) == 8
        checks['transcript identical to recorded'] = tr == json.loads((HERE / 'evidence/route/transcript.json').read_text())
        for pol, mets in EXPECT.items():
            for k, (n, d) in mets.items():
                v = comp[pol]['metrics'][k]
                checks[f'{pol} {k} = {n}/{d}'] = (v['numerator'], v['denominator']) == (n, d)
        checks['new vision inference calls = 0'] = comp['agent']['new_vision_inference_calls'] == 0
    for k, ok in checks.items(): print(('PASS ' if ok else 'FAIL ') + k)
    sys.exit(0 if all(checks.values()) else 1)
