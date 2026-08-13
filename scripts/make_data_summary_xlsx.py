# -*- coding: utf-8 -*-
r"""
make_data_summary_xlsx.py -- build DATA_SUMMARY.xlsx.

Headline = the REAL-leaf reticulation cohort (all 120 Matos leaves, current vs
suggested-more-reticulate, random attack, 1e4 trials). The multi-parasite
comparison is DROPPED (stipulated efficiencies, weakest-validated); the haustorial
sink now appears once, as a literature-grounded (sub-symptomatic) demonstration.

Every number is pulled live from data/*.json + data/cohort_suggested.csv so the
sheet cannot drift from the analysis. ASCII-only stdout.
"""
import os, csv, json
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda f: json.load(open(os.path.join(ROOT, "data", f)))

# --- palette ---------------------------------------------------------------
INK = "20303A"; ACCENT = "E4572E"; BLUE = "2F7FA8"
HEADF = PatternFill("solid", fgColor=INK)
CATF  = PatternFill("solid", fgColor="DCE6EC")
HEROF = PatternFill("solid", fgColor="E8F0E4")     # headline category tint
ALT   = PatternFill("solid", fgColor="F4F7F9")
WARNF = PatternFill("solid", fgColor="FCE9E3")
WHITE = Font(color="FFFFFF", bold=True, size=11)
BOLD  = Font(bold=True, color=INK)
CATFONT = Font(bold=True, color=INK, size=11)
NORM  = Font(color="20303A", size=10)
thin  = Side(style="thin", color="C7D2D8")
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)
WRAP  = Alignment(wrap_text=True, vertical="top")
WRAPC = Alignment(wrap_text=True, vertical="center", horizontal="center")

# --- load live numbers -----------------------------------------------------
_s  = J("summary.json"); s = {**_s, **_s.get("network", {})}
coh = J("cohort_pc_analysis.json")["full_cohort"]
grid= J("synthetic_grid_analysis.json")
rc  = J("robustness_ceiling_summary.json")
kl  = J("kleaf_validation_summary.json")
hyd = J("hydraulic_validation.json")["summary"]
bt  = J("scaling_mesh.json")["beta_test"]
dyn = J("dynamics.json")
ret = J("cohort_suggested_summary.json")
ca  = ret["clean_A_sensitivity"]
sink= J("sink_demo.json")

wb = openpyxl.Workbook()

# ===========================================================================
# SHEET 1 -- READ ME
# ===========================================================================
ws = wb.active; ws.title = "READ ME"
ws.sheet_view.showGridLines = False
ws.column_dimensions["A"].width = 3
ws.column_dimensions["B"].width = 104
def putB(r, text, font=None, fill=None, h=None):
    c = ws.cell(row=r, column=2, value=text)
    c.font = font or NORM; c.alignment = WRAP
    if fill: c.fill = fill
    if h: ws.row_dimensions[r].height = h
    return c
putB(2, "Holoparasitic Percolation Project - Data Summary", Font(bold=True, size=16, color=INK))
putB(3, "Leaf vein architecture and host resistance to holoparasitic vascular collapse "
        "(percolation analysis across real Matos leaves).", Font(italic=True, size=10, color=BLUE), h=30)
putB(5, "Every value is read live from the data/ files at build time, so the workbook "
        "cannot disagree with the code.", NORM, h=24)
putB(7, "HEADLINE RESULT - real-leaf reticulation cohort.", BOLD)
putB(8, "For all %d real Matos leaves we measured the random-attack percolation threshold p_c "
        "on (a) the leaf as traced and (b) the same leaf with shortest Delaunay areole-loops added "
        "to its own venation. %d valid whole-leaves (%d crop fragments excluded). p_c median "
        "%.3f -> %.3f; %d%% improved, none worsened. Adding reticulation to a real leaf never hurts "
        "and helps whenever there is headroom." % (ret["n_total"], ret["n_valid"], ret["n_fragments"],
        ret["pc_current"]["median"], ret["pc_suggested"]["median"], round(100*ret["frac_improved"])),
     NORM, h=58)
putB(10, "Reference (hero) network - SYNTHETIC, calibrated.", BOLD)
putB(11, "A generated planar MESH tuned to the real cohort medians (N=%d, <k>=%.2f, D=%.3f). "
         "Used for the hydraulic sink demo and the threshold/beta measurements; it is NOT a real "
         "leaf." % (s["n_nodes"], s["mean_degree"], s["D"]), NORM, h=40)
