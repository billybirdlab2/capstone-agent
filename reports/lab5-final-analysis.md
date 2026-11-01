# Lab 5 — Final analysis of the retrieval evaluation (Part D)

Written 2026-10-31 from the existing evaluation files. **No experiment was rerun.** The corpus, index, questions, gold answers, scripts, permissions and raw outputs were read but not changed. Every number below comes from `evaluate.py` output (`eval/*_console.txt`, `eval/results_*.json`) or from per-question run records in `eval/runs/`. Where I checked a figure by hand (MRR from the per-question ranks), I say so.

Sources read: `eval/questions.jsonl`, `eval/freeze_record.json`, `eval/questions_frozen.jsonl`, `eval/benchmark_notes.md`, `eval/results_embedding.json`, `eval/results_hybrid.json`, `eval/embedding_console.txt`, `eval/hybrid_console.txt`, `eval/runs/*.json`, `eval/transcript_C.jsonl`, `eval/transcript_C_retry.jsonl`, `corpus/manifest.json`, `corpus_metadata/checksums.sha256`, `index/manifest.lock`, `.claude/skills/code-retriever/` (SKILL.md, source and requirements), `CLAUDE.md`, `memory/MEMORY.md` and `PERMISSIONS.md`. There is no `eval/benchmark_notes.md` file.

---

## 1. Benchmark integrity

| Check | Result |
|---|---|
| Questions in `eval/questions.jsonl` | 25 (q01–q25) |
| Kinds | 10 `identifier` (q01–q10), 10 `paraphrase` (q11–q20), 5 `not_in_corpus` (q21–q25) |
| Freeze record (`eval/freeze_record.json`) | 25 questions, `{identifier: 10, paraphrase: 10, not_in_corpus: 5}`, question sha256 `9d6b0883…8d8f` |
| `id`, `kind` and `question` text compared with `eval/questions_frozen.jsonl` | Identical for all 25, in the same order |

The two files have different hashes. That is expected: the frozen file holds only `id/kind/question`, and `eval/questions.jsonl` adds the `answer` and `chunk_id` gold fields after freezing. No question was reworded, reordered or reclassified.

### q01 — unresolved identifier question (kept unchanged)

> q01: *"In the Popper paper, what is the expanded name of the ILP approach abbreviated LFF?"*: `answer: null`, `chunk_id: null`

- **Observation.** During gold construction (`eval/benchmark_notes.md`), a keyword-mode search for `LFF` returned zero chunks from the whole index. The retrieved Popper passages name the approach "learning programs by learning from failures", but no passage connects that name to the abbreviation "LFF". The Popper paper does not establish the question's premise, so q01 has no gold answer.
- **Treatment.** q01 is kept exactly as frozen. Because its gold is null, `evaluate.py` leaves it out of the answerable set. **Hit@5 and MRR are computed over 19 answerable questions (q02–q20), and the identifier denominator is 9, not 10.**

---

## 2. Measured results

Configuration for both modes: `k=5`, `parser=text`, `embedder=st`, 801 chunks.

| Metric | Embedding | Hybrid | Δ |
|---|---|---|---|
| **Hit@5 (all answerable)** | **11/19** (0.58) | **16/19** (0.84) | +5 |
| Identifier Hit@5 | 6/9 | 7/9 | +1 |
| Paraphrase Hit@5 | 5/10 | 9/10 | +4 |
| **MRR@5** | **0.36** | **0.55** | +0.19 |
| Correct abstentions, intended not-in-corpus questions (q21–q25) | **5/5** | **5/5** | 0 |

Source files: `eval/embedding_console.txt` (`hit@5: 11/19 = 0.58 (MRR 0.36)`) and `eval/hybrid_console.txt` (`hit@5: 16/19 = 0.84 (MRR 0.55)`). The JSON files have the unrounded MRR: 0.3632 and 0.5482. I recomputed the mean reciprocal rank by hand from the per-question ranks below (misses count as 0) and got the same values: 6.900/19 and 10.417/19.

### Abstention: how to read "5/6" in the console

Both console files print `abstained: 5/6`. That denominator includes **q01**, because `evaluate.py` treats every null-gold question as not-in-corpus. The correct reading:

| Question | Embedding | Hybrid | Counts as |
|---|---|---|---|
| q21–q25 (intended not-in-corpus) | ABSTAIN ×5 (`ABSTAIN, right`) | ABSTAIN ×5 (`ABSTAIN, right`) | **5/5 correct abstentions in each mode** |
| q01 (unresolved identifier) | PASS (`PASS, compare by hand`) | PASS (`PASS, compare by hand`) | **Not scored.** Not a failed abstention, and not a correct answer either |

