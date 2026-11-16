# Lab Report 3 — evidence audit (option A, grounding-route demo)

Audit date 2026-11-15. Auditor: Claude Code development agent (Claude Opus 5.5). Machine-readable results:
`../audit/LAB3_AUDIT.json`, produced by `../audit/audit_lab3.py`, which only reads the run.
Verdicts: **PASS** · **FAIL** · **UNVERIFIED** (the evidence needed is not available) · **N/A**.

Sources audited:
- `lab3_demo/run_demo.py`, `route.py` and `evidence_view.py`.
- `evidence/route/{run.json, transcript.json, comparison.json, decisions/R01–R08.json, DEMO_EVIDENCE.html}`.
- `runs/route/agent/*.json` and `runs/route/fixed/*.json`, 8 + 8 receipts plus `policy.json`.
- `route_data/{public/cases.json, private/R0x_{native,sam,dino}.json}`, the 24 archived frame × route rows.
- The raw boxes:
  - Gold: dataset `dylan_anchor_329068e889228c5c`, `gold.jsonl`.
  - Route predictions: the N17 replay `replay_qwen3vl32b.jsonl` (native) and the October export `anchor_lane_predictions.jsonl` (sam_joint, sam_dino).
  - Both reach the audit through the N18 build `data.js` (sha256 67c0dd8d…).
- `VERIFY_ROUTE.json`, `CARD.md`, and git commits d5df638, 9cc3c43 and faa1e8d.

## A. Did Claude make the eight decisions? (transcript → decision → execution → receipt)

| Case | What Claude saw: native boxes / above-limit / errors | Claude's choice | Receipt route = choice | Receipt SHA-256 = chosen lane (≠ the other two) | Matched / Gold: agent | Matched / Gold: native | Stop state: agent / baseline | Decided at (UTC) | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| R01 | 1 / 0 / 0 | native | yes | b290943317eb… yes | 0/4 | 0/4 | escalate / escalate | 17:40:53 | PASS |
| R02 | 20 / 0 / 0 | native | yes | 8d16403d4e02… yes | 3/23 | 3/23 | accepted / accepted | 17:40:58 | PASS |
| R03 | 0 / 0 / 0 | dino | yes | 6dfb74563549… yes | 1/19 | 0/19 | accepted / **escalate** | 17:41:04 | PASS |
| R04 | 50 / 30 / 1 | sam | yes | 752b9a09ab5e… yes | 6/20 | 5/20 | accepted / accepted | 17:41:12 | PASS |
| R05 | 23 / 3 / 0 | native | yes | 3b4844246384… yes | 5/24 | 5/24 | accepted / accepted | 17:41:21 | PASS |
| R06 | 1 / 0 / 0 | native | yes | ca9e985eb04e… yes | 0/3 | 0/3 | escalate / escalate | 17:41:26 | PASS |
| R07 | 52 / 32 / 2 | sam | yes | f08a49d8b0b7… yes | 4/24 | 3/24 | accepted / accepted | 17:41:32 | PASS |
| R08 | 49 / 29 / 2 | sam | yes | 3af2a4df99de… yes | 4/15 | 3/15 | accepted / accepted | 17:41:37 | PASS |

All checks below were run per case.

| Check | Verdict |
|---|---|
| The prompt sent equals the prompt rebuilt by `run_demo.public_prompt` from the public case record. | PASS (8/8) |
| The prompt's observation keys are exactly `case, initial_native, review_frame, scene, split, video_frame, video_id`. It contains no `tp/fn/gold/counts/category/coverage/layer/IoU` fields, no other route's results and no Gold. | PASS (8/8) |
| The raw response parses to the stored choice and reason. | PASS (8/8) |
| The transcript event equals the decision file. | PASS (8/8) |
| The receipt's action, reason and observation equal the decision. The receipt's `result_sha256` equals the SHA-256 of the chosen lane file and differs from the other two lanes. | PASS (8/8) |
| The scored counts in `comparison.json` equal the chosen lane file. The baseline receipts all chose `native`, and their SHA-256 equals the native lane. | PASS (8/8) |
| No retries or replacements. No `format_failures/` folder exists. One decision file per case, written in case order 17:40:53 → 17:41:37. | PASS |
| Tamper-evidence of the decision files themselves. The files are not signed. Evidence of authenticity is the CLI metadata in each file (usage, duration, cost) and the commit (9cc3c43, 17:43:21Z) about 2 min after the last decision. Manual replacement cannot be excluded cryptographically. | UNVERIFIED (no signature), consistent |
| Model ID: `modelUsage` lists only `claude-opus-5-5` in all 8 calls. `run.json` records CLI `2.1.325 (Claude Code)` and model_requested `claude-opus-5-5`. | PASS |
| 8 model calls. CLI-reported cost USD 0.231714 (0.0256–0.0318 each). Durations 3.6–8.6 s. | PASS (as reported by the CLI; not checked against billing) |
| Claude called no tools. The CLI ran with `--tools ""`, an empty MCP config and a temp working folder. Python (`run_demo.py`) ran `route.py`. | PASS (code + run.json) |

