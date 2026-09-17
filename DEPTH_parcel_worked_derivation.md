# Parcel — one worked derivation

Instantiates the three open decisions (`DEPTH_fresh_evaluator_contract.md` §9) on the parcel
example. Not a contract, not a benchmark. One case, worked end to end.

**Revision 2** — two interpretation errors corrected. A carrier scan was treated as delivery; a
discovered copy was treated as disproving a signature. The formal traces are retained; what the
documents warrant is corrected. Contract and mapping unchanged.

## 1. The rule language `R_parcel`

Pure Datalog: finite rules over named propositions, **no function symbols**, so no rule invents an
entity. The Herbrand base is finite and the least fixpoint terminates — which is what makes the
exhaustion check in §7 possible at all.

Constants: `d1`, `d2`, `d3` (documents), `p` (the parcel).

```prolog
r1 :  delivered(P) :- carrier_record(D, P), issued_by_carrier(D),
                      status_delivered(D), a_carrier_status_reliable.
r2 :  delivered(P) :- receipt_document(D, P), signed_by_recipient(D).
```

Predicate meanings are declared, not inferred from their names:

| predicate | means |
|---|---|
| `carrier_record(D,P)` | D is a carrier-system record concerning P |
| `status_delivered(D)` | D's status field reads delivered to the destination — **not** merely that a scan occurred |
| `receipt_document(D,P)` | D is a delivery receipt form concerning P. Claims the form, not the signature |
| `signed_by_recipient(D)` | the signature on D is the recipient's or an authorized party's |
| `a_carrier_status_reliable` | **declared assumption**: the carrier's delivered status means handover at the destination address |

Herbrand base: `carrier_record/2` 16 + `receipt_document/2` 16 + five unary predicates ×4 = 20 +
`a_carrier_status_reliable` 1 = **53 ground atoms**.

### Correction 1 — a scan is not a delivery

The previous version fired `delivered(p)` from `scan_record(d1,p)` grounded in *"Scanned at 14:02,
unit 7"*. That span is satisfied by a parcel still at the depot. The rule was valid and the
calculation correct; the conclusion was unwarranted. Executed perfectly, it would have been wrong.

Two things changed. `status_delivered/1` is now a separate premise that only a status field
actually reading delivered can warrant — a scan event does not. And the step from *carrier says
delivered* to *delivered* is now the named assumption `a_carrier_status_reliable`, carried **inside**
the justification rather than left implicit, so withdrawing it kills the alternative like any other
premise.

## 2. Material, formalized

d1 is a carrier record that includes a signature capture. d2 is a separate photograph. d3 is the
writer's own account.

| leaf | proposition | doc | span | interpretation |
|---|---|---|---|---|
| `L1` | `carrier_record(d1, p)` | d1 | tracking id matches p | REVIEWED (illustrative — see §9) |
| `L2` | `issued_by_carrier(d1)` | d1 | carrier header, depot code | REVIEWED |
| `L3` | `status_delivered(d1)` | d1 | status field: "DELIVERED — handed to resident" | REVIEWED |
| `A1` | `a_carrier_status_reliable` | — | declared assumption, not derived | ASSUMED |
| `L4` | `receipt_document(d2, p)` | d2 | receipt form, tracking id visible | REVIEWED |
| `L5` | `signed_by_recipient(d2)` | d2 | signature against printed recipient name | REVIEWED |
| `L6` | `self_blame(d3)` | d3 | "I'm hopeless at tracking deliveries" | REVIEWED |

## 3. Derivation, and what it did not require

```
iter 0  EDB: L1 L2 L3 A1 L4 L5 L6
iter 1  r1[L1,L2,L3,A1] ⊢ delivered(p)      ← Alt₁
        r2[L4,L5]       ⊢ delivered(p)      ← Alt₂
iter 2  no rule body mentions delivered/1 → no new facts → FIXPOINT
```

```
justification(delivered(p)) = { {L1,L2,L3,A1}, {L4,L5} }
coverage = complete_within(R_parcel)
indispensable_among_recorded = ∅
```

**The positive answer needed no exhaustive search.** `delivered(p)` is admissible the moment `r1`
fires and its checks pass, at iteration 1. The fixpoint run matters only for the negative claim in
§6. Exhaustion is spent where a negative claim is made, not before every useful positive one.

## 4. Probe A — withdraw d1

Withdraw the carrier record, and per mapping §3 everything cached from it. `L1`, `L2`, `L3` go.

```
iter 1  r1: no carrier_record → does not fire
        r2[L4,L5] ⊢ delivered(p)
iter 2  FIXPOINT

justification = { {L4,L5} }     outcome: narrowed
```

> Delivery still stands, now supported by the signed receipt only.

A conclusion-only reader reports `unaffected` here and concludes the carrier record never mattered.

## 5. Probe B1 — d2 turns out to photograph d1

### Correction 2 — a copy is not a disproof

The previous version admitted `copy_of(d2,d1)` and retracted the signature premise, reading the
discovery as *nobody signed*. That does not follow. A photograph can preserve a genuine signature.
Two different revisions were collapsed into one:

| discovery | what it changes | what it does not |
|---|---|---|
| **shared origin** — d2 photographs d1 | the material has one independent origin, not two | does not withdraw what d2 depicts |
| **interpretation disproved** — the signature is not the recipient's | withdraws `L5` | is not established by discovering a copy |

Nor is the origin claim itself established by resemblance. Matching pixel dimensions and a shared
EXIF device id are *consistent with* d2 photographing d1 and do not establish it — they are
resemblance metrics, and the claim is about the chain of custody. Admitting it requires evidence of
that chain: that the carrier's system holds one record under this id, that no second physical form
entered the chain, that what d2 depicts carries d1's record id and depot stamp. Pending such
evidence the origin claim stays `PROPOSED` and nothing revises.