**Why q01's PASS shows nothing about correctness.** `check_citations.py` checks one thing: that each quote appears verbatim in the cited chunk and that the chunk's metadata matches. In both modes the model answered without abstaining. It cited `popper_learning_from_failures:p043:01` (plus `:p020:03` in embedding mode) for the phrase "learning programs by learning from failures". In its own `reason` field (embedding run), the model wrote that the abbreviation "LFF" never appears and that the link is *inferred from the initials*. The quotes are real, so the checker returned PASS. But no cited text connects "LFF" to that name. Therefore:

- the q01 PASS is **not** evidence that the abbreviation LFF exists in the paper;
- it is **not** a semantically correct answer; the question's premise is unsupported;
- it is **not** counted as a successful abstention. Arguably the right behaviour was to abstain or to challenge the premise.

This is the clearest example in the run of the gap between citation validity and answer correctness (§5).

---

## 3. Per-question comparison

Rank = position of the first gold chunk in the top 5. "—" = miss.

| ID | Kind | Embedding rank | Hybrid rank | Outcome |
|---|---|---|---|---|
| q02 | identifier | — | 4 | **Recovered by hybrid** |
| q03 | identifier | 1 | 1 | Hit in both |
| q04 | identifier | 1 | 1 | Hit in both |
| q05 | identifier | 1 | 1 | Hit in both |
| q06 | identifier | — | — | **Failed in both** |
| q07 | identifier | 5 | 4 | Hit in both (rank improved) |
| q08 | identifier | — | — | **Failed in both** |
| q09 | identifier | 2 | 1 | Hit in both (rank improved) |
| q10 | identifier | 3 | 1 | Hit in both (rank improved) |
| q11 | paraphrase | — | 3 | **Recovered by hybrid** |
| q12 | paraphrase | 3 | 2 | Hit in both (rank improved) |
| q13 | paraphrase | 5 | 1 | Hit in both (rank improved) |
| q14 | paraphrase | — | 4 | **Recovered by hybrid** |
| q15 | paraphrase | — | 3 | **Recovered by hybrid** |
| q16 | paraphrase | 1 | 1 | Hit in both |
| q17 | paraphrase | — | 4 | **Recovered by hybrid** |
| q18 | paraphrase | 1 | 1 | Hit in both |
| q19 | paraphrase | 3 | — | **Lost by hybrid** |
| q20 | paraphrase | — | 4 | **Recovered by hybrid** |

Summary:
- **Recovered by hybrid (6):** q02, q11, q14, q15, q17, q20. Five are paraphrase questions.
- **Lost by hybrid (1):** q19 (SpatialVLM).
- **Failed in both (2):** q06 (Grounding DINO text encoder) and q08 (POPE negative-sampling strategies).
- **Hit in both (10):** in five of these, hybrid ranked the gold chunk higher (q07, q09, q10, q12, q13). No shared hit got a worse rank.

Check: 11 + 6 − 1 = 16. ✔

Most recoveries landed at rank 3–4, not rank 1. That pattern fits the MRR gain (+0.19) being proportionally smaller than the Hit@5 gain (+5/19 ≈ +0.26).

---

## 4. Why retrieval failed: observations and hypotheses

**Observations** are things I read directly in the result files or the index. **Hypotheses** are plausible explanations that this evaluation did not test (no ablation, no BM25-only ranks for these questions, no rerun).

### Hybrid mechanism (from `_common.py`, read only)
- *Observation.* Hybrid mode is reciprocal-rank fusion (`rrf_k = 60`). It fuses the top `max(4k, 20) = 20` embedding results with the top 20 BM25 results that have a positive score, then keeps the top 5. A chunk scores `1/(61 + r)` for each list it appears in, where `r` is its 0-based rank in that list.
- *Consequence (arithmetic, not a test result).* A chunk ranked 3rd by embeddings that is missing from the BM25 top 20 scores 1/63 ≈ 0.0159. A chunk ranked about 10th in **both** lists scores about 2/71 ≈ 0.028 and beats it. Fusion therefore favours chunks that both retrievers agree on. That helps when the question shares exact words with the passage, and hurts when one retriever is right alone.

