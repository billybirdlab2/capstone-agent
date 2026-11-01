# Lab 5 Part D.1 — retrieval evidence for the frozen benchmark

Generated 2026-10-31 by Claude (Claude Code) for the owner. **Provisional.** Reference answers and gold chunk IDs below were proposed only from passages returned by `.claude/skills/code-retriever/retrieve.py` (hybrid mode, k=5, run with `.venv/bin/python3`). **No PDF has been inspected and no human verification has happened yet.** The page numbers listed are the index's `page` field, for later independent human checking.

- Questions: `eval/questions_frozen.jsonl` (sha256 `9d6b0883…8d8f`, unchanged). IDs, wording, order, and kinds are preserved exactly in `eval/questions.jsonl`.
- The previous (archived) benchmark and its results were not consulted. `evaluate.py` was not run. The corpus, index, settings, and skills were not modified.
- Retrieval pass 1 used the verbatim question. Pass 2 (where needed) used a targeted reformulation. Pass 3 (q01 only) used `--mode keyword`.

## Summary

| Category | Count |
|---|---|
| Answerable questions with fully supported reference answers | 19 |
| Answerable questions UNRESOLVED (answer/chunk_id null) | 1 (q01) |
| Supported, but with a questionable reference or framing (for human review) | 5 (q06, q08, q12, q15, q17) |
| not_in_corpus questions that retrieval suggests might be answerable | 0 of 5 |

## Per-question evidence

### q01 · identifier

**Question:** In the Popper paper, what is the expanded name of the ILP approach abbreviated LFF?

**Retrieval queries and top-5 chunk IDs:**

- pass 1 (hybrid): `In the Popper paper, what is the expanded name of the ILP approach abbreviated LFF?`
  - `popper_learning_from_failures:p043:01`, `popper_learning_from_failures:p004:02`, `popper_learning_from_failures:p004:03`, `popper_learning_from_failures:p044:06`, `popper_learning_from_failures:p031:02`
- pass 2 (hybrid): `LFF learning from failures abbreviation`
  - `popper_learning_from_failures:p016:02`, `popper_learning_from_failures:p001:01`, `popper_learning_from_failures:p002:02`, `popper_learning_from_failures:p044:06`, `popper_learning_from_failures:p048:02`
- pass 3 (keyword): `LFF`
  - *no results*

**Proposed reference answer:** *null (UNRESOLVED)*

**Supporting chunk IDs:** none. Candidate passages for human check: `popper_learning_from_failures.pdf` pp. 1, 2, 43.

**Notes:** **UNRESOLVED.** No retrieved passage contains the abbreviation "LFF". A keyword-mode search for `LFF` returned **zero** results across the whole index, so the token does not appear in the indexed text. The retrieved passages name the approach "learning programs by learning from failures" (`popper_learning_from_failures:p001:01`, `:p002:02`, `:p043:01`), but nothing ties that name to the abbreviation LFF. Answer and chunk_id are left null rather than inferring the expansion. **Human check:** search the PDF for "LFF". If it's absent, the question premise may be flawed (the questions are frozen, so flag it rather than edit it). If it's present, the parser probably lost it; add the page as gold.

### q02 · identifier

**Question:** What component of the Neuro-Symbolic Concept Learner converts a natural-language question into an executable symbolic program?

**Retrieval queries and top-5 chunk IDs:**

- pass 1 (hybrid): `What component of the Neuro-Symbolic Concept Learner converts a natural-language question into an executable symbolic program?`
  - `neurosymbolic_concept_learner:p001:01`, `neurosymbolic_concept_learner:p004:04`, `neurosymbolic_concept_learner:p002:03`, `neurosymbolic_concept_learner:p004:01`, `neurosymbolic_concept_learner:p026:01`

**Proposed reference answer:** The semantic parsing module, which translates the input natural-language question into an executable program in a domain-specific language (DSL).

**Supporting chunk IDs (PDF · page, for human check):**
- `neurosymbolic_concept_learner:p004:01` — `corpus/neurosymbolic_concept_learner.pdf` p. 4 (Figure 3: We treat attributes such as Shape and Color as neu)

**Notes:** Supported. `p004:01` states the semantic parsing module "translate[s] a question into an executable program" in a DSL. `p001:01` (abstract) says the model "translates sentences into executable" programs, but it doesn't name the component.

### q03 · identifier

**Question:** Which four object-property families are systematically varied in CLEVR scenes?

**Retrieval queries and top-5 chunk IDs:**

- pass 1 (hybrid): `Which four object-property families are systematically varied in CLEVR scenes?`
  - `clevr:p002:04`, `clevr:p004:02`, `clevr:p002:05`, `clevr:p002:02`, `clevr:p002:06`

**Proposed reference answer:** Shape (cube, sphere, cylinder), size (small, large), material (shiny metal, matte rubber), and color (eight colors).

**Supporting chunk IDs (PDF · page, for human check):**
- `clevr:p002:04` — `corpus/clevr.pdf` p. 2–4 (3. The CLEVR Diagnostic Dataset)

