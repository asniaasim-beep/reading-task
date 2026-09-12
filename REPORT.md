# The depth grammar of the reading task

**What I was working from.** The repository holds three files: a README, and two
copies of the experiment. There is no stored summary of earlier linguistic work
here, and no earlier conversation available to this session, so nothing below is
recalled from previous notes. Everything is reconstructed from the stimulus
itself and stated so you can check it. Where a number is a measurement it says
so; where it is my linguistic judgment it says that too, with the reasoning
attached.

Everything here is reproducible: `analysis/` contains the code, and every figure
quoted below is printed by a script in it.

---

## 1. What the study is, structurally

Verified by reading the sealed `STIMULI` object out of `reading_study_engine.html`
(`analysis/extract_stimuli.py`):

- 10 cells: 2 frames (`plain`, `setaside`) x 5 rungs.
- Across all 10 cells the **cause**, **scene** and **neutral** sentences are
  literally one string each. They never change.
- The **self-blame** sentence takes 5 distinct values. The **question** takes 2.
- So the design is clean: within a frame exactly one thing varies, and across
  frames exactly one thing varies.

Each participant reads four sentences in a random order and picks one. That is
one trial per person, four alternatives, between subjects. It matters for
section 4 that this is a *choice* and not a *rating*.

---

## 2. The core of the depth grammar

I coded all five self-blame sentences on six dimensions. The codes are my
judgments; the rationale for every cell is in `analysis/depth_grammar.py` and
printed by it. What the coding is *for* is to ask a question the ladder cannot
answer informally: **is depth one thing, and is it evenly spaced?**

| dim | what rises along the ladder |
|---|---|
| **σ** predication | a bounded event → an individual-level property of the self |
| **τ** temporal | one past act → universal quantification over a lifetime |
| **ε** commitment | counterfactual wish → full epistemic certainty |
| **δ** domain | one named person → anyone at all |
| **α** agency | agent of an act → patient of a property |
| **κ** binding | tied to the birthday → a free-standing claim about the person |

Scores, and the step between adjacent rungs:

| rung | σ | τ | ε | δ | α | κ | mean | step from previous |
|---|---|---|---|---|---|---|---|---|
| 1 | .00 | .10 | .05 | .00 | .00 | .00 | .03 | — |
| 2 | .30 | .25 | .30 | .10 | .15 | .00 | .18 | 0.95 |
| 3 | .60 | .80 | .40 | .70 | .35 | **1.00** | .64 | **2.75** |
| 4 | .90 | .85 | .70 | .85 | .80 | 1.00 | .85 | 1.25 |
| 5 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.90 |

### The ladder has a hinge, and the hinge is between rungs 2 and 3

The step from rung 2 to rung 3 is **2.75 of the 5.85 total — 47% of the entire
ladder in one move.** A principal components decomposition of the coding matrix
says the same thing: PC1 takes 93.9% of the variance (so depth really is close to
one dial), but the spacing along that dial is not even — the gaps are
+0.36, **+1.20**, +0.48, +0.34. PC2, the only other component with any mass
(5.6%), is loaded almost entirely on κ.

That arithmetic is arithmetic on my own coding, so it cannot be evidence about
readers. What it does is make the design's own structure explicit, and the
structure is this:

> **Rungs 1 and 2 are still about the birthday. Rungs 3, 4 and 5 are about the person.**

Rung 1 says *the invitation*; rung 2 says *I forgot to include one of my closest
friends*. Both are lexically anaphoric to the cause sentence — they cannot be
understood without it. Rung 3 onward, Anna is gone, the birthday is gone, the
invitation is gone. "Good people," "hold on to," "lovable," "alone" refer to
nothing in the paragraph.

This is not a difference of degree in how bad the writer feels. It is a change in
**what kind of sentence it is**. Rungs 1–2 are subordinate to the causal story —
they elaborate it. Rungs 3–5 are a *rival* story, competing with the cause
sentence to be what the paragraph is about.

That reframes the whole instrument. The question "which is the most important
sentence" asks the reader to pick the best answer to an unstated question. For
rungs 1–2 there is no real contest: only one sentence answers *what happened*.
From rung 3 there are two sentences making two different claims about what the
paragraph is for, and the reader has to choose between them.

