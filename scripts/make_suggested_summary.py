# -*- coding: utf-8 -*-
r"""
make_suggested_summary.py -- summarise data/cohort_suggested.csv (the all-120
current-vs-suggested-reticulation percolation run) into:
  * data/cohort_suggested_summary.json   headline aggregate stats
  * figures/cohort_suggested.png          current-vs-suggested scatter + delta histogram
  * console tables (paste-ready)

Segments VALID leaf-venation networks from degenerate fragments (tiny N / p_c=0),
so the headline cohort mean is not polluted. Run AFTER run_cohort_suggested.py.
ASCII-only stdout.
"""
import os, sys, csv, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CSV = os.path.join(ROOT, "data", "cohort_suggested.csv")
INK = "#20303A"; ACCENT = "#E4572E"; BLUE = "#2F7FA8"
N_MIN = 1000          # below this a Matos window is a fragment, not a usable network
PC_MIN = 0.02         # p_c==0 => already collapsed => degenerate


def load():
    rows = []
    for r in csv.DictReader(open(CSV, newline="")):
        for k in ("N", "E", "loops_current", "loops_added"):
            r[k] = int(float(r[k]))
        for k in ("k_current", "k_suggested", "D", "pc_current", "pc_suggested",
                  "delta_pc", "seconds"):
            try: r[k] = float(r[k])
            except Exception: r[k] = float("nan")
        r["valid"] = (r["N"] >= N_MIN and r["pc_current"] >= PC_MIN)
        rows.append(r)
    return rows


def stats(vals):
    a = np.array(vals, float); a = a[np.isfinite(a)]
    return {"n": int(a.size), "median": float(np.median(a)), "mean": float(a.mean()),
            "min": float(a.min()), "max": float(a.max())}


def block(rows_subset):
    """Aggregate stats for a subset of valid leaves."""
    if not rows_subset:
        return {"n": 0}
    dpc = [r["delta_pc"] for r in rows_subset]
    return {
        "n": len(rows_subset),
        "pc_current": stats([r["pc_current"] for r in rows_subset]),
        "pc_suggested": stats([r["pc_suggested"] for r in rows_subset]),
        "delta_pc": stats(dpc),
        "frac_improved": sum(1 for d in dpc if d > 0) / len(rows_subset),
        "median_relative_gain_pct": float(np.median(
            [100 * r["delta_pc"] / r["pc_current"] for r in rows_subset if r["pc_current"] > 0])),
    }