**Notes:** Supported directly: shapes, sizes, materials, colors (also lists the four spatial relationships, which are not object properties).

### q04 · identifier

**Question:** What kind of learning signal is used to train the policy that chooses module layouts in End-to-End Module Networks?

**Retrieval queries and top-5 chunk IDs:**

- pass 1 (hybrid): `What kind of learning signal is used to train the policy that chooses module layouts in End-to-End Module Networks?`
  - `end_to_end_module_networks:p005:03`, `end_to_end_module_networks:p006:04`, `end_to_end_module_networks:p003:01`, `end_to_end_module_networks:p002:01`, `end_to_end_module_networks:p004:02`
- pass 2 (hybrid): `policy gradient reinforcement learning layout policy reward answer loss`
  - `end_to_end_module_networks:p005:02`, `end_to_end_module_networks:p005:03`, `end_to_end_module_networks:p006:08`, `constrained_policy_optimization:p008:06`, `constrained_policy_optimization:p001:01`

**Proposed reference answer:** Reinforcement learning: the layout policy is trained with a policy-gradient method that minimizes the expected final question-answering (softmax) loss of the assembled network; it can optionally be initialized by behavior cloning from an expert layout policy.

**Supporting chunk IDs (PDF · page, for human check):**
- `end_to_end_module_networks:p005:02` — `corpus/end_to_end_module_networks.pdf` p. 5–6 (3.3. End-to-end training)
- `end_to_end_module_networks:p005:03` — `corpus/end_to_end_module_networks.pdf` p. 5–6 (3.3. End-to-end training)

**Notes:** Supported. `p005:02` says the non-differentiable layout policy is optimized with the "policy gradient method in reinforcement learning" on the expected question-answering (softmax) loss. `p005:03` adds optional behavior cloning from an expert policy before RL fine-tuning.

### q05 · identifier

**Question:** In Visual Genome, what three elements constitute an annotated relationship between two objects?

**Retrieval queries and top-5 chunk IDs:**

- pass 1 (hybrid): `In Visual Genome, what three elements constitute an annotated relationship between two objects?`
  - `visual_genome:p027:01`, `visual_genome:p011:02`, `visual_genome:p001:05`, `visual_genome:p040:02`, `visual_genome:p037:02`

**Proposed reference answer:** A subject, an object, and a predicate linking them, written as predicate(subject, object), e.g. swinging(man, bat).

**Supporting chunk IDs (PDF · page, for human check):**
- `visual_genome:p027:01` — `corpus/visual_genome.pdf` p. 27 (5.5 Relationship Statistics)

**Notes:** Supported: relationships are "relationship(subject, object)" with subject, object, and predicate.

### q06 · identifier

**Question:** What language-encoding architecture does Grounding DINO use to represent the input text?

**Retrieval queries and top-5 chunk IDs:**

- pass 1 (hybrid): `What language-encoding architecture does Grounding DINO use to represent the input text?`
  - `grounding_dino:p003:06`, `grounding_dino:p007:03`, `grounding_dino:p005:01`, `grounding_dino:p012:01`, `grounding_dino:p005:03`
- pass 2 (hybrid): `Grounding DINO text backbone BERT image backbone Swin Transformer`
  - `grounding_dino:p008:02`, `grounding_dino:p003:06`, `grounding_dino:p003:07`, `grounding_dino:p009:09`, `grounding_dino:p004:03`

**Proposed reference answer:** A BERT text backbone (the paper says 'a text backbone like BERT') that extracts the vanilla text features.

**Supporting chunk IDs (PDF · page, for human check):**
- `grounding_dino:p004:03` — `corpus/grounding_dino.pdf` p. 4–5 (3.1. Feature Extraction and Enhancer)

**Notes:** Supported, with a hedge: the paper says "a text backbone **like** BERT" (`p004:03`). Human check: whether the paper specifies a particular BERT variant elsewhere (not retrieved).

### q07 · identifier

**Question:** What is the name of the large segmentation dataset introduced by Segment Anything?

**Retrieval queries and top-5 chunk IDs:**

- pass 1 (hybrid): `What is the name of the large segmentation dataset introduced by Segment Anything?`
  - `segment_anything:p025:01`, `segment_anything:p026:11`, `segment_anything:p001:01`, `segment_anything:p005:04`, `segment_anything:p027:24`

**Proposed reference answer:** SA-1B (about 1.1B masks on 11M images).

**Supporting chunk IDs (PDF · page, for human check):**
- `segment_anything:p005:04` — `corpus/segment_anything.pdf` p. 5–6 (4. Segment Anything Data Engine)
- `segment_anything:p005:06` — `corpus/segment_anything.pdf` p. 5–6 (4. Segment Anything Data Engine)

**Notes:** Supported: "our 1.1B mask dataset, SA-1B" (`p005:04`); "the resulting dataset, SA-1B" (`p005:06`).

### q08 · identifier

**Question:** What are the three strategies POPE uses to select absent objects for negative object-presence questions?

**Retrieval queries and top-5 chunk IDs:**