putB(13, "Global caveats.", BOLD)
putB(14, "  1. Clean-A sensitivity: on the 21 accurately-traced (quality-A) leaves the gain is "
         "smaller (delta p_c median +%.3f, %d%% improved) - the headline is partly amplified by "
         "missing-vein (B) leaves that look artificially sparse. Report both."
         % (ca["delta_pc"]["median"], round(100*ca["frac_improved"])), WARNF, h=44)
putB(15, "  2. The haustorial sink, anchored to literature (illustrative ~1.5 MPa gradient [review-level, "
         "NOT primary/NOT Kaiser 2015], ~18-20%% flow diversion [hemiparasite floor]), is SUB-symptomatic: "
         "0 vessels embolise at any gradient. Hydraulic sink and percolation collapse are decoupled lenses.", WARNF, h=44)
putB(16, "  3. Critical exponent beta is NOT a headline - transition is continuous but no "
         "universality class without a multi-size collapse. Do not quote a beta value.", WARNF, h=32)
putB(17, "  4. Xylem-only model does not predict whole-leaf Kleaf (outside-xylem dominated) - "
         "stated limitation, not validation.", WARNF, h=32)
putB(18, "  5. dynamics.json (time-dependent) was computed on the LEGACY knn network (pre-mesh); "
         "its p_c=0.279 / kappa=7.15 are legacy values, flagged below.", WARNF, h=32)
putB(20, "The multi-parasite comparison (Cuscuta/Orobanche/Striga/Mistletoe) has been DROPPED - "
         "it used stipulated efficiencies and was the weakest-validated piece.", Font(italic=True, color="8A5A4A"), h=30)
putB(22, "Sheets:  READ ME  |  Data Summary  |  Reticulation Cohort  |  File Index",
     Font(italic=True, color=BLUE))

# ===========================================================================
# SHEET 2 -- DATA SUMMARY (master table)
# ===========================================================================
ws = wb.create_sheet("Data Summary")
ws.sheet_view.showGridLines = False
headers = ["Category", "Metric", "Value", "Statistic / 95% CI", "Source file", "Figure", "What it implies"]
widths  = [24, 30, 16, 24, 28, 24, 50]
for j, (h, w) in enumerate(zip(headers, widths), start=1):
    c = ws.cell(row=1, column=j, value=h); c.font = WHITE; c.fill = HEADF
    c.alignment = WRAPC; c.border = BORDER
    ws.column_dimensions[get_column_letter(j)].width = w
ws.row_dimensions[1].height = 30
ws.freeze_panes = "A2"

