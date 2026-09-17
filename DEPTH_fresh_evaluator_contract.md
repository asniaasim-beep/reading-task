# Fresh evaluator — contract

**Status:** contract only. No implementation, no estimate, no test programme. This specifies a
**candidate-only** component. It does not replace, wrap or reorder the existing executor.

**Revision 2** — §3 corrected (validation targets a derivation, not a leaf set; save vs admit),
§4 resolved into three scopes, §6 rewritten as an isolation requirement, §7 comparison added.

**Why it is separate.** Maintaining alternative justifications extends the existing store
(`DEPTH_reading_mapping.md` §4 — the *justification adapter*). Discovering them in prose does not.
A small interface does not make that problem small.

| component | job | substrate |
|---|---|---|
| justification adapter | preserve, compare and update **declared** derivations | existing store |
| **fresh evaluator** (this document) | receive question + material, propose **source-grounded** derivations | new capability |

## 1. Inputs

| field | meaning |
|---|---|
| `question` | the question being answered. Relevance is question-relative (mapping §8); the evaluator is never told which node is root |
| `material` | leaves with stable ids, each carrying document id and span |
| `withheld` | the candidate edge plus every cached conclusion and annotation derived from it |
| `rule_system` | the inference rules and assumptions the evaluator may use. `coverage` is meaningless without a declared system |
| `budget` | search budget |

## 2. Outputs — `CandidateReading`

| field | meaning |
|---|---|
| `claim` | the proposed answer to `question` |
| `justification` | `{Alt₁, …}` over leaf ids, no returned alternative a superset of another returned one |
| `grounding` | per leaf: document id + span. Every leaf resolves to retained material; none may be invented |
| `coverage` | `complete_within(rule_system)` \| `incomplete(reason, budget_consumed)` \| `unknown` |
| `indispensable_among_recorded` | `⋂ Altᵢ` — see §4 |
| `origin_claims` | proposed shared-source relations between leaves (§5) |
| `status` | always `PROPOSED` |
| `search_trace` | enough to make `coverage` auditable |

## 3. Admission boundary

### Validation targets a derivation, not a leaf set

The previous draft rule — a conclusion is `VALIDATED` when every leaf of one alternative is
`VALIDATED` — was wrong. Validated premises do not validate an unchecked inference. *The parcel
weighs 2 kg* can be fully validated without making *the parcel arrived* valid.

A conclusion is `VALIDATED` only if **at least one alternative** has passed checks on all four of:

| component | what is checked |
|---|---|
| premises | each leaf grounded in retained material and itself admitted |
| inference steps | each step an instance of a stated rule |
| applicable conditions | the rule's side conditions hold on this material |
| interpretation warrant | the prose → proposition reading is warranted |

Each carries a validation record: **what** was validated, **under which rules**, **by which
procedure**. A second AI agreeing is not automatically sufficient — it is another proposal, and is
recorded as one unless the procedure that produced it is itself admitted.

### Save is not admit

Two distinct acts, and conflating them is how `PROPOSED` structure becomes support by attrition:

- **save** — every `PROPOSED` reading is retained with status, provenance and history. Nothing
  generated is discarded.
- **admit** — a derivation is allowed to serve as support for other conclusions.

Saving is unrestricted. Admission is gated by the four checks above. A `PROPOSED` reading sitting
in the store is a record, not support, and must not become support by sitting there.

### What mechanical checks establish

- every leaf id resolves to retained material at its stated span
- no returned alternative is a superset of another **returned** alternative — this is set
  comparison over what came back. That no smaller, undiscovered sufficient set exists is **not**
  established by it
- no withheld item or derivative appears anywhere in the output
- every rule application is an instance of `rule_system`

### What they do not establish

- whether this is the right reading of the text (interpretation warrant is checked, not computed)
- whether an edge is `support` or `evaluative` (mapping §2)
- whether two leaves share an evidential source
- whether a search reporting `complete_within(R)` exhausted R, absent a verified exhaustion argument