- pass 1 (hybrid): `What are the three strategies POPE uses to select absent objects for negative object-presence questions?`
  - `pope_object_hallucination:p007:03`, `pope_object_hallucination:p008:01`, `pope_object_hallucination:p010:01`, `pope_object_hallucination:p006:04`, `pope_object_hallucination:p007:01`
- pass 2 (hybrid): `random popular adversarial sampling objects not present in the image negative`
  - `pope_object_hallucination:p008:02`, `pope_object_hallucination:p007:01`, `pope_object_hallucination:p008:01`, `pope_object_hallucination:p007:02`, `pope_object_hallucination:p010:01`

**Proposed reference answer:** Random sampling; popular sampling (the top-k most frequent dataset objects that are absent from the image); and adversarial sampling (the top-k objects that most often co-occur with the ground-truth objects but are absent from the image).

**Supporting chunk IDs (PDF · page, for human check):**
- `pope_object_hallucination:p001:05` — `corpus/pope_object_hallucination.pdf` p. 1–3 (1 Introduction)
- `pope_object_hallucination:p008:02` — `corpus/pope_object_hallucination.pdf` p. 8–10 (5.2 Evaluation on MSCOCO)

**Notes:** Supported. `p001:05` names the three strategies (random, popular, co-occurring). `p008:02` defines Popular and Adversarial sampling as selecting objects that "do not exist in the image". The bullet that formally defines *Random* sampling was not retrieved; it probably directly precedes `p008:02` (end of p.7/8). Human check: confirm that page.

### q09 · identifier

**Question:** What is the name of the trainable bridging component between BLIP-2’s frozen image encoder and its language model?

**Retrieval queries and top-5 chunk IDs:**

- pass 1 (hybrid): `What is the name of the trainable bridging component between BLIP-2’s frozen image encoder and its language model?`
  - `blip2:p001:01`, `blip2:p006:01`, `blip2:p001:04`, `blip2:p008:04`, `blip2:p002:03`

**Proposed reference answer:** The Querying Transformer (Q-Former).

**Supporting chunk IDs (PDF · page, for human check):**
- `blip2:p002:03` — `corpus/blip2.pdf` p. 2 (3. Method)
- `blip2:p001:04` — `corpus/blip2.pdf` p. 1–2 (Figure 1. Overview of BLIP-2’s framework. We pre-train a)
- `blip2:p001:01` — `corpus/blip2.pdf` p. 1 ((start of document))

**Notes:** Supported: "Querying Transformer (Q-Former)" (`p002:03`, `p001:01`, `p001:04`).

### q10 · identifier

**Question:** What formal framework does Constrained Policy Optimization use to express reward optimization under cost limits?

**Retrieval queries and top-5 chunk IDs:**

- pass 1 (hybrid): `What formal framework does Constrained Policy Optimization use to express reward optimization under cost limits?`
  - `constrained_policy_optimization:p002:03`, `constrained_policy_optimization:p001:01`, `constrained_policy_optimization:p001:03`, `constrained_policy_optimization:p011:02`, `constrained_policy_optimization:p008:06`

**Proposed reference answer:** A constrained Markov decision process (CMDP): an MDP augmented with auxiliary cost functions C_i and limits d_i, where the policy maximizes expected return subject to each expected discounted cost J_Ci(pi) <= d_i.

**Supporting chunk IDs (PDF · page, for human check):**
- `constrained_policy_optimization:p002:03` — `corpus/constrained_policy_optimization.pdf` p. 2–3 (4. Constrained Markov Decision Processes)

**Notes:** Supported: Section 4, "Constrained Markov Decision Processes" (`p002:03`).

### q11 · paraphrase

**Question:** When searching for a correct logic program, how does Popper prioritize compact explanations rather than simply accepting an arbitrarily complex consistent program?

**Retrieval queries and top-5 chunk IDs:**

- pass 1 (hybrid): `When searching for a correct logic program, how does Popper prioritize compact explanations rather than simply accepting an arbitrarily complex consistent program?`
  - `popper_learning_from_failures:p024:02`, `popper_learning_from_failures:p033:02`, `popper_learning_from_failures:p020:03`, `popper_learning_from_failures:p032:02`, `popper_learning_from_failures:p030:01`
- pass 2 (hybrid): `optimal solution smallest program minimal number of literals increasing size`
  - `popper_learning_from_failures:p007:03`, `popper_learning_from_failures:p032:01`, `popper_learning_from_failures:p042:03`, `popper_learning_from_failures:p014:01`, `popper_learning_from_failures:p032:02`

**Proposed reference answer:** Popper searches programs in order of increasing size (total number of literals), starting from one literal and raising the bound only when the space at that size is exhausted, and it returns the first program that is complete and consistent. The result is therefore an optimal solution: no other solution has fewer literals.

**Supporting chunk IDs (PDF · page, for human check):**
- `popper_learning_from_failures:p020:03` — `corpus/popper_learning_from_failures.pdf` p. 20–21 (4 Popper)
- `popper_learning_from_failures:p014:01` — `corpus/popper_learning_from_failures.pdf` p. 14 (14 Andrew Cropper, Rolf Morel)
- `popper_learning_from_failures:p007:03` — `corpus/popper_learning_from_failures.pdf` p. 7–8 (2.4 Optimality)

