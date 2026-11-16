# Lab Report 3: Git branch audit

Status as of 2026-11-15, after the owner ran `capstone_branch/finalize_lab3_branch.sh`. Its log is `capstone_branch/BRANCH_RESULT.txt`; the agent confirmed the results read-only in the repo.

## Two repositories (important)

| | `~/helios-agent` (research agent repo) | `~/ME295/capstone-agent` (course repo) |
|---|---|---|
| Remote | none (local only) | `https://github.com/billybirdlab2/capstone-agent.git` (verified with `git remote -v`) |
| Holds Lab 3 commits d5df638, 9cc3c43, faa1e8d, 7fff7d0, 5fd15fc | **yes**: the original experiment history, preserved and not rewritten | **no**: `git cat-file` reports "Not a valid object name" for all three named commits |
| Also holds | restricted research data (Gold names, frame images, Helios evidence). **Must not** be published. | Lab 1–2 course work |

The experiment's history therefore stays in `helios-agent`. The course repo receives a **sanitized, executable copy** (`lab3_route_demo/`) as new commits on the new branch, and that copy points back to the original commits in its README and audit. No history is rewritten or transplanted.

## Course repo state before branching (read-only inspection by the development agent, 2026-11-15)

| Item | Value |
|---|---|
| Repository root | `/Users/billywelch/ME295/capstone-agent` |
| Current branch / HEAD | `lab5-evaluation` / `5503ce8d5c204b993a04e9e212844ee2d1364039` ("Finalize Lab Report 2 and supporting evaluation evidence") |
| Tracking | `origin/lab5-evaluation`, in sync |
| Course lineage | HEAD contains `origin/main` (69ebe45, merged PR #6). Lab 2 history (80f62dc, 8e5ebb8, PRs #2–#6) is present. |
| Working tree | no staged or modified tracked files; untracked Lab 2 items: `corpus_metadata/`, `eval/transcript_C.jsonl`, `eval/v2/` (left alone, **not** staged) |
| `lab3-route-demo` | does not exist locally or among the cached remote branches (the script also checks the live remote) |
| Local `main` | 09de665, behind `origin/main` by 5 (not changed) |

## Branch creation

| Step | Result |
|---|---|
| Development agent ran `git switch -c lab3-route-demo` in the course repo | **FAIL — blocked by the agent's sandbox** (`cannot lock ref … Operation not permitted`). The agent has no write access to `~/ME295`. Nothing changed; the repo stayed on `lab5-evaluation`. |
| Owner ran `bash …/final/capstone_branch/finalize_lab3_branch.sh` | **PASS**: all pre-checks passed, the branch was created from `lab5-evaluation` 5503ce8, and 69 files were committed (the 68-file package plus `LOG.md`); the untracked Lab 2 items were not staged. The script re-runs the 2.1 inspection, stops unless the remote, lineage, absence of the branch and absence of staged changes all check out, then runs `git switch -c lab3-route-demo` from `5503ce8`. It adds `lab3_route_demo/` and the LOG entry by explicit path, refuses unexpected or restricted-looking files, commits, verifies the branch, and replays from a clean `git archive` export. It **does not push**. |
| Final branch name / local commit | `lab3-route-demo` / **`d7c0f7e52171b5c32e5d9be221dbfc246f447d35`** (parent 5503ce8; contains origin/main 69ebe45) |
| New commits | 1: "Lab Report 3: grounding-route decision demo (cached replay, recorded Claude decisions, receipts, audit)". A second commit with the final report and slides follows via `commit_final_reports.sh`, after the gates are cleared. |

## Files intentionally included (`lab3_route_demo/`, 67 files plus `SHA256SUMS.txt`)
- **Code:** `run_demo.py`, `route.py`, `evidence_view.py`, `verify_replay.py`.
- **Cases:** `route_data/public/cases.json`; `route_data/private/*.json` (24 per-frame, per-route Gold-match **counts**: no boxes, names or images).
- **Recorded run:** `evidence/route/` (8 decisions with prompts, raw responses and model metadata; transcript; comparison; HTML evidence page; `run.json`); `runs/route/{agent,fixed}/` (16 receipts).
- **Audit:** `audit/` (`audit_lab3.py`, `LAB3_AUDIT.json`, `verify_route_vs_repo.py`, `VERIFY_ROUTE.json`).
- **Report notes:** `report/` (evidence audit, experiment card, log entry).
- `README.md` and `SHA256SUMS.txt`.
- **`LOG.md`:** one dated entry appended.

## Files deliberately excluded
- Frame images and video (they show real workers).
- Gold boxes with names (`gold.jsonl`), the N18 `data.js`, and the October route boxes. These are needed only for the raw-box recomputation, whose outputs are included.
- Helios evidence collections and all other `helios-agent` research folders.
- The ChatGPT walkthrough (`REPORT_WALKTHROUGH.md`, `START_HERE.html`; they contain personal ChatGPT library links).
- The category and toy datasets (options B and C, not run).
- Lock files and Claude Code bookkeeping folders.
- No credentials or keys exist in the package (scanned).

## Reproduction result
- **Development agent, clean temporary copies of `final/lab3_route_demo/`, `claude` absent from PATH:** `python3 verify_replay.py` gives 14/14 PASS under Python 3.9.6 and 3.12.10, and `shasum -c` reports 0 failures. That covers 8 decisions reused, 8 + 8 receipts, transcript identical, agent 23/132, 13/132, 23/200 and 12/23, baseline 19/132, 11/132, 19/196 and 11/19, and 0 new vision calls.
- **From the branch's `git archive` export (owner's run of the script):** 14/14 PASS with `/usr/bin/python3` and no `claude` on PATH. The agent confirmed by reading the branch read-only that there are no `.jpg`/`.png`/`.mp4`, `gold.jsonl` or `data.js` files under `lab3_route_demo/`.
- **The full branch script was not dry-run by the agent.** Its sandbox blocked writes to the course repo and changing the remote URL of a scratch clone. The script was syntax-checked, and its replay step was tested separately.

## Publication
| Item | Status |
|---|---|
| Pushed to GitHub | **No** (no upstream configured; verified 2026-11-15). Pushing is the owner's decision: `cd ~/ME295/capstone-agent && git push -u origin lab3-route-demo` |
| Staff access verified | **No.** The repo is private (Lab 2 report). Add the course staff, or follow the course's access instructions, then confirm the branch URL opens for them. |
| Link in the report | Only after both rows above are done (gate G3 in `gate.json`). |