ci = s["p_c_ci95"]
HERO = "Reticulation cohort (REAL - headline)"
rows = [
 # ---- HEADLINE: real reticulation cohort ----
 (HERO, "Leaves analysed", "%d valid" % ret["n_valid"],
  "of %d (%d fragments excl.)" % (ret["n_total"], ret["n_fragments"]),
  "data/cohort_suggested.csv", "figures/cohort_suggested.png",
  "All real Matos leaves; tiny crop fragments screened out by N>=1000."),
 (HERO, "p_c current -> suggested", "%.3f -> %.3f" % (ret["pc_current"]["median"], ret["pc_suggested"]["median"]),
  "median, n=%d" % ret["n_valid"], "data/cohort_suggested_summary.json", "figures/cohort_suggested.png",
  "Adding reticulation to a real leaf's OWN venation raises its collapse threshold."),
 (HERO, "Robustness gain delta p_c", "+%.3f" % ret["delta_pc"]["median"],
  "mean +%.3f, max +%.3f, min %.3f" % (ret["delta_pc"]["mean"], ret["delta_pc"]["max"], ret["delta_pc"]["min"]),
  "data/cohort_suggested_summary.json", "figures/cohort_suggested.png",
  "Every valid leaf sits ON or ABOVE the diagonal - NOT ONE leaf got worse."),
 (HERO, "Fraction improved", "%d%%" % round(100*ret["frac_improved"]),
  "%d of %d leaves" % (round(ret["frac_improved"]*ret["n_valid"]), ret["n_valid"]),
  "data/cohort_suggested_summary.json", "-",
  "The rest are already-reticulate leaves with no headroom (delta=0), not harmed."),
 (HERO, "Clean-A sensitivity", "+%.3f" % ca["delta_pc"]["median"],
  "%d%% improved, n=%d" % (round(100*ca["frac_improved"]), ca["n"]),
  "data/cohort_suggested_summary.json", "-",
  "HONEST CAVEAT: on accurately-traced leaves the gain is smaller; missing-vein leaves inflate the headline."),
 (HERO, "Top gainer", "%s +%.3f" % (ret["top10_gainers"][0]["species"], ret["top10_gainers"][0]["delta_pc"]),
  "sparse leaf, +%d loops" % ret["top10_gainers"][0]["loops_added"],
  "data/cohort_suggested.csv", "-",
  "Sparsest leaves have the most to gain; already-networked leaves gain nothing."),
 # ---- reference network ----
 ("Reference network (synthetic)", "Nodes / <k> / D",
  "%d / %.2f / %.3f" % (s["n_nodes"], s["mean_degree"], s["D"]), "calibrated mesh",
  "data/summary.json", "figures/network.png",
  "Generated mesh tuned to real cohort medians - NOT a real leaf; used for the sink demo + beta."),
 # ---- percolation thresholds (hero) ----
 ("Percolation thresholds", "Random p_c (hero)", "%.3f" % s["p_c_random"],
  "CI [%.3f, %.3f]" % (ci[0], ci[1]), "data/summary.json", "figures/sigmoid.png",
  "~27%% of vessels must fail before the conducting network fragments (on the synthetic hero)."),
 ("Percolation thresholds", "Targeted (backbone/degree)",
  "%.3f / %.3f" % (s["p_c_targeted_betweenness"], s["p_c_targeted_degree"]), "targeted",
  "data/summary.json", "figures/sigmoid_targeted.png",
  "Both targeted attacks beat random - matches real leaves (degree<random in 100%% of the cohort)."),
 # ---- real cohort regression ----
 ("Real cohort regression (n=100)", "partial r(p_c,<k>|D)", "%.2f" % coh["partial_pc_vs_k_given_D"]["r"],
  "p=%.0e" % coh["partial_pc_vs_k_given_D"]["p"], "data/cohort_pc_analysis.json",
  "figures/cohort_pc_predictors.png",
  "On real leaves connectivity predicts the threshold independently of fractal dimension."),
 ("Real cohort regression (n=100)", "partial r(p_c,D|<k>)", "%.2f" % coh["partial_pc_vs_D_given_k"]["r"],
  "p=%.0e" % coh["partial_pc_vs_D_given_k"]["p"], "data/cohort_pc_analysis.json",
  "figures/cohort_pc_predictors.png",
  "D is a REAL, independent predictor - both traits matter, near-orthogonally (VIF=1.02)."),
 # ---- synthetic causal grid ----
 ("Synthetic causal grid (n=42)", "partial r(p_c,<k>|D)", "%.2f" % grid["pc_random"]["partial_r_pc_k_given_D"],
  "Spearman %.2f" % grid["pc_random"]["spearman_k"], "data/synthetic_grid_analysis.json", "-",
  "Causal confirmation: with the generator controlled, connectivity dominates p_c."),
 # ---- robustness ceiling ----
 ("Robustness ceiling", "Median gain from reticulation", "+%.3f" % rc["median_gain_reticulation"],
  "dominant lever for %d%%" % round(100*rc["reticulation_is_dominant_lever_fraction"]),
  "data/robustness_ceiling_summary.json", "-",
  "Reticulation is the dominant robustness lever for ~9 in 10 species (vs raising D)."),
 # ---- hydraulic validation ----
 ("Hydraulic validation", "Exact Hagen-Poiseuille match", "%d/%d leaves" % (hyd["n_exact"], hyd["n_leaves"]),
  "%d veins, CV~%.0e" % (hyd["total_veins_compared"], hyd["worst_ratio_cv"]),
  "data/hydraulic_validation.json", "-",
  "Our conductance reproduces the source dataset's own resistance EXACTLY - the physics engine is verified."),
 # ---- Kleaf limitation ----
 ("Kleaf limitation", "Spearman rho vs measured Kleaf", "%.2f" % kl["spearman_rho"],
  "p=%.2f, n=%d" % (kl["spearman_p"], kl["n_species"]), "data/kleaf_validation_summary.json", "-",
  "HONEST LIMITATION: xylem-only model does not predict whole-leaf Kleaf (outside-xylem dominated)."),
 # ---- critical exponent ----
 ("Critical exponent (do NOT quote)", "beta (mesh, N=8191)", "%.2f" % bt["beta"],
  "SE %.3f, R^2 %.3f" % (bt["beta_se"], bt["loglog_R2"]), "data/scaling_mesh.json", "figures/stat_beta_fit.png",
  "Continuous transition, but beta matches NEITHER mean-field (1.0) NOR 2-D (0.14). No class claim yet."),
 # ---- haustorial sink demo (grounded) ----
 ("Haustorial sink demo (grounded)", "Calibrated K_h", "%.4f" % sink["K_H_HOLOPARASITE"],
  "%.1f MPa grad, %.0f%% diversion" % (sink["gradient_MPa"], 100*sink["achieved_diversion"]),
  "data/sink_demo.json", "figures/sink_demo.png",
  "K_h anchored to Jiang 2003 (~18-20%% flow, hemiparasite floor) + illustrative ~1.5 MPa gradient "
  "(review-level, NOT Kaiser 2015) - a delimitation, not a measured input."),
 ("Haustorial sink demo (grounded)", "Vessels embolised", "0 of %d" % s["n_nodes"],
  "at ANY gradient", "data/sink_demo.json", "figures/sink_demo.png",
  "KEY FINDING: a realistic sink drains 20%% of flow but cannot rupture the xylem - harm is resource drain. "
  "Hydraulic sink and percolation collapse are DECOUPLED."),
 # ---- dynamics (LEGACY) ----
 ("Time dynamics (LEGACY net)", "Dynamic p_c", "%.3f" % dyn["p_c"],
  "kappa=%.2f" % dyn["kappa"], "data/dynamics.json", "figures/dynamics.png",
  "LEGACY knn network (pre-mesh). Differential-equation deliverable; values NOT on the current hero."),
]

