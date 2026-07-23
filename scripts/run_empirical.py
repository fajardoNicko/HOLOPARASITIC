r"""
run_empirical.py — the EMPIRICAL VALIDATION phase.

Tests the model against real leaves. It has two jobs, and it degrades gracefully
if you have not collected any data yet (it will just tell you what to put where).

  A. MEASURE D from real leaf images, using the *identical* windowed box-counting
     core (holoparasitic.fractal.box_counting_from_points) that measured the
     synthetic networks. Same code path => like-for-like comparison.

  B. RUN THE FOUR STATISTICAL TESTS from the methodology, against the model
     results already sitting in data/results.npz:

       1. one-sample t-test  D_real vs D_model, per species
                              -> is synthetic architecture a defensible stand-in?
       2. one-way ANOVA of D across species
                              -> does the venation-density gradient actually exist?
       3. Murray's-law exponent from vessel radii; H0: exponent = 3
                              -> is the one assumption the model inherits true?
       4. Pearson r: D_measured x p_c_predicted
                              -> the central prediction (denser hosts resist longer)

USAGE
  # 1) box-count every image under empirical/venation_topdown/<species>/... and
  #    write the measured D into empirical/measurements/venation_metrics.csv:
  ...python.exe scripts\run_empirical.py --measure

  # or point it at any folder (e.g. the downloaded Matos venation_form/images):
  ...python.exe scripts\run_empirical.py --measure --images-dir path\to\images

  # 2) just run the tests on whatever is already in the CSVs:
  ...python.exe scripts\run_empirical.py

INPUT LAYOUT (species is the immediate sub-folder name)
  empirical/venation_topdown/<species>/<anything>.png|jpg|tif   -> D per leaf
  empirical/measurements/venation_metrics.csv                   -> box_counting_D column
  empirical/measurements/vessel_radii.csv                       -> parent/daughter radii

Real leaf venation is white-on-black in most segmentations; raw cleared leaves are
dark-veins-on-light. The measurer auto-picks the MINORITY pixel class as "vein"
(veins are thin) and logs the pixel split so you can sanity-check; override with
--invert if a particular image set is the other polarity.
"""

import os
import sys
import csv
import json
import glob
import argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

import config
from holoparasitic import fractal

IMG_EXTS = (".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp")
MAX_VEIN_POINTS = 400_000        # parity with fractal._edge_point_cloud cap
MODEL_D_DEFAULT = 1.4344         # summary["D"]; overridable with --d-model
MURRAY_NULL = 3.0


# ----------------------------------------------------------------------------
# Image -> vein-pixel point cloud -> D  (shared box-counting core)
# ----------------------------------------------------------------------------
def _imread_gray(path):
    """Load an image as a 2-D float array in [0, 1]. Tries matplotlib first
    (native PNG), falls back to Pillow for JPG/TIF. Returns None on failure."""
    arr = None
    try:
        arr = matplotlib.image.imread(path)
    except Exception:
        try:
            from PIL import Image
            arr = np.asarray(Image.open(path))
        except Exception as e:
            print(f"    ! cannot read {os.path.basename(path)}: {e}", flush=True)
            return None
    arr = np.asarray(arr, float)
    if arr.ndim == 3:                      # RGB(A) -> luminance
        arr = arr[..., :3] @ np.array([0.2126, 0.7152, 0.0722])
    if arr.max() > 1.0:                    # 0..255 -> 0..1
        arr = arr / 255.0
    return arr


def _otsu(gray):
    """Otsu threshold on a [0,1] image (256-bin histogram), in pure numpy."""
    hist, edges = np.histogram(gray.ravel(), bins=256, range=(0.0, 1.0))
    hist = hist.astype(float)
    w = np.cumsum(hist)
    total = w[-1]
    if total == 0:
        return 0.5
    centers = (edges[:-1] + edges[1:]) / 2.0
    cummean = np.cumsum(hist * centers)
    gmean = cummean[-1] / total
    wb = w
    wf = total - w
    valid = (wb > 0) & (wf > 0)
    mb = np.divide(cummean, wb, out=np.zeros_like(cummean), where=wb > 0)
    mf = np.divide(gmean * total - cummean, wf,
                   out=np.zeros_like(cummean), where=wf > 0)
    between = wb * wf * (mb - mf) ** 2
    between[~valid] = -1.0
    return float(centers[int(np.argmax(between))])


