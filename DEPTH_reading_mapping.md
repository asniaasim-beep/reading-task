# Reading → dependency mapping (adapter spec)

**Status:** specification only. No engine, no scheduler. This is a bounded adapter over the
existing composer (backward route construction, prerequisite-first execution, exact-basis reuse,
support checks, selective reopening). Interface names below are placeholders pending the
composer's actual API.

**Revision 2** — §3 rewritten (reopening cannot establish edges; three perturbation types;
support-set read-out), §6 split into three cost components, §7 relevance redefined against the
question.

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

## 3. Probing proposed structure

### Reopening follows edges; it cannot establish them

Selective reopening propagates along **registered** dependencies. It answers *does a change travel
this edge*, which presupposes the edge exists. Using it to establish that edge is circular — the
machinery confirms what was registered, not what is warranted. Testing whether an existing
connection propagates is a different operation from discovering that connection.

A proposed edge `B → A` is therefore tested by **re-evaluating the altered material
independently**: recompute A's support from the perturbed material with the proposed edge withheld
from the structure used for that re-evaluation. Propagation is what gets tested afterwards, once
an edge is registered on independent grounds.

### Three distinct perturbations

| operation | what it does | what it can show |
|---|---|---|
| **remove evidence** | B deleted from the material | whether A's support drew on B at all |
| **negate** | ¬B asserted in B's place | whether contrary evidence conflicts with A. Not equivalent to removal: it can supply support for a rival conclusion rather than merely withdrawing support for A |
| **intervene** | B set irrespective of its own antecedents, severing B's incoming edges | whether the relation is causal rather than evidential — removal and negation cannot separate a causal edge from a shared antecedent |

These are not interchangeable and the probe log must record which was used.

### Read the support set, not the conclusion

An unchanged conclusion does not mean the perturbed node was inert. Two witnesses confirm a parcel
arrived; remove one and the conclusion stands on the remaining witness, with weaker support. The
removed witness still mattered.

The criterion for registering `B → A` is a change in A's **support set or support strength**, not a
change in A's conclusion. Record per probe:

- conclusion: same / changed
- supporting set: members lost or gained
- support strength: before / after

An engine reading only conclusion-stability will score redundantly-supported dependencies as
absent, and will mistake "still true" for "never mattered".

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
Successful calculation calls alone are not the cost.

Report the budget **split three ways** — they do not behave alike, and collapsing them hides the
prediction:

| component | covers | expected across rungs 1→5 |
|---|---|---|
| initial interpretation | reading, proposition extraction, first-pass support assessment | **rises** |
| planning | route construction, ordering | rises modestly at most |
| downstream recomputation | work triggered in dependents once the material is interpreted | **flat** for a relevance-recognizing engine |

Interpretation rises because determining that something is irrelevant is itself work: the escalated
material has to be read and assessed before it can be set aside. Recognition is paid for.

So the mechanism-specific prediction sits on the third row only, and **total cost slope is
expected to be positive**. Predicting flat total cost from relevance would be wrong.

A salience-driven engine is expected to show rising *downstream recomputation*, because escalation
draws work the material does not warrant.

## 7. Comparisons

- **C1 — same supported answer, less total work.** Unbounded semantics equal, §6 budget lower.
- **C2 — better answer under equal budget.** Anytime curves under a fixed cap, not unbounded runs.
- **C3 — correct revision.**

  **Relevance is defined against the question being asked**, not against a preselected root. A
  perturbation is relevant iff it changes what is warranted *as an answer to that question*. The
  same edit can be relevant to "why was the delivery late" and irrelevant to "how did the driver
  feel about it". Relevance is therefore a property of the question–material pair, fixed before
  the run, and never derived from whichever node the engine or the theory calls root.

  Paired perturbations per scenario:
  - *relevant* ("the driver left two hours late") → supported answer should change
  - *irrelevant* ("I'm terrible at my job", escalated) → supported answer should hold

  Score against §3's support-set read-out, not conclusion identity: a perturbation that leaves the
  conclusion standing on reduced support counts as a change in support, not as no effect.

  Report sensitivity **and** specificity. An engine that never updates scores perfectly on
  stability and fails the task; one that updates on everything is a salience engine.
  C3 is the discriminating comparison.

## 8. Items — gap in the current study

`reading_study_engine.html` is one vignette (Anna / birthday), 2 frames × 5 rungs. In C3 terms
it has **only the irrelevant-perturbation arm**. There is no relevant-perturbation arm, so it
cannot measure sensitivity, only stability — which is the half an inert engine passes for free.

A second caution now that §7 fixes relevance to the question: the study asks *which sentence is
most important*, and it is not established that affective escalation is irrelevant to that
question — that is partly what the study measures. The delivery scenario is cleaner as an
irrelevance arm because *why was the delivery late* has a determinate relation to the edit.
The Anna arm should not be assumed to be an irrelevant perturbation; it is a candidate one.

Needed before generalizing about human reading:
- multiple scenarios (the delivery item is #2)
- each with a matched relevant / irrelevant perturbation pair, relevance fixed per question
- independent judgments per scenario

## Open — needs the composer

- can material be re-evaluated with a nominated edge withheld from the structure, or does
  evaluation always run against the full registered graph?
- are removal, negation and intervention separable operations, or is there only one edit path?
- are support sets and support strength exposed per conclusion, or only conclusions?
- actual signatures for route construction and support check
- whether exact-basis reuse keys can accept text-derived nodes unchanged