## B. Metrics recomputed from raw boxes (IoU ≥ 0.50; 8 development frames, 5 scenes, 132 Gold object-frames)

**Matching rule (vendor evaluator, sha256 816adef7…):**
- One-to-one Hungarian assignment. Pairs with IoU ≥ 0.50 get a bonus, so the rule maximises the number of matches first and then their summed IoU.
- Category is not required for a geometric match.

**Independent check:** the audit adds a separately written min-cost max-flow matcher, with its own IoU function. It agrees with the vendor matcher exactly on all 24 frame × route rows: same pairs, same counts, IoU-sum difference 0.
The original `VERIFY_ROUTE.json` reused the vendor matcher only. It was not an independent implementation; this audit adds one.

| Policy (status) | Gold localization recall | Category-aware recall | Gold-support yield | Conditional IoU | Matched category agreement | Min-evidence frames |
|---|---|---|---|---|---|---|
| Claude agent (measured) | 23/132 | 13/132 | 23/200 | 19.774342/23 = 0.860 | 12/23 | 6/8 |
| Always native (pre-registered baseline) | 19/132 | 11/132 | 19/196 | 15.190128/19 = 0.799 (archived 15.191163 → 0.800) | 11/19 | 5/8 |
| Always SAM 2 (exploratory: tabulated before the run, after viewing outcomes) | 22/132 | 12/132 | 22/196 | 0.884 | 11/22 | 5/8 |
| Always DINO→SAM 2 (exploratory) | 10/132 | 7/132 | 10/38 | 0.985 | 7/10 | 5/8 |
| Rule: SAM 2 unless native empty, then DINO (**post-hoc**, written after the run) | 23/132 | 13/132 | 23/200 | 0.889 | 12/23 | 6/8 |
| Per-frame best of the 3 routes (ORACLE, Gold-based, retrospective) | 23/132 | 13/132 | 23/200 | 0.860 | 12/23 | 6/8 |

Verdict: **PASS.** All six reported agent and baseline figures reproduce. The baseline's conditional IoU is 0.7995 archived and 0.7995 recomputed; the two differ in the 4th decimal of the sum, which is why it rounds to 0.800 from the archive and 0.799 from the raw boxes.

**Metric definitions:**
- **Gold localization recall** = unique matched Gold object-frames / all Gold object-frames on the 8 frames. Gold is a reviewed but *partial* inventory.
- **Category-aware recall** = the number of pairs from a *separate* one-to-one matching run inside each Gold category (Gold category = prediction category), divided by all Gold.
- **Gold-support yield** = matched predictions / emitted predictions. This is not precision: unmatched predictions may be real but unreviewed objects.
- **Conditional IoU** = summed box IoU over geometric matches / the number of matches.
- **Matched category agreement** = geometric matches whose Gold category equals the prediction's mapped category (`CATEGORY_MAP_V1`), divided by geometric matches.
- **Min-evidence frame** = a frame with category-aware matches ≥ 1. This uses Gold, so it is an evaluation flag, not a deployable check.

**Why 13 (category-aware) vs 12 (agreement):** the two statistics use different assignments. In R07 (SAM 2 route):

| Gold object | Geometric assignment | Class-constrained assignment |
|---|---|---|
| Gold #0 person | pred #0 person, IoU 0.977 | pred #0 person, IoU 0.977 |
| Gold #1 person | pred #8 **protective_equipment**, IoU 0.928 | pred #2 **person**, IoU 0.713 |
| Gold #4 person | pred #1 person, IoU 0.978 | pred #1 person, IoU 0.978 |
| Gold #14 machine_equipment | pred #20 other, IoU 0.570 | (none) |

So the geometric assignment has 2 category agreements and the class-constrained matching has 3. All other frames agree, giving 12 vs 13 in total.

**`other` / `unknown` / mapping:**
- Predictions are mapped with the frozen `CATEGORY_MAP_V1`. Words such as object, cable, zone or hook map to `other`; unknown words map to `unmapped`.
- Agreement is plain equality, so an `other` = `other` pair counts as agreement. That is the archived evaluator's definition and reproduces the package in 24/24 rows. It was not changed.
- 8 of the agent's 23 matches involve `other`. 2 are other = other, both in R08.
- Holding out every pair that involves `other` (the N18 viewer convention) gives agreement of 10/15. This is reported as a sensitivity check only.
- No `unknown` or `unmapped` category occurs in the agent's matches.