def vein_points(gray, invert=None):
    """Coordinates of vein pixels. Threshold via Otsu; take the MINORITY class
    as vein (veins are thin) unless `invert` forces a polarity.
    Returns (pts Nx2, frac_vein). pts is empty if nothing plausible found."""
    t = _otsu(gray)
    dark = gray < t                        # pixels below threshold
    n_dark = int(dark.sum())
    n_light = dark.size - n_dark
    if invert is None:
        vein = dark if n_dark <= n_light else ~dark   # minority = vein
    else:
        vein = (~dark) if invert else dark
    ys, xs = np.nonzero(vein)
    pts = np.column_stack([xs, ys]).astype(float)
    if len(pts) > MAX_VEIN_POINTS:         # subsample for speed / density parity
        idx = np.linspace(0, len(pts) - 1, MAX_VEIN_POINTS).astype(int)
        pts = pts[idx]
    return pts, (len(pts) / gray.size if gray.size else 0.0)


def measure_image_D(path, invert=None, verbose=True):
    """Box-counting D of one leaf image via the SHARED fractal core."""
    gray = _imread_gray(path)
    if gray is None:
        return None
    pts, frac = vein_points(gray, invert=invert)
    if len(pts) < 50:
        if verbose:
            print(f"    ! {os.path.basename(path)}: only {len(pts)} vein px "
                  f"({frac:.1%}) — skipped (check polarity / --invert)",
                  flush=True)
        return None
    D = fractal.box_counting_from_points(pts)["D"]
    if verbose:
        print(f"    {os.path.basename(path):40s} D={D:.3f}  "
              f"vein={frac:5.1%}  px={len(pts)}", flush=True)
    return D


# ----------------------------------------------------------------------------
# CSV read / write
# ----------------------------------------------------------------------------
def _is_example(row):
    return "example row" in (row.get("notes", "") or "").lower()


def read_metrics(path):
    """Return list of {species, box_counting_D(float), sample_id, ...} for rows
    that carry a numeric D (ignores empty template / example rows)."""
    if not os.path.exists(path):
        return []
    out = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            if _is_example(row):
                continue
            v = (row.get("box_counting_D") or "").strip()
            if not v:
                continue
            try:
                row["box_counting_D"] = float(v)
            except ValueError:
                continue
            out.append(row)
    return out


def read_radii(path):
    """Return list of (parent, d1, d2) radius triples with all three numeric."""
    if not os.path.exists(path):
        return []
    out = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            if _is_example(row):
                continue
            try:
                p = float(row["parent_radius_um"])
                a = float(row["daughter1_radius_um"])
                b = float(row["daughter2_radius_um"])
            except (KeyError, ValueError, TypeError):
                continue
            if p > 0 and a > 0 and b > 0:
                out.append((p, a, b))
    return out


METRIC_HEADER = ["sample_id", "species", "plant_id", "leaf_id", "box_counting_D",
                 "vein_density_mm_per_mm2", "leaf_area_mm2", "image_file",
                 "measured_by", "notes"]


def measure_dir(images_dir, metrics_path, invert=None):
    """Box-count every image under images_dir/<species>/... and MERGE the results
    into venation_metrics.csv (keyed by sample_id; existing non-example rows kept
    unless re-measured). Returns the number of images measured."""
    paths = [p for p in glob.glob(os.path.join(images_dir, "**", "*"),
                                  recursive=True)
             if p.lower().endswith(IMG_EXTS)]
    if not paths:
        print(f"    (no images under {images_dir})", flush=True)
        return 0

    # preserve existing non-example rows, indexed by sample_id
    existing = {}
    if os.path.exists(metrics_path):
        with open(metrics_path, newline="") as f:
            for row in csv.DictReader(f):
                if not _is_example(row) and (row.get("sample_id") or "").strip():
                    existing[row["sample_id"]] = row

    print(f"[measure] {len(paths)} images under {images_dir}", flush=True)
    n = 0
    for p in sorted(paths):
        species = os.path.basename(os.path.dirname(p)) or "unknown"
        stem = os.path.splitext(os.path.basename(p))[0]
        sample_id = stem
        D = measure_image_D(p, invert=invert)
        if D is None:
            continue
        rel = os.path.relpath(p, ROOT).replace("\\", "/")
        row = existing.get(sample_id, {k: "" for k in METRIC_HEADER})
        row.update(sample_id=sample_id, species=species,
                   box_counting_D=f"{D:.4f}", image_file=rel,
                   measured_by="run_empirical.py (box-counting)")
        existing[sample_id] = row
        n += 1

    os.makedirs(os.path.dirname(metrics_path), exist_ok=True)
    with open(metrics_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=METRIC_HEADER, extrasaction="ignore")
        w.writeheader()
        for row in existing.values():
            w.writerow({k: row.get(k, "") for k in METRIC_HEADER})
    print(f"[measure] wrote {n} measured rows -> "
          f"{os.path.relpath(metrics_path, ROOT)}", flush=True)
    return n


