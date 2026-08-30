"""
run_dynamics.py — time-dependent extension: when does the host collapse, and how
big is the pre-symptomatic window?

Couples the STATIC threshold p_c (from the percolation model) with a DYNAMIC
logistic growth of haustorial load rho(t) (holoparasitic.dynamics). Outputs:

  * collapse time t_c (rho reaches p_c)      -- functional, pre-symptomatic
  * wilting time  t_wilt (rho reaches f_c)   -- visible
  * the early-warning window t_wilt - t_c    -- what the metric buys the farmer

Sweeps three infestation growth rates and, using data/parasites.json, reports the
window per parasite. Saves figures/dynamics.png + data/dynamics.json.

    C:\\laragon\\bin\\python\\python-3.13\\python.exe scripts\\run_dynamics.py
"""

import os
import sys
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import config
from holoparasitic import network, dynamics


def _load_pc_random(default=0.279):
    try:
        with open(os.path.join(config.PATHS.data, "summary.json")) as f:
            return float(json.load(f)["p_c_random"])
    except Exception:
        return default


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass

    figdir, datadir = config.PATHS.figures, config.PATHS.data
    os.makedirs(datadir, exist_ok=True)
    os.makedirs(figdir, exist_ok=True)

    # --- host constants: p_c (functional collapse) and f_c (full fragmentation) ---
    G = network.generate()
    deg = np.array([d for _, d in G.degree()], float)
    kappa = (deg ** 2).mean() / deg.mean()
    f_c = 1.0 - 1.0 / (kappa - 1.0)          # analytic GCC->0 point (Callaway)
    p_c = _load_pc_random()
    rho0 = 0.02                               # 2 % initial infestation

    print(f"host: kappa={kappa:.2f}  p_c(functional)={p_c:.3f}  "
          f"f_c(visible)={f_c:.3f}  rho0={rho0}", flush=True)

    # --- sweep three growth rates (slow / moderate / aggressive parasite) ------
    rates = {"slow (r=0.15)": 0.15, "moderate (r=0.25)": 0.25,
             "aggressive (r=0.40)": 0.40}
    runs = {}
    print("\n growth rate            t_c     t_wilt   window   (analytic err)")
    for label, r in rates.items():
        s = dynamics.simulate(r=r, rho0=rho0, p_c=p_c, f_c=f_c)
        runs[label] = s
        print(f"  {label:20s}  {s['t_c']:6.2f}  {s['t_wilt']:6.2f}  "
              f"{s['window']:6.2f}   ({s['max_abs_err_vs_numeric']:.1e})",
              flush=True)

    # The per-parasite window table was REMOVED (2026-08-14). It read from
    # data/parasites.json, i.e. the multi-parasite comparison that was dropped
    # from the study's scope because its efficiencies were stipulated rather than
    # measured. Leaving it in the payload risked its reappearing in a figure that
    # the Methods no longer covers.

    # --- figure ---------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    colors = {"slow (r=0.15)": "#1f6f4a", "moderate (r=0.25)": "#c1121f",
              "aggressive (r=0.40)": "#8c4a2f"}
    for label, s in runs.items():
        ax.plot(s["t"], s["rho"], lw=2, color=colors[label], label=label)

    # Both lines are MODEL criteria on the same removal process. Neither is a
    # symptom: the model contains no symptom variable, so f_c must not be
    # labelled "wilting" and the gap must not be called pre-symptomatic.
    ax.axhline(p_c, color="black", ls="--", lw=1.4)
    ax.text(0.2, p_c + 0.015, f"$p_c$ = {p_c:.2f}  (fragmentation criterion)",
            fontsize=9)
    ax.axhline(f_c, color="0.4", ls=":", lw=1.4)
    ax.text(0.2, f_c + 0.015, f"$f_c$ = {f_c:.2f}  (giant component lost)",
            fontsize=9)

    # shade the separation between the two criteria for the moderate rate
    m = runs["moderate (r=0.25)"]
    ax.axvspan(m["t_c"], m["t_wilt"], color="#ffd000", alpha=0.25)
    ax.annotate("", xy=(m["t_wilt"], 0.44), xytext=(m["t_c"], 0.44),
                arrowprops=dict(arrowstyle="<->", color="black"))
    # sits below f_c so it cannot collide with the criterion label on that line
    ax.text((m["t_c"] + m["t_wilt"]) / 2, 0.335,
            f"separation\n{m['window']:.1f} growth-time units", ha="center",
            fontsize=9)
    for s in runs.values():
        ax.scatter([s["t_c"]], [p_c], color="black", zorder=5, s=25)

    # The time unit is set by the assumed growth rate r and is NOT calibrated to
    # any measured infestation time-course; the window's existence and shape,
    # not its duration, is the result.
    ax.set_xlabel("time since infestation  (arbitrary units set by the assumed "
                  "growth rate $r$)")
    ax.set_ylabel(r"affected node fraction  $\rho(t)$")
    ax.set_ylim(0, 1.0)
    ax.set_title(r"Logistic load growth $d\rho/dt = r\,\rho(1-\rho)$ crossing the "
                 r"two collapse criteria"
                 + "\n(the gap is the separation between $p_c$ and $f_c$, "
                   "not a physiological window)")
    ax.legend(loc="center right"); ax.grid(alpha=0.25)
    fig.tight_layout()
    path = os.path.join(figdir, "dynamics.png")
    fig.savefig(path, dpi=160); plt.close(fig)

    # --- save data ------------------------------------------------------------
    def _py(d):
        return {k: (v.tolist() if isinstance(v, np.ndarray) else v)
                for k, v in d.items()}
    payload = {"p_c": p_c, "f_c": f_c, "rho0": rho0, "kappa": kappa,
               "p_c_source": ("random-attack threshold of the SYNTHETIC "
                              "reference network (data/summary.json); the "
                              "empirical cohort median is 0.1998"),
               "f_c_definition": ("analytic removal fraction at which the giant "
                                  "component vanishes (Callaway), a different "
                                  "criterion from p_c, which is the fraction at "
                                  "which the giant component falls below half "
                                  "its initial size"),
               "time_units": ("arbitrary; set by the assumed growth rate r. Not "
                              "calibrated to any measured infestation "
                              "time-course."),
               "rates": {k: _py(v) for k, v in runs.items()},
               "per_parasite_removed": ("the multi-parasite comparison was "
                                        "dropped from the study's scope; see "
                                        "the note in this script")}
    with open(os.path.join(datadir, "dynamics.json"), "w") as f:
        json.dump(payload, f, indent=2)

    print(f"\nfigure -> {path}", flush=True)
    print(f"data   -> {os.path.join(datadir, 'dynamics.json')}", flush=True)


if __name__ == "__main__":
    main()