## C. Archived package rows vs the raw-box recomputation

| Quantity | Result | Verdict |
|---|---|---|
| Integer counts (gold, predictions, tp, fn, matched_correct_category, category_aware_tp) | identical in 24/24 rows | PASS (exact) |
| Summed matched IoU | bitwise equal in 16/24 rows; within 1e-6 in 20/24 rows; differs in 4/24 rows | NOT identical — see below |
| Rows that differ | R02 native 2.49e-4, R04 native 3.24e-4, R05 native 2.26e-4, R07 native 6.88e-4 | — |
| Cause | Only native-route rows differ; SAM and DINO rows agree to < 1e-6, and the integer matches are identical. The native boxes we hold are fractional, converted pixel coordinates (e.g. `[230.4, 33.6, 332.8, 329.76]`) from the N17 replay, not the archive's own copy. A coordinate-precision or conversion difference is the most likely cause. An assignment difference is unlikely, since matcher outputs are equal. | **UNVERIFIED** (the archive's native boxes are not available) |
| Tolerance | The 0.001 tolerance in `verify_route_vs_repo.py` was set **after** seeing these differences, and the script comment says so. The earlier wording "verified 24/24" means 24/24 integer-identical, plus IoU sums within the post-hoc tolerance. | Disclosed; earlier wording corrected |

## D. Protocol

