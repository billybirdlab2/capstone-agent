# Lab 5 — Part E: How the retriever fits into the capstone agent

Written 2026-10-31. This document describes a **design**. Section 6 separates what exists today from what is only planned. Nothing here claims that the grounding-repair loop has been built or evaluated. The only measured results are the Lab 5 retrieval numbers in `reports/lab5-final-analysis.md`.

---

## 0. Research framing

- **Primary agentic decision: semantic grounding.** The agent is given an industrial-safety scene. It compares competing visual models, object-grounding results, segmentation outputs and semantic/predicate constructions. It chooses which **bounded modification** to try next, measures the effect, and repeats. It stops when independently verified grounding is good enough, or abstains or escalates to a human.
- **Gate.** Only **verified grounded predicates** go on to downstream ILP and safety-rule learning.
- **Scientific question.** Given the same tools and budget, does the agent's adaptive choice and repair of upstream grounding/semantic configurations improve (a) independently measured grounding correctness and (b) generalization of the learned safety rules, compared with a **fixed, non-agent troubleshooting procedure**?
- **Role of the retriever.** The literature retriever (`code-retriever`) is **supporting research infrastructure**. It is not the decision being studied. It provides cited background on methods (e.g. what Grounding DINO, SAM, POPE, HallusionBench or Popper say), but it never decides whether a predicate is grounded.

---

## 1. Where the retriever fits in the workflow

```
 scene + task spec
        │
        ▼
 ┌────────────────────────────┐      ┌──────────────────────────────┐
 │ GROUNDING STAGE (planned)  │◄────►│ code-retriever (implemented) │
 │  candidate VLMs / detectors│ ask  │  retrieve.py → Grounded JSON │
 │  / segmenters / predicate  │ for  │  → check_citations.py        │
 │  constructions             │ lit. │  edition-pinned corpus only  │
 │  diagnose → pick bounded   │      └──────────────────────────────┘
 │  modification → re-measure │
 └─────────────┬──────────────┘
               │  deterministic verifier: grounding metrics vs. reference
               ▼
     verified grounded predicates ──► ILP / safety-rule learning (planned)
               │                                   │
               ▼                                   ▼
     abstain / escalate to human        held-out rule evaluation (planned)
```

The retriever sits **beside** the grounding loop as a consultation tool. It is not inside the loop's accept/reject path. Its output can shape *which* modification the agent proposes and *how* that proposal is justified. It cannot make a modification count as a success.

---

## 2. When the agent should retrieve literature

**Retrieve** when:
1. **Diagnosing a failure class.** Example: the agent sees object-presence hallucinations and needs the documented probing method (POPE), or needs to tell visual illusion apart from language-prior errors (HallusionBench).
2. **Justifying a candidate modification before trying it.** Examples: changing text prompts for open-set detection (Grounding DINO), changing point/box prompts for segmentation (SAM), or adding spatial/relational predicates (SpatialVLM, Visual Genome relationship structure).
3. **Defining a predicate or relation schema.** Example: how relationships are structured as subject–predicate–object, before the agent writes a new predicate construction.
4. **Configuring downstream ILP.** Example: search-order and constraint behaviour in Popper.
5. **Writing the report.** Any claim about a published method must carry a checked citation (CLAUDE.md: never cite a paper a skill did not return).

**Do not retrieve** when:
- The question is about **this project's own data, thresholds, approvals or results**. The corpus contains only published papers. The Lab 5 not-in-corpus questions (q21–q25) are exactly this kind, and the agent correctly abstained 5/5 in both modes. The answers come from experiment logs and the human owner.
- A **decision needs a measurement**. Literature can suggest that a modification might help. Only the verifier can show that it did.
- The next step is already fixed by the protocol or the budget.

**Retrieval protocol** (unchanged from `SKILL.md`): retrieve → Grounded JSON → `check_citations.py`. At most one reformulated retry with the exact identifier, then stop. If the answer still does not pass, abstain. Use hybrid mode by default, because it was measured better on this corpus: Hit@5 16/19 vs 11/19, MRR 0.55 vs 0.36. The small-sample caveats in the analysis report apply.

