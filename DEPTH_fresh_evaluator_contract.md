# Fresh evaluator — contract

**Status:** contract only. No implementation, no estimate, no test programme. This specifies a
**candidate-only** component. It does not replace, wrap or reorder the existing executor.

**Why it is separate.** Maintaining alternative justifications extends the existing store
(see `DEPTH_reading_mapping.md` §4 — the *justification adapter*). Discovering them in prose does
not. A small interface does not make that problem small, and calling it wiring would hide the
decision.

| component | job | substrate |
|---|---|---|
| justification adapter | preserve, compare and update **declared** derivations | existing store |
| **fresh evaluator** (this document) | receive question + material, propose **source-grounded** derivations | new capability |

Semantics borrowed, not invented: minimal-witness provenance (Tannen et al.) and assumption-based
truth maintenance, both of which already represent alternative sets of jointly required premises.

## 1. Inputs

| field | meaning |
|---|---|
| `question` | the question being answered. Relevance is question-relative (mapping §8); the evaluator is never told which node is root |
| `material` | leaves with stable ids, each carrying document id and span |
| `withheld` | the candidate edge plus every cached conclusion and annotation derived from it. Excluded **before** evaluation, never filtered from output afterwards |
| `rule_system` | the inference rules and assumptions the evaluator may use. `coverage` is meaningless without a declared system |
| `budget` | search budget. Governs §4 |

## 2. Outputs — `CandidateReading`

| field | meaning |
|---|---|
| `claim` | the proposed answer to `question` |
| `justification` | `{Alt₁, …}`, **inclusion-minimal**, over leaf ids |
| `grounding` | per leaf: document id + span. Every leaf resolves to retained material; none may be invented |
| `coverage` | `complete_within(rule_system)` \| `incomplete(reason, budget_consumed)` \| `unknown` |
| `indispensable_among_recorded` | `⋂ Altᵢ`. Named this way on purpose — see §4 |
| `origin_claims` | proposed shared-source relations between leaves (§5) |
| `status` | always `PROPOSED` |
| `search_trace` | enough to make `coverage` auditable |

**Inclusion-minimal**, not shortest: an alternative is admitted only if no proper subset of it also
suffices. A shorter alternative does not dominate a longer one.

## 3. Admission boundary

Mechanical checks establish provenance and structural validity. They do not establish that an
interpretation is correct.

**Checkable mechanically**

- every leaf id resolves to retained material at its stated span
- each alternative is inclusion-minimal; no dangling ids
- no withheld item or derivative appears anywhere in the output
- every rule application is an instance of `rule_system`

**Not checkable mechanically**

- whether this is the right reading of the text
- whether an edge is `support` or `evaluative` (mapping §2) — that is interpretation
- whether two leaves share an evidential source
- whether a search that reports `complete_within(R)` actually exhausted R

**Consequence.** Passing every mechanical check leaves a reading at `PROPOSED`. Nothing the
evaluator can do to its own output promotes it. Promotion to `VALIDATED` requires an independent
check that did not generate the reading — for the study, the blind annotators of mapping §6.

Registration into the store requires `VALIDATED`. Registering `PROPOSED` structure would
reintroduce the circularity the probe design exists to remove, by a different door.

Where `PROPOSED` structure is carried operationally rather than for the study, status propagates
along the alternative/joint semantics: a conclusion is `VALIDATED` only if every leaf of at least
one of its alternatives is `VALIDATED`. Otherwise it inherits `PROPOSED`.

## 4. Incomplete search

`coverage` defaults to `unknown`. `complete_within(R)` is asserted only when the space under `R`
was exhausted, and the exhaustion argument is recorded in `search_trace`.

**An empty justification is not a negative result.**

| `justification` | `coverage` | licensed reading |
|---|---|---|
| `{}` | `complete_within(R)` | no justification exists under R |
| `{}` | `incomplete` / `unknown` | **not found** — nothing more |

"No justification found" must never be reported as "no justification exists". This bounds
mapping §4's outcome classes: `unsupported` is assignable only under `complete_within(R)`;
otherwise the outcome is `not_found`.

Likewise `indispensable_among_recorded` is indispensability **among the alternatives on record**.
It establishes global necessity only under `complete_within(R)`. Under `incomplete` or `unknown` it
is a statement about the search, not about the material.

On budget exhaustion: return what was found with `incomplete(reason, budget_consumed)`. Never
silently narrow.

## 5. Shared origin

An assertion that two leaves reduce to one evidential source is itself a `PROPOSED` claim
requiring its own evidence.

- distinct document ids do **not** establish independence
- similarity does **not** establish identity
- both documents remain retained and reachable after any collapse — nothing is merged away

Collapsing `{ {scan}, {receipt} }` to `{ {scan} }` is a consequence of an **admitted** origin
claim, never an inference from resemblance. Once admitted, the collapse is a revision event: the
adapter revises the justification and propagation carries the consequence.

This is the practical case end to end: lose the scan and support narrows to `{ {receipt} }` with
the answer intact; later discover the receipt merely copies the scan and there was one source all
along; lose that source and the conclusion is unsupported by the available material.

## 6. Discovery is re-evaluation, not filtering

Intersection-based invalidation handles removal from recorded positive derivations. It cannot see
new contradictory information, a negation, or an assumption change — each can matter without
intersecting the prior leaf set. So intersection is a **propagation** mechanism and correct there,
and not a discovery one.

Contract requirement: the re-derivation is produced from `question` + `material` + `rule_system`,
not by filtering a prior justification.

Conformance check: output must be identical whether or not a prior justification was reachable
from the calling context. If it differs, the component is filtering, not evaluating.

## 7. Non-goals

- no scheduling, ordering or execution policy
- does not replace, wrap or modify the executor
- does not write to the store — it returns candidates
- no confidence numbers (mapping §4)
- no test programme; the single probe in mapping §9 is unchanged

## 8. Open

- what `rule_system` is expressed in, and whether the study needs more than one
- whether `search_trace` can support an exhaustion argument at all, or whether
  `complete_within(R)` is unreachable in practice and `unsupported` therefore never assignable
- implementation effort: unestimated