# ----------------------------------------------------------------------------
# Model reference (data/results.npz)
# ----------------------------------------------------------------------------
def load_model_curve():
    """Return (D_grid, pc_grid) for the p_c-vs-D curve, or (None, None)."""
    for f in ("results.npz", "results_preview.npz"):
        path = os.path.join(config.PATHS.data, f)
        if os.path.exists(path):
            z = np.load(path, allow_pickle=True)
            if "pcd_D" in z.files and "pcd_pc" in z.files:
                D = np.asarray(z["pcd_D"], float)
                pc = np.asarray(z["pcd_pc"], float)
                order = np.argsort(D)
                return D[order], pc[order]
    return None, None


def predict_pc(D_values, D_grid, pc_grid):
    """Interpolate measured D onto the model's p_c-vs-D curve. Flags any value
    outside the grid (extrapolation via np.interp clamps to the endpoints)."""
    D_values = np.asarray(D_values, float)
    pc = np.interp(D_values, D_grid, pc_grid)
    n_out = int(np.sum((D_values < D_grid[0]) | (D_values > D_grid[-1])))
    return pc, n_out


# ----------------------------------------------------------------------------
# Murray exponent: solve  r_p^n = r_d1^n + r_d2^n  per branch
# ----------------------------------------------------------------------------
def murray_exponent(p, a, b):
    """Exponent n for one bifurcation, or nan if no root in [0.3, 8]."""
    from scipy.optimize import brentq
    f = lambda n: a ** n + b ** n - p ** n
    lo, hi = 0.3, 8.0
    flo, fhi = f(lo), f(hi)
    if flo == 0:
        return lo
    if flo * fhi > 0:
        return float("nan")          # daughters not consistent with a single n
    try:
        return float(brentq(f, lo, hi, maxiter=200))
    except Exception:
        return float("nan")


# ----------------------------------------------------------------------------
# The four tests
# ----------------------------------------------------------------------------
def by_species(rows):
    g = {}
    for r in rows:
        g.setdefault(r["species"], []).append(r["box_counting_D"])
    return {s: np.asarray(v, float) for s, v in g.items()}


