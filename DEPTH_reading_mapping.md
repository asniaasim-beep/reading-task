# Reading → dependency mapping (adapter spec)

**Status:** specification only. No engine, no scheduler. Bounded spec pass over the existing
composer (backward route construction, prerequisite-first execution, exact-basis reuse, support
checks, selective reopening).

**Revision 5** — §4 and §9 amended for the three negative-result scopes, derivation-level
admission and qualified reporting; `no_recorded_support` replaces `unsupported`.

**Revision 4** — §3, §4 and §10 amended for coverage, evidenced shared origin, and the
adapter/evaluator split; evaluator contract split out to `DEPTH_fresh_evaluator_contract.md`.

**Revision 3** — §3 corrected (text intervention ≠ world intervention; withholding must exclude
derived cache), §4 added (justification interface, alternative vs joint), §7 predictions made
conditional, §9 reduced to one redundant-support probe, §10 records what the runtime provides.

## Why this comes first

The executor consumes a dependency structure. For text input, nothing currently produces one.
If the structure is hand-supplied — labelling the causal sentence "root" and the self-blame
sentence "dependent" — the study's conclusion is encoded in its input.

> Can DEPTH recognize warranted dependencies, or only execute dependencies we supplied?

## 1. Nodes

Propositions, not sentences. A sentence may carry a claim and a stance about that claim; those are
different nodes. Keep a `sentence_id → [node_id]` map, because the study's response unit is the
sentence.

## 2. Edge types

| type | relation | example |
|---|---|---|
| `support` | B is part of what makes A warranted | road closed → delivery late |
| `evaluative` | A is a stance *about* B, contributing no independent support | "I'm terrible at my job" |
| `background` | A holds context fixed for B | scene / neutral sentences |

Separating the first two is the capability under test.

## 3. Probing proposed structure

### Reopening follows edges; it cannot establish them

Selective reopening propagates along **registered** dependencies. It answers *does a change travel
this edge*, which presupposes the edge. Using it to establish that edge is circular. Discovering a
dependency and updating a recorded one are different jobs.

A proposed edge `B → A` is tested by re-evaluating the altered material with that edge withheld.

### Withholding is not arrow removal

Withholding must exclude everything **derived from** the edge, not just the edge itself:

- the edge
- any cached conclusion whose justification mentions it (see §4)
- any annotation, label or summary produced while it was in force

Operationally: invalidate every cache entry whose justification intersects the withheld set. An
edge left out of the graph but alive in a cached intermediate has not been withheld.

But intersection is not sufficient for **discovery**. It handles removal from recorded positive
derivations; new contradictory information, a negation or an assumption change can matter without
intersecting the prior leaf set. Intersection-based invalidation is a propagation mechanism and
correct there. Discovery re-evaluates the changed material from scratch — evaluator contract §6.

### Three perturbations, and what each licenses

| operation | what it does | what it licenses |
|---|---|---|
| **withdraw** | leaf deleted from the material | whether the recorded justification drew on it |
| **negate** | ¬B asserted in B's place | not equivalent to withdrawal — it can supply support for a rival conclusion rather than withdrawing support for A |
| **intervene** | B set irrespective of its antecedents | a causal reading, *only under stated assumptions* — see below |

Two limits, both previously overstated here:

**Text intervention is not world intervention.** Editing "the road was closed" tests the reader's
response to changed information. It does not establish what opening the road would cause. Every
causal claim from a text edit is a claim about the reader, not about the world, unless separately
argued.

