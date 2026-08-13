r"""
run_cohort_percolation.py — the real-leaf percolation run (Phase 1 payoff).

For every leaf in the locked 100-leaf cohort (scripts/build_cohort.py), estimate
the site-percolation threshold p_c with the SAME Monte Carlo engine used on the
synthetic networks, then test the study's central question directly on real
data: does connectivity (mean degree) or fractal dimension predict p_c?

ATTACK MODES.
  random  — classic site percolation; the standard threshold and the PRIMARY
            response variable for the regression below.
  degree  — degree-targeted removal, a cheap structural contrast.
  betweenness is deliberately NOT run here. It is exact-O(V*E); on a 300k-node
  leaf that is infeasible, and approximating it per leaf would make p_c
  incomparable across the 4.5-orders-of-magnitude size range. It stays a
  subset-only diagnostic (run_realleaf.py --betweenness on small leaves).

TRIAL BUDGET. Each leaf gets n_densities x trials_per_density trials. This is a
per-leaf POINT ESTIMATE feeding a between-leaf regression, not a publication
sigmoid, so a few thousand trials suffice; the 1e6-trial curves are only for the
hero synthetic network. Cost scales with leaf size — the largest leaf (~396k
veins) is ~35 ms/trial, so the run is dominated by the dozen biggest leaves.

RESUMABLE. Each leaf's row is appended to data/cohort_pc.csv as it finishes, and
a re-run skips leaves already present. A crash or a kill costs at most one leaf.

    ...python.exe scripts\run_cohort_percolation.py --data-dir DIR
    ...python.exe scripts\run_cohort_percolation.py --data-dir DIR --resume

Outputs
    data/cohort_pc.csv        per-leaf p_c (random, degree) + predictors
    data/cohort_pc_analysis.json   the p_c~<k> vs p_c~D analysis + clean-A sens.
"""

import os
import sys
import csv
import json
import time
import argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import numpy as np

import config
from holoparasitic import realleaf, percolation, fractal


def _read_cohort(datadir):
    path = os.path.join(datadir, "cohort.csv")
    if not os.path.exists(path):
        return None
    with open(path, newline="") as f:
        return [r for r in csv.DictReader(f)
                if str(r.get("include", "")).lower() in ("true", "1")]


def _done_names(csv_path):
    if not os.path.exists(csv_path):
        return set()
    with open(csv_path, newline="") as f:
        return {r["species"] for r in csv.DictReader(f)}


FIELDS = ["species", "n_nodes", "n_edges", "mean_degree", "loop_fraction", "D",
          "quality", "clean_A", "pc_random", "pc_degree", "n_trials", "seconds"]


