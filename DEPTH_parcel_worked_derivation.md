# Parcel — one worked derivation

Instantiates the three open decisions (`DEPTH_fresh_evaluator_contract.md` §9) on the existing
parcel example. Not a contract, not a benchmark. One case, worked end to end.

## 1. The rule language `R_parcel`

Pure Datalog: a finite set of rules over named propositions, **no function symbols**, so no rule
can invent a new entity. The Herbrand base is therefore finite and the least fixpoint is reached in
finitely many steps — which is what makes decision 2 possible at all.

Constants: `d1`, `d2`, `d3` (documents), `p` (the parcel).
Predicates: `scan_record/2`, `signed_receipt/2`, `issued_by_carrier/1`, `signed_by_recipient/1`,
`self_blame/1`, `delivered/1`. Herbrand base: **48 ground atoms**.

```prolog
r1 :  delivered(P) :- scan_record(D, P),    issued_by_carrier(D).
r2 :  delivered(P) :- signed_receipt(D, P), signed_by_recipient(D).
```

Each rule body is a **joint** requirement (two premises together); the two rules are
**alternatives**. Both dimensions of §4's justification format are exercised, not just the `+`.

## 2. Material, formalized

| leaf | proposition | document | span | interpretation |
|---|---|---|---|---|
| `L1` | `scan_record(d1, p)` | d1 | "Scanned at 14:02, unit 7" | REVIEWED |
| `L2` | `issued_by_carrier(d1)` | d1 | header: carrier logo + depot code | REVIEWED |
| `L3` | `signed_receipt(d2, p)` | d2 | signature block, "received" | REVIEWED |
| `L4` | `signed_by_recipient(d2)` | d2 | "A. Okoye" against printed name | REVIEWED |
| `L5` | `self_blame(d3)` | d3 | "I'm hopeless at tracking deliveries" | REVIEWED |

## 3. Derivation, and what it did not require

```
iter 0  EDB: L1 L2 L3 L4 L5
iter 1  r1[L1,L2] ⊢ delivered(p)          ← Alt₁
        r2[L3,L4] ⊢ delivered(p)          ← Alt₂
iter 2  no rule body mentions delivered/1 → no new facts → FIXPOINT
```

```
justification(delivered(p)) = { {L1,L2}, {L3,L4} }
coverage = complete_within(R_parcel)
indispensable_among_recorded = ∅
```

**The positive answer needed no exhaustive search.** `delivered(p)` is admissible via Alt₁ the
moment `r1` fires and its checks pass. The fixpoint run below is required only for the *negative*
claim in §5. Rigour is spent where a negative claim is made, not before every useful positive one.

## 4. Probe A — withdraw the scan

Withdraw `L1`, and per mapping §3 every cached conclusion or annotation whose justification
mentions it.

```
iter 1  r1: no scan_record → does not fire
        r2[L3,L4] ⊢ delivered(p)
iter 2  FIXPOINT

justification = { {L3,L4} }     outcome: narrowed
```

Answer unchanged, support changed. A conclusion-only reader reports `unaffected` here and concludes
the scan never mattered. The report is:

> Delivery still stands, now supported by the signed receipt only.

## 5. Probe B — the receipt is a photograph of the scan

The origin claim `copy_of(d2, d1)` arrives with its own evidence (identical pixel dimensions and
EXIF device id; the "signature" is within the photographed region). It is `PROPOSED`, reviewed
under the §6 rubric, then **admitted**.

**Where it acts.** Not on `r2`, and not on the edge. It retracts `L4`: nobody signed d2, so the
span never warranted `signed_by_recipient(d2)`. The origin claim is an **interpretation** revision,
not an inference revision — which is why the contract puts interpretation warrant on its own axis.
`r2` is untouched and still valid; it simply has no premise.

Both documents stay retained. `L3` stays: d2 does depict a receipt-shaped record.

```
EDB: L2 L3 L5          (L1 withdrawn in probe A, L4 retracted here)
iter 1  r1: no scan_record → does not fire
        r2: no signed_by_recipient → does not fire
iter 2  FIXPOINT — delivered(p) ∉ fixpoint
```

Outcome: **`no_recorded_support`**, and because the fixpoint was actually run over a finite
Herbrand base, additionally **`no_derivation_within(R_parcel)`**.

What that licenses:

> Delivery was supported by two recorded routes; neither now stands, and no derivation exists
> under `R_parcel` from this formalization. Other possible readings of the documents have not been
> exhaustively searched.

What it does not license: that the parcel did not arrive, or that the documents contain no support.
`complete_within(R_parcel)` is a boundary inside the formalization. It says nothing about whether
the prose → proposition translation captured everything.

Dependent answers are reconsidered, not silently kept.

## 6. Probe C — escalate the self-blame

Replace `L5` with a stronger stance ("I'm hopeless at tracking deliveries" → "I ruin everything I
touch"). `self_blame/1` appears in no rule body. The fixpoint is unchanged, atom for atom.

Outcome: **`unaffected`** — and here that is a mechanical fact about the fixpoint, not a judgment.
Relevance is against the question *did the parcel arrive*; a different question could make `d3`
relevant, and the rule set would be different.

## 7. Exhaustion, as an actual check

`complete_within(R_parcel)` is asserted only with this recorded:

1. the rule set applied, and that it is function-symbol-free
2. the constant set, giving the finite Herbrand base (48 atoms)
3. each iteration's derived facts, to fixpoint
4. the final iteration deriving nothing new

A budget interruption before step 4 yields `incomplete(reason, budget_consumed)` and the negative
claim is not available — only "not found".

## 8. Interpretation review, scoped

For this pilot, prose → proposition is adjudicated by a person, not a model.

- the reviewer is **not** the proposer
- the reviewer sees the span and the proposed proposition against the declared predicate
  definitions, and answers only *does this span warrant this proposition*
- the reviewer does **not** see which conclusion the proposition will support — otherwise the
  review is confirmatory rather than independent
- disagreement leaves the interpretation `PROPOSED`. It is recorded, not broken by a third model

## 9. The receipt

Interpretation and inference are never collapsed into one "verified" flag:

```
delivered(p)                    ADMITTED via Alt₁
  premises
    L1  scan_record(d1,p)       interpretation REVIEWED   rubric v1 · reviewer R2 · 2026-09-17
                                grounding d1 "Scanned at 14:02, unit 7"
    L2  issued_by_carrier(d1)   interpretation REVIEWED   rubric v1 · reviewer R2 · 2026-09-17
  inference
    r1                          CHECKED — instance of r1; body conditions hold
  coverage                      complete_within(R_parcel)
```

`REVIEWED` is a person's judgment about a reading. `CHECKED` is a mechanical fact about a rule
application. Neither is unconditional truth, and an alternative carrying a `PROPOSED` premise
cannot admit its conclusion — though another alternative may.

## 10. What this does not show

One scenario, one rule set, hand-formalized. It demonstrates the three decisions are instantiable
and mutually consistent. It does not show that an evaluator can produce `R_parcel` or the §2 table
from prose unaided — that component is unbuilt and unestimated. It establishes what supports what,
not what becomes what, through which activity, at what rate.
