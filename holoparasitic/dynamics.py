"""
dynamics.py — temporal progression of haustorial load and the pre-symptomatic
intervention window.

The STATIC model gives a collapse THRESHOLD p_c: the fraction of vessels drained
at which the vascular giant component drops below 50 %. That answers *how much*
loss collapses the host — but not *when*. This module adds TIME: it models how the
haustorial load rho(t) grows and computes WHEN it crosses the threshold.

MODEL — logistic growth of infestation (a parasite spreads, then saturates):

    d(rho)/dt = r * rho * (1 - rho),      rho(0) = rho0

with closed-form solution

    rho(t) = 1 / (1 + A e^{-r t}),        A = (1 - rho0) / rho0

CROSSING TIME (time at which rho(t) reaches a target level):

    t* = (1/r) * ln[ (target / (1 - target)) * (1 - rho0) / rho0 ]

Two crossings carry the whole argument of the paper:

    t_c    : rho = p_c   -> FUNCTIONAL collapse (GCC < 50 %)  -- PRE-SYMPTOMATIC
    t_wilt : rho = f_c   -> FULL fragmentation (GCC -> 0)     -- VISIBLE wilting
    window = t_wilt - t_c  : the early-warning window the p_c metric exposes and
                             that symptom-based (visual) detection misses.

Units of t are arbitrary "growth-time"; read them as days when r is a per-day rate.
"""

from __future__ import annotations

import numpy as np


def rho_of_t(t, r, rho0):
    """Closed-form logistic load rho(t)."""
    A = (1.0 - rho0) / rho0
    return 1.0 / (1.0 + A * np.exp(-r * np.asarray(t, float)))


def crossing_time(target, r, rho0):
    """Time at which rho(t) reaches `target` (0 < target < 1).

    Returns nan for out-of-range inputs; a negative value means the target is
    below rho0 (already crossed at t = 0)."""
    if not (0.0 < target < 1.0) or r <= 0.0 or not (0.0 < rho0 < 1.0):
        return float("nan")
    A = (1.0 - rho0) / rho0
    return float(np.log((target / (1.0 - target)) * A) / r)


def _numeric_check(r, rho0, t):
    """Solve the ODE numerically and return max abs error vs the closed form —
    proves the analytic solution is correct (used in the paper's methods)."""
    from scipy.integrate import solve_ivp
    sol = solve_ivp(lambda _t, y: r * y * (1.0 - y), (t[0], t[-1]), [rho0],
                    t_eval=t, rtol=1e-9, atol=1e-12)
    return float(np.max(np.abs(sol.y[0] - rho_of_t(t, r, rho0))))


def simulate(r, rho0, p_c, f_c, t_max=None, n=400, verify=True):
    """Full trajectory + the two crossing times + the pre-symptomatic window.

    Returns a dict with t, rho, t_c, t_wilt, window (and, if verify, the
    numerical-vs-analytic error)."""
    t_c = crossing_time(p_c, r, rho0)
    t_wilt = crossing_time(f_c, r, rho0)
    if t_max is None:
        t_max = 1.30 * max(t_wilt, t_c, 1.0)
    t = np.linspace(0.0, t_max, n)
    out = {"t": t, "rho": rho_of_t(t, r, rho0),
           "t_c": t_c, "t_wilt": t_wilt, "window": t_wilt - t_c,
           "r": r, "rho0": rho0, "p_c": p_c, "f_c": f_c}
    if verify:
        out["max_abs_err_vs_numeric"] = _numeric_check(r, rho0, t)
    return out


if __name__ == "__main__":
    s = simulate(r=0.25, rho0=0.02, p_c=0.279, f_c=0.84)
    print(f"t_c (functional collapse) = {s['t_c']:.2f}")
    print(f"t_wilt (visible wilting)  = {s['t_wilt']:.2f}")
    print(f"pre-symptomatic window    = {s['window']:.2f}")
    print(f"analytic vs numeric error = {s['max_abs_err_vs_numeric']:.2e}")
