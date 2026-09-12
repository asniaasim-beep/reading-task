#!/usr/bin/env python3
"""The depth grammar of the self-blame ladder, coded and measured.

Two kinds of number live here, and they must not be confused:

  * SURFACE metrics (word counts, negation counts, lexical hits) are computed
    from the strings. They are facts about the stimulus.
  * GRAMMAR codes (the six dimensions below) are my linguistic judgments,
    entered by hand with a written rationale per cell. Anything derived from
    them - including the PCA - describes the DESIGN's intended structure.
    It is arithmetic on an authored matrix, not evidence about readers.
"""
import json, pathlib, re
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
STIM = json.loads((ROOT / "analysis" / "stimuli.json").read_text(encoding="utf-8"))

DIMS = ["sigma_predication", "tau_temporal", "epsilon_commitment",
        "delta_domain", "alpha_agency", "kappa_free"]

DIM_GLOSS = {
    "sigma_predication": "scope of predication: bounded event -> individual-level property of the self",
    "tau_temporal":      "temporal quantification: one past act -> universal over the lifetime",
    "epsilon_commitment":"speaker's epistemic commitment to the self-ascription",
    "delta_domain":      "width of the domain of other people quantified over",
    "alpha_agency":      "loss of agency: agent of an act -> patient of a property",
    "kappa_free":        "anaphoric freedom: bound to the birthday event vs free-standing claim about the person",
}

# rung -> {dim: (score, rationale)}
CODES = {
1: {
 "sigma_predication": (0.00, "complement is an event ('send her the invitation'); nothing is predicated of the self"),
 "tau_temporal":      (0.10, "'keep' iterates the wishing, but its content is one bounded past act"),
 "epsilon_commitment":(0.05, "'wish' + past perfect = counterfactual desire; asserts nothing about the self"),
 "delta_domain":      (0.00, "one referent: 'her'"),
 "alpha_agency":      (0.00, "'I ... remembered', 'I ... send': the self is agent throughout"),
 "kappa_free":        (0.00, "lexically bound to the cause: 'invitation', 'remembered to send'"),
},
2: {
 "sigma_predication": (0.30, "'stupid' is a property word but sits under 'feel' and is tied to the episode"),
 "tau_temporal":      (0.25, "present-tense feeling about a bounded past act"),
 "epsilon_commitment":(0.30, "'feel X that P': P is presupposed (factive), but 'feel' not 'am' hedges the property"),
 "delta_domain":      (0.10, "'one of my closest friends': still one referent, but a partitive evokes the set"),
 "alpha_agency":      (0.15, "matrix subject is an experiencer; the self is still agent of the omission"),
 "kappa_free":        (0.00, "still bound to the cause: 'forgot to include'"),
},
3: {
 "sigma_predication": (0.60, "predicate is an ability ('be able to connect'): a disposition, not an event"),
 "tau_temporal":      (0.80, "'will ever': NPI under a question-embedding verb, unbounded future"),
 "epsilon_commitment":(0.40, "'wonder if' embeds an INTERROGATIVE - nothing is asserted; 'have started to' hedges again"),
 "delta_domain":      (0.70, "'good people': bare plural, kind-level. Domain jumps from a person to a kind"),
 "alpha_agency":      (0.35, "'connect with' is agentive but embedded under 'be able to': capacity, not act"),
 "kappa_free":        (1.00, "the event is gone: no Anna, no birthday, no invitation"),
},
4: {
 "sigma_predication": (0.90, "copular 'I am just not interesting enough': individual-level property of the self"),
 "tau_temporal":      (0.85, "individual-level predicates are temporally unbounded by default"),
 "epsilon_commitment":(0.70, "'believe' is doxastic and commits; hedged only by 'am starting to' and 'just'"),
 "delta_domain":      (0.85, "'to hold on to' has an arbitrary implicit subject: anyone at all"),
 "alpha_agency":      (0.80, "the self is the OBJECT of 'hold on to' and subject of a copula"),
 "kappa_free":        (1.00, "free-standing claim about the person"),
},
5: {
 "sigma_predication": (1.00, "'lovable': -able marks inherent potential - individual-level and modal"),
 "tau_temporal":      (1.00, "'my whole life': explicit universal quantification over the lifespan"),
 "epsilon_commitment":(1.00, "'certain that': full commitment, no hedge anywhere in the clause"),
 "delta_domain":      (1.00, "'lovable' = by anyone; 'alone' = universal negation of all company"),
 "alpha_agency":      (1.00, "-able is passive-potential: the self is patient of an unrealised loving; 'deserve' delivers a verdict on the self"),
 "kappa_free":        (1.00, "free-standing claim about the person"),
},
}

NEG = re.compile(r"\b(not|never|no|nothing|n't)\b|n't", re.I)
HEDGE = re.compile(r"\b(wish|wishing|wonder|feel|believe|starting|started|keep|seem|maybe|might)\b", re.I)
MODAL = re.compile(r"\b(will|would|can|could|able|ever|deserve|must)\b", re.I)