### With the origin claim admitted

```
iter 1  r1: L1,L2,L3 withdrawn in probe A → does not fire
        r2[L4,L5] ⊢ delivered(p)
iter 2  FIXPOINT

justification = { {L4,L5} }     conclusion: unchanged and still supported
independent origins: 1 (both alternatives trace to d1)
```

`L5` stands. The signature is genuine whether photographed or not.

Two consequences worth keeping. **Alt₁ and Alt₂ were never two independent routes** — the
justification's origin bookkeeping now says so, which is the distinction between *another route*
and *another copy* that a confidence number would have erased. And **probe A did not remove d1's
content**: withdrawing a document while retaining a photograph of it leaves the information in the
material, so `narrowed` there was about the recorded alternatives, not about what the material
still carries.

Both documents remain retained and reachable.

## 6. Probe B2 — the signature is independently disproved

This is a **different** discovery, and the only one that reaches `L5`: the carrier's system records
no signature capture for this delivery, and the mark on the form matches a pre-printed placeholder
used at that depot. On that evidence `signed_by_recipient(d2)` loses its warrant and `L5` is
withdrawn. `L4` is untouched — d2 is still a receipt form; `receipt_document` never claimed the
signature, which is why the predicates were separated in §1.

```
EDB: A1 L4 L6            (L1,L2,L3 withdrawn in probe A; L5 withdrawn here)
iter 1  r1: no carrier_record → does not fire
        r2: no signed_by_recipient → does not fire
iter 2  FIXPOINT — delivered(p) ∉ fixpoint
```

Outcome: **`no_recorded_support`**, and because the fixpoint ran over a finite Herbrand base,
additionally **`no_derivation_within(R_parcel)`**.

> Delivery was supported by two recorded routes; neither now stands, and no derivation exists under
> `R_parcel` from this formalization. Other possible readings of these documents have not been
> exhaustively searched.

Not licensed: that the parcel did not arrive, or that the documents contain no support.
`complete_within(R_parcel)` bounds the formalization, not the meaning of the originals.

**The premise of this probe is explicit.** It applies because `L5` independently lost its warrant —
not because a copy was discovered in B1.

## 7. Probe C — escalate the self-blame

Replace `L6` with a stronger stance. `self_blame/1` appears in no rule body; the fixpoint is
unchanged atom for atom. Outcome **`unaffected`**, here a mechanical fact rather than a judgment.
Relevance is against *did the parcel arrive*; another question would need another rule set.

## 8. Exhaustion, as an actual check

`complete_within(R_parcel)` is asserted only with this recorded: the rule set applied and that it
is function-symbol-free; the constant set, giving the finite Herbrand base of 53 atoms; each
iteration's derived facts to fixpoint; and a final iteration deriving nothing new. A budget
interruption before the last step yields `incomplete(reason, budget_consumed)`, and the negative
claim is unavailable — only *not found*.

## 9. Interpretation review, scoped

For this pilot, prose → proposition is adjudicated by a person, not a model. The reviewer is not
the proposer, and answers only *does this span warrant this proposition* against the declared
predicate meanings in §1. Disagreement leaves the interpretation `PROPOSED`, recorded, not broken
by a third model.

Blinding the reviewer to the downstream conclusion is sensible bias control and is the default
here. It is not a validity condition: a review is not void because the reviewer could see what the
proposition would support.

**No review has occurred.** Every `REVIEWED` label in §2 and the receipt below is illustrative,
showing the shape of the record, not reporting an event.

```
delivered(p)                    ADMITTED via Alt₁          [ILLUSTRATIVE]
  premises
    L1  carrier_record(d1,p)    interpretation REVIEWED    rubric v1 · reviewer · date
    L2  issued_by_carrier(d1)   interpretation REVIEWED    rubric v1 · reviewer · date
    L3  status_delivered(d1)    interpretation REVIEWED    rubric v1 · reviewer · date
    A1  a_carrier_status…       ASSUMED — declared, not derived
  inference
    r1                          CHECKED — instance of r1; body conditions hold
  coverage                      complete_within(R_parcel)
```

`REVIEWED` is a person's judgment about a reading, `ASSUMED` is a stated premise nobody checked,
`CHECKED` is a mechanical fact about a rule application. None is unconditional truth, and they are
never collapsed into one flag.

## 10. What the two corrections teach

Revision can act at three different places, and they are not interchangeable:

| site | what changed | effect on support |
|---|---|---|
| **identity** | how many independent origins the material has | support may be entirely unchanged; independence bookkeeping changes |
| **interpretation** | what a span warrants | the leaf is withdrawn; alternatives resting on it fail |
| **inference** | whether a rule is applicable or warranted at all | the rule is withdrawn; every alternative using it fails |

Correction 1 was an inference-site error — the rule licensed more than the record warranted.
Correction 2 conflated the identity site with the interpretation site.

Two screenshots of one delivery confirmation are not two confirmations — and discovering the
duplicate does not mean the parcel was never delivered. Recursion must propagate the particular
change, not treat all three sites as deletion.

## 11. What this does not show

One scenario, one hand-formalized rule set, no review actually performed. It shows the three
decisions are instantiable and mutually consistent, and that the two error classes above are
distinguishable in this machinery. It does not show that an evaluator can produce `R_parcel` or the
§2 leaf table from prose unaided; that component is unbuilt and unestimated.

Alternative/joint provenance (Green, Karvounarakis & Tannen) and the proposer/checker separation
(Lean's kernel) are borrowed here. This example establishes no superiority over either, and Lean's
kernel likewise does not establish that prose was interpreted correctly. It establishes what
supports what — not what becomes what, through which activity, at what rate, sustained by which
continuing activities.

*Closes the worked-example pass.*