**Notes:** Supported. `p020:03`: "To learn optimal solutions … Popper searches for programs of increasing size" (Algorithm 1 increments num_literals). `p014:01`: Definitions 13–14 define size as the total number of literals, and an optimal solution as one where no other solution is smaller. `p007:03`: Popper learns optimal solutions measured by literal count.

### q12 · paraphrase

**Question:** How can a system trained on visual concepts and question answering handle new combinations of familiar objects, attributes, or relations without retraining a separate classifier for each combination?

**Retrieval queries and top-5 chunk IDs:**

- pass 1 (hybrid): `How can a system trained on visual concepts and question answering handle new combinations of familiar objects, attributes, or relations without retraining a separate classifier for each combination?`
  - `neurosymbolic_concept_learner:p010:01`, `neurosymbolic_concept_learner:p006:02`, `neurosymbolic_concept_learner:p001:03`, `end_to_end_module_networks:p001:04`, `neurosymbolic_concept_learner:p010:02`
- pass 2 (hybrid): `generalization to new compositions of attributes combinatorial CoGenT`
  - `neurosymbolic_concept_learner:p007:06`, `clevr:p008:02`, `visual_genome:p011:03`, `neurosymbolic_concept_learner:p001:03`, `clevr:p006:03`

**Proposed reference answer:** In the Neuro-Symbolic Concept Learner, attributes are neural operators that map object representations into attribute-specific embedding spaces, and concepts (e.g., Red, Cube) are embeddings in those spaces. Questions are parsed into programs that compose these concepts and are executed symbolically. Because each attribute has a distinct representation space, the model generalizes to new compositions: on CLEVR-CoGenT it scores 98.8% on split A and 98.9% on split B, which reverses the color-shape pairings.

**Supporting chunk IDs (PDF · page, for human check):**
- `neurosymbolic_concept_learner:p007:06` — `corpus/neurosymbolic_concept_learner.pdf` p. 7–8 (4.3 G ENERALIZATION TO NEW ATTRIBUTES AND COMPOSITIONS)
- `neurosymbolic_concept_learner:p006:02` — `corpus/neurosymbolic_concept_learner.pdf` p. 6 (4.1 V ISUAL CONCEPT LEARNING)
- `neurosymbolic_concept_learner:p010:02` — `corpus/neurosymbolic_concept_learner.pdf` p. 10–17 (5 D ISCUSSION AND FUTURE WORK)

**Notes:** Supported, but **questionable reference**: the question names no paper. The evidence is from NS-CL (attributes as operators; CLEVR-CoGenT 98.8%/98.9%). Retrieval also surfaced N2NMN (`end_to_end_module_networks:p001:04`) on compositional structure. If the question was meant for a different paper, revisit the gold.

### q13 · paraphrase

**Question:** Why was CLEVR deliberately generated with controlled objects, questions, and answers instead of relying only on naturally collected image-question pairs?

**Retrieval queries and top-5 chunk IDs:**

- pass 1 (hybrid): `Why was CLEVR deliberately generated with controlled objects, questions, and answers instead of relying only on naturally collected image-question pairs?`
  - `clevr:p002:01`, `clevr:p002:02`, `clevr:p008:03`, `clevr:p002:04`, `clevr:p004:01`
- pass 2 (hybrid): `CLEVR minimizes biases questions answered without visual reasoning detailed annotations`
  - `clevr:p002:01`, `clevr:p001:03`, `clevr:p001:01`, `clevr:p008:03`, `clevr:p002:05`

**Proposed reference answer:** To minimize biases in prior VQA datasets that let systems answer correctly without visual reasoning (Clever Hans-style shortcuts), and to provide detailed ground-truth annotations (scene graphs and functional programs) for in-depth diagnostic analysis of specific reasoning skills. Question-conditional bias is reduced by rejection sampling within question families.

**Supporting chunk IDs (PDF · page, for human check):**
- `clevr:p002:01` — `corpus/clevr.pdf` p. 2 (2. Related Work)
- `clevr:p001:03` — `corpus/clevr.pdf` p. 1–2 (Figure 1. A sample image and questions from CLEVR. Questions)
- `clevr:p008:03` — `corpus/clevr.pdf` p. 8–10 (5. Discussion and Future Work)

**Notes:** Supported: minimize VQA biases that allow answering without visual reasoning; detailed annotations / functional programs for diagnostic analysis; rejection sampling within question families (`p001:03`).

### q14 · paraphrase

**Question:** When a visual question requires several reasoning operations, how can End-to-End Module Networks learn an appropriate computation sequence using supervision from final answers?

**Retrieval queries and top-5 chunk IDs:**

- pass 1 (hybrid): `When a visual question requires several reasoning operations, how can End-to-End Module Networks learn an appropriate computation sequence using supervision from final answers?`
  - `end_to_end_module_networks:p003:01`, `end_to_end_module_networks:p001:03`, `end_to_end_module_networks:p001:01`, `end_to_end_module_networks:p005:03`, `end_to_end_module_networks:p005:01`