**Prediction that follows:** the response curve should be a step, not a line.

*(One wrinkle: because paragraph order is shuffled, in roughly half the orders
the bound self-blame sentence precedes the cause sentence it depends on, making
the dependency cataphoric. That is a real processing cost that lands only on
rungs 1–2, and it is randomised, not controlled.)*

---

## 3. Against general grammar: what the ladder is made of

Each dimension is a known piece of machinery, which is why the ladder works.

- **σ is the stage-level / individual-level distinction.** Rung 1's complement
  denotes an event. By rung 4 the predicate is copular and individual-level
  (*I am not interesting enough*), and by rung 5 it is `-able` — inherent
  potential. "Not lovable" is not something that is true of a moment.
- **δ is genericity.** *Her* → *one of my closest friends* (a partitive, which
  evokes a set) → *good people* (bare plural, kind-level) → the arbitrary
  implicit subject of *to hold on to*: anyone. The domain widens from one person
  to the universe of possible others.
- **ε is complement selection**, and it is the most carefully built dimension.
  *Wish* + past perfect asserts nothing (counterfactual). *Feel stupid that P*
  presupposes P but hedges the property. *Wonder if* embeds an **interrogative** —
  nothing is asserted at all. *Believe* commits. *Certain that* commits fully.
  Read as a series, the writer's grip on the claim tightens clause by clause.
- **τ rides on polarity and quantification.** *Ever* in rung 3 is an NPI licensed
  by the question-embedding verb; rung 5 quantifies explicitly with *my whole
  life*.
- **α is voice and morphology.** `-able` is passive-potential: *lovable* means
  *able to be loved*, so the self is the **patient** of an unrealised action by
  unnamed others. The grammar drains agency out of the subject position as the
  ladder climbs. *Deserve to be alone* then delivers a verdict of which the self
  is the recipient. This is the quietest dimension and possibly the most
  important one.
- **κ is discourse anaphora**, and it is the hinge.

### Where the frame manipulation does not reach

The `setaside` question is: *"Setting aside how it makes the writer feel, which
is the most important sentence in this paragraph?"*

In information-structure terms this is a restriction on the question under
discussion — it tells the reader which question to answer. Two problems, both
grammatical:

1. **The pronoun has no antecedent.** *It* is introduced before any referent
   exists. The reader must accommodate one — the event? the paragraph? the
   friendship? Different readers will resolve it differently.

2. **It names a feeling, and the top of the ladder is not feelings.** The
   instruction says *how it makes the writer feel*. Rung 2 is literally
   *"I feel stupid…"* — a perfect lexical match. But rungs 3–5 are **belief
   reports**: *wonder if*, *starting to believe*, *certain that*. A belief that
   you are unlovable is not a feeling, and a reader complying precisely with the
   instruction has no grounds to set it aside.

So the manipulation is strongest exactly where its lexical hook lands (rung 2)
and weakest exactly where the construct is most extreme (rungs 3–5). That is
either a confound or the most interesting hypothesis in the study, depending on
whether you declare it in advance. My view: **declare it.** "The instruction to
disregard feeling fails to reach self-blame that has become belief" is a sharper
and more publishable claim than "framing reduces self-blame salience." But see
section 4 — it is also the expensive claim.

---

## 4. What is happening in the maths

### It is a discrete choice experiment, not a 2x5 ANOVA

One trial, four alternatives, pick one. The estimator that matches is McFadden's
conditional logit. Depth enters as a shift in the utility of the self-blame
option *only*, because that is the only option the manipulation touches:

```
V_ij = a_role(j) + p_pos(j) + 1[role(j)=B] * (b0 + b_d*d(r_i) + b_f*f_i + b_x*d(r_i)*f_i)

P(i picks j) = exp(V_ij) / sum_k exp(V_ik)
```

This buys three things a chi-square on `picked_is_cause` does not: serial
position is absorbed as a nuisance term instead of inflating error; the other
three options stay in the model instead of being collapsed; and `b_x` — the
interaction that section 3 argues is the real question — is an actual parameter.

