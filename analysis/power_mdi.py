#!/usr/bin/env python3
"""Minimum detectable interaction: what CAN this design see, at what price?

Holds the plain frame fixed and varies only how much of the frame's
suppressive power survives at depth. b_x = 0 means the 'setting aside'
instruction works equally well on a belief report as on a feeling report;
b_x = 0.818 means it does nothing at all once the sentence goes global.
"""
import json, pathlib
import numpy as np
from choice_model import simulate, design, fit, wald_p, alpha_B_for_pB, STEP

ROOT = pathlib.Path(__file__).resolve().parents[1]
PLAIN = {1: .20, 2: .22, 3: .38, 4: .42, 5: .45}
AS, AN = -1.6, -1.8
REST = 1 + np.exp(AS) + np.exp(AN)

p_of_a = lambda a: np.exp(a) / (REST + np.exp(a))
a_of_p = lambda p: alpha_B_for_pB(p, AS, AN)

DELTA_SHALLOW = a_of_p(.21) - a_of_p(.105)     # 0.818: frame suppression at rungs 1-2


def truth_for(b_x):
    """setaside probabilities implied by an interaction of size b_x."""
    out = {"plain": dict(PLAIN), "setaside": {}}
    for r in range(1, 6):
        delta = DELTA_SHALLOW - (b_x if r >= 3 else 0.0)
        out["setaside"][r] = float(p_of_a(a_of_p(PLAIN[r]) - delta))
    return out


if __name__ == "__main__":
    REPS = 250
    print("=" * 78)
    print("MINIMUM DETECTABLE INTERACTION  (2x5, step coding, Wald a=.05, %d sims)" % REPS)
    print("=" * 78)
    print("  b_x is how much of the frame's suppression is LOST at rungs 3-5.")
    print("  b_x=0.42 is the scenario used earlier; b_x=0.82 = the instruction")
    print("  stops working entirely once the sentence stops naming the event.\n")
    header = ["N=500", "N=1000", "N=2000", "N=3000"]
    print(f"  {'b_x':>6}{'OR shallow->deep':>20}" + "".join(h.rjust(10) for h in header))
    res = {}
    for b_x in (0.20, 0.42, 0.60, 0.82, 1.00):
        t = truth_for(b_x)
        or_s = np.exp(DELTA_SHALLOW); or_d = np.exp(DELTA_SHALLOW - b_x)
        row = []
        for N in (500, 1000, 2000, 3000):
            rng = np.random.default_rng(4000 + int(b_x * 100) + N)
            hit = 0
            for _ in range(REPS):
                X, y, _ = design(simulate(N // 10, t, rng=rng), STEP)
                th, se, _ = fit(X, y)
                hit += wald_p(th, se, 8) < .05
            row.append(hit / REPS)
        res[f"{b_x:.2f}"] = {"or_shallow": or_s, "or_deep": or_d,
                             "power": dict(zip([500, 1000, 2000, 3000], row))}
        print(f"  {b_x:>6.2f}{f'{or_s:.2f} -> {or_d:.2f}':>20}" + "".join(f"{p:>10.3f}" for p in row))
    (ROOT / "analysis" / "power_mdi.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
