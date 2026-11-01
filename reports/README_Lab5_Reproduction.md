# Lab 5 reproduction notes

## Scope and recorded configuration
William Welch, AM/ME/CE 295, November 1, 2026. This file describes the measured local literature-retrieval module, not an implemented visual-grounding repair agent.

The repository is `https://github.com/billybirdlab2/capstone-agent`. The recorded local evaluation branch is `lab5-evaluation`, based on `69ebe45`. The final report, evidence and two project-venv permission rules must be committed and made accessible to course staff; no final publication commit has been supplied.

The index contains 801 chunks from 13 arXiv-v1 PDFs. It uses pypdf text extraction, 350-word target chunks with 50-word overlap, and `BAAI/bge-small-en-v1.5` Sentence Transformers embeddings. Hybrid retrieval uses BM25 (k1=1.5, b=0.75) and reciprocal-rank fusion (constant 60), with up to 20 candidates per component for final k=5. The recorded Python is 3.12.10. Exact installed dependency versions and the model-weight revision are not yet locked; the current source manifest pins PDF bytes, not a full software environment.

## Source and access policy
The working corpus and index are local. Do not upload them, or snippets in transcripts, contrary to the source permissions. The repository is private; instructor/TA access must be confirmed. The manifest's `licensed` values require source-level verification. A reproducible authorized source-acquisition or private distribution path is needed; a private GitHub setting alone is not permission to redistribute.

The document inventory, source/version URLs and hashes are in `Corpus_Experiment_Record.json`. Match all PDFs to their manifest names under `corpus/`. Use the same arXiv versions and compare hashes. Do not silently substitute a newer manuscript edition.

## Owner setup and index reconstruction
The following is the intended rebuild route for a separate fresh checkout after the authorized PDFs are available. Do not run it over the working evidence index merely to prepare this submission.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r .claude/skills/code-retriever/requirements.txt
python3 -m pip install fonttools
python3 .claude/skills/code-retriever/build_index.py --check
python3 .claude/skills/code-retriever/build_index.py
```

The first embedding build downloads model weights. Parsing, chunking and embedding run locally; passages passed to the authenticated Claude answerer enter provider model processing. Keep those permissions separate from local indexing access. A rebuild has not been demonstrated from a fresh checkout with a frozen environment. Before accepting new ranks as reproductions, compare the manifest lock, PDF hashes and chunk IDs with the retained evidence.

## Retrieval and evidence locations
The working local commands are:

```bash
.venv/bin/python3 .claude/skills/code-retriever/retrieve.py --show "Explain Popper's generate-test-constrain method"
.venv/bin/python3 .claude/skills/code-retriever/check_citations.py --help
```

The successful agent trace is `eval/transcript_C_retry.jsonl`. The two script-specific `.venv/bin/python3` command forms are the only added execution allowances; do not replace them with a general Python wildcard. Synchronize their documentation in SKILL.md/PERMISSIONS.md and record the final commit. The trace must include actual tool calls and checker tool results, not only the agent's narrative.

The benchmark is `eval/questions.jsonl`; reference-review evidence and the student's confirmation record accompany it. q01 remains unchanged with null gold fields because the acronym premise was not established. The file contains 25 question texts, but the evaluator scores 19 answerable items and places q01 among six null-gold items. Report the five intended negatives separately while retaining the raw 5/6 abstention statistic.

Recorded evaluation commands (not requests to rerun the completed study):

```bash
.venv/bin/python3 .claude/skills/code-retriever/evaluate.py --mode embedding
.venv/bin/python3 .claude/skills/code-retriever/evaluate.py --mode hybrid
```

Retain the real `eval/results_embedding.json`, `eval/results_hybrid.json`, console outputs and `eval/runs/` records from the Mac. The `Metric_Crosscheck.json` supplied with this report is an independently labelled arithmetic reconstruction of the console ranks; it is not a replacement for those raw files. The expected measured Hit@5 values are 11/19 and 16/19, and MRR@5 is 0.3632 and 0.5482. Optional repeated-run reliability testing was not performed.