**`d(r)` is where the linguistics becomes arithmetic.** Three codings are three
rival theories:

| coding | `d(r)` | the claim |
|---|---|---|
| linear | (r−1)/4 | depth is a dial |
| **step** | **1[r ≥ 3]** | **depth is a switch: episode-bound vs person-bound** |
| free | 4 dummies | let the data say |

Section 2 predicts the step. Both restricted codings nest inside the free one, so
a likelihood-ratio test against the saturated model tests the shape directly.

### The estimator works

Simulated under a hinge-shaped truth and re-fitted 300 times (`analysis/power.py`).
Recovery at n=200/cell — true values in brackets:

| term | estimate | truth |
|---|---|---|
| scene | −1.616 | [−1.6] |
| neutral | −1.809 | [−1.8] |
| pos 2 | −0.148 | [−0.15] |
| pos 3 | −0.248 | [−0.25] |
| pos 4 | −0.301 | [−0.30] |

Unbiased, and the position randomisation does its job. False-positive rates under
a flat truth are nominal: .030, .027, .047 at α = .05.

### Power: one term is cheap, one is affordable, one is out of reach

300 simulations per row, step coding, α = .05:

| n/cell | N total | depth | frame | **depth × frame** |
|---|---|---|---|---|
| 50 | 500 | .96 | .57 | **.10** |
| 75 | 750 | .98 | .70 | **.23** |
| 100 | 1000 | 1.00 | .81 | **.24** |
| 150 | 1500 | 1.00 | .93 | **.36** |
| 200 | 2000 | 1.00 | .98 | **.47** |

The depth effect is nearly free. The frame main effect needs about N = 1500.
**The interaction — the claim from section 3 — is at 47% power even at N = 2000.**

Reallocating helps but does not rescue it. Dropping to a 2x2 (one clearly
episode-bound rung, one clearly person-bound) at matched total N:

| N total | 2x5 | 2x2 |
|---|---|---|
| 800 | .23 | .29 |
| 1200 | .24 | .35 |
| 2000 | .40 | .50 |
| 3000 | .52 | .68 |

So: if the interaction is the point, the five-rung ladder is a luxury. If the
ladder *shape* is the point, you need all five and you need N ≈ 2000 (power to
reject the straight-line coding: .23 at N=500, .54 at N=1000, .83 at N=2000).

The cheap headline is the pooled hinge contrast — P(cause) for rungs 1–2 vs 3–5,
plain frame only, as a plain two-proportion test. That reaches .79 at N = 750 and
.92 at N = 1000. **If the budget is one study, buy this one.**

### The trap: the interaction changes sign-of-story with the scale

This one will bite if it is not seen coming. Under the simulated truth, the frame
effect on choosing self-blame:

| | plain | setaside | difference in points | odds ratio |
|---|---|---|---|---|
| episode-bound (r1–2) | .210 | .105 | **+10.5 pts** | **2.27** |
| person-bound (r3–5) | .417 | .327 | **+9.0 pts** | **1.47** |

In percentage points the frame effect is essentially flat — 10.5 → 9.0 — and you
would write "no interaction." In odds the frame's suppressive power is cut by more
than a third — 2.27 → 1.47 — and you would write "the instruction loses its grip
at depth." Same data. The logit model reports the second because it works in log
odds.

Neither is wrong, but they answer different questions, and the one that matches
section 3 ("does the instruction still reach the reader?") is the odds one. Decide
which scale the claim lives on **before** looking, and say so in the write-up.

### What size of interaction can this design see at all?

Holding the plain frame fixed and varying only how much of the frame's grip
survives at depth (`analysis/power_mdi.py`, 250 sims per cell). `b_x` is the
amount of suppression lost; the odds ratio is the frame effect at rungs 1–2
versus rungs 3–5:

