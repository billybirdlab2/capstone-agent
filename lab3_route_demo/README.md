# lab3_route_demo: Lab Report 3 grounding-route decision demo (AM/ME/CE 295, W. Welch)

**What it is.** For each of 8 development frames, Claude (`claude-opus-5-5`) sees only the diagnostics of a first Qwen3-VL-32B pass and picks one cached grounding route:
- `native`: Qwen boxes;
- `sam`: Qwen boxes refined by SAM 2;
- `dino`: Grounding DINO → SAM 2.

Python executes the choice. A deterministic evaluator scores it offline against reviewer-approved ("Dylan Gold") boxes at IoU ≥ 0.50, next to an always-native baseline. No new vision inference runs; the route outputs were cached from an October 2026 GPU campaign.

## Requirements
- Python 3 with the standard library only; no `pip install`.
- Tested on macOS with CPython 3.9.6 and 3.12.10.
- `run_demo.py` uses `fcntl`, so run it on macOS or Linux.
- No network, GPU or model weights are needed for the replay.

## 1. Replay the recorded run (no model calls). This is what a TA should run.

```bash
cd lab3_route_demo
python3 verify_replay.py
```

It copies this folder to a temporary directory, removes `claude` from PATH, and runs `python3 run_demo.py route --model claude-opus-5-5`. Expected output (last lines):

```
PASS replay exit code 0 without claude on PATH
PASS 8 committed decisions reused
PASS 8 agent receipts
PASS 8 baseline receipts (all native)
PASS transcript identical to recorded
PASS agent gold_localization_recall = 23/132
PASS agent category_aware_grounding_recall = 13/132
PASS agent gold_support_yield = 23/200
PASS agent matched_category_agreement = 12/23
PASS baseline gold_localization_recall = 19/132
PASS baseline category_aware_grounding_recall = 11/132
PASS baseline gold_support_yield = 19/196
PASS baseline matched_category_agreement = 11/19
PASS new vision inference calls = 0
```

You can also run `python3 run_demo.py route --model claude-opus-5-5` in place. Because `evidence/route/decisions/` already holds the 8 committed decisions, it re-executes them without calling any model and rebuilds `evidence/route/` (the comparison table and `DEMO_EVIDENCE.html`).

## 2. Fresh inference (differs from the replay)
1. Copy the folder.
2. Delete `evidence/` and `runs/` in the copy.
3. Run the same command with a signed-in Claude Code CLI on PATH (the original used 2.1.325).

This makes 8 new model calls (about USD 0.23 on 2026-11-15). The new choices may differ from the recorded ones, so the results are a *new* run, not a reproduction.

## Recorded result (8 development frames, 5 scenes, 132 reviewed Gold objects)

| Policy | Gold matched | Support yield | Category agreement |
|---|---|---|---|
| Claude | 23/132 | 23/200 | 12/23 |
| Always native (pre-registered baseline) | 19/132 | 19/196 | 11/19 |
| Always SAM 2 (exploratory) | 22/132 | 22/196 | 11/22 |
| Rule "SAM 2 unless native empty, then DINO" (post-hoc) | 23/132 | 23/200 | 12/23 |

Claude beat always-native, but **no advantage over the simple rule is shown**. This is one run on 8 frames, with no significance claim.

## Files

| Path | Content |
|---|---|
| `run_demo.py` | Orchestrator. Builds the prompt, calls Claude (print mode, no tools), validates the JSON and dispatches the choice. |
| `route.py` | Tool commands: `inspect`, `choose` (reads one cached route, checks invariants, write-once receipt with SHA-256), `baseline`, `summary`. |
| `route_data/public/cases.json` | The 8 frozen cases and their selection rule. |
| `route_data/private/` | Per-frame, per-route Gold-match **counts** from the archived evaluation. No boxes, names or images. |
| `evidence/route/` | The recorded run: prompts, raw responses, model metadata, receipts, comparison and an HTML evidence page. |
| `runs/route/` | Write-once receipts (`agent/`, `fixed/`). |
| `audit/` | `audit_lab3.py` and `LAB3_AUDIT.json`, `verify_route_vs_repo.py` and `VERIFY_ROUTE.json`. |
| `report/` | `LAB3_EVIDENCE_AUDIT.md` (PASS / FAIL / UNVERIFIED per claim), the experiment card and the dated log entry. |
| `SHA256SUMS.txt` | Checksums of every file. Check with `shasum -a 256 -c SHA256SUMS.txt`. |

## What the replay does and does not verify
- **Verifies (no model involved):**
  - The 8 recorded decisions match their receipts and the cached route files (SHA-256).
  - The evaluator's counts and metrics.
  - Replay without any model call.
- **Raw-box recomputation is not runnable from this folder.** `audit/` recomputed every frame × route row from the original Gold boxes and route boxes, with the course evaluator's matcher and with an independent min-cost max-flow matcher (identical results). Those inputs are restricted project data (reviewer annotations of industrial video, with names) and are not redistributed. Their outputs are included in `audit/`.
- **The reference is human-reviewed.** Gold is the dataset `Dylan_original_approved_native_anchors`; every row has `geometry_source = original_proposal_bbox_approved_by_Dylan`. Frames are joined to Gold by exact frame SHA-256.
- **The reference is partial** (`gold_is_exhaustive: false`). Support yield is therefore not precision, and unmatched boxes are unverified, not wrong.
- **Scope.** The results establish agreement with the reviewed reference subset. They do not establish exhaustive scene precision or independently verified object boundaries.
- **Known discrepancy.** Integer counts equal the archive in 24/24 frame × route rows. Summed IoU differs by 2.3–6.9 × 10⁻⁴ in 4 native-route rows; the cause is unverified. The 0.001 tolerance in `verify_route_vs_repo.py` was chosen after these differences were seen.
- **Last-digit float difference.** A replay under a different Python version may change the last digit of one float (the baseline IoU sum). All counts and rounded metrics are unchanged.

## Provenance
- The demo package (`run_demo.py`, `route.py`, `evidence_view.py`, cases) was generated with ChatGPT and is used unchanged.
- The audit and documentation were prepared with Claude Code.
- `cases.json` and `comparison.json` record an opaque ChatGPT library-file ID as the data-source reference. It is not a credential.
