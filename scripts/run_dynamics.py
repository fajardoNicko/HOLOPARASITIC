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

    # --- per-parasite window at the moderate rate ------------------------------
    r_ref = 0.25
    par_rows = []
    try:
        with open(os.path.join(datadir, "parasites.json")) as f:
            parasites = json.load(f)
        print(f"\n per-parasite pre-symptomatic window (r={r_ref}, rho0={rho0}):")
        for p in parasites:
            t_c = dynamics.crossing_time(p["p_c"], r_ref, rho0)
            window = f_c and (dynamics.crossing_time(f_c, r_ref, rho0) - t_c)
            par_rows.append({"name": p["name"], "kind": p["kind"],
                             "p_c": p["p_c"], "t_c": t_c, "window": window})
            print(f"  {p['name']:22s} p_c={p['p_c']:.3f}  "
                  f"t_c={t_c:5.2f}  window={window:5.2f}", flush=True)
    except Exception as e:
        print(f"  (skipped per-parasite table: {e})", flush=True)

    # --- figure ---------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    colors = {"slow (r=0.15)": "#1f6f4a", "moderate (r=0.25)": "#c1121f",
              "aggressive (r=0.40)": "#8c4a2f"}
    for label, s in runs.items():
        ax.plot(s["t"], s["rho"], lw=2, color=colors[label], label=label)

    ax.axhline(p_c, color="black", ls="--", lw=1.4)
    ax.text(0.2, p_c + 0.015, f"$p_c$ = {p_c:.2f}  (functional collapse)",
            fontsize=9)
    ax.axhline(f_c, color="0.4", ls=":", lw=1.4)
    ax.text(0.2, f_c + 0.015, f"$f_c$ = {f_c:.2f}  (visible wilting)", fontsize=9)

    # shade the pre-symptomatic window for the moderate parasite
    m = runs["moderate (r=0.25)"]
    ax.axvspan(m["t_c"], m["t_wilt"], color="#ffd000", alpha=0.25)
    ax.annotate("", xy=(m["t_wilt"], 0.5), xytext=(m["t_c"], 0.5),
                arrowprops=dict(arrowstyle="<->", color="black"))
    ax.text((m["t_c"] + m["t_wilt"]) / 2, 0.53,
            f"window\n{m['window']:.1f} time-units", ha="center", fontsize=9)
    for s in runs.values():
        ax.scatter([s["t_c"]], [p_c], color="black", zorder=5, s=25)

    ax.set_xlabel("time since infestation  (growth-time units, read as days)")
    ax.set_ylabel(r"haustorial load  $\rho(t)$")
    ax.set_ylim(0, 1.0)
    ax.set_title(r"Logistic infestation $d\rho/dt = r\,\rho(1-\rho)$ crossing the "
                 r"collapse threshold" + "\n(the gap = pre-symptomatic window "
                 "visual scouting misses)")
    ax.legend(loc="center right"); ax.grid(alpha=0.25)
    fig.tight_layout()
    path = os.path.join(figdir, "dynamics.png")
    fig.savefig(path, dpi=160); plt.close(fig)

    # --- save data ------------------------------------------------------------
    def _py(d):
        return {k: (v.tolist() if isinstance(v, np.ndarray) else v)
                for k, v in d.items()}
    payload = {"p_c": p_c, "f_c": f_c, "rho0": rho0, "kappa": kappa,
               "rates": {k: _py(v) for k, v in runs.items()},
               "per_parasite": par_rows}
    with open(os.path.join(datadir, "dynamics.json"), "w") as f:
        json.dump(payload, f, indent=2)

    print(f"\nfigure -> {path}", flush=True)
    print(f"data   -> {os.path.join(datadir, 'dynamics.json')}", flush=True)


if __name__ == "__main__":
    main()