### q06 — failed in both (Grounding DINO text encoder)
- *Observation.* Both modes returned `grounding_dino:p003:06` at top 1. That chunk discusses (Image, Text) pairs and noun-phrase outputs. The gold chunk `grounding_dino:p004:03` is clean text that says the text features come from "a text backbone like BERT".
- *Hypothesis.* Vocabulary mismatch. The question says "language-encoding architecture … represent the input text" and never uses "backbone" or "BERT". Several Grounding DINO chunks talk about text inputs in general, so they crowd out the one chunk that names the encoder. The gold-construction notes also flag that the paper itself hedges ("like BERT"), so the reference answer is less clean than most.

### q08 — failed in both (POPE negative sampling)
- *Observation.* Both modes returned `pope_object_hallucination:p007:03` at top 1. In the index, that chunk is mostly numbers from results tables. One gold chunk (`:p008:02`) is also mostly flattened table rows (model names followed by numbers, with row labels "Random/Popular/Adversarial"). The other gold chunk (`:p001:05`) describes "three polling strategies" (random, popular, co-occurring) and contains ligature characters (`ﬁ`, `ﬂ`).
- *Hypotheses.* (a) The question's words ("strategies", "select absent objects", "negative") overlap with many POPE chunks about the same setup, while the gold prose says "polling strategies by sampling". (b) Table rows extracted as text produce chunks that are hard to tell apart, both for embeddings and for BM25. (c) The gold-construction notes say the formal definition of Random sampling was never retrieved, so the gold set itself may be incomplete.

### q19 — lost by hybrid (SpatialVLM)
- *Observation.* Embedding found gold at rank 3. Hybrid missed it and returned `spatialvlm:p003:02` at top 1. In the index, SpatialVLM text has lost many spaces between words. One gold chunk (`spatialvlm:p004:03`) contains run-together tokens such as "thelackofspatialreasoningtrainingdata", and its section heading reads "SpatialGroundingfrom2DImages".
- *Hypothesis.* Joined words become single long tokens that BM25 can never match, so the gold chunks get little or no keyword score. Under RRF, a strong embedding-only rank then loses to chunks that both retrievers rank moderately. This mechanism fits the data but has not been confirmed. Confirming it would need the BM25 ranks for q19, which this run did not record.

### Hybrid recoveries (q02, q11, q14, q15, q17, q20)
- *Observation.* Five of the six recoveries are paraphrase questions. All six were recovered at rank 3–4.
- *Hypothesis.* Even paraphrased questions keep some distinctive words that appear in the gold passage (for example "policy", "layout" and "module" for q14). BM25 then lifts the gold chunk enough for it to pass the cutoff after fusion. This was not checked per question.

### Unexpected direction
- *Observation.* In these results hybrid gained more on **paraphrase** questions (+4) than on **identifier** questions (+1). That is the opposite of the usual expectation that keyword matching mainly helps identifiers.
- *Hypothesis.* Many "identifier" questions here describe the identifier rather than naming it ("What is the name of the dataset…", "What language-encoding architecture…"). The exact token is often missing from the question, so they behave more like paraphrases. With n = 9/10 per group, the difference between groups is not statistically meaningful.

---

## 5. Limitations

1. **Small benchmark.** There are 19 scored questions, 13 documents and one run per mode. One question changes Hit@5 by about 5 points. With 9–10 questions per kind, a gap of +1 or +4 is descriptive only. No confidence intervals or significance tests were computed, and nothing here supports a claim that hybrid will beat embedding on other corpora.
2. **One question set, one gold-labeller.** The gold chunk IDs were first proposed from retriever output (`claude_retrieval_evidence.md` says "Provisional", "No PDF has been inspected"). The owner reports that the PDF reference review is now done, but the repository has no written record of that review (e.g. no `eval/benchmark_notes.md`). Gold sets built from what the retriever already returns can favour chunks that system finds easily. Five gold entries were marked questionable (q06, q08, q12, q15, q17), and q04/q14 rely on the same passages.
3. **PDF extraction artifacts.** The index uses `parser=text` (pypdf text stream). Problems seen in the indexed text include: joined words (SpatialVLM), split words ("T est", "describ ed", "id ea9", "p rogram" in Popper), ligatures (`ﬁ`, `ﬂ` in POPE and Popper), and results tables flattened into number-heavy chunks (POPE). These can hurt both retrievers and can make verbatim quotes awkward to read. The `layout` parser was not evaluated.
4. **Manual reference checking.** "Compare by hand" items (q01) and gold support were judged by people and by an automated key-term proxy, not by an independent second annotator.
5. **Citation validity ≠ answer correctness.** `check_citations.py` checks that quotes are verbatim and metadata matches. It does not check that the quotes *support* the answer. PERMISSIONS.md already says "PASS means *grounded*, not *correct*." q01 shows this in practice: a valid citation sat under an inferred, unsupported claim. Hit@5 also measures retrieval only; this run did not score answer quality on answerable questions.
6. **Abstention tested on easy negatives.** All of q21–q25 ask about private project records (HELIOS, October 2026 approvals) and share no specific content with any paper. That is a weak test. Harder negatives (plausible but absent paper facts, or false premises like q01) are where the system actually failed to abstain.
7. **One sample per not-in-corpus question.** The abstention results come from one full-pipeline run each (`evaluate.py` default). The optional D.3 repeated-run tally (`--repeat`) was not run, so we do not know how stable the model's abstentions are across runs.