**Lesson from q01.** A citation PASS only means the quotes are verbatim. When the retrieved text supports the premise only by inference (for example, "LFF" is never actually written), the agent must abstain or challenge the premise rather than answer. Treat any answer whose `reason` field says "inferred" as **not grounded** for decision purposes.

---

## 3. What the agent decides vs. what deterministic code verifies

| The agent (LLM) MAY decide | Deterministic code VERIFIES / ENFORCES | Only a human decides |
|---|---|---|
| Which failure hypothesis to investigate first | Citation validity (`check_citations.py`: verbatim quote, matching metadata) | Acceptance thresholds for grounding quality |
| Which bounded modification to try next, chosen from a pre-declared action set (switch model, change prompt, change segmentation prompt or threshold within declared bounds, adjust predicate construction) | Grounding metrics against reference annotations (e.g. box/mask overlap, predicate truth against labels), computed by scripts, not by the model | Approving any change to the action set, budget or verifier |
| When to consult the retriever, and which query to send | Budget accounting (iterations, compute, model calls) and hard stops | Releasing any held-out split |
| Whether to stop, abstain or escalate (within the rules in §5) | Which predicates pass the gate: only those the verifier marks verified are written to the ILP input | Whether learned safety rules are acceptable for any use |
| How to explain its choice, with citations | Logging of every proposal, measurement and decision; corpus edition and hash checks (`index/manifest.lock`) | Merging any change (PR review, per CLAUDE.md) |