def run_tests(metrics_rows, radii, D_grid, pc_grid, d_model, figdir):
    report = {"d_model": d_model}
    groups = by_species(metrics_rows)

    print("=" * 66, flush=True)
    print("EMPIRICAL VALIDATION — statistical report", flush=True)
    print("=" * 66, flush=True)
    print(f"species measured : {len(groups)}", flush=True)
    print(f"leaves measured  : {len(metrics_rows)}", flush=True)
    print(f"model D          : {d_model:.4f}", flush=True)
    if D_grid is not None:
        print(f"model p_c-vs-D   : D {D_grid[0]:.3f}..{D_grid[-1]:.3f}  "
              f"-> p_c {pc_grid.min():.3f}..{pc_grid.max():.3f}", flush=True)
    print("-" * 66, flush=True)

    # ---- Test 1: one-sample t-test D_real vs D_model, per species ----------
    print("[1] one-sample t-test  D_real vs D_model (per species)", flush=True)
    t1 = {}
    for s, vals in sorted(groups.items()):
        if len(vals) < 2:
            print(f"    {s:24s} n={len(vals)}  (need >=2 for a t-test)",
                  flush=True)
            continue
        tstat, pval = stats.ttest_1samp(vals, d_model)
        t1[s] = {"n": len(vals), "mean_D": float(vals.mean()),
                 "sd": float(vals.std(ddof=1)), "t": float(tstat),
                 "p": float(pval)}
        verdict = "differs from model" if pval < 0.05 else "consistent w/ model"
        print(f"    {s:24s} n={len(vals):2d}  D={vals.mean():.3f}"
              f"±{vals.std(ddof=1):.3f}  t={tstat:+.2f}  p={pval:.3f}  "
              f"-> {verdict}", flush=True)
    report["test1_ttest_vs_model"] = t1

    # ---- Test 2: one-way ANOVA of D across species -------------------------
    print("[2] one-way ANOVA of D across species", flush=True)
    anova_groups = [v for v in groups.values() if len(v) >= 2]
    if len(anova_groups) >= 2:
        F, p = stats.f_oneway(*anova_groups)
        report["test2_anova"] = {"F": float(F), "p": float(p),
                                 "n_species": len(anova_groups)}
        verdict = ("gradient EXISTS (species differ)" if p < 0.05
                   else "no significant difference across species")
        print(f"    F={F:.2f}  p={p:.4f}  ({len(anova_groups)} species)  "
              f"-> {verdict}", flush=True)
    else:
        report["test2_anova"] = None
        print("    (need >=2 species with >=2 leaves each)", flush=True)

    # ---- Test 3: Murray exponent, H0: n = 3 --------------------------------
    print("[3] Murray's-law exponent  (H0: exponent = 3)", flush=True)
    if radii:
        ns = np.array([murray_exponent(*t) for t in radii], float)
        ns = ns[np.isfinite(ns)]
        if len(ns) >= 2:
            tstat, pval = stats.ttest_1samp(ns, MURRAY_NULL)
            ci = stats.t.interval(0.95, len(ns) - 1, loc=ns.mean(),
                                  scale=stats.sem(ns))
            report["test3_murray"] = {"n_branches": len(ns),
                                      "mean_exponent": float(ns.mean()),
                                      "ci95": [float(ci[0]), float(ci[1])],
                                      "t": float(tstat), "p": float(pval)}
            verdict = ("differs from 3" if pval < 0.05
                       else "consistent with 3")
            print(f"    n={len(ns)} branches  exponent={ns.mean():.2f} "
                  f"95%CI=[{ci[0]:.2f}, {ci[1]:.2f}]  t={tstat:+.2f}  "
                  f"p={pval:.3f}  -> {verdict}", flush=True)
        else:
            report["test3_murray"] = None
            print(f"    only {len(ns)} solvable branches (need >=2)", flush=True)
    else:
        report["test3_murray"] = None
        print("    (no vessel_radii.csv data yet)", flush=True)

    # ---- Test 4: Pearson r  D_measured x p_c_predicted ---------------------
    print("[4] Pearson r  D_measured x p_c_predicted  (central prediction)",
          flush=True)
    if D_grid is None:
        report["test4_pearson"] = None
        print("    (no data/results.npz p_c-vs-D curve — run run_full.py first)",
              flush=True)
    elif len(groups) < 3:
        report["test4_pearson"] = None
        print(f"    only {len(groups)} species (need >=3 for a correlation)",
              flush=True)
    else:
        sp = sorted(groups)
        mD = np.array([groups[s].mean() for s in sp])
        pc, n_out = predict_pc(mD, D_grid, pc_grid)
        r, p = stats.pearsonr(mD, pc)
        report["test4_pearson"] = {"r": float(r), "p": float(p),
                                   "n_species": len(sp),
                                   "D_range": [float(mD.min()), float(mD.max())],
                                   "pc_range": [float(pc.min()), float(pc.max())],
                                   "n_extrapolated": n_out}
        print(f"    r={r:+.3f}  p={p:.4f}  ({len(sp)} species)", flush=True)
        print(f"    real D {mD.min():.3f}..{mD.max():.3f}  ->  "
              f"predicted p_c {pc.min():.3f}..{pc.max():.3f}"
              f"  ({100*(pc.max()-pc.min()):.1f} pp spread in vulnerability)",
              flush=True)
        if n_out:
            print(f"    ! {n_out} species outside the model D grid "
                  f"(p_c clamped to curve ends)", flush=True)
        # HONEST CAVEAT — do not oversell this test.
        print("    NOTE: p_c_predicted is read from the model's OWN p_c(D) curve,"
              " so this r\n"
              "          is largely fixed by that monotonic mapping — it is a"
              " CONSISTENCY check\n"
              "          (real D falls where the model can act on it), NOT an"
              " independent test\n"
              "          of p_c. Measuring real p_c would require destroying"
              " live plants, which is\n"
              "          the impossibility that justifies the simulation in the"
              " first place.", flush=True)
        _plot_D_vs_pc(sp, mD, pc, D_grid, pc_grid, figdir)

    print("-" * 66, flush=True)
    return report