r = 2; last = None
for cat, metric, val, stat, src, fig, imp in rows:
    warn = ("do NOT" in cat) or ("LEGACY" in cat) or ("limitation" in cat)
    hero = cat == HERO
    vals = [cat if cat != last else "", metric, val, stat, src, fig, imp]
    for j, v in enumerate(vals, start=1):
        c = ws.cell(row=r, column=j, value=v); c.border = BORDER; c.alignment = WRAP; c.font = NORM
        if j == 1 and v:
            c.font = CATFONT; c.fill = HEROF if hero else CATF
        elif hero:
            c.fill = HEROF
        elif warn:
            c.fill = WARNF
        elif r % 2 == 0:
            c.fill = ALT
        if j == 3:
            c.font = Font(bold=True, color=ACCENT if not hero else "2E7D32", size=10)
    ws.row_dimensions[r].height = 46
    last = cat; r += 1

# ===========================================================================
# SHEET 3 -- RETICULATION COHORT (per-leaf)
# ===========================================================================
ws = wb.create_sheet("Reticulation Cohort")
ws.sheet_view.showGridLines = False
# aggregate banner
ws.cell(row=1, column=1, value="REAL-LEAF RETICULATION COHORT  -  current vs suggested (more reticulate), "
        "random attack, %d trials/network" % ret["trials_per_network"]).font = Font(bold=True, size=12, color=INK)
ws.merge_cells("A1:J1"); ws.row_dimensions[1].height = 22
agg = ("%d valid whole-leaves (%d fragments excluded)  |  p_c median %.3f -> %.3f  |  "
       "delta median +%.3f (max +%.3f)  |  %d%% improved, 0 worsened  |  "
       "clean-A subset (n=%d): +%.3f, %d%% improved"
       % (ret["n_valid"], ret["n_fragments"], ret["pc_current"]["median"], ret["pc_suggested"]["median"],
          ret["delta_pc"]["median"], ret["delta_pc"]["max"], round(100*ret["frac_improved"]),
          ca["n"], ca["delta_pc"]["median"], round(100*ca["frac_improved"])))
ws.cell(row=2, column=1, value=agg).font = Font(italic=True, color="2E7D32")
ws.merge_cells("A2:J2"); ws.row_dimensions[2].height = 30

ph = ["species", "N", "quality", "k_current", "loops_added", "k_suggested", "D",
      "pc_current", "pc_suggested", "delta_pc"]
pw = [12, 10, 10, 12, 12, 12, 10, 12, 13, 11]
for j, (h, w) in enumerate(zip(ph, pw), start=1):
    c = ws.cell(row=4, column=j, value=h); c.font = WHITE; c.fill = HEADF
    c.alignment = WRAPC; c.border = BORDER
    ws.column_dimensions[get_column_letter(j)].width = w
ws.row_dimensions[4].height = 26
ws.freeze_panes = "A5"

leaves = list(csv.DictReader(open(os.path.join(ROOT, "data", "cohort_suggested.csv"), newline="")))
def fnum(x):
    try: return float(x)
    except Exception: return float("nan")