| `b_x` | frame effect, shallow → deep | N=500 | N=1000 | N=2000 | N=3000 |
|---|---|---|---|---|---|
| 0.20 | OR 2.27 → 1.86 (*weakens slightly*) | .09 | .10 | .12 | .16 |
| 0.42 | OR 2.27 → 1.49 (*weakens clearly*) | .14 | .26 | .42 | .59 |
| 0.60 | OR 2.27 → 1.24 (*nearly gone*) | .22 | .46 | .68 | .88 |
| **0.82** | **OR 2.27 → 1.00 (*no effect at all at depth*)** | **.39** | **.70** | **.93** | 1.00 |
| 1.00 | OR 2.27 → 0.83 (*reverses*) | .52 | .87 | 1.00 | 1.00 |

Read the rows, not the columns. **If the instruction merely weakens at depth,
this design cannot detect it at any budget you would plausibly spend.** If it
stops working entirely, you have .70 power at N = 1000 and .93 at N = 2000.

And that is the payoff of section 3. The grammatical argument — that "setting
aside how it makes the writer *feel*" has no purchase on *wonder if*, *believe*,
*certain that*, because those are beliefs and not feelings — does not predict a
gentle attenuation. It predicts the instruction failing outright once the
sentence stops naming the event. **That is the one version of the interaction
this study can afford to test.** A vaguer prediction of "reduced framing effect
at depth" is, at this N, untestable.

---

## 5. Python, SQL, and the Rosetta

The four notations have to be the same object or the analysis is not measuring
the design. `analysis/` makes that checkable rather than asserted.

| the thing | grammar | maths | Python | SQL |
|---|---|---|---|---|
| what the reader faced | 4 sentences, one predicating a property of the self | alternative set *J*, utilities *V_ij* | `X` of shape (N, 4, K) | 4 rows of `v_choice_set` sharing a `pid` |
| the judgment | "most important" | argmax over *J* | `y`, the chosen index | `chosen = 1` |
| depth | σ τ ε δ α rising | `d(r)` | `LINEAR` / `STEP` / `FREE` | `rung` |
| **the hinge** | **κ: bound vs free** | **1[r ≥ 3]** | **`STEP`** | **`person_bound`** |
| the frame | restriction on the question under discussion | `f_i` | `B:frame` | `frame` |
| the real claim | the instruction names feelings; r3–5 are beliefs | `b_x` | `th[8]` | query Q4 |
| topic-sentence pull | first position reads as the thesis | `p_pos` | `pos2..pos4` | `v_choice_set.position` |

`analysis/rosetta_check.py` **proves the middle three columns agree** rather than
claiming it. It rebuilds the design matrix twice — once by letting SQLite
reconstruct the choice sets out of `v_choice_set`, once in Python straight from
the wide row — and asserts the tensors are identical, the fitted coefficients
differ by 0, and SQL's `AVG()` and Python's `.mean()` return the same cell
proportions to machine precision. On 1,413 synthetic participants it passes.

The load-bearing insight is in the SQL: **the saved wide row is a compressed
choice set.** `pos1_role…pos4_role` plus `picked_position` is exactly enough to
reconstruct every option's role, its serial position, and — by joining the
extracted stimuli — its text. Nothing about the design is lost at save time. The
`v_choice_set` view unpivots it back into the four rows the model needs. That is
genuinely good news about the engine's logging, and it is worth knowing because
it means you never need to re-run anyone.

`analysis/ingest.py` handles what DataPipe actually delivers: one CSV per
participant, each with its own header row. It checks every file against the exact
column list the engine emits and refuses mismatches, drops duplicate `pid`s,
builds the participant map, and asserts the integrity conditions (every option
row joins a sentence; exactly 4 options and exactly 1 pick per participant).

---

## 6. Things to fix, in priority order

**1. The length confound is collinear with the hinge.** This is the most serious
finding in the report. Word counts:

| | words | vs. cause (14) | episode-bound? |
|---|---|---|---|
| rung 1 | 12 | shorter | yes |
| rung 2 | 13 | shorter | yes |
| rung 3 | 17 | **longer** | no |
| rung 4 | 15 | **longer** | no |
| rung 5 | 16 | **longer** | no |

corr(rung, length) = **.76**, and "is the self-blame sentence longer than the
cause sentence?" flips at exactly the same place as the grammar does. Since
"pick the most important sentence" is known to be pulled by length and
informativeness, **a step at rung 2→3 is currently unattributable** — depth and
length predict the identical pattern.

