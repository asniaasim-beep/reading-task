#!/usr/bin/env python3
"""Where should the participants go? 2x5 (all five rungs) vs 2x2 (endpoints only).

Same money, different allocation. The interaction is the expensive term, so
the question is whether spreading N over five rungs is worth what it costs
in power to detect that the frame bites differently at depth.
"""
import json, pathlib
import numpy as np
from scipy.stats import norm
from choice_model import simulate, design, fit, wald_p, STEP
from power import TRUTH

ROOT = pathlib.Path(__file__).resolve().parents[1]


def two_by_two(n_per_cell, rng):
    """Only rungs 2 and 4: one clearly episode-bound, one clearly person-bound."""
    sub = {f: {r: TRUTH[f][r] for r in (2, 4)} for f in TRUTH}
    recs = []
    for f, fname in enumerate(("plain", "setaside")):
        for r in (2, 4):
            from choice_model import alpha_B_for_pB
            aB = alpha_B_for_pB(sub[fname][r], -1.6, -1.8)
            util = np.array([0.0, aB, -1.6, -1.8])
            for _ in range(n_per_cell):
                order = rng.permutation(4)
                v = util[order] + np.array([0.0, -0.15, -0.25, -0.30])
                p = np.exp(v - v.max()); p /= p.sum()
                recs.append((f, r, order.copy(), rng.choice(4, p=p)))
    return recs


def pooled_hinge_power(n_per_cell, reps, seed):
    """Cheapest headline test: P(cause) for rungs 1-2 vs 3-5, plain frame only,
    as a two-proportion z test. No model, no covariates."""
    rng = np.random.default_rng(seed)
    hit = 0
    for _ in range(reps):
        recs = simulate(n_per_cell, TRUTH, rng=rng)
        lo = [r for r in recs if r[0] == 0 and r[1] <= 2]
        hi = [r for r in recs if r[0] == 0 and r[1] >= 3]
        c = lambda g: sum(1 for (_, _, order, k) in g if order[k] == 0)
        x1, n1, x2, n2 = c(lo), len(lo), c(hi), len(hi)
        p1, p2 = x1 / n1, x2 / n2
        pp = (x1 + x2) / (n1 + n2)
        se = np.sqrt(pp * (1 - pp) * (1 / n1 + 1 / n2))
        hit += (2 * norm.sf(abs(p1 - p2) / se)) < .05
    return hit / reps


if __name__ == "__main__":
    REPS = 250
    print("=" * 78)
    print("A. CHEAPEST HEADLINE TEST: P(cause) rungs 1-2 vs 3-5, plain frame,")
    print("   two-proportion z test (no model). Truth: .578 vs .426")
    print("=" * 78)
    print(f"  {'n/cell':>7}{'N total':>9}{'n in test':>11}{'power':>9}")
    A = {}
    for n in (25, 40, 50, 75, 100):
        pw = pooled_hinge_power(n, REPS, 31 + n)
        A[n] = pw
        print(f"  {n:>7}{n*10:>9}{n*5:>11}{pw:>9.3f}")

    print()
    print("=" * 78)
    print(f"B. THE INTERACTION, 2x5 vs 2x2, AT MATCHED TOTAL N  ({REPS} sims)")
    print("=" * 78)
    print(f"  {'N total':>9}{'2x5 (10 cells)':>18}{'2x2 (4 cells)':>17}")
    B = {}
    for N in (400, 800, 1200, 2000, 3000):
        rng = np.random.default_rng(9000 + N)
        h5 = h2 = 0
        for _ in range(REPS):
            X, y, _ = design(simulate(N // 10, TRUTH, rng=rng), STEP)
            th, se, _ = fit(X, y)
            h5 += wald_p(th, se, 8) < .05
            X, y, _ = design(two_by_two(N // 4, rng), STEP)
            th, se, _ = fit(X, y)
            h2 += wald_p(th, se, 8) < .05
        B[N] = {"2x5": h5 / REPS, "2x2": h2 / REPS}
        print(f"  {N:>9}{h5/REPS:>18.3f}{h2/REPS:>17.3f}")

    (ROOT / "analysis" / "power_designs.json").write_text(
        json.dumps({"pooled_hinge": A, "interaction_by_design": B}, indent=2), encoding="utf-8")