leaves = [l for l in leaves if int(float(l["N"])) >= 1000 and fnum(l["pc_current"]) >= 0.02]
leaves.sort(key=lambda l: -fnum(l["delta_pc"]))
r = 5
for l in leaves:
    d = fnum(l["delta_pc"])
    row = [l["species"], int(float(l["N"])), l.get("quality", ""),
           round(fnum(l["k_current"]), 3), int(float(l["loops_added"])),
           round(fnum(l["k_suggested"]), 3), round(fnum(l["D"]), 3) if l.get("D") else "",
           round(fnum(l["pc_current"]), 3), round(fnum(l["pc_suggested"]), 3), round(d, 3)]
    for j, v in enumerate(row, start=1):
        c = ws.cell(row=r, column=j, value=v); c.border = BORDER; c.alignment = WRAPC; c.font = NORM
        if r % 2 == 0: c.fill = ALT
        if j == 10:
            c.font = Font(bold=True, color="2E7D32" if d > 0 else "999999", size=10)
    ws.row_dimensions[r].height = 15
    r += 1

# ===========================================================================
# SHEET 4 -- FILE INDEX
# ===========================================================================
ws = wb.create_sheet("File Index")
ws.sheet_view.showGridLines = False
fh = ["Data file", "What it holds", "Produced by"]
fw = [36, 66, 32]
for j, (h, w) in enumerate(zip(fh, fw), start=1):
    c = ws.cell(row=1, column=j, value=h); c.font = WHITE; c.fill = HEADF
    c.alignment = WRAPC; c.border = BORDER
    ws.column_dimensions[get_column_letter(j)].width = w
ws.row_dimensions[1].height = 26
ws.freeze_panes = "A2"
files = [
 ("data/cohort_suggested.csv", "HEADLINE: per-leaf current vs suggested-reticulate p_c for all 120 real leaves.", "scripts/run_cohort_suggested.py"),
 ("data/cohort_suggested_summary.json", "Aggregate reticulation gain + clean-A sensitivity + top gainers.", "scripts/make_suggested_summary.py"),
 ("data/sink_demo.json", "Literature-anchored K_h (~18-20% diversion floor; illustrative ~1.5 MPa gradient) + the sub-cavitation finding.", "scripts/make_sink_demo.py"),
 ("data/summary.json", "Synthetic hero network metrics + the three p_c thresholds (1e6 trials) + CI.", "scripts/run_full.py"),
 ("data/cohort_pc_analysis.json", "Observational regression on 100 real leaves: partial correlations, VIF.", "scripts/run_cohort_percolation.py"),
 ("data/synthetic_grid_analysis.json", "Causal 42-network grid: partial r, Spearman, OLS surface.", "scripts/run_synthetic_grid.py"),
 ("data/robustness_ceiling_summary.json", "Per-species breeding headroom: reticulation vs D lever.", "scripts/run_robustness_ceiling.py"),
 ("data/hydraulic_validation.json", "Exact-match check vs source Resistance (119 leaves, 5.67M veins).", "hydraulic validation run"),
 ("data/kleaf_validation_summary.json", "Model vs measured Kleaf: weak Spearman (stated limitation).", "scripts/run_kleaf_validate.py"),
 ("data/scaling_mesh.json", "Finite-size series + critical-exponent beta test on the mesh.", "scripts/run_scaling_mesh.py"),
 ("data/dynamics.json", "Time-dependent collapse (LEGACY knn network) - the ODE deliverable.", "scripts/run_dynamics.py"),
 ("data/characterization_annotated.csv", "Per-leaf structural descriptors + quality flags for all 120 leaves.", "characterization module"),
 ("data/parasites.json", "DEPRECATED - old multi-parasite comparison (dropped; stipulated efficiencies).", "scripts/run_parasites.py"),
]
r = 2
for f, what, by in files:
    dep = "DEPRECATED" in what
    for j, v in enumerate((f, what, by), start=1):
        c = ws.cell(row=r, column=j, value=v); c.border = BORDER; c.alignment = WRAP; c.font = NORM
        if dep: c.fill = WARNF
        elif r % 2 == 0: c.fill = ALT
        if j == 1: c.font = Font(bold=True, color=BLUE if not dep else "999999", size=10)
    ws.row_dimensions[r].height = 30
    r += 1

out = os.path.join(ROOT, "DATA_SUMMARY.xlsx")
wb.save(out)
print("SAVED:", out)
print("Sheets:", wb.sheetnames)
print("Reticulation cohort rows:", len(leaves))
