# Reading → dependency mapping (adapter spec)

**Status:** specification only. No engine, no scheduler. This is a bounded adapter over the
existing composer (backward route construction, prerequisite-first execution, exact-basis reuse,
support checks, selective reopening). Interface names below are placeholders pending the
composer's actual API.

## Why this comes first

The executor consumes a dependency structure. For text input, nothing currently produces one.
If the structure is hand-supplied — labelling the causal sentence "root" and the self-blame
sentence "dependent" — the study's conclusion is encoded in its input.

So the mapping is the object under test, not scaffolding for it:

> Can DEPTH recognize warranted dependencies, or only execute dependencies we supplied?

## 1. Nodes

Propositions, not sentences. A sentence may carry a claim and a stance about that claim, and
those are different nodes. Keep a `sentence_id → [node_id]` map, because the study's response
unit is the sentence.

## 2. Edge types

The discriminating capability is telling the first of these from the second.

| type | relation | example |
|---|---|---|
| `support` | B is part of what makes A warranted | road closed → delivery late |
| `evaluative` | A is a stance *about* B, contributing no independent support | "I'm terrible at my job" |
| `background` | A holds context fixed for B | scene / neutral sentences |

Self-blame is `evaluative` at every rung. "The driver left two hours late" is `support`.
An engine that cannot separate these cannot do the task, whatever its graph looks like.

## 3. Warrant test — edges are earned, not labelled

An edge `B → A` is warranted iff perturbing B changes what is warranted about A.

Operationalize as a probe the engine runs itself: negate or substitute the candidate node and
re-run support checks on the downstream claim. Evaluative nodes fail — negating "I'm terrible at
my job" leaves "the delivery was late because the road closed" fully supported.

This reuses selective reopening and support checking as a *recognition* procedure rather than an
efficiency mechanism. No new execution machinery.

## 4. Read-out is separate from structure, and declared in advance

The adapter emits a graph. A distinct read-out function maps graph → predicted most-important
sentence. Candidate read-outs (pick and freeze **before** running):

- most-depended-upon node (max support out-degree)
- node whose removal most changes warrant elsewhere
- deepest fully-supported node

Keeping these separate is what prevents "root" from silently meaning "answer". If DEPTH only
tracks human judgment under one read-out, that is a result to report, not a parameter to tune.
It must remain possible for the graph to be correct and the human judgment to fall elsewhere.

## 5. Two independent ground truths — never merged

1. **Dependency key**: annotators blind to DEPTH, using the §2 rubric. Report inter-annotator
   agreement. Not labelled by anyone who holds the hypothesis.
2. **Importance judgments**: the Prolific study's `picked_role`.

Scoring against (1) tests the mapping. Scoring against (2) tests the claim about human reading.
A failure against (2) with a pass against (1) is informative, not a wash.

## 6. Cost accounting

Count as one budget: reading, graph construction, planning, verification, and calculation calls.
Successful calculation calls alone are not the cost. Report:

- total budget to first supported answer
- budget slope across rungs 1→5 (irrelevant escalation). Mechanism-specific prediction:
  **slope ≈ 0** for a relevance-recognizing engine, because the escalation is skippable.
  Rising cost is the salience-driven pattern.

## 7. Comparisons

- **C1 — same supported answer, less total work.** Unbounded semantics equal, §6 budget lower.
- **C2 — better answer under equal budget.** Anytime curves under a fixed cap, not unbounded runs.
- **C3 — correct revision.** Paired perturbations per scenario:
  - *relevant* ("the driver left two hours late") → explanation should change
  - *irrelevant* ("I'm terrible at my job", escalated) → explanation should hold

  Report sensitivity **and** specificity. An engine that never updates scores perfectly on
  stability and fails the task; one that updates on everything is a salience engine.
  C3 is the discriminating comparison.

## 8. Items — gap in the current study

`reading_study_engine.html` is one vignette (Anna / birthday), 2 frames × 5 rungs. In C3 terms
it has **only the irrelevant-perturbation arm**. There is no relevant-perturbation arm, so it
cannot measure sensitivity, only stability — which is the half an inert engine passes for free.

Needed before generalizing about human reading:
- multiple scenarios (the delivery item is #2)
- each with a matched relevant / irrelevant perturbation pair
- independent judgments per scenario

## Open — needs the composer

- actual signatures for route construction, support check, selective reopening
- whether exact-basis reuse keys can accept text-derived nodes unchanged
- whether the §3 probe can be expressed with existing reopening, or needs an adapter shim