**Intervention is not the only route to a causal reading.** Observational identification is
available under explicit causal assumptions (Pearl's calculus — back-door, front-door). The
requirement is that any causal claim states its assumptions; the edit type alone does not confer
one, and no edit type is disqualified a priori.

## 4. Justification interface

This is the missing reader capability. It borrows the alternative/joint distinction from
provenance algebra (Green, Karvounarakis & Tannen, *Provenance semirings*, 2007), where `+` is
alternative derivation and `×` is joint use. Established machinery, not new theory.

### Form

```
Justification = { Alt₁, Alt₂, … }    -- alternatives: any one suffices
Alt           = { leaf_id, … }       -- joint: all members required together
```

Sum-of-products over leaf identifiers. Alternatives kept **inclusion-minimal** — inclusion-minimal,
not shortest: a shorter alternative does not dominate a longer one. What is mechanically checkable
is that no returned alternative is a superset of another **returned** one. That no smaller,
undiscovered sufficient set exists is a claim about the search, not a set comparison.

Every justification carries a **coverage** field: `complete_within(rule_system)` / `incomplete` /
`unknown`, defaulting to `unknown`. Completeness inside a bounded, decidable rule system is
attainable; completeness over prose is not, and the field never claims the second. See
`DEPTH_fresh_evaluator_contract.md` §4 for the three scopes a negative result can occupy.

Deliberately **no numeric strength**. Two justifications are not twice the confidence; they may
share a leaf. `{ {a,b}, {a,c} }` shows `a` as common to both — a scalar hides exactly that. If a
signed receipt turns out to be a photo of the courier scan, the honest justification is `{ {scan} }`,
not two alternatives. Numbers would have reported two.

That collapse must be **evidenced**, not inferred. Distinct document ids do not establish
independence; similarity does not establish identity. A shared-origin claim carries its own
evidence, and both documents stay retained and reachable after the collapse — nothing is merged
away. Evaluator contract §5.

`⋂ Altᵢ` is recorded as **`indispensable_among_recorded`**: necessity **within this formalization
and rule system**, over the alternatives on record. There is no coverage value that turns it into
global necessity — completeness inside the model does not certify the prose → formal translation.

### Operations

| call | returns | notes |
|---|---|---|
| `justify(claim)` | `Justification` | minimal alternatives over leaf ids |
| `evaluate_fresh(material, withheld)` | `(claim, Justification)` | **discovery.** Re-derives with `withheld` and everything derived from it excluded per §3. Must not consult the registered graph for the withheld edge. |
| `propagate(change)` | reopened set | **update.** Runs over the registered graph; presupposes edges. |

**Separation rule:** an edge may be registered only on evidence from `evaluate_fresh`.
`propagate` establishes consequences of registered edges, never the existence of one. Record which
call produced each registration.

### Outcome classification

This replaces "did the answer change":

| outcome | justification before → after | reading |
|---|---|---|
| `unaffected` | identical | leaf played no recorded part |
| `narrowed` | some alternatives dropped, ≥1 remains | conclusion holds on fewer justifications |
| `no_recorded_support` | every recorded alternative has lost a required premise | set comparison over the store — a claim about what is on record |
| `no_derivation_within(R)` | additionally, exhaustive evaluation of R over the formalized material | stronger, and only with a verified exhaustion argument |
| `changed` | conclusion itself differs | |

`narrowed` is why this section exists. A conclusion-only reader collapses `narrowed` into
`unaffected` and concludes the withdrawn leaf never mattered.

`no_recorded_support` is **not** "unsupported". It is reported in the qualified form: *neither
recorded justification remains supported; other possible readings have not been exhaustively
searched.* Promoting it to `no_derivation_within(R)` requires the exhaustion argument, and neither
class ever licenses "no possible support in this text or the world".

## 5. Read-out is separate from structure, and declared in advance

The adapter emits a graph; a distinct read-out maps graph → predicted most-important sentence.
Freeze the choice before running (most-depended-upon node / node whose withdrawal most changes
justifications elsewhere / deepest supported node). This is what stops "root" meaning "answer". It
must stay possible for the graph to be right and the human judgment to fall elsewhere.

## 6. Two independent ground truths — never merged

1. **Dependency key**: annotators blind to DEPTH, using the §2 rubric, agreement reported. Not
   labelled by anyone holding the hypothesis.
2. **Importance judgments**: the study's `picked_role`.

A failure against (2) with a pass against (1) is informative, not a wash.

## 7. Cost accounting

Count reading, graph construction, planning, verification and calculation calls — not successful
calculation calls alone. Report **three components separately**:

| component | covers |
|---|---|
| initial interpretation | reading, proposition extraction, first-pass justification |
| planning | route construction, ordering |
| downstream recomputation | work triggered in dependents once material is interpreted |

**Predictions are conditional on the mechanism, and no total-slope prediction is made.** Revision 1
predicted flat total cost across rungs; revision 2 replaced it with guaranteed-positive. Both were
unwarranted. The measured slope depends on input length, caching, batching and the chosen cost
measure, so those four must be declared before the run and held fixed.

What a relevance-recognizing engine is committed to, conditionally: given a fixed cost measure and
caching/batching configuration, downstream recomputation should not track escalation that leaves
the question's justification unchanged. Interpretation may rise; whether it does is a property of
the reader, not of relevance.

## 8. Comparisons

- **C1 — same supported answer, less total work.** Same justification, lower §7 budget.
- **C2 — better answer under equal budget.** Anytime curves under a fixed cap.
- **C3 — correct revision.** Relevance is defined **against the question asked**, not a preselected
  root: a perturbation is relevant iff it changes what is warranted as an answer to that question.
  Score by §4 outcome class, not conclusion identity. Report sensitivity **and** specificity — an
  engine that never updates scores perfectly on stability and fails the task; one that updates on
  everything is a salience engine.

## 9. One redundant-support probe

Not a testing programme. One item, three probes, no new dataset.

Claim: *the parcel arrived.* Leaves: `scan` (courier scan), `receipt` (signed receipt),
`blame` ("I'm hopeless at tracking deliveries"), plus background.
Expected: `{ {scan}, {receipt} }`.

| edit | relevance to *did the parcel arrive* | required outcome |
|---|---|---|
| withdraw `scan` | relevant, redundant | `narrowed` → `{ {receipt} }` |
| withdraw both | relevant, decisive | `no_recorded_support`, reported in qualified form |
| escalate `blame` | irrelevant | `unaffected` |

Pass condition: all three classified correctly — above all `narrowed` distinguished from
`unaffected`, and the second reported as *neither recorded justification remains supported; broader
discovery remains incomplete* rather than as unconditional absence of support. This tests the
reader interface, not human reading.

The existing vignette (`reading_study_engine.html`: one scenario, 2 frames × 5 rungs) has only the
irrelevant-perturbation arm, and now that relevance is question-relative it is a *candidate*
irrelevant perturbation rather than an established one — the question asked there is which sentence
is most important, and whether escalation is irrelevant to that is part of what is measured.
Generalizing about human reading needs multiple scenarios with matched pairs; that is not this pass.

## 10. What the runtime provides

Inspected dependency operations and verified result reader:

| needed | present today | gap |
|---|---|---|
| justification | exact recorded inputs + child results, verified standing | records *the* derivation used — one joint set. The alternative (`+`) dimension is absent |
| withdraw / replace | yes | — |
| negation semantics, intervention | no | distinct meanings not implemented |
| strength | no | **not wanted** — §4 is deliberately non-numeric |
| `evaluate_fresh` over prose | no | reruns registered calculations on changed inputs; no evaluator that discovers dependencies with a candidate edge excluded |

Two honest consequences:

1. The bounded extension is **one dimension**: record sufficient sets, not only the used set.
   Everything else in §4 is present or deliberately out of scope.
2. `evaluate_fresh` is the exception and is **not** adapter work. Discovery over prose does not
   exist in the runtime. A small interface does not make that problem small.

The two are therefore scoped apart:

| component | job | substrate | document |
|---|---|---|---|
| justification adapter | preserve, compare, update **declared** derivations | existing store | this file, §4 |
| fresh evaluator | propose source-grounded derivations from question + material | new capability | `DEPTH_fresh_evaluator_contract.md` |

Nothing the evaluator produces is admitted structure. Its output is **saved** as `PROPOSED` with
status and history — nothing generated is discarded — but saving is not admitting, and a `PROPOSED`
reading must not become support by sitting in the store. Admission requires a checked *derivation*,
not merely checked leaves: premises, inference steps, applicable conditions and interpretation
warrant each pass their own procedure, recorded. Evaluator contract §3.