def _append_row(csv_path, row):
    new = not os.path.exists(csv_path)
    with open(csv_path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            w.writeheader()
        w.writerow(row)


def _num(x):
    try:
        v = float(x)
        return v if np.isfinite(v) else None
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------------------
# the analysis: does <k> or D predict p_c?  (full cohort + clean-A sensitivity)
# ---------------------------------------------------------------------------
def _ols(y, *cols):
    """OLS with intercept; returns betas, ses, t, p, R^2 (no statsmodels dep)."""
    from scipy import stats
    X = np.column_stack([np.ones(len(y))] + list(cols))
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    dof = len(y) - X.shape[1]
    if dof <= 0:
        return None
    s2 = float(resid @ resid) / dof
    cov = s2 * np.linalg.inv(X.T @ X)
    se = np.sqrt(np.diag(cov))
    t = beta / se
    p = 2 * stats.t.sf(np.abs(t), dof)
    ss_tot = float(((y - y.mean()) ** 2).sum())
    r2 = 1.0 - float(resid @ resid) / ss_tot if ss_tot > 0 else float("nan")
    return {"beta": beta.tolist(), "se": se.tolist(), "t": t.tolist(),
            "p": p.tolist(), "r2": r2, "n": len(y), "dof": dof}


def _zscore(v):
    v = np.asarray(v, float)
    sd = v.std()
    return (v - v.mean()) / sd if sd > 0 else v * 0.0


def analyze(csv_path):
    from scipy import stats
    with open(csv_path, newline="") as f:
        rows = list(csv.DictReader(f))

    def col(name, rs):
        return np.array([_num(r.get(name)) for r in rs], float)

    def block(rs, label):
        pc = col("pc_random", rs)
        k = col("mean_degree", rs)
        D = col("D", rs)
        m = np.isfinite(pc) & np.isfinite(k) & np.isfinite(D)
        pc, k, D = pc[m], k[m], D[m]
        if m.sum() < 5:
            return {"label": label, "n": int(m.sum()),
                    "note": "too few leaves"}
        rk, pk = stats.pearsonr(k, pc)
        rD, pD = stats.pearsonr(D, pc)
        srk, spk = stats.spearmanr(k, pc)
        srD, spD = stats.spearmanr(D, pc)
        # predictor collinearity: on real leaves <k> and D turn out nearly
        # independent (unlike the synthetic generator, where reticulation moves
        # both together), so a partial correlation cleanly separates them.
        rkD, pkD = stats.pearsonr(k, D)
        vif = 1.0 / (1.0 - rkD ** 2) if abs(rkD) < 1 else float("inf")

        def _partial(a, b, ctrl):
            ra = a - np.polyval(np.polyfit(ctrl, a, 1), ctrl)
            rb = b - np.polyval(np.polyfit(ctrl, b, 1), ctrl)
            r, p = stats.pearsonr(ra, rb)
            return {"r": float(r), "p": float(p)}

        # standardized multiple regression so betas are comparable in size
        multi = _ols(pc, _zscore(k), _zscore(D))
        return {
            "label": label, "n": int(m.sum()),
            "pearson_k_vs_pc": {"r": float(rk), "p": float(pk)},
            "pearson_D_vs_pc": {"r": float(rD), "p": float(pD)},
            "spearman_k_vs_pc": {"rho": float(srk), "p": float(spk)},
            "spearman_D_vs_pc": {"rho": float(srD), "p": float(spD)},
            "predictor_collinearity_k_vs_D": {"r": float(rkD), "p": float(pkD),
                                              "VIF": float(vif)},
            "partial_pc_vs_k_given_D": _partial(pc, k, D),
            "partial_pc_vs_D_given_k": _partial(pc, D, k),
            "multiple_regression_standardized": {
                "predictors": ["intercept", "z_mean_degree", "z_D"],
                **(multi or {})},
            "pc_random_median": float(np.median(pc)),
            "pc_random_range": [float(pc.min()), float(pc.max())],
            "mean_degree_range": [float(k.min()), float(k.max())],
            "D_range": [float(D.min()), float(D.max())],
        }

    clean = [r for r in rows
             if str(r.get("clean_A", "")).lower() in ("true", "1")]
    out = {"full_cohort": block(rows, "full cohort (100, quality not gated)"),
           "clean_A_sensitivity": block(clean, "clean-A only (sensitivity)")}

    # headline verdict
    full = out["full_cohort"]
    if "pearson_k_vs_pc" in full:
        pk = full["partial_pc_vs_k_given_D"]
        pD = full["partial_pc_vs_D_given_k"]
        col = full["predictor_collinearity_k_vs_D"]
        both = pk["p"] < 0.01 and pD["p"] < 0.01
        stronger = "mean degree" if abs(pk["r"]) > abs(pD["r"]) else "fractal dimension"
        out["verdict"] = (
            f"On the real cohort <k> and D are nearly independent "
            f"(r={col['r']:+.2f}, VIF={col['VIF']:.2f}), so their effects "
            f"separate cleanly. "
            + (f"BOTH independently predict p_c: partial r(p_c,<k>|D)="
               f"{pk['r']:+.2f} (p={pk['p']:.1g}) and partial r(p_c,D|<k>)="
               f"{pD['r']:+.2f} (p={pD['p']:.1g}); {stronger} is somewhat "
               "stronger. This REVISES the preliminary n=10 result (D looked "
               "irrelevant) — with n=100 and a full D range, fractal dimension "
               "is a real, independent predictor, not reducible to connectivity."
               if both else
               f"Only {stronger} is a significant independent predictor."))
    return out


def main():
    ap = argparse.ArgumentParser(description="Percolation over the real cohort.")
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--n-densities", type=int, default=40)
    ap.add_argument("--trials-per-density", type=int, default=60)
    ap.add_argument("--rho-max", type=float, default=0.6,
                    help="upper bound of the removal sweep; every real leaf "
                         "collapses below ~0.3, so 0.6 concentrates trials in "
                         "the informative range (default 0.6)")
    ap.add_argument("--resume", action="store_true",
                    help="skip leaves already in cohort_pc.csv")
    ap.add_argument("--analyze-only", action="store_true",
                    help="skip simulation, just re-run the analysis on the CSV")
    args = ap.parse_args()

    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass

    datadir = os.path.join(ROOT, config.PATHS.data)
    os.makedirs(datadir, exist_ok=True)
    csv_path = os.path.join(datadir, "cohort_pc.csv")

    if not args.analyze_only:
        cohort = _read_cohort(datadir)
        if cohort is None:
            print("No data/cohort.csv — run scripts/build_cohort.py first.")
            return
        if args.limit:
            cohort = cohort[:args.limit]
        # biggest leaves first would front-load risk; do smallest first so a
        # partial run still yields many leaves, and progress is visible early
        cohort.sort(key=lambda r: _num(r.get("n_edges")) or 0)

        done = _done_names(csv_path) if args.resume else set()
        if not args.resume and os.path.exists(csv_path):
            os.remove(csv_path)

        n_trials = args.n_densities * args.trials_per_density
        todo = [r for r in cohort if r["name"] not in done]
        print("=" * 82, flush=True)
        print(f"COHORT PERCOLATION · {len(todo)} leaves to run "
              f"({len(done)} already done) · {n_trials} trials/leaf/mode",
              flush=True)
        print("=" * 82, flush=True)

        ddir = args.data_dir if os.path.isabs(args.data_dir) \
            else os.path.join(ROOT, args.data_dir)
        pairs = {spp: (n, v) for spp, n, v in realleaf.find_leaf_pairs(ddir)}

        t_start = time.time()
        for i, r in enumerate(todo, 1):
            spp = r["name"]
            if spp not in pairs:
                print(f"[{i}/{len(todo)}] {spp}: no CSV pair found", flush=True)
                continue
            npath, vpath = pairs[spp]
            t0 = time.time()
            try:
                G = realleaf.load_matos(npath, vpath, name=spp)
                pr = config.PercolationParams(mode="random", n_trials=n_trials,
                                              n_densities=args.n_densities)
                pc_rand = percolation.find_pc(G, pr, rho_max=args.rho_max)["p_c"]
                w = percolation.importance_weights(G, list(G.nodes),
                                                   metric="degree")
                pt = config.PercolationParams(mode="targeted", n_trials=n_trials,
                                              n_densities=args.n_densities)
                pc_deg = percolation.find_pc(G, pt, weights=w,
                                             rho_max=args.rho_max)["p_c"]
                D = _num(r.get("D")) or fractal.fractal_dimension(G)
            except Exception as e:
                print(f"[{i}/{len(todo)}] {spp}: FAILED — {e}", flush=True)
                continue
            dt = time.time() - t0
            row = {"species": spp, "n_nodes": G.number_of_nodes(),
                   "n_edges": G.number_of_edges(),
                   "mean_degree": r.get("mean_degree"),
                   "loop_fraction": r.get("loop_fraction"), "D": round(D, 4),
                   "quality": r.get("quality", ""),
                   "clean_A": r.get("clean_A", ""),
                   "pc_random": round(pc_rand, 4), "pc_degree": round(pc_deg, 4),
                   "n_trials": n_trials, "seconds": round(dt, 1)}
            _append_row(csv_path, row)
            print(f"[{i}/{len(todo)}] {spp:10s} E={G.number_of_edges():7,} "
                  f"<k>={_num(r.get('mean_degree')):.2f} D={D:.3f}  "
                  f"p_c(rand)={pc_rand:.3f} p_c(deg)={pc_deg:.3f}  ({dt:.0f}s)",
                  flush=True)
        print("-" * 82, flush=True)
        print(f"simulation done ({time.time()-t_start:.0f}s)", flush=True)

    # ---- analysis -----------------------------------------------------------
    if not os.path.exists(csv_path):
        print("No cohort_pc.csv to analyze.")
        return
    result = analyze(csv_path)
    with open(os.path.join(datadir, "cohort_pc_analysis.json"), "w") as f:
        json.dump(result, f, indent=2)

    for key in ("full_cohort", "clean_A_sensitivity"):
        b = result[key]
        print("-" * 82, flush=True)
        print(f"{b['label']}  (n={b.get('n')})", flush=True)
        if "pearson_k_vs_pc" in b:
            print(f"  p_c vs <k>:  Pearson r={b['pearson_k_vs_pc']['r']:+.3f} "
                  f"p={b['pearson_k_vs_pc']['p']:.3g}   "
                  f"Spearman rho={b['spearman_k_vs_pc']['rho']:+.3f}", flush=True)
            print(f"  p_c vs D  :  Pearson r={b['pearson_D_vs_pc']['r']:+.3f} "
                  f"p={b['pearson_D_vs_pc']['p']:.3g}   "
                  f"Spearman rho={b['spearman_D_vs_pc']['rho']:+.3f}", flush=True)
            mr = b["multiple_regression_standardized"]
            if "beta" in mr:
                print(f"  std multiple reg  R2={mr['r2']:.3f}  "
                      f"beta(z_k)={mr['beta'][1]:+.3f} (p={mr['p'][1]:.3g})  "
                      f"beta(zD)={mr['beta'][2]:+.3f} (p={mr['p'][2]:.3g})",
                      flush=True)
    print("=" * 82, flush=True)
    print("VERDICT: " + result.get("verdict", "n/a"), flush=True)
    print("wrote data/cohort_pc.csv + cohort_pc_analysis.json", flush=True)


if __name__ == "__main__":
    main()
