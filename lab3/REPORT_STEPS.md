# Lab Report 3 — finishing steps after the Option A run

Due: Sunday, Nov 15, 11:59 pm Pacific, on CodeGrade. Separate submission: the Week 7
Guide & Check. Budget: roughly 45–75 min for the report and slides after the run.

Every number below must come from `reports/lab3/option_a_run_*/evidence/comparison.json` or the
verification script. Each number is reported with its inputs and the tool that produced it.

## 0. Collect before writing (10 min)
- [ ] `reports/lab3/PROTOCOL.md` committed **before** the run.
- [ ] `reports/lab3/RESULTS.md`: paired table, the two cases, the failure, and limitations.
- [ ] Screenshots from `DEMO_EVIDENCE.html`: R04 (or your chosen case) input diagnostic,
      Claude's decision + reason, executor receipt, checker result, comparison table.
- [ ] Your own check: one decision traced raw response → receipt → score, plus one IoU and one
      recall fraction you recomputed. Note what you checked; this goes in the AI declaration.

## 1. Report sections (course Word template, ~5 pages)

**A. Project description and goal (≤5 sentences).** Keep the industrial-safety objective from
Lab 2. Incorrect visual facts propagate into learned safety rules, so grounding must be verified
before ILP. This week's question: *Can an agent use diagnostics from the initial Qwen32B output
to choose a grounding configuration (keep native, Qwen→SAM, Qwen→DINO→SAM) that recovers more
reviewed objects than always keeping native Qwen?* Scope: 8 Dylan development frames, cached
predictions, one live Claude decision per frame.

**B. Why an agent?** The evidence varies per frame: box count, entities over the prompt limit,
generator errors, sparse output. Those may justify a different route, and a fixed rule cannot
read them. The always-native baseline, given the same frames, budget and checker, tests whether
that flexibility helped.

**C.1 Architecture diagram.** Reuse the Lab 2 diagram. Highlight the path that ran:
cached grounding outputs + diagnostics → Claude decision → Python executor (fetches chosen
branch) → independent checker (Gold on the checker side only). Draw the fixed baseline feeding
the same checker. Use a three-state legend: *ran this week* / *demonstrated earlier (retriever,
citation checker, digest)* / *planned (in-loop repair with retry, predicate store, ILP)*.

**C.2 Roles and tools.** Give each component one sentence on what would be lost without it:
- Diagnostics tool: without it, Claude has no case-specific evidence.
- Claude: without it, only the fixed baseline remains.
- Executor: without it, a recommendation has no measured consequence.
- Checker: without it, you can't tell whether a decision worked.
- Retriever (Lab 2): supplies cited method background. It never decides grounding.

**C.3 Demonstration.** Give the Google Slides link (set to "anyone with the link can view" and
test it in a private window). Also give the exact commands
(`bash lab3/helios_option_a.sh run` → `python3 run_demo.py route`), the transcript path,
the repo URL, and the commit hash.

**D. Evaluation.** State the unit scored (object-frame observations; eligible denominator,
e.g. 132), the IoU cutoff and operator (≥ 0.50 in the archive), the baseline (always native),
the budget (one cached branch lookup per frame), and the run count (1). Paste the paired table
from RESULTS.md. Explain one case where the decision changed the outcome, or say none did. A tie
or a loss is reportable: explain it.

**E. Progress, bottleneck, next steps.**
- Lab 2 (already shown): retriever + citation checker, digest, memory and permissions.
- This week: live routing decision over real grounding outputs, scored against Gold with a
  paired baseline.
- Bottleneck: the most consequential one you actually observed (e.g. count-based diagnostics
  cannot tell good boxes from duplicates; the model never sees pixels; the check is post hoc
  rather than driving a retry).
- Nov 29: put the checker inside the loop (FAIL → retry within budget or abstain); run on
  held-out frames with repeats; pass verified objects to the predicate store and on to ILP.
  For each, state what evidence would show it works.

**Repository.** Give the repo link, current commit, README run instructions, and progress from
LOG.md. Confirm TA access to the private repo.

**AI Use Declaration.** Name each tool and its role:
- ChatGPT: designed the demo package and the report guidance.
- Claude Code (cloud): wrote the Helios wrapper and prompt.
- Claude Code on Helios: ran, verified and drafted results.
- Claude via `claude -p` inside `run_demo.py`: made the measured decisions. Give the model and
  version from the provenance file.

Then list what you personally verified or changed.

## 2. Slides (4)
1. Architecture and status, with the three-state legend.
2. One complete decision: case ID, diagnostic, Claude's choice and reason, executed branch,
   and Gold recovered by the agent vs the baseline.
3. Second decision or failure: what came back, what you expected, and your best explanation.
4. Paired table with denominators, plus one next change motivated by the results.

## 3. Submit
- [ ] Merge the PR (you, on GitHub) and check that the README links work on `main`.
- [ ] Report PDF on CodeGrade. Slides link in C.3. Repo link and commit hash included.
- [ ] Week 7 Guide & Check (separate): read first, write your 2–3 sentence note, then the
      initial answer plus **three** follow-ups, one claim checked against a named figure or
      table, the full conversation, the paper link, the model, and the AI declaration.