def surface(text: str) -> dict:
    words = re.findall(r"[A-Za-z']+", text)
    return {"words": len(words),
            "chars": len(text),
            "mean_wordlen": round(sum(map(len, words)) / len(words), 2),
            "neg": len(NEG.findall(text)),
            "hedge": len(HEDGE.findall(text)),
            "modal": len(MODAL.findall(text))}


def main() -> None:
    cell = STIM["stimuli"]["plain"]
    fixed = {r: cell["1"][r] for r in ("cause", "scene", "neutral")}

    print("=" * 78)
    print("1. THE THREE FIXED SENTENCES (identical in all 10 cells)")
    print("=" * 78)
    for name, t in fixed.items():
        s = surface(t)
        print(f"  {name:<8} {s['words']:>3}w {s['chars']:>3}c  neg={s['neg']} hedge={s['hedge']} modal={s['modal']}")
        print(f"           {t}")

    print()
    print("=" * 78)
    print("2. THE LADDER: SURFACE METRICS")
    print("=" * 78)
    print(f"  {'rung':<5}{'words':>6}{'chars':>7}{'wlen':>7}{'neg':>5}{'hedge':>7}{'modal':>7}   text")
    surf = {}
    for r in range(1, 6):
        t = cell[str(r)]["selfblame"]
        s = surf[r] = surface(t)
        print(f"  {r:<5}{s['words']:>6}{s['chars']:>7}{s['mean_wordlen']:>7}{s['neg']:>5}{s['hedge']:>7}{s['modal']:>7}   {t}")

    rungs = np.arange(1, 6)
    wc = np.array([surf[r]["words"] for r in rungs], float)
    cause_w = surface(fixed["cause"])["words"]
    print()
    print(f"  corr(rung, word count)      = {np.corrcoef(rungs, wc)[0,1]: .3f}")
    print(f"  word count range            = {wc.min():.0f} .. {wc.max():.0f}  (spread {wc.max()-wc.min():.0f} words)")
    print(f"  cause sentence word count   = {cause_w}  -> rungs 1-2 are SHORTER than the cause, rungs 3-5 LONGER")

    print()
    print("=" * 78)
    print("3. THE LADDER: GRAMMAR CODES  (hand-coded; see rationales below)")
    print("=" * 78)
    M = np.array([[CODES[r][d][0] for d in DIMS] for r in rungs])
    print("  " + "rung".ljust(6) + "".join(d.split('_')[0][:7].rjust(9) for d in DIMS) + "     mean")
    for i, r in enumerate(rungs):
        print(f"  {r:<6}" + "".join(f"{v:>9.2f}" for v in M[i]) + f"{M[i].mean():>9.2f}")

    print()
    print("  step sizes between adjacent rungs (where does the ladder actually jump?)")
    D = np.diff(M, axis=0)
    print("  " + "step".ljust(8) + "".join(d.split('_')[0][:7].rjust(9) for d in DIMS) + "      SUM")
    for i in range(4):
        print(f"  {rungs[i]}->{rungs[i+1]}   " + "".join(f"{v:>9.2f}" for v in D[i]) + f"{D[i].sum():>9.2f}")
    big = int(np.argmax(D.sum(axis=1)))
    print(f"\n  LARGEST JUMP: rung {rungs[big]} -> {rungs[big+1]}  (total {D[big].sum():.2f} of {D.sum():.2f} = {100*D[big].sum()/D.sum():.0f}% of the whole ladder)")

    # PCA on the authored coding matrix (descriptive of the design, not of readers)
    Mc = M - M.mean(axis=0)
    U, S, Vt = np.linalg.svd(Mc, full_matrices=False)
    var = S**2 / (S**2).sum()
    print()
    print("  PCA of the coding matrix (5 rungs x 6 dimensions):")
    for k in range(3):
        print(f"    PC{k+1}: {100*var[k]:5.1f}% of variance   loadings " +
              " ".join(f"{d.split('_')[0][:5]}={v:+.2f}" for d, v in zip(DIMS, Vt[k])))
    pc1 = U[:, 0] * S[0]
    if pc1[0] > pc1[-1]:
        pc1 = -pc1
    print(f"    PC1 score by rung: " + " ".join(f"r{r}={v:+.2f}" for r, v in zip(rungs, pc1)))
    print(f"    PC1 gaps:          " + " ".join(f"{rungs[i]}->{rungs[i+1]}={pc1[i+1]-pc1[i]:+.2f}" for i in range(4)))

    print()
    print("=" * 78)
    print("4. RATIONALES")
    print("=" * 78)
    for d in DIMS:
        print(f"\n  {d}  -- {DIM_GLOSS[d]}")
        for r in rungs:
            v, why = CODES[r][d]
            print(f"    r{r} {v:.2f}  {why}")

    out = {"dims": DIMS, "gloss": DIM_GLOSS,
           "codes": {str(r): {d: {"score": CODES[r][d][0], "why": CODES[r][d][1]} for d in DIMS} for r in rungs},
           "surface": {str(r): surf[r] for r in rungs},
           "pc1": {str(r): float(v) for r, v in zip(rungs, pc1)},
           "pc1_var": float(var[0])}
    (ROOT / "analysis" / "grammar_codes.json").write_text(json.dumps(out, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