def _plot_D_vs_pc(species, mD, pc, D_grid, pc_grid, figdir):
    os.makedirs(figdir, exist_ok=True)
    fig, ax = plt.subplots(figsize=(6.2, 4.4))
    ax.plot(D_grid, pc_grid, "-", color="0.6", lw=2, label="model p_c(D)")
    ax.scatter(mD, pc, s=42, color="#0f766e", zorder=3, label="species (measured D)")
    for s, x, y in zip(species, mD, pc):
        ax.annotate(s, (x, y), fontsize=7, xytext=(4, 3),
                    textcoords="offset points")
    ax.set_xlabel("measured fractal dimension  D")
    ax.set_ylabel("predicted percolation threshold  $p_c$")
    ax.set_title("Empirical D mapped onto the model's vulnerability curve")
    ax.legend(fontsize=8)
    fig.tight_layout()
    out = os.path.join(figdir, "empirical_D_vs_pc.png")
    fig.savefig(out, dpi=160)
    plt.close(fig)
    print(f"    figure -> {os.path.relpath(out, ROOT)}", flush=True)


# ----------------------------------------------------------------------------
def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass

    ap = argparse.ArgumentParser(description="Empirical validation phase.")
    ap.add_argument("--measure", action="store_true",
                    help="box-count images and write D into venation_metrics.csv")
    ap.add_argument("--images-dir", default=os.path.join("empirical",
                    "venation_topdown"),
                    help="root of <species>/<image> folders to measure")
    ap.add_argument("--invert", dest="invert", action="store_true",
                    default=None, help="force vein = brighter pixels")
    ap.add_argument("--no-invert", dest="invert", action="store_false",
                    help="force vein = darker pixels")
    ap.add_argument("--d-model", type=float, default=None,
                    help=f"model mean D (default: summary.json or {MODEL_D_DEFAULT})")
    args = ap.parse_args()

    emp = os.path.join(ROOT, "empirical")
    metrics_path = os.path.join(emp, "measurements", "venation_metrics.csv")
    radii_path = os.path.join(emp, "measurements", "vessel_radii.csv")
    figdir = os.path.join(ROOT, config.PATHS.figures)

    if args.measure:
        measure_dir(os.path.join(ROOT, args.images_dir) if not
                    os.path.isabs(args.images_dir) else args.images_dir,
                    metrics_path, invert=args.invert)

    metrics_rows = read_metrics(metrics_path)
    radii = read_radii(radii_path)
    D_grid, pc_grid = load_model_curve()

    # model D: CLI > summary.json > constant
    d_model = args.d_model
    if d_model is None:
        sp = os.path.join(ROOT, config.PATHS.data, "summary.json")
        if os.path.exists(sp):
            try:
                d_model = float(json.load(open(sp)).get("D", MODEL_D_DEFAULT))
            except Exception:
                d_model = MODEL_D_DEFAULT
        else:
            d_model = MODEL_D_DEFAULT

    if not metrics_rows and not radii:
        print("=" * 66)
        print("EMPIRICAL VALIDATION — no data yet")
        print("=" * 66)
        print("Nothing measured. To proceed, either:")
        print("  * drop leaf images into empirical/venation_topdown/<species>/")
        print("    and run:  python scripts/run_empirical.py --measure")
        print("  * or point at a downloaded set:")
        print("    python scripts/run_empirical.py --measure --images-dir DIR")
        print("  * or fill box_counting_D / vessel radii into the CSVs under")
        print("    empirical/measurements/ and run without --measure.")
        print()
        print(f"model p_c-vs-D curve present: "
              f"{'yes' if D_grid is not None else 'no (run run_full.py first)'}")
        return

    report = run_tests(metrics_rows, radii, D_grid, pc_grid, d_model, figdir)

    out = os.path.join(emp, "measurements", "empirical_summary.json")
    with open(out, "w") as f:
        json.dump(report, f, indent=2)
    print(f"summary -> {os.path.relpath(out, ROOT)}", flush=True)
    print("done.", flush=True)


if __name__ == "__main__":
    main()