| Claim | Evidence | Verdict |
|---|---|---|
| The 8 frames were selected without reference to outcomes | Rule in `cases.json`: development split, all three routes DONE, scenes sorted, round-robin taking the earliest frame. Rebuilt from the export: 39 eligible development frames in 5 scenes, and the rule reproduces R01–R08 exactly. The rule uses no outcomes. Whether its author saw outcomes cannot be checked. | PASS (rule reproduced); author knowledge UNVERIFIED |
| Development split | All 8 frames are `dev` in the dataset; no held-out frame is used | PASS |
| Success criterion committed before the run | `CARD.md` commit d5df638 at 17:37:23Z; first decision 17:40:53Z | PASS |
| … and before outcomes were known | The development agent tabulated all three routes' outcomes for the 8 frames *before* writing the card. The prompt and route menu were not changed: the package is byte-identical to the downloaded zip (sha256 a14b6634…) | Pre-registration of the criterion: PASS. Blindness of the experimenter: FAIL. Disclosed in the report |
| Fixed model and prompt for all 8 cases | Same template (rebuilt prompt = sent prompt) and same model in every call | PASS |
| No new GPU / vision inference | `route.py` and `run_demo.py` only read JSON and call the Claude CLI; no GPU/network imports. 8 cached-lane reads per policy | PASS |
| Historical GPU cost of the routes | Not available in the audited files | UNVERIFIED (not claimed) |
| Git chronology | d5df638 17:37:23Z (card + package) → decisions 17:40:53–17:41:37Z → 9cc3c43 17:43:21Z (evidence) → faa1e8d 17:48:12Z (first report). No history rewritten | PASS |
| Reproduction from the intended folder | A fresh copy (`lab3_route_demo/`), with the `claude` CLI absent from PATH, reran `python3 run_demo.py route --model claude-opus-5-5`: exit 0, all 8 committed decisions reused, transcript byte-identical, every integer metric identical. One float differs in the 16th significant digit: baseline IoU sum 15.191163281926814 → …816 (likely Python 3.12's compensated `sum`; the original interpreter version is not recorded) | PASS (results); bitwise identity of `comparison.json`: FAIL (last-digit float), immaterial |

## E. Specific questions

| Question | Finding | Verdict |
|---|---|---|
| Is R03 the extra baseline failure (agent 6/8 vs baseline 5/8)? | Yes. The baseline escalates R01, R03 and R06; the agent escalates R01 and R06 | PASS |
| "20-entity limit truncates DINO" | Only Claude's reasoning. The field `entities_above_prompt_limit_20` exists, but no pipeline evidence shows DINO truncation. The DINO route emits fewer boxes on dense frames (R04: 9 vs 50 native), which is consistent with, but not proof of, truncation | UNVERIFIED (reported as a hypothesis) |
| How R03's DINO prompts arose | The native replay for R03 is `COMPLETED_EMPTY` (0 predictions), yet the `sam_dino` lane holds 4 boxes labelled machine, person, platform and support_surface. On other frames DINO labels are also short nouns (door, load, person), not Qwen's full descriptions. The prompt-generation step is not in the files audited | UNVERIFIED (the report states this) |
| R03's single DINO match has IoU 1.000 | The match is exact. Gold boxes are approved automatic mask proposals, so an identical mask box is plausible | Noted |
| "Agent reached the ceiling" | True only as the retrospective best of 3 routes on these 8 frames (23/132) | Wording limited |
| Significance / population claims | One run, 8 frames, 5 scenes. None are made | N/A (not claimed) |
| Repeated runs | None | Gap (planned) |
| Gold completeness | Gold is a reviewed, partial inventory; yield ≠ precision | Preserved |
| Evidence page shows every case in red | `evidence_view.py` styles a case `fail` whenever any Gold object was missed, which is true on all 8 frames. It is not a per-decision verdict | Explained on slides |

## F. Corrections relative to the first report (faa1e8d)
1. "Verified 24/24 vs repo" became: integer counts identical 24/24; IoU sums not identical in 4 native rows; tolerance chosen post hoc; matcher reused (an independent matcher has now been added).
2. Added always-SAM (22/132) and the post-hoc rule (23/132) to the main table. The main conclusion now states that no advantage over a simple rule was shown.
3. Separated integrity checks, offline Gold evaluation and the (planned) deployment-time verifier.
4. Cost: an equal *lookup* budget, not an equal GPU cost. Historical GPU cost is unmeasured.
5. Pre-registration nuance: the experimenter knew the outcomes, though the prompt was unchanged.
6. R03's DINO prompt provenance and the "truncation" claim are marked unverified.
7. The ASCII diagram was replaced by a figure. The slides were rebuilt from genuine evidence-page excerpts.
8. The repository is the course repo `capstone-agent` (Lab 2 URL, verified from the local git remote). The Lab 3 folder is staged but not pushed (owner action).

## G. External reference data: provenance (added 2026-11-15, second pass)

Internal numerical consistency (sections A–C) and external reference validity are separate questions.

| Question | Evidence | Verdict |
|---|---|---|
| Source of the reviewed annotations | `dataset.json` of `dylan_anchor_329068e889228c5c`. Fields: `name = Dylan_original_approved_native_anchors`, `gold_observations = 2870`, `frame_count = 193`, `source_scenes = 24`, `gold_revision 4fecf118…`, `source_revision 740803c1…`, and 54 hashed source fingerprints (anchor manifest, source-frame crosswalk, per-video fingerprints) from the parity run `cosmos3_native_parity_v1/cosmos3_20261107T205655Z_16d874d` | PASS (RECORDED, Helios evidence collection 20261112T171348Z) |
| What shows human approval | Every one of the 2,870 Gold rows has `geometry_source = original_proposal_bbox_approved_by_Dylan`; `dataset.json` has `reference_geometry = "reviewed proposal boxes; no fabricated Gold masks"`. Dylan's original review records themselves (the reviewer UI or export) were not re-opened in this audit. | PASS for the recorded approval field; the upstream review log was not re-inspected (UNVERIFIED) |
| Approved vs. unreviewed | Gold holds only approved rows. Route predictions are separate files (`raw_vlm` / `sam_joint` / `sam_dino`), never mixed with Gold. An unmatched prediction is "unverified" because `gold_is_exhaustive = false` and each frame has `exhaustive = false` | PASS |
| Joining frames to Gold | `frames.jsonl` records `alignment_evidence = exact_frame_sha256`. For R03 and R01 the agent hashed the local frame images: R03 `11eb969f…` and R01 `3a0dc739…`, equal to `frames.jsonl`. The R03 native Qwen record carries the same `source_frame_sha256` (`11eb969f…`). Gold row counts 19 (R03) and 4 (R01) equal the package's denominators | PASS (R01, R03); other 6 frames matched by video/frame ID and Gold count (24/24 rows) |
| Visual inspection of source frames | Local-only overlay pages (`final/owner_private/R03_overlay.html`, `R01_overlay.html`; git-ignored, never shipped) show Gold and every route's boxes on the hash-matched frame. **No person has inspected them yet.** | **UNVERIFIED (pending owner inspection)** |
| Independent re-annotation from footage | Not done | NOT APPLICABLE to this submission (stated as a limitation) |

**Scope statement used in the report:** the cached predictions were scored deterministically against reviewer-approved Dylan Gold object annotations, and a separately implemented matcher reproduced the recorded assignments. These results establish agreement with the reviewed reference subset. They do not establish exhaustive scene precision or independently verified object-boundary truth.