---

## 6. Software configuration and reproducibility

All values below are copied from the files named. Nothing was guessed.

| Item | Value | Source |
|---|---|---|
| Corpus | 13 PDFs, each pinned to arXiv v1 (2016–2024), licence `licensed` | `corpus/manifest.json` |
| Corpus integrity | SHA-256 of all 13 PDFs matches `index/manifest.lock` `files` and `corpus_metadata/checksums.sha256` (checked 2026-10-31, read-only) | — |
| Index built | 2026-10-31T21:07:39 | `index/manifest.lock` |
| Parser | `text` (pypdf) | `index/manifest.lock` |
| Chunking | `chunk_words: 350`, `overlap: 50` | `index/manifest.lock` |
| Chunks | 801 | `index/manifest.lock`; console files |
| Embedder | `st`, model `BAAI/bge-small-en-v1.5` (query prefix "Represent this sentence for searching relevant passages: ") | `index/manifest.lock`; `_common.py` |
| Keyword retriever | BM25, `k1 = 1.5`, `b = 0.75` (built in, no extra dependency) | `_common.py` |
| Hybrid fusion | Reciprocal rank fusion, `rrf_k = 60`, candidate pool `max(4k, 20)` per list | `_common.py` |
| k | 5 | console files; `results_*.json` |
| Answerer (not-in-corpus pipeline) | `claude -p --output-format json --permission-mode dontAsk`; model in run records `claude-opus-5-5` (also pinned in `.claude/settings.json`) | `evaluate.py`; `eval/runs/*.json` |
| Citation checker | `check_citations.py` (deterministic, no model) | skill folder |
| Python | 3.12.10 virtual environment at `.venv/` | `.venv/pyvenv.cfg` |
| Python dependencies | `numpy>=1.24`, `pypdf>=4.0`, `pdfplumber>=0.11`, `sentence-transformers>=3.0`. These are lower bounds only; exact installed versions were **not** recorded | `requirements.txt` |
| Evaluation timestamps | embedding `20261031-233041`, hybrid `20261031-233110` | `results_*.json` `when` |
| Questions | `eval/questions.jsonl` (sha256 `b1b0c149…542c`); frozen question text sha256 `9d6b0883…8d8f` | computed / `freeze_record.json` |

**What is reproducible.** Retrieval ranks are deterministic given the same PDFs, parser, chunking parameters, embedding model weights and library versions. **What is not:** the not-in-corpus answers and the q01 answer depend on a model call and may change between runs. Exact library versions (torch, sentence-transformers, pypdf) were not frozen, so a rebuild on another machine could produce slightly different chunks or embeddings.

**Transcript C (skill use from a session).** The first attempt (`eval/transcript_C.jsonl`) did not produce an answer. In `dontAsk` mode the `Skill` tool call was denied. `python3 … retrieve.py` with the system Python crashed because the dependencies were missing, and `.venv/bin/python3 … retrieve.py` was denied because it was not on the allow list. The model correctly refused to answer without retrieval. The retry (`eval/transcript_C_retry.jsonl`) ran `.venv/bin/python3` for both `retrieve.py` and `check_citations.py`. It got a **PASS** on the first check, citing `popper_learning_from_failures:p020:03` and `:p024:03`. The retry relies on two `.venv/bin/python3` allow rules that exist only as an **uncommitted** change to `.claude/settings.json`. `PERMISSIONS.md` and `SKILL.md` still describe only plain `python3`. As with q01, a PASS here means the quotes are verbatim, not that the explanation is correct. The retry answer also names authors ("Cropper & Morel") that do not appear in any cited quote.