def main():
    rows = load()
    valid = [r for r in rows if r["valid"]]
    frag  = [r for r in rows if not r["valid"]]
    # clean-A sensitivity: leaves with NO vein-miscount flag (quality == 'A')
    clean_A = [r for r in valid if (r.get("quality") or "").strip() == "A"]
    dpc = [r["delta_pc"] for r in valid]
    improved = sum(1 for d in dpc if d > 0)

    summary = {
        "n_total": len(rows), "n_valid": len(valid), "n_fragments": len(frag),
        "validity_rule": f"N>={N_MIN} and pc_current>={PC_MIN}",
        "trials_per_network": 10000, "attack": "random (site percolation)",
        "target_mean_degree": 2.811,
        "pc_current": stats([r["pc_current"] for r in valid]),
        "pc_suggested": stats([r["pc_suggested"] for r in valid]),
        "delta_pc": stats(dpc),
        "frac_improved": improved / len(valid) if valid else 0.0,
        "clean_A_sensitivity": block(clean_A),
        "median_relative_gain_pct": float(np.median(
            [100 * r["delta_pc"] / r["pc_current"] for r in valid if r["pc_current"] > 0])),
        "top10_gainers": sorted(
            [{"species": r["species"], "N": r["N"], "k_current": r["k_current"],
              "loops_added": r["loops_added"], "pc_current": r["pc_current"],
              "pc_suggested": r["pc_suggested"], "delta_pc": r["delta_pc"]}
             for r in valid], key=lambda x: -x["delta_pc"])[:10],
        "smallest_gainers": sorted(
            [{"species": r["species"], "k_current": r["k_current"],
              "delta_pc": r["delta_pc"]} for r in valid],
            key=lambda x: x["delta_pc"])[:5],
    }
    out = os.path.join(ROOT, "data", "cohort_suggested_summary.json")
    json.dump(summary, open(out, "w"), indent=2)

    print("=== COHORT CURRENT -> SUGGESTED RETICULATION (random attack, 1e4 trials) ===")
    print("leaves: %d total  |  %d valid networks  |  %d fragments excluded"
          % (summary["n_total"], summary["n_valid"], summary["n_fragments"]))
    s0, s1, sd = summary["pc_current"], summary["pc_suggested"], summary["delta_pc"]
    print("  p_c current    median %.3f  (range %.3f-%.3f)" % (s0["median"], s0["min"], s0["max"]))
    print("  p_c suggested  median %.3f  (range %.3f-%.3f)" % (s1["median"], s1["min"], s1["max"]))
    print("  delta p_c      median %+.3f  mean %+.3f  (max %+.3f)" % (sd["median"], sd["mean"], sd["max"]))
    print("  improved: %d/%d leaves (%.0f%%)   median relative gain %.1f%%"
          % (int(summary["frac_improved"] * summary["n_valid"]), summary["n_valid"],
             100 * summary["frac_improved"], summary["median_relative_gain_pct"]))
    ca = summary["clean_A_sensitivity"]
    if ca.get("n"):
        print("  clean-A only (no vein-miscount, n=%d): delta p_c median %+.3f, %.0f%% improved"
              % (ca["n"], ca["delta_pc"]["median"], 100 * ca["frac_improved"]))
    print("  top gainers:", ", ".join("%s(%+.3f)" % (g["species"], g["delta_pc"])
                                       for g in summary["top10_gainers"][:5]))

    # --- figure: scatter + histogram --------------------------------------
    xc = [r["pc_current"] for r in valid]; xs = [r["pc_suggested"] for r in valid]
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(13, 5.4))
    lim = max(max(xc), max(xs)) * 1.08
    ax.plot([0, lim], [0, lim], color="0.6", lw=1, ls="--")
    ax.scatter(xc, xs, s=26, color=BLUE, edgecolor=INK, linewidth=0.3, alpha=0.85)
    ax.set_xlim(0, lim); ax.set_ylim(0, lim); ax.set_aspect("equal")
    ax.set_xlabel("p_c  (current real leaf)", color=INK)
    ax.set_ylabel("p_c  (suggested: + areole loops)", color=INK)
    ax.set_title("Every valid leaf moves ABOVE the diagonal\n(more reticulate = more collapse-resistant)",
                 fontsize=11, color=INK)
    ax2.hist(dpc, bins=18, color=ACCENT, edgecolor=INK, linewidth=0.4)
    ax2.axvline(np.median(dpc), color=INK, lw=1.6, ls="--",
                label="median %+.3f" % np.median(dpc))
    ax2.set_xlabel(r"$\Delta p_c$  (suggested - current)", color=INK)
    ax2.set_ylabel("leaves", color=INK)
    ax2.set_title("Distribution of the robustness gain\n(n=%d valid whole-leaves, random attack)"
                  % summary["n_valid"], fontsize=11, color=INK)
    ax2.legend()
    fig.suptitle("Real Matos leaves: adding reticulation to each leaf's OWN venation raises "
                 "its percolation threshold", fontsize=12.5, color=INK, y=1.02)
    fig.tight_layout()
    figpath = os.path.join(ROOT, "figures", "cohort_suggested.png")
    fig.savefig(figpath, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("\nsaved:", os.path.relpath(out, ROOT), "+", os.path.relpath(figpath, ROOT))


if __name__ == "__main__":
    main()
