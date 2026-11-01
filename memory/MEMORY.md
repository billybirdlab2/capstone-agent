# MEMORY.md — curated durable facts and decisions

<!-- Short, durable, sourced. Not a transcript and not a daily log (that is memory/daily/).
     Format: - fact.  (date · source) -->

## Project
- Lab 4 agent created from the course template.  (2026-10-21 · owner)
- Capstone (AM/ME/CE 295) investigates industrial safety reasoning using vision-language models, visually grounded relational predicates, inductive logic programming, and independently verified safety rules. No results recorded yet.  (2026-11-01 · owner, stated in interactive session)
- Intended (planned, not yet demonstrated) agentic contribution: diagnosing failures and selecting bounded corrective actions based on evidence.  (2026-11-01 · owner, stated in interactive session)

## Decisions
- Morning arXiv digest is customized to five research tracks: (1) vision-language models and visual grounding, (2) neuro-symbolic reasoning and inductive logic programming, (3) robotic safety, (4) robot learning and control, (5) robotics systems. It replaces the template's metamaterials query (`cat:cond-mat.soft AND all:metamaterial`); do not revert.  (2026-11-01 · owner; config in `routine/ROUTINE_PROMPT.md`, merged via PR #2, commit 23bee2e)
- Digest parameters: one `arxiv_digest.py` run with all five `--query` arguments, `--days 7` lookback, `--max 6` per query (≤30 candidates before dedup), select at most 8 papers into `digests/YYYY-MM-DD.md`.  (2026-11-01 · `routine/ROUTINE_PROMPT.md`; first run recorded in `memory/daily/2026-11-01.md`)
