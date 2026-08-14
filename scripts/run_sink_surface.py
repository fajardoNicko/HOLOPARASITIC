r"""
run_sink_surface.py — the (K_h, D) coupled-hydraulic threshold surface, REBUILT
on the cohort-calibrated planar mesh.

Replaces the legacy surface in `sweep.pc_surface()`, which was computed on the
pre-2026-07 `knn` generator (mean degree 4.4-7.0, far above the cohort's
2.15-2.99) at sink strengths K_h = 0.3-2.5 (8-64x the literature-calibrated
K_H_HOLOPARASITE = 0.0392), with 600 trials per cell and no confidence
intervals. Everything the paper reports from that surface was therefore off
-calibration on all three axes.

WHAT THIS RUN CHANGES
  * generator      cohort-calibrated planar MESH (calibrate.calibrated_base),
                   N = 1023, <k> held at the cohort median by tuning mesh_frac
  * D axis         realised at CONSTANT N by tuning length_ratio to hit a target
                   box-counting D, then MEASURING it (never asserted)
  * K_h axis       anchored on the calibrated K_h and swept in multiples of it,
                   so every column can be read as "x times the literature value"
  * budget         N_TRIALS per cell (vs 600) + bootstrap percentile CI
  * reporting      a cell whose collapse probability never reaches .50 at ANY
                   haustorial density is recorded as "no threshold" (NaN) rather
                   than silently extrapolated

WHAT p_c MEANS HERE (this is NOT the topological threshold)
  In `percolation.py` hydraulic mode, rho is the fraction of nodes that BEAR a
  haustorium, not the fraction removed. Each trial places rho*N haustoria, solves
  the Kirchhoff water-potential field, and removes only those nodes whose psi falls
  below PSI_CAVITATION. p_c is therefore a critical HAUSTORIAL ATTACHMENT DENSITY
  and is not comparable cell-for-cell with the topological p_c reported for the
  empirical cohort.

    C:\laragon\bin\python\python-3.13\python.exe scripts\run_sink_surface.py
"""

import os
import sys
import json
import csv
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import config
from holoparasitic import network, fractal, percolation, calibrate as cal

GENERATIONS = 9                       # N = 1023, the hero size
TARGET_K = 2.4888                     # hero mean degree (cohort-calibrated)
D_TARGETS = (1.23, 1.39, 1.50, 1.54)  # the D axis, realised at constant N
KH_MULTIPLES = (1, 2, 3, 4, 6, 8, 16, 32, 64)
N_TRIALS = 6000
N_DENSITIES = 40
SEED = 11


# ---------------------------------------------------------------------------
# generator tuning: length_ratio -> D, mesh_frac -> <k>, iterated
# ---------------------------------------------------------------------------
def _measure(params):
    G = network.generate(params)
    return G, network.summary(G)["mean_degree"], fractal.fractal_dimension(G)


def _bisect(make, measure, lo, hi, target, tol, iters=14):
    """Generic monotone bisection on one generator knob."""
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        val = measure(make(mid))
        if abs(val - target) <= tol:
            return mid, val
        if val < target:
            lo = mid
        else:
            hi = mid
    mid = 0.5 * (lo + hi)
    return mid, measure(make(mid))


def tuned_network(d_target, verbose=True):
    """A calibrated-mesh network at GENERATIONS with measured D ~ d_target and
    measured <k> ~ TARGET_K. Returns (G, params, mean_degree, D)."""
    base = cal.calibrated_base(generations=GENERATIONS)
    lr, mf = base.length_ratio, base.mesh_frac
    for _ in range(3):
        mk_lr = lambda x: config.NetworkParams(
            **{**base.__dict__, "length_ratio": x, "mesh_frac": mf})
        lr, D = _bisect(mk_lr, lambda p: _measure(p)[2],
                        0.45, 1.45, d_target, 0.004)
        mk_mf = lambda x: config.NetworkParams(
            **{**base.__dict__, "length_ratio": lr, "mesh_frac": x})
        mf, k = _bisect(mk_mf, lambda p: _measure(p)[1],
                        0.01, 0.40, TARGET_K, 0.004)
    p = config.NetworkParams(**{**base.__dict__,
                                "length_ratio": lr, "mesh_frac": mf})
    G, k, D = _measure(p)
    if verbose:
        print(f"  tuned D_target={d_target:.3f} -> length_ratio={lr:.4f} "
              f"mesh_frac={mf:.4f}  N={G.number_of_nodes()} "
              f"<k>={k:.4f} D={D:.4f}", flush=True)
    return G, p, k, D