- pass 2 (hybrid): `layout policy trained with reinforcement learning from question answering loss without expert layout`
  - `end_to_end_module_networks:p006:08`, `end_to_end_module_networks:p005:03`, `end_to_end_module_networks:p005:02`, `end_to_end_module_networks:p008:01`, `end_to_end_module_networks:p006:02`

**Proposed reference answer:** A layout policy (a sequence-to-sequence RNN) predicts a question-specific layout of module tokens, from which the network is assembled. Training minimizes the expected final question-answering loss over sampled layouts, using back-propagation for the differentiable parts and policy-gradient reinforcement learning for the discrete layout choice. This can optionally follow an initialization by behavior cloning from an expert layout policy.

**Supporting chunk IDs (PDF · page, for human check):**
- `end_to_end_module_networks:p005:02` — `corpus/end_to_end_module_networks.pdf` p. 5–6 (3.3. End-to-end training)
- `end_to_end_module_networks:p005:03` — `corpus/end_to_end_module_networks.pdf` p. 5–6 (3.3. End-to-end training)

**Notes:** Supported (overlaps with q04's evidence): seq2seq layout policy plus expected-loss minimization via policy gradient and back-propagation (`p005:02`); behavior-cloning initialization, then end-to-end RL (`p005:03`; `p006:08` describes the same two stages on CLEVR).

### q15 · paraphrase

**Question:** If a safety engineer provides a novel equipment description as text, how does Grounding DINO try to localize matching image regions without retraining a closed-set detector for that equipment type?

**Retrieval queries and top-5 chunk IDs:**

- pass 1 (hybrid): `If a safety engineer provides a novel equipment description as text, how does Grounding DINO try to localize matching image regions without retraining a closed-set detector for that equipment type?`
  - `grounding_dino:p002:03`, `grounding_dino:p001:02`, `grounding_dino:p003:06`, `grounding_dino:p007:03`, `grounding_dino:p009:09`
- pass 2 (hybrid): `open-set object detection fuse language and vision features detect arbitrary objects specified by text`
  - `grounding_dino:p002:02`, `grounding_dino:p002:04`, `grounding_dino:p001:02`, `grounding_dino:p002:03`, `grounding_dino:p002:05`

**Proposed reference answer:** It performs open-set detection with the text as an input prompt. A text backbone encodes the description, and image and text features are fused in three phases (a feature-enhancer neck, language-guided query selection, and a cross-modality decoder). The model outputs object boxes paired with the matching noun phrases, so novel categories can be detected zero-shot rather than only from a fixed label set.

**Supporting chunk IDs (PDF · page, for human check):**
- `grounding_dino:p002:04` — `corpus/grounding_dino.pdf` p. 2–3 (Figure 2. Existing approaches to extending closed-set detect)
- `grounding_dino:p002:05` — `corpus/grounding_dino.pdf` p. 2–3 (Figure 2. Existing approaches to extending closed-set detect)
- `grounding_dino:p003:06` — `corpus/grounding_dino.pdf` p. 3–4 (3. Grounding DINO)

**Notes:** Supported for the mechanism. **Note:** the "safety engineer / novel equipment" framing is a hypothetical; the paper doesn't discuss industrial equipment. The answer describes only the paper's general open-set detection mechanism. `p002:02` ("detect arbitrary objects specified by human language inputs") is also an acceptable alternative.

### q16 · paraphrase

**Question:** How does Segment Anything’s annotation workflow scale from hands-on human annotation toward producing a much larger collection of masks?

**Retrieval queries and top-5 chunk IDs:**

- pass 1 (hybrid): `How does Segment Anything’s annotation workflow scale from hands-on human annotation toward producing a much larger collection of masks?`
  - `segment_anything:p005:04`, `segment_anything:p001:01`, `segment_anything:p005:05`, `segment_anything:p022:02`, `segment_anything:p026:01`
- pass 2 (hybrid): `fully automatic stage regular grid of points ambiguity-aware masks`
  - `segment_anything:p005:05`, `segment_anything:p005:06`, `segment_anything:p019:08`, `segment_anything:p008:05`, `segment_anything:p001:04`

**Proposed reference answer:** Through a three-stage data engine. (1) Assisted-manual: annotators click points with SAM in the loop (4.3M masks on 120k images). (2) Semi-automatic: confident masks are pre-filled automatically and annotators add the missing objects (+5.9M masks), with SAM periodically retrained. (3) Fully automatic: SAM is prompted with a 32x32 point grid, keeping confident, stable masks after NMS. Stage 3 was applied to all 11M images, producing 1.1B masks (SA-1B).

**Supporting chunk IDs (PDF · page, for human check):**
- `segment_anything:p005:04` — `corpus/segment_anything.pdf` p. 5–6 (4. Segment Anything Data Engine)
- `segment_anything:p005:05` — `corpus/segment_anything.pdf` p. 5–6 (4. Segment Anything Data Engine)
- `segment_anything:p005:06` — `corpus/segment_anything.pdf` p. 5–6 (4. Segment Anything Data Engine)

**Notes:** Supported, with numbers taken verbatim from `p005:04`–`p005:06`.

### q17 · paraphrase

**Question:** Why can asking a vision-language model direct yes/no questions about whether objects are present reveal hallucination behavior that broad caption scoring may overlook?

**Retrieval queries and top-5 chunk IDs:**

- pass 1 (hybrid): `Why can asking a vision-language model direct yes/no questions about whether objects are present reveal hallucination behavior that broad caption scoring may overlook?`
  - `pope_object_hallucination:p001:04`, `hallusionbench:p003:04`, `pope_object_hallucination:p004:01`, `pope_object_hallucination:p006:01`, `pope_object_hallucination:p001:05`
- pass 2 (hybrid): `CHAIR metric unstable caption parsing polling-based yes or no questions`
  - `pope_object_hallucination:p006:01`, `pope_object_hallucination:p004:03`, `pope_object_hallucination:p004:04`, `pope_object_hallucination:p008:03`, `pope_object_hallucination:p007:02`

**Proposed reference answer:** Caption-based evaluation (e.g., CHAIR) is sensitive to instruction design, biased by caption length, and relies on hand-crafted parsing rules that can omit or misclassify objects. POPE instead asks direct Yes/No questions about sampled objects, including ones the model is prone to hallucinate. Those answers need no complex parsing, which makes the evaluation stable, fair, and flexible.

**Supporting chunk IDs (PDF · page, for human check):**
- `pope_object_hallucination:p007:02` — `corpus/pope_object_hallucination.pdf` p. 7–8 (5.1 Overview of POPE)
- `pope_object_hallucination:p006:01` — `corpus/pope_object_hallucination.pdf` p. 6 (Table 3: HRF @10 and HRC@10 results of LVLMs on)

**Notes:** Supported, with a slight framing mismatch: the paper argues caption-based metrics (CHAIR) are *unstable*, sensitive to instructions and caption length, and error-prone because of parsing rules. It doesn't literally say they "overlook" hallucinations. `p001:05` (yes/no polling, reduced parsing error) is an acceptable alternative.

### q18 · paraphrase

**Question:** Why does HallusionBench distinguish errors caused by misleading visual perception from those caused by a model relying on language priors or unsupported assumptions?

**Retrieval queries and top-5 chunk IDs:**

- pass 1 (hybrid): `Why does HallusionBench distinguish errors caused by misleading visual perception from those caused by a model relying on language priors or unsupported assumptions?`
  - `hallusionbench:p003:05`, `hallusionbench:p001:02`, `hallusionbench:p001:01`, `hallusionbench:p002:02`, `hallusionbench:p003:01`
- pass 2 (hybrid): `visual illusion language hallucination failure analysis diagnose`
  - `hallusionbench:p003:05`, `hallusionbench:p001:03`, `hallusionbench:p002:02`, `hallusionbench:p003:01`, `hallusionbench:p004:02`

**Proposed reference answer:** Because the two failure types have different causes. Language Hallucination comes from reasoning bias in the LLM's parametric memory (false prior assumptions about the input), while Visual Illusion is a misinterpretation of the visual input. Separating them gives a granular view of where and how LVLMs fail and points to different remedies: balancing parametric memory against image context versus improving visual capability.

**Supporting chunk IDs (PDF · page, for human check):**
- `hallusionbench:p003:05` — `corpus/hallusionbench.pdf` p. 3 (2.2 Taxonomies of Failure Types)
- `hallusionbench:p002:02` — `corpus/hallusionbench.pdf` p. 2 (2. We explore HALLUSION BENCH and provide a detailed in-dept)
- `hallusionbench:p001:03` — `corpus/hallusionbench.pdf` p. 1–2 (1 Introduction)

**Notes:** Supported: taxonomy in `p003:05`; causes (parametric-memory bias vs. visual misinterpretation) in `p002:02`; purpose ("granular view of where and how LVLMs stumble … paves the way for future enhancements") in `p001:03`. `p004:02` gives the per-type findings.

### q19 · paraphrase

**Question:** How can depth estimates and object-centered image annotations be converted into training signals for relative position and physical-scale reasoning?

**Retrieval queries and top-5 chunk IDs:**

- pass 1 (hybrid): `How can depth estimates and object-centered image annotations be converted into training signals for relative position and physical-scale reasoning?`
  - `spatialvlm:p003:02`, `spatialvlm:p002:02`, `spatialvlm:p019:06`, `neurosymbolic_concept_learner:p004:02`, `spatialvlm:p003:01`
- pass 2 (hybrid): `metric depth 3D point cloud synthesize spatial reasoning question answer data`
  - `spatialvlm:p004:03`, `spatialvlm:p019:05`, `spatialvlm:p004:01`, `spatialvlm:p003:02`, `spatialvlm:p006:01`

**Proposed reference answer:** In SpatialVLM, expert models extract object-centric segments and captions from images. Monocular metric depth estimation lifts the pixels to metric-scale 3D point clouds, which are canonicalized using horizontal-surface segmentation. 3D properties such as bounding boxes are then extracted, and templated question/answer generation synthesizes qualitative and quantitative spatial QA (about 2B pairs on 10M images), which is mixed with other VQA and captioning data for training.

**Supporting chunk IDs (PDF · page, for human check):**
- `spatialvlm:p004:03` — `corpus/spatialvlm.pdf` p. 4–5 (3.1. SpatialGroundingfrom2DImages)
- `spatialvlm:p006:01` — `corpus/spatialvlm.pdf` p. 6 (Figure 3| Example data entries from the synthetic dataset. G)
- `spatialvlm:p004:01` — `corpus/spatialvlm.pdf` p. 4 (Figure 2| Anoverview ofour datasynthesis pipeline.(a) We use)

**Notes:** Supported (SpatialVLM data-synthesis pipeline).

### q20 · paraphrase

**Question:** What purpose do multi-turn or complex-reasoning visual instructions serve beyond basic image captions when tuning an assistant to follow requests about images?

**Retrieval queries and top-5 chunk IDs:**

- pass 1 (hybrid): `What purpose do multi-turn or complex-reasoning visual instructions serve beyond basic image captions when tuning an assistant to follow requests about images?`
  - `visual_instruction_tuning:p002:01`, `visual_instruction_tuning:p001:02`, `visual_instruction_tuning:p005:02`, `visual_instruction_tuning:p002:05`, `visual_instruction_tuning:p015:01`
- pass 2 (hybrid): `conversation detailed description complex reasoning instruction-following data types`
  - `visual_instruction_tuning:p004:01`, `visual_instruction_tuning:p006:02`, `visual_instruction_tuning:p002:05`, `visual_instruction_tuning:p002:06`, `visual_instruction_tuning:p005:02`

**Proposed reference answer:** Simple caption-based instruction pairs lack diversity and in-depth reasoning. Conversation, detailed-description, and complex-reasoning data add multi-turn interaction and step-by-step reasoning. In the ablation, adding detailed-description and complex-reasoning data improved overall capability by about 7 points and also improved performance on conversational questions.

**Supporting chunk IDs (PDF · page, for human check):**
- `visual_instruction_tuning:p002:05` — `corpus/visual_instruction_tuning.pdf` p. 2–4 (3 GPT-assisted Visual Instruction Data Generation)
- `visual_instruction_tuning:p004:01` — `corpus/visual_instruction_tuning.pdf` p. 4 (Table 9 in the Appendix. For each image, we randomly sample )
- `visual_instruction_tuning:p006:02` — `corpus/visual_instruction_tuning.pdf` p. 6–7 (5.1 Multimodal Chatbot)

**Notes:** Supported. `p002:05`: simple caption-expanded instructions "lack diversity and in-depth reasoning". `p004:01`: the three data types (58K conversation / 23K detailed / 77K complex reasoning). `p006:02`: ablation shows +7 points overall and improved conversation performance.

### q21 · not_in_corpus

**Question:** Which candidate grounding model achieved the highest verified pixel-level mask IoU on our private HELIOS industrial-safety held-out set on October 31, 2026?

**Retrieval queries and top-5 chunk IDs:**

- pass 1 (hybrid): `Which candidate grounding model achieved the highest verified pixel-level mask IoU on our private HELIOS industrial-safety held-out set on October 31, 2026?`
  - `segment_anything:p005:06`, `segment_anything:p016:04`, `segment_anything:p019:08`, `segment_anything:p012:16`, `grounding_dino:p003:03`
- pass 2 (hybrid): `HELIOS held-out set mask IoU`
  - `segment_anything:p012:16`, `segment_anything:p016:03`, `segment_anything:p005:06`, `segment_anything:p022:02`, `segment_anything:p019:08`

**Gold:** answer = null, chunk_id = null (intended).

**Assessment:** Hits are SAM mask-IoU / thresholding passages and one Grounding DINO results passage. None mentions HELIOS, a private held-out set, October 2026, or a comparison of candidate grounding models on industrial data. **Not answerable from the corpus.** Distractor risk: a model might cite SAM's generic IoU results.

### q22 · not_in_corpus

**Question:** Which specific frame identifier in our internal industrial video collection had the highest false-positive hazard score in the October 2026 campaign?

**Retrieval queries and top-5 chunk IDs:**

- pass 1 (hybrid): `Which specific frame identifier in our internal industrial video collection had the highest false-positive hazard score in the October 2026 campaign?`
  - `segment_anything:p022:03`, `segment_anything:p026:02`, `segment_anything:p006:01`, `neurosymbolic_concept_learner:p022:02`, `segment_anything:p008:04`
- pass 2 (hybrid): `false-positive hazard score frame identifier industrial video`
  - `segment_anything:p027:33`, `segment_anything:p027:32`, `segment_anything:p027:34`, `segment_anything:p022:03`, `hallusionbench:p003:06`

**Gold:** answer = null, chunk_id = null (intended).

**Assessment:** Hits are the SAM datasheet (collection timeframe, annotator Q&A), SAM evaluation, and an NS-CL table. No industrial video, frame identifiers, or hazard scores. **Not answerable.**

### q23 · not_in_corpus

**Question:** What predicate-confidence acceptance threshold did our lab approve for its October 2026 industrial-safety grounding gate?

**Retrieval queries and top-5 chunk IDs:**

- pass 1 (hybrid): `What predicate-confidence acceptance threshold did our lab approve for its October 2026 industrial-safety grounding gate?`
  - `grounding_dino:p001:01`, `popper_learning_from_failures:p042:02`, `grounding_dino:p008:01`, `segment_anything:p027:14`, `grounding_dino:p015:01`
- pass 2 (hybrid): `predicate confidence acceptance threshold`
  - `segment_anything:p024:01`, `popper_learning_from_failures:p044:03`, `segment_anything:p019:08`, `popper_learning_from_failures:p004:04`, `segment_anything:p019:01`

**Gold:** answer = null, chunk_id = null (intended).

**Assessment:** Hits are Grounding DINO ablations, Popper sensitivity and predicate-invention sections, and SAM statistics. No lab-approved predicate-confidence threshold. **Not answerable.** Mild distractor risk: SAM's mask-stability threshold (0.5±δ) and Popper's "predicate invention" share vocabulary.

### q24 · not_in_corpus

**Question:** How many private October 2026 industrial-video annotations did our project team manually approve for deployment?

**Retrieval queries and top-5 chunk IDs:**

- pass 1 (hybrid): `How many private October 2026 industrial-video annotations did our project team manually approve for deployment?`
  - `segment_anything:p027:17`, `segment_anything:p027:15`, `segment_anything:p027:06`, `segment_anything:p027:16`, `segment_anything:p027:09`
- pass 2 (hybrid): `industrial video annotations manually approved for deployment`
  - `segment_anything:p027:15`, `segment_anything:p027:17`, `segment_anything:p027:05`, `visual_instruction_tuning:p002:05`, `segment_anything:p027:06`

**Gold:** answer = null, chunk_id = null (intended).

**Assessment:** Hits are the SAM data-annotation card (annotator quality and communication) and LLaVA data generation. No private October 2026 industrial-video annotations or approval counts. **Not answerable.** Distractor risk: SAM annotation counts (e.g., 4.3M masks).

### q25 · not_in_corpus

**Question:** Which exact safety-rule revision identifier did our project team approve during its October 31, 2026 research review?

**Retrieval queries and top-5 chunk IDs:**

- pass 1 (hybrid): `Which exact safety-rule revision identifier did our project team approve during its October 31, 2026 research review?`
  - `segment_anything:p026:13`, `segment_anything:p026:02`, `popper_learning_from_failures:p004:04`, `segment_anything:p027:06`, `popper_learning_from_failures:p044:03`
- pass 2 (hybrid): `safety rule revision identifier approved`
  - `popper_learning_from_failures:p050:03`, `constrained_policy_optimization:p002:01`, `segment_anything:p026:16`, `segment_anything:p026:13`, `grounding_dino:p007:06`

**Gold:** answer = null, chunk_id = null (intended).

**Assessment:** Hits are Popper references, CPO related work (safety constraints in RL), and the SAM datasheet (dataset use and export restrictions). No safety-rule revision identifiers or project review records. **Not answerable.**

## Unresolved or questionable references (for human review)

- **q01 — UNRESOLVED.** "LFF" doesn't occur anywhere in the index (keyword search returned zero results). Check `popper_learning_from_failures.pdf` for the abbreviation.
- **q06** — the paper hedges ("a text backbone like BERT"); confirm the exact text encoder.
- **q08** — the formal definition of *Random* sampling was not retrieved; check `pope_object_hallucination.pdf` pp. 7–8.
- **q12** — the question doesn't name a paper; the gold assumes NS-CL.
- **q15** — the industrial-equipment framing is hypothetical; the gold covers only the paper's general open-set mechanism.
- **q17** — the paper's rationale is instability and parsing error in caption metrics, which differs slightly from the question's "may overlook" framing.
- **q04 / q14** — both are answered by the same passages (`end_to_end_module_networks:p005:02`/`:p005:03`); the two questions overlap substantially.

## Potentially answerable negative questions

None. No retrieved passage for q21–q25 mentions HELIOS, October 2026, private/internal industrial video, hazard scores, approved thresholds, annotation approvals, or rule-revision identifiers. All five refer to private project records outside this published-paper corpus. Distractor risk (topically similar but non-answering passages) is noted for q21, q23, and q24.

## Validation performed (2026-10-31)

- 25 valid JSONL records; keys `id, kind, question, answer, chunk_id`; distribution 10 identifier / 10 paraphrase / 5 not_in_corpus.
- IDs, question text, kinds, and order exactly match `eval/questions_frozen.jsonl`; the frozen file's sha256 matches `freeze_record.json`.
- All non-null gold chunk IDs exist in `index/chunks.jsonl`; answer/chunk_id are null together for q01 and q21–q25.
- Support check: for each supported answer, its key terms (e.g., "SA-1B", "policy gradient", "Q-Former", "increasing size") were confirmed to appear in the text of its listed chunks (q13 after removing PDF line-break hyphens). This is an automated proxy plus my reading of the passages; it is **not** a human check against the PDFs.