Mechanical checks establish provenance and structural validity. They do not establish that an
interpretation is correct.

## 4. What a negative result can say

Three scopes, distinct and not interchangeable:

| statement | what establishes it |
|---|---|
| no surviving recorded justification | every recorded alternative has lost a required premise — set comparison over the store |
| no derivation within this model | verified exhaustive evaluation of the specified rules over the specified formalized material |
| no possible support in this text or the world | neither of the above |

`complete_within(R)` **is** attainable for a bounded, decidable rule system over formalized
material. It is not a certificate that the prose → formal translation captured everything, so it
never discharges row 3. The earlier worry that completeness is unreachable and every negative
result is permanently provisional was scoped wrongly: completeness inside the model and
completeness over prose are different claims.

Canonical report form — qualified, not paralysed:

> Delivery was supported by two recorded routes; neither now stands, and broader discovery remains
> incomplete.

`coverage` defaults to `unknown`, and an empty justification under `incomplete` or `unknown` means
*not found*, never *does not exist*.

`indispensable_among_recorded` is necessity **within this formalization and rule system**, over the
alternatives on record. Not global necessity; there is no scope in which this field delivers that.

## 5. Shared origin

An assertion that two leaves reduce to one evidential source is itself `PROPOSED` and requires its
own evidence.

- distinct document ids do **not** establish independence
- similarity does **not** establish identity
- both documents remain retained and reachable after any collapse — nothing is merged away

Collapsing `{ {scan}, {receipt} }` to `{ {scan} }` follows from an **admitted** origin claim, never
from resemblance. Once admitted it is a revision event: the adapter revises the justification and
propagation carries the consequence.

End to end: lose the scan and support narrows to `{ {receipt} }` with the answer intact; later
discover the receipt copies the scan and there was one source throughout; lose that source and no
recorded justification survives — reported in the §4 qualified form, not as proof of absence.

## 6. Freshness is isolation, not output comparison

The previous draft required output to be identical whether or not a prior justification was
reachable, and read a difference as filtering. That overclaims in both directions: differing
outputs do not prove filtering, and identical outputs do not prove fresh evaluation.

Freshness is **architectural**, enforced at the boundary:

- the evaluator receives only its declared §1 inputs
- excluded context and caches derived from the withheld edge are **inaccessible**, not merely unused
- no back-channel to the registered graph for the withheld edge

Where execution is deterministic, compare **normalized** outputs under identical settings as a
regression check. Where it is stochastic, do not require literal identity and do not diagnose a
mechanism from a single differing answer.

Intersection-based invalidation stays a propagation mechanism: it handles removal from recorded
positive derivations and cannot see new contradictory information, a negation or an assumption
change, none of which need intersect the prior leaf set.

## 7. Comparison

**This component.** Proof checkers already separate proposing a derivation from checking it —
Lean's kernel checks what the elaborator produced, and does not trust it. Provenance methods
already represent alternative supporting sets. Both disciplines are borrowed here. DEPTH has no
demonstrated advantage over either on this component, and the contract should not imply one.

**DEPTH as a whole.** GraphRAG already provides text-derived graphs with hierarchical querying;
LangGraph already provides persistent state and historical checkpoints. Possessing a graph or a
memory is not the distinction. The candidate distinction is integrating meaning-preserving
recognition, lawful calculation, source return and dependency-aware revision into one usable
system — and that whole-system claim is currently unproved.

## 8. Non-goals

- no scheduling, ordering or execution policy
- does not replace, wrap or modify the executor
- does not write admitted structure to the store — it returns candidates, which are saved as
  `PROPOSED` (§3)
- no confidence numbers (mapping §4)
- no test programme; the single probe in mapping §9 is unchanged

## 9. Open

- what `rule_system` is expressed in, whether it is decidable, and whether the study needs more
  than one
- what counts as a verified exhaustion argument in `search_trace` for a given R
- what procedures are admissible for checking interpretation warrant (§3), given that a second
  model's agreement is not one by default
- implementation effort: unestimated