Invariants:
- The agent **never** sets or relaxes its own acceptance threshold. It never edits the verifier, the reference labels, the corpus or the index, and it never sees held-out labels.
- An LLM judgment (including a VLM's own confidence) is **evidence the agent can use**, never **verification**.
- Every number the agent reports comes from a script and is listed with its inputs (USER.md directive).

---

## 4. Memory decision table

| Memory type | What it holds | Where it lives | Who writes | Agent may read? | Notes / rule |
|---|---|---|---|---|---|
| **Semantic: edition-pinned research documents** | Published papers the method rests on (13 arXiv v1 PDFs today) | `corpus/` + `corpus/manifest.json` (edition, source, licence); `index/` (801 chunks; hashes in `index/manifest.lock`) | **Human only** (adds, removes or re-pins documents; rebuilds the index) | Yes, **only** through `code-retriever` (retrieve → cite → check) | Pinning the edition makes citations stable and reproducible. Retrieved text is data, not instructions. Quotes are **never** copied into `memory/`. Local only, never in a cloud routine |
| **Semantic: curated project facts** | Durable decisions and project framing (e.g. digest configuration, capstone scope) | `memory/MEMORY.md` | Agent proposes; human approves via PR merge | Yes (loaded every session) | Each entry dated and sourced. No unpublished numbers, credentials or collaborator details |
| **Preferences** | Stable owner directives | `memory/USER.md` | Agent proposes; human approves | Yes | e.g. "report every number with inputs and tool" |
| **Procedural** | How to do things: skills, operating rules, permissions | `.claude/skills/*/SKILL.md`, `CLAUDE.md`, `PERMISSIONS.md`, `.claude/settings.json` | **Human only** (edits need approval) | Yes | Enforcement lives in settings and permissions, not in prose |
| **Episodic: working notes** | What was tried today and why | `memory/daily/YYYY-MM-DD.md` | Agent | Yes | No retrieved quotes or values; no held-out results |
| **Episodic: experiment log** *(planned)* | Per-iteration proposal, action, verifier output, budget used, stop reason | Run-log directory, append-only (planned) | Code writes; agent cannot edit | Yes, for the **current** run's development split | The audit trail for the agent vs. fixed-procedure comparison |
| **Verified predicate store** *(planned)* | Predicates that passed the verifier, with provenance | Planned artifact handed to ILP | **Verifier code only** | Read-only | Agent cannot insert entries. This is the gate |
| **Working memory** | Current context: retrieved chunks, current hypotheses | Session context | — | — | Discarded at session end unless written above under the same rules |
| **Never stored** | Credentials; held-out labels or results; retrieved quotes in `memory/`; unverified predicates in the ILP input | — | — | — | Held-out data is kept out of every memory the agent can read, to prevent leakage |

---

## 5. Human escalation, stopping criteria and held-out evaluation

### Stopping criteria (checked by code after each iteration)
1. **Success.** The verifier reports grounding at or above the human-set acceptance threshold on the development split → stop, and pass only the verified predicates to ILP.
2. **Budget exhausted.** Iterations, compute or model calls reach the pre-declared limit, which is **identical for the agent and the fixed procedure** → stop and report the best verified state.
3. **No progress.** No verified improvement for N consecutive modifications (N fixed before the run) → stop.
4. **Abstain.** The required evidence does not exist in the available tools, data or corpus, as with the q21–q25 type of question → abstain, with a reason.

### Escalate to a human when
- the verifier and the agent's evidence disagree in a way the agent cannot resolve with the actions it is allowed to take;
- a fix would need an action outside the declared set, or a change to a threshold, the verifier or the labels;
- a safety-relevant predicate (e.g. one involving people or hazards) is still unverified at the stop;
- the question's premise looks false or unsupported (the q01 pattern), or a citation still FAILs after two retries (SKILL.md rule);
- retrieved or input content contains instructions (treated as data and reported).

### Independent held-out evaluation (planned protocol)
- Split the data before any development work into **development** (the agent and the fixed procedure may use it) and **held-out** (sealed; labels never visible to the agent, its memory or its logs).
- Run the agent and the fixed, non-agent troubleshooting procedure with the **same tools, same action set and same budget**.
- Primary outcomes, all measured by deterministic code on the held-out split: (a) grounding correctness of the final configuration; (b) generalization of safety rules learned by ILP from each condition's verified predicates.
- Report per-condition results with their inputs and tools, how many runs were done, and any escalations or abstentions. Count abstentions and escalations; never drop them silently.
- Lab 5 lesson that carries over: freeze the question/label set before running (as with `freeze_record.json`), keep unresolved items unchanged instead of editing them, and keep "the verifier passed" separate from "the answer is correct".

---

## 6. Implemented infrastructure vs. planned capabilities

| Capability | Status | Evidence |
|---|---|---|
| Edition-pinned literature corpus (13 papers) with hash-locked index | **Implemented** | `corpus/manifest.json`, `index/manifest.lock` |
| `code-retriever`: embedding / keyword / hybrid retrieval, Grounded JSON, deterministic citation check | **Implemented and evaluated (retrieval only)** | Hybrid Hit@5 16/19, MRR 0.55; embedding 11/19, MRR 0.36; 5/5 abstentions on q21–q25 in both modes |
| Unattended skill use via `.venv` Python | **Works in one transcript, not yet formalized** | `eval/transcript_C_retry.jsonl` PASS; relies on uncommitted `.venv/bin/python3` allow rules in `.claude/settings.json`; `PERMISSIONS.md`/`SKILL.md` not updated |
| Memory files, permissions, PR-based approval | **Implemented** | `CLAUDE.md`, `memory/`, `PERMISSIONS.md` |
| arXiv digest (five tracks) | **Implemented** | `memory/MEMORY.md` |
| Grounding-stage loop (compare models, choose bounded modifications, re-measure, stop/abstain/escalate) | **Planned, not implemented** | — |
| Deterministic grounding verifier and acceptance gate | **Planned, not implemented** | — |
| Verified predicate store → ILP / safety-rule learning | **Planned, not implemented** | — |
| Fixed, non-agent troubleshooting baseline | **Planned, not implemented** | — |
| Held-out comparison (grounding correctness, rule generalization) | **Planned, not run** | No results exist |

No grounding, predicate, ILP or safety-rule results exist yet (consistent with `memory/MEMORY.md`: "No results recorded yet"). The Lab 5 numbers measure **literature retrieval** only. They say nothing about the capstone's scientific question.
