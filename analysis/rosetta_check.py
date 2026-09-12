#!/usr/bin/env python3
"""Rosetta: the same object in four notations, and a proof they agree.

A translation table is a claim. This is the test of the claim. The choice set
a participant faced is:

  GRAMMAR  four sentences, one of which predicates a property of the self
  MATHS    an alternative set J with utilities V_ij and an argmax
  PYTHON   a tensor X of shape (N, 4, K) plus a chosen index y
  SQL      four rows of v_choice_set sharing a pid, one with chosen = 1

If those are really one object, then building the design matrix through SQL
and building it through Python must give byte-identical arrays and identical
coefficients. That is what this asserts. Run it and it either passes or the
translation is wrong somewhere.
"""
import pathlib, sqlite3, sys
import numpy as np
from choice_model import design, fit, STEP

ROLES = ["C", "B", "S", "N"]


def via_sql(con):
    """Path A: let the database reconstruct the choice sets."""
    rows = con.execute("""
        SELECT pid, frame, rung, position, role, chosen
        FROM v_choice_set ORDER BY pid, position""").fetchall()
    by_pid = {}
    for pid, frame, rung, pos, role, chosen in rows:
        by_pid.setdefault(pid, []).append((pos, role, chosen, frame, rung))
    recs = []
    for pid in sorted(by_pid):
        opts = sorted(by_pid[pid])
        frame, rung = opts[0][3], opts[0][4]
        order = np.array([ROLES.index(o[1]) for o in opts])
        k = [i for i, o in enumerate(opts) if o[2] == 1][0]
        recs.append((0 if frame == "plain" else 1, rung, order, k))
    return recs


def via_python(con):
    """Path B: reconstruct them in Python straight from the wide row."""
    rows = con.execute("""
        SELECT pid, frame, rung, pos1_role, pos2_role, pos3_role, pos4_role, picked_position
        FROM v_clean ORDER BY pid""").fetchall()
    recs = []
    for pid, frame, rung, p1, p2, p3, p4, picked in rows:
        order = np.array([ROLES.index(r) for r in (p1, p2, p3, p4)])
        recs.append((0 if frame == "plain" else 1, rung, order, picked - 1))
    return recs


def main(db):
    con = sqlite3.connect(db)
    A, B = via_sql(con), via_python(con)

    print("=" * 74)
    print("ROSETTA ROUND TRIP")
    print("=" * 74)
    print(f"  choice sets via SQL    : {len(A)}")
    print(f"  choice sets via Python : {len(B)}")
    assert len(A) == len(B), "different number of choice sets"

    XA, yA, names = design(A, STEP)
    XB, yB, _     = design(B, STEP)
    assert np.array_equal(XA, XB), "design tensors differ"
    assert np.array_equal(yA, yB), "chosen indices differ"
    print(f"  design tensor          : {XA.shape} identical through both paths  OK")
    print(f"  chosen index vector    : {yA.shape} identical through both paths  OK")

    thA, seA, llA = fit(XA, yA)
    thB, seB, llB = fit(XB, yB)
    assert np.allclose(thA, thB, atol=1e-9), "coefficients differ"
    print(f"  fitted coefficients    : max |diff| = {np.abs(thA-thB).max():.2e}  OK")

    # Third path: the SQL aggregate, the model's fitted marginals, and the raw
    # counts should all describe the same P(self-blame) per cell.
    print()
    print("  P(self-blame) three ways -- SQL aggregate / raw count / model fit")
    print(f"  {'frame':<10}{'rung':<6}{'SQL':>8}{'count':>8}{'model':>8}")
    V = XA @ thA
    V -= V.max(axis=1, keepdims=True)
    e = np.exp(V); P = e / e.sum(axis=1, keepdims=True)
    is_B = XA[:, :, 0] == 1.0                       # role dummy B is column 0
    model_pB = (P * is_B).sum(axis=1)
    frames = np.array([r[0] for r in A]); rungs = np.array([r[1] for r in A])
    picked_B = np.array([A[i][2][yA[i]] == 1 for i in range(len(A))])
    worst = 0.0
    for fi, fname in enumerate(("plain", "setaside")):
        for r in range(1, 6):
            sq = con.execute("SELECT p_selfblame FROM v_cell_rates WHERE frame=? AND rung=?",
                             (fname, r)).fetchone()[0]
            m = (frames == fi) & (rungs == r)
            cnt, mod = picked_B[m].mean(), model_pB[m].mean()
            worst = max(worst, abs(sq - cnt))
            print(f"  {fname:<10}{r:<6}{sq:>8.3f}{cnt:>8.3f}{mod:>8.3f}")
    assert worst < 1e-9, f"SQL and Python disagree on P(self-blame) by {worst}"
    print(f"\n  SQL vs Python counts   : max |diff| = {worst:.2e}  OK")

    print()
    print("  fitted model (step coding), for reference")
    for nm, t, s in zip(names, thA, seA):
        star = "  *" if abs(t / s) > 1.96 else ""
        print(f"    {nm:<14}{t:+8.3f}  (se {s:.3f}){star}")
    con.close()
    print("\n  ALL TRANSLATIONS AGREE.")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "study.db")
