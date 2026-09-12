#!/usr/bin/env python3
"""The reading task is a discrete-choice experiment. This is its estimator.

Each participant sees ONE choice set of 4 options {C,B,S,N} in a random order
and picks one. That is McFadden's conditional logit, not a 2x5 ANOVA:

    V_ij = a_role(j) + p_pos(j) + 1[role=B]*(b0 + b_d*d(r_i) + b_f*f_i + b_x*d(r_i)*f_i)
    P(i picks j) = exp(V_ij) / sum_k exp(V_ik)

Depth enters as a shift in the utility of the SELF-BLAME option only, because
that is the only option the manipulation touches. Frame is allowed to move
self-blame too, and b_x is the interaction the whole study is really about.

d(r) is the depth coding, and it is where the linguistics becomes arithmetic:
    linear d(r) = (r-1)/4        "depth is a dial"
    step   d(r) = 1[r >= 3]      "depth is a switch: episode-bound vs person-bound"
    free   4 dummies             "let the data say"
"""
import numpy as np
from scipy.optimize import minimize
from scipy.stats import norm, chi2

ROLES = ["C", "B", "S", "N"]
RNG_SEED = 20260912

# ----------------------------------------------------------------- truth ----
def alpha_B_for_pB(pB, aS, aN):
    """Utility of the self-blame option that yields marginal P(B)=pB.

    With a_C = 0 fixed and a_S, a_N fixed, P(B) pins a_B uniquely:
        pB = e^aB / (1 + e^aB + e^aS + e^aN)
    """
    rest = 1.0 + np.exp(aS) + np.exp(aN)
    return np.log(pB * rest / (1.0 - pB))


def simulate(n_per_cell, pB, aS=-1.6, aN=-1.8, pos=(0.0, -0.15, -0.25, -0.30), rng=None):
    """pB[frame][rung] -> marginal P(self-blame). Returns (X_roles, X_pos, y, frame, rung)."""
    rng = rng or np.random.default_rng(RNG_SEED)
    recs = []
    for f, fname in enumerate(("plain", "setaside")):
        for r in range(1, 6):
            aB = alpha_B_for_pB(pB[fname][r], aS, aN)
            util = np.array([0.0, aB, aS, aN])           # order = ROLES
            for _ in range(n_per_cell):
                order = rng.permutation(4)               # order[k] = role index at position k
                v = util[order] + np.asarray(pos)        # position 0..3 bonus/penalty
                p = np.exp(v - v.max()); p /= p.sum()
                k = rng.choice(4, p=p)                   # chosen POSITION
                recs.append((f, r, order.copy(), k))
    return recs


# --------------------------------------------------------------- design -----
def design(recs, depth_code):
    """Build (N,4,K) design tensor, chosen index, and parameter names.

    depth_code: callable rung -> array of depth regressors (len m).
    Params: [B, S, N] role dummies, [pos2,pos3,pos4],
            B*depth (m), B*frame, B*depth*frame (m)
    """
    m = len(depth_code(1))
    K = 3 + 3 + m + 1 + m
    N = len(recs)
    X = np.zeros((N, 4, K)); y = np.zeros(N, int)
    for i, (f, r, order, k) in enumerate(recs):
        d = np.asarray(depth_code(r), float)
        for kpos in range(4):
            role = order[kpos]
            x = X[i, kpos]
            if role in (1, 2, 3):
                x[role - 1] = 1.0                       # B,S,N dummies (C = reference)
            if kpos in (1, 2, 3):
                x[3 + kpos - 1] = 1.0                   # pos2,pos3,pos4 (pos1 = reference)
            if role == 1:                                # self-blame option only
                x[6:6 + m] = d
                x[6 + m] = f
                x[7 + m:7 + m + m] = d * f
        y[i] = k
    names = (["B", "S", "N", "pos2", "pos3", "pos4"]
             + [f"B:d{j}" for j in range(m)] + ["B:frame"]
             + [f"B:d{j}:frame" for j in range(m)])
    return X, y, names


def fit(X, y):
    N, J, K = X.shape
    idx = np.arange(N)

    def nll_grad(th):
        V = X @ th                                       # (N,4)
        Vm = V - V.max(axis=1, keepdims=True)
        e = np.exp(Vm); P = e / e.sum(axis=1, keepdims=True)
        ll = (Vm[idx, y] - np.log(e.sum(axis=1))).sum()
        xbar = np.einsum("nj,njk->nk", P, X)
        g = (X[idx, y] - xbar).sum(axis=0)
        return -ll, -g

    res = minimize(nll_grad, np.zeros(K), jac=True, method="BFGS")
    th = res.x
    V = X @ th; V -= V.max(axis=1, keepdims=True)
    e = np.exp(V); P = e / e.sum(axis=1, keepdims=True)
    xbar = np.einsum("nj,njk->nk", P, X)
    H = np.einsum("nj,njk,njl->kl", P, X, X) - np.einsum("nk,nl->kl", xbar, xbar)
    cov = np.linalg.pinv(H)
    return th, np.sqrt(np.clip(np.diag(cov), 0, None)), -res.fun


LINEAR = lambda r: [(r - 1) / 4.0]
STEP   = lambda r: [1.0 if r >= 3 else 0.0]
FREE   = lambda r: [1.0 if r == k else 0.0 for k in (2, 3, 4, 5)]


def wald_p(th, se, i):
    return 2 * norm.sf(abs(th[i] / se[i])) if se[i] > 0 else 1.0