Fix by breaking the collinearity with two extra sentences that cross the two
factors (both written and word-counted):

- *episode-bound but long (17 words, matching rung 3):*
  "I keep going over the day I wrote the guest list, wondering how I missed her name."
- *person-bound but short (12 words, matching rung 1):*
  "I have started to think I am simply not someone people keep."

Adding these two makes length and depth orthogonal, and it is cheap — two cells,
no change to the engine beyond the stimulus object.

**2. Two live engines writing to two different destinations.**
`reading_study_engine.html` → DataPipe `rrW097Bp4DWq`, real completion code
`CX864VBB`. `reading_study_study.html` → DataPipe `xTRjQwQBv3yi`, completion code
`PLACEHOLDER-CODE`. They also assign conditions differently: the engine uses
`jsPsychPipe.getCondition` for balanced rotation over the 10 cells, the study file
uses client-side `Math.random()`. Anyone who reaches the wrong file gets a
placeholder code, cannot submit on Prolific, and their data lands in a different
experiment. Archive or delete the study file before recruiting.

**3. The assignment fallback is invisible.** In `boot()`, if `getCondition`
throws, the engine silently falls back to `Math.random()` — correct behaviour
(never lose a participant), but nothing in the saved row records which path was
taken, so balanced and unbalanced assignments are indistinguishable afterwards.
One line: add `assign_method: 'datapipe' | 'fallback'` to the wide row.

**4. Every value is saved as a string.** The row is built with `String(v)`, so
`picked_is_cause` is the four characters `true`, not `1`. A natural
`df[df.picked_is_cause == True]` returns nothing, silently. `v_typed` casts once,
in one place; use it rather than casting ad hoc.

**5. Consider the failure mode at save.** The DataPipe save runs *before* the
completion-code screen, which is the right order for data safety. But if the save
throws, the participant may never reach the code and cannot submit. A fallback
that shows the code regardless costs you a reconcilable payment instead of a
support ticket and a lost participant.

**6. Smaller notes.** The attention check is on a different text than the
stimulus, so it measures attention to the task, not to the paragraph — fine, but
say so. `total_ms` includes consent and instruction reading. Declining consent
aborts without saving a row, so decliners cannot be counted in a flow diagram.
Rungs 4 and 5 carry overt negation and 1–3 do not, so negation is confounded with
the top of the ladder, though not with the hinge.

---

## 7. What I would do next

1. **Add the two de-confounding sentences.** Without them a step at 2→3 has two
   equally good explanations and the study cannot separate them.
2. **Pre-register the hinge as the primary hypothesis**, tested as the pooled
   rungs 1–2 vs 3–5 contrast on P(cause). It is the cheapest well-powered test
   you have (.92 at N = 1000) and it is the claim the grammar actually makes.
3. **Demote the interaction to secondary** and say in advance that it is
   underpowered, or reallocate to a 2x2 and buy it properly. Do not run a 2x5 at
   N = 500 and interpret the interaction — at that size it is at 10% power, which
   means a significant result is more likely to be noise than signal.
4. **Fix the scale question before unblinding.** Points or odds — decide, write it
   down.
5. **Code the `why_text` against the same six dimensions.** It is the only channel
   where a reader says what they thought they were doing, and it is the natural
   place to test whether readers who pick self-blame at rung 5 are describing a
   different task than readers who pick it at rung 1. Query Q10 pulls it.

---

### Running any of this

```
python3 analysis/extract_stimuli.py                    # HTML -> stimuli.json
python3 analysis/depth_grammar.py                      # the coding, the hinge, the PCA
python3 analysis/power.py                              # recovery, power, shape tests
python3 analysis/power_designs.py                      # 2x5 vs 2x2 allocation
python3 analysis/power_mdi.py                          # minimum detectable interaction
python3 analysis/ingest.py --demo 1500 --db demo.db    # build a database from synthetic data
python3 analysis/ingest.py --csv-dir <export> --db study.db   # ...or from the real export
python3 analysis/rosetta_check.py demo.db              # prove SQL and Python agree
```