def make_figure(out):
    """Draw the surface from the result dict, so the figure can be redrawn from
    a stored run (`--replot`) without repeating the Monte Carlo."""
    khs = out["k_h_values"]
    kh0 = out["calibrated_k_h"]
    mults = out["k_h_multiples"]
    Ds = out["D_measured"]
    pc = np.full((len(Ds), len(khs)), np.nan)
    lo = np.full_like(pc, np.nan)
    hi = np.full_like(pc, np.nan)
    for c in out["cells"]:
        i = min(range(len(Ds)), key=lambda k: abs(Ds[k] - c["D"]))
        j = mults.index(c["k_h_multiple_of_calibrated"])
        if c["threshold_exists"]:
            pc[i, j] = c["p_c_haustorial_density"]
            lo[i, j], hi[i, j] = c["ci95"]

    min_mult = out["smallest_k_h_multiple_with_a_threshold"]
    max_no = out["largest_k_h_multiple_with_NO_threshold_in_any_row"]

    fig, ax = plt.subplots(1, 2, figsize=(11.5, 4.4))
    colors = plt.cm.viridis(np.linspace(0.1, 0.85, len(Ds)))
    for i, D in enumerate(Ds):
        m = np.isfinite(pc[i])
        ax[0].plot(np.array(khs)[m] / kh0, pc[i][m], "o-", color=colors[i],
                   label=f"D = {D:.2f}")
        if np.any(m):
            ax[0].fill_between(np.array(khs)[m] / kh0, lo[i][m], hi[i][m],
                               color=colors[i], alpha=0.18, linewidth=0)
    # Shade only the region in which NO row has a threshold: from the left edge
    # to the geometric midpoint between the last all-none column and the first
    # column in which any network collapses.
    edge = ((max_no * min_mult) ** 0.5 if (max_no and min_mult)
            else max(mults))
    ax[0].axvspan(0.75, edge, color="0.85", zorder=0)
    ax[0].text(0.79, 0.5, "no collapse at any haustorial density",
               transform=ax[0].get_xaxis_transform(), fontsize=8,
               va="center", ha="center", color="0.35", rotation=90)
    ax[0].axvline(1.0, color="crimson", ls="--", lw=1.2)
    ax[0].text(1.12, 0.5, "calibrated $K_h$", color="crimson", fontsize=8,
               rotation=90, va="center", ha="center",
               transform=ax[0].get_xaxis_transform())
    ax[0].set_xscale("log")
    ax[0].set_xlim(0.75, max(mults) * 1.4)
    ax[0].set_xlabel("haustorial sink strength ($\\times$ calibrated $K_h$)")
    ax[0].set_ylabel("critical haustorial density")
    ax[0].set_title("A. Threshold vs sink strength", loc="left", fontsize=10)
    ax[0].legend(fontsize=8, frameon=False)

    im = ax[1].imshow(np.ma.masked_invalid(pc), aspect="auto", origin="lower",
                      cmap="magma")
    ax[1].set_xticks(range(len(khs)))
    ax[1].set_xticklabels([f"{m}x" for m in mults], fontsize=8)
    ax[1].set_yticks(range(len(Ds)))
    ax[1].set_yticklabels([f"{d:.2f}" for d in Ds], fontsize=8)
    ax[1].set_xlabel("sink strength ($\\times$ calibrated $K_h$)")
    ax[1].set_ylabel("fractal dimension $D$")
    ax[1].set_title("B. Surface (grey = no threshold exists)", loc="left",
                    fontsize=10)
    for i in range(len(Ds)):
        for j in range(len(khs)):
            if not np.isfinite(pc[i, j]):
                ax[1].add_patch(plt.Rectangle((j - .5, i - .5), 1, 1,
                                              color="0.8"))
    fig.colorbar(im, ax=ax[1], label="critical haustorial density")
    fig.tight_layout()
    fpath = os.path.join(config.PATHS.figures, "sink_surface.png")
    fig.savefig(fpath, dpi=200)
    plt.close(fig)
    print(f"wrote {fpath}")


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    t0 = time.time()
    kh0 = config.K_H_HOLOPARASITE
    khs = [round(kh0 * m, 6) for m in KH_MULTIPLES]
    print("Coupled (K_h, D) surface on the CALIBRATED MESH")
    print(f"  calibrated K_h = {kh0}  ->  columns are {KH_MULTIPLES} x that")
    print(f"  {N_TRIALS} trials/cell over {N_DENSITIES} densities, "
          f"bootstrap CI per cell\n")

    nets = [tuned_network(d) for d in D_TARGETS]
    Ds = [n[3] for n in nets]
    ks = [n[2] for n in nets]

    pp = config.PercolationParams(mode="hydraulic", n_trials=N_TRIALS,
                                  n_densities=N_DENSITIES, seed=SEED)
    pc = np.full((len(nets), len(khs)), np.nan)
    maxP = np.zeros_like(pc)
    lo = np.full_like(pc, np.nan)
    hi = np.full_like(pc, np.nan)
    cells = []
    print()
    for i, (G, params, k, D) in enumerate(nets):
        for j, kh in enumerate(khs):
            t = time.time()
            res = percolation.find_pc(G, pp, k_h=kh, with_ci=True)
            mp = float(np.max(res["p_collapse"]))
            maxP[i, j] = mp
            has = mp >= 0.5 and np.isfinite(res["p_c"])
            if has:
                pc[i, j] = float(res["p_c"])
                ci = res.get("ci", {}).get("ci95", (np.nan, np.nan))
                lo[i, j], hi[i, j] = float(ci[0]), float(ci[1])
            cells.append({
                "D": D, "mean_degree": k, "k_h": kh,
                "k_h_multiple_of_calibrated": KH_MULTIPLES[j],
                "p_c_haustorial_density": (float(pc[i, j]) if has else None),
                "ci95": ([lo[i, j], hi[i, j]] if has else None),
                "max_p_collapse": mp,
                "threshold_exists": bool(has),
            })
            print(f"  D={D:.3f}  K_h={kh:.5f} ({KH_MULTIPLES[j]:>2d}x)  "
                  f"p_c={'%.4f' % pc[i, j] if has else 'none (max P=%.2f)' % mp}"
                  f"   [{time.time() - t:.1f}s]", flush=True)

    # Summarise by COLUMN, because a threshold can appear in one row (the least
    # reticulate network) while the others still never collapse.
    by_mult = {}
    for c in cells:
        by_mult.setdefault(c["k_h_multiple_of_calibrated"], []).append(
            c["threshold_exists"])
    mults = sorted(by_mult)
    min_mult = next((m for m in mults if any(by_mult[m])), None)
    all_mult = next((m for m in mults if all(by_mult[m])), None)
    # largest multiple below which NO row collapses at any density
    max_no = None
    for m in mults:
        if any(by_mult[m]):
            break
        max_no = m

    out = {
        "what_p_c_means": ("critical HAUSTORIAL ATTACHMENT DENSITY under the "
                           "coupled hydraulic model (fraction of nodes bearing a "
                           "haustorium at which P(GCC < 50% of N0) = .50). NOT "
                           "the fraction of nodes removed, and not comparable to "
                           "the topological p_c of the empirical cohort."),
        "generator": ("cohort-calibrated planar mesh "
                      "(calibrate.calibrated_base), N=%d, <k> held at %.4f by "
                      "tuning mesh_frac; D axis realised at constant N by tuning "
                      "length_ratio and then MEASURED"
                      % (nets[0][0].number_of_nodes(), TARGET_K)),
        "N": nets[0][0].number_of_nodes(),
        "calibrated_k_h": kh0,
        "k_h_multiples": list(KH_MULTIPLES),
        "k_h_values": khs,
        "D_measured": Ds,
        "mean_degree_measured": ks,
        "n_trials_per_cell": N_TRIALS,
        "n_densities": N_DENSITIES,
        "seed": SEED,
        "cells": cells,
        "smallest_k_h_multiple_with_a_threshold": min_mult,
        "smallest_k_h_multiple_with_a_threshold_in_every_row": all_mult,
        "largest_k_h_multiple_with_NO_threshold_in_any_row": max_no,
        "threshold_exists_by_multiple": {str(m): {
            "n_rows_with_threshold": int(sum(by_mult[m])),
            "n_rows": len(by_mult[m])} for m in mults},
        "psi_parasite": config.PSI_PARASITE,
        "psi_cavitation": config.PSI_CAVITATION,
        "supersedes": ("sweep.pc_surface() on the legacy knn generator "
                       "(data/results.npz: surface_*), which used <k> 4.4-7.0, "
                       "K_h 0.3-2.5 and 600 trials/cell"),
        "seconds": round(time.time() - t0, 1),
    }
    dpath = os.path.join(config.PATHS.data, "sink_surface.json")
    with open(dpath, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nwrote {dpath}")

    csvdir = os.path.join(config.PATHS.data, "csv")
    os.makedirs(csvdir, exist_ok=True)
    cpath = os.path.join(csvdir, "sink_surface.csv")
    with open(cpath, "w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["D_measured", "mean_degree", "k_h",
                     "k_h_multiple_of_calibrated",
                     "p_c_haustorial_density", "ci95_lo", "ci95_hi",
                     "max_p_collapse", "threshold_exists"])
        for c in cells:
            ci = c["ci95"] or [None, None]
            wr.writerow([f"{c['D']:.4f}", f"{c['mean_degree']:.4f}",
                         f"{c['k_h']:.6f}", c["k_h_multiple_of_calibrated"],
                         "" if c["p_c_haustorial_density"] is None
                         else f"{c['p_c_haustorial_density']:.4f}",
                         "" if ci[0] is None else f"{ci[0]:.4f}",
                         "" if ci[1] is None else f"{ci[1]:.4f}",
                         f"{c['max_p_collapse']:.4f}",
                         int(c["threshold_exists"])])
    print(f"wrote {cpath}")

    make_figure(out)

    print(f"\nHEADLINE: at up to {max_no}x the calibrated K_h no network "
          "collapses at any haustorial density; a threshold first appears in "
          f"some network at {min_mult}x and in every network at {all_mult}x.")
    print(f"total {time.time() - t0:.0f}s")


if __name__ == "__main__":
    if "--replot" in sys.argv:
        with open(os.path.join(config.PATHS.data, "sink_surface.json")) as _f:
            make_figure(json.load(_f))
    else:
        main()
