# Research plan — Grounding-first industrial safety reasoning
**William Welch · AM/ME/CE 295 · November 1, 2026**

## Research question and scope
Does an LLM agent that adaptively selects visual models, grounding configurations and semantic constructions produce more correct grounded predicates than a fixed troubleshooting policy using the same tools and resources? Does the difference persist in the generalization of safety rules learned from those predicates?

The first agent decision is upstream semantic grounding. An unverified image description is not a logical fact. The agent may select a bounded intervention, but it may not set the definition of success, edit reference labels or declare its own repair correct. The initial setting is offline industrial images or short video windows. Robot actuation, deployment approval and safety certification are outside this stage.

The completed digest and literature-retrieval modules are supporting infrastructure. The integrated grounding-repair loop, its verifier, fixed-policy comparator and held-out comparison have not yet been implemented or evaluated in this capstone.

## Stage 1 — Define the task and verification contract
Specify a finite set of observable predicates, entity types and allowed argument bindings. Every candidate predicate carries a scene/frame identifier, entity identifiers, supporting region or mask, source model/configuration and an uncertainty state. Absence of evidence is not automatically evidence that a predicate is false.

Construct reviewed development annotations for objects, masks and the selected relations. Ambiguous or occluded cases receive an explicit unresolved label. Split by capture group rather than adjacent frames, before development, to reduce near-duplicate leakage. Keep a separate held-out split whose labels and metrics never enter the agent's working context or durable memory.

Before the comparison, freeze the acceptance specification: object-match criteria, mask/box overlap requirements, binding rules, predicate-label agreement, the minimum accepted precision, resource limits, no-progress limit and number of repeats. These values have not yet been selected. They must be justified using task requirements and development annotation quality, not chosen by the agent or tuned on held-out results.

## Stage 2 — Implement bounded action selection
The available actions are declared in advance: switch among approved candidate models; change an allowed text prompt; change an allowed segmentation prompt or threshold; adjust a permitted semantic/predicate construction; request a diagnostic; or stop and escalate. Training a new model, expanding permissions, changing the verifier or accessing an unapproved service is not an ordinary action.

The decision agent reads the scene/task specification, candidate outputs, current development diagnostics, prior permitted actions and remaining budget. It returns an action record containing the run/scene IDs, configuration identifier, one allowed action, parameters, evidence references, intended diagnostic effect and stop/escalation status. The executor validates this record before running anything.

The executor returns artifact identifiers, measurements and resource use. An independent verifier compares the result with the reviewed development references. The agent may use the feedback to choose its next action, but only verifier code can insert a fact into the accepted-predicate store. The action/result log is append-only. An unsuccessful intervention does not silently replace the best verified configuration.

The literature retriever may supply source-backed method assumptions or failure taxonomies. Its citation checker establishes quotation/metadata fidelity only; no paper citation verifies an observation in the current industrial scene.

## Stage 3 — Define the non-agent comparison
Use the same starting inputs, tool versions, candidate models, allowed changes and computational budget in both conditions. The primary baseline applies a fixed, preregistered troubleshooting order rather than LLM-selected actions. It receives the same permitted development feedback. Retain the initial, unmodified configuration as a second descriptive reference when available.

Do not make the baseline artificially weak by restricting its tool catalogue. Freeze the order and any deterministic tie-breaking before evaluation. Record actual calls, elapsed/GPU time and consumed budget, including failures. Repeated stochastic runs use recorded seeds or run identifiers where the model interface supports them; the repeat count is fixed before comparison. No repeated-run claim is made from the present literature benchmark.

## Stage 4 — Independent evaluation
Primary measures are grounded-predicate precision, recall and F1, entity-binding validity, box/mask overlap, false acceptance and accepted coverage. Report abstention and human escalation separately: rejecting every difficult case must not be credited as an unconditional improvement. A successful policy improves F1 at the same accepted-precision requirement and comparable resource use. Report per-scene paired results, dispersion across repeated runs and representative failures, not only a pooled average.

The development loop may use annotated development feedback. After choosing the policy/configuration, evaluate held-out scenes without feeding their label-derived scores back into the agent. Hold the downstream learner, rule language and its training/evaluation protocol fixed when comparing the safety rules induced from the two conditions' accepted predicates. Downstream precision, recall and F1 are secondary outcomes, distinct from grounding accuracy.

Independence here means the acceptance computation is not an LLM judgment. It still depends on the quality of the human reference labels. Cross-model agreement alone is not a ground-truth label.

## Stops and human oversight
Stop on independently verified acceptance, exhausted resources, the preregistered no-progress rule or unavailable evidence. Escalate if an action would exceed the declared catalogue, change a threshold, alter the verifier, require a new permission or leave a safety-relevant predicate unresolved. A human reviews changes to durable policy or project memory through a PR. Unaccepted predicates never enter the ILP input.

## Schedule and deliverables
| Date | Deliverable | Acceptance evidence |
|---|---|---|
| Nov 1 | Defined proposal and tested supporting modules | This report; digest/memory audit; fixed corpus; two-script trace; retrieval measurements |
| Nov 2–8 | Annotation protocol, typed interfaces and fixed action catalogue | Reviewed development sample; schema tests; recorded threshold/budget decisions |
| Nov 9–15 | One small grounding loop and fixed-policy baseline | End-to-end action/result trace; independent measurements; stop/escalation cases |
| Nov 16–22 | Connect the accepted-predicate store to a fixed rule learner | Provenance-preserving hand-off; binding/consistency checks; development comparison |
| Nov 23–29 | Frozen held-out and repeated-run study | Paired grounding/rule metrics, costs, failures, abstentions and limitations |

The intermediate dates are planned work, not completed experiments. Thresholds, resource caps, dataset size and repeat count remain protocol decisions to record before the study.

## Principal risks and mitigations
Poor relation annotations can invalidate a precise evaluator; retain ambiguous labels and audit disagreements. Limited compute can favor cheap actions rather than correct ones; compare equal budgets and record cost. The agent can overfit development cases; isolate capture groups and freeze evaluation criteria. A caption, citation or model consensus can look persuasive without being supported; preserve evidence provenance and require independent checks. The largest TA question is whether the proposed reference protocol and fixed-policy comparator are sufficiently strong for a defensible grounding-first study.
