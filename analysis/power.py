#!/usr/bin/env python3
"""Recovery check + power for the reading task, by Monte Carlo simulation."""
import json, pathlib
import numpy as np
from scipy.stats import chi2
from choice_model import (simulate, design, fit, wald_p, alpha_B_for_pB,
                          LINEAR, STEP, FREE, ROLES)

ROOT = pathlib.Path(__file__).resolve().parents[1]

# A hinge-shaped truth: self-blame gains pulling power exactly where the
# sentence stops referring to the birthday (rung 2 -> 3), and the 'setting
# aside how it makes the writer feel' frame suppresses it LESS at deep rungs,
# because rungs 3-5 are belief reports, not feeling reports.
TRUTH = {"plain":    {1: .20, 2: .22, 3: .38, 4: .42, 5: .45},
         "setaside": {1: .10, 2: .11, 3: .28, 4: .33, 5: .37}}

# A null-ish truth for the false-positive check: nothing moves.
FLAT  = {"plain":    {r: .25 for r in range(1, 6)},
         "setaside": {r: .25 for r in range(1, 6)}}


def cell_probs(pB, aS=-1.6, aN=-1.8):
    out = {}
    for f in pB:
        for r in pB[f]:
            aB = alpha_B_for_pB(pB[f][r], aS, aN)
            v = np.array([0.0, aB, aS, aN]); e = np.exp(v)
            out[(f, r)] = e / e.sum()
    return out


def run(n_per_cell, truth, code, reps, seed, test_idx):
    """Return rejection rate for each parameter index in test_idx, + mean estimates."""
    rng = np.random.default_rng(seed)
    rej = np.zeros(len(test_idx)); ests = []
    for _ in range(reps):
        recs = simulate(n_per_cell, truth, rng=rng)
        X, y, names = design(recs, code)
        th, se, _ = fit(X, y)
        ests.append(th)
        for a, i in enumerate(test_idx):
            rej[a] += wald_p(th, se, i) < .05
    return rej / reps, np.mean(ests, axis=0), names


def lrt_shape(n_per_cell, truth, reps, seed):
    """Under a hinge truth, how often do we (a) reject a straight line,
       (b) fail to reject the step? Both LRTs are against the saturated model."""
    rng = np.random.default_rng(seed)
    rej_lin = rej_step = 0
    for _ in range(reps):
        recs = simulate(n_per_cell, truth, rng=rng)
        lls = {}
        for nm, code in (("free", FREE), ("linear", LINEAR), ("step", STEP)):
            X, y, _ = design(recs, code)
            lls[nm] = fit(X, y)[2]
        rej_lin  += (1 - chi2.cdf(2 * (lls["free"] - lls["linear"]), 6)) < .05
        rej_step += (1 - chi2.cdf(2 * (lls["free"] - lls["step"]),   6)) < .05
    return rej_lin / reps, rej_step / reps


if __name__ == "__main__":
    np.set_printoptions(precision=3, suppress=True)
    print("=" * 78)
    print("IMPLIED CELL PROBABILITIES UNDER THE HINGE-SHAPED TRUTH")
    print("=" * 78)
    cp = cell_probs(TRUTH)
    print(f"  {'frame':<10}{'rung':<6}" + "".join(f"P({r})".rjust(9) for r in ROLES))
    for f in ("plain", "setaside"):
        for r in range(1, 6):
            print(f"  {f:<10}{r:<6}" + "".join(f"{v:>9.3f}" for v in cp[(f, r)]))
    d_plain = cp[("plain", 5)][0] - cp[("plain", 1)][0]
    print(f"\n  P(cause) plain: rung1 {cp[('plain',1)][0]:.3f} -> rung5 {cp[('plain',5)][0]:.3f}  (drop {-d_plain:.3f})")

    REPS = 300
    print()
    print("=" * 78)
    print(f"RECOVERY + POWER  (step coding, {REPS} sims per row, Wald alpha=.05)")
    print("=" * 78)
    # step coding param order: B,S,N,pos2,pos3,pos4, B:d0, B:frame, B:d0:frame
    IDX = {"depth (B:d0)": 6, "frame (B:frame)": 7, "depth x frame": 8}
    true_th = None
    print(f"  {'n/cell':>7}{'N total':>9}" + "".join(k.rjust(18) for k in IDX))
    rows = {}
    for n in (50, 75, 100, 150, 200):
        pw, est, names = run(n, TRUTH, STEP, REPS, 101 + n, list(IDX.values()))
        rows[n] = {"power": dict(zip(IDX, pw.tolist())), "est": dict(zip(names, est.tolist()))}
        print(f"  {n:>7}{n*10:>9}" + "".join(f"{p:>18.3f}" for p in pw))
        if true_th is None:
            true_th = est
    print("\n  mean estimates at n=200/cell (sanity: signs and rough magnitudes)")
    pw, est, names = run(200, TRUTH, STEP, 120, 777, [6, 7, 8])
    for nm, v in zip(names, est):
        print(f"    {nm:<16}{v:+.3f}")

    print()
    print("=" * 78)
    print(f"FALSE-POSITIVE CHECK (flat truth: nothing moves)  {REPS} sims")
    print("=" * 78)
    pw, _, _ = run(100, FLAT, STEP, REPS, 909, list(IDX.values()))
    print(f"  n=100/cell  rejection rates: " + "  ".join(f"{k}={p:.3f}" for k, p in zip(IDX, pw)))

    print()
    print("=" * 78)
    print("CAN WE SEE THE HINGE? (LRT vs saturated, 6 df, hinge truth)")
    print("=" * 78)
    print(f"  {'n/cell':>7}{'N total':>9}{'reject LINEAR':>16}{'reject STEP':>14}   (want high / low)")
    shape = {}
    for n in (50, 100, 150, 200):
        a, b = lrt_shape(n, TRUTH, 200, 555 + n)
        shape[n] = {"reject_linear": a, "reject_step": b}
        print(f"  {n:>7}{n*10:>9}{a:>16.3f}{b:>14.3f}")

    (ROOT / "analysis" / "power_results.json").write_text(
        json.dumps({"truth": TRUTH, "power": rows, "shape": shape,
                    "cell_probs": {f"{f}_{r}": cp[(f, r)].tolist() for (f, r) in cp}},
                   indent=2), encoding="utf-8")
