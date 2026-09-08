# -*- coding: utf-8 -*-
r"""
make_ppt_guide_pdf.py -- typeset the deck build guide as a PDF.

    C:\laragon\bin\python\python-3.13\python.exe scripts\make_ppt_guide_pdf.py

Companion to make_defense_script_pdf.py; same fonts, same palette, same markup,
different page furniture. The guide text lives in GUIDE below so the PDF is the
only deliverable and there is no parallel markdown to drift.

Every figure path in the slide table is checked against the working tree at
build time, and the run fails if one is missing, so the guide cannot ship a
path that does not resolve. Figures known to be absent are declared in
TO_GENERATE and reported rather than treated as an error; that set is currently
empty because every referenced figure exists.

Markup accepted in GUIDE:
    @TITLE / @SUB        document title and subtitle lines
    @PART text           section heading (starts a new page)
    @H text              subheading
    @SLIDE n | title | block   slide entry heading
    @F key: value        a labelled field line inside a slide entry
    @FIG path            a figure path (verified at build time)
    @THEAD a | b | c     table header row
    @TABLE a | b | c     table row
    @BULLET text         bullet line
    @RULE                horizontal rule
    text                 plain paragraph
Inline: **bold**, *italic*, `mono`.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, CondPageBreak, Frame,
                                KeepTogether, PageBreak, PageTemplate,
                                Paragraph, Spacer, Table, TableStyle)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "PPT_BUILD_GUIDE.pdf"
FONT_DIR = Path(r"C:\Windows\Fonts")

MARGIN_X = 0.85 * inch
MARGIN_TOP = 0.8 * inch
MARGIN_BOT = 0.8 * inch

INK = colors.HexColor("#1A1D21")
MUTED = colors.HexColor("#6B7280")
VEIN = colors.HexColor("#2E7D5B")
LOSS = colors.HexColor("#C1462F")
RULE = colors.HexColor("#D9D9D2")

DOC_TITLE = "Deck Build Guide"

# Figures the deck needs that the repository does not yet contain. Empty is the
# correct state; entries here are reported rather than failing the build.
TO_GENERATE: set[str] = set()


GUIDE = r"""
@TITLE Deck Build Guide
@SUB Percolation Analysis of Vein Reticulation as a Structural Basis for Damage Tolerance in Leaf Venation Networks under Simulated Vascular Damage
@SUB Nicko Fajardo  |  16 core slides + 7 hidden appendix  |  companion to DEFENSE_SCRIPT.pdf

Slide numbers below map to the numbered blocks of `DEFENSE_SCRIPT.pdf`. Every figure
path was verified against the working tree when this PDF was generated. Every number
was taken from Part 8 of `STUDY_MASTERY_GUIDE.md`.

@RULE

@PART 1. Deck specification

@THEAD Setting | Value
@TABLE Aspect ratio | 16:9, 1920 x 1080
@TABLE Slide count | 16 core, 7 appendix (hidden)
@TABLE Spoken runtime | 14 min 45 s across 10 script blocks
@TABLE Longest blocks | 8 (2:35), 10 (2:05), 9 (1:45)
@TABLE Margins | 80 px on all four sides
@TABLE Export | PPTX and PDF; PDF is the projector fallback
@TABLE Fonts | embed: File, Options, Save, Embed all characters

@H Type

@THEAD Role | Font | Size
@TABLE Slide title | Inter SemiBold (fallback Calibri) | 40 pt
@TABLE Body | Inter Regular | 24 to 28 pt, never below 22
@TABLE Hero number | Inter Bold | 90 to 140 pt, one per slide
@TABLE Hero caption | Inter Regular | 20 pt
@TABLE Figure axis text | from matplotlib | 18 pt equivalent minimum

@H Colour

@THEAD Token | Hex | Applied to
@TABLE Ink | #1A1D21 | body text, titles
@TABLE Paper | #FAFAF7 | slide background
@TABLE Vein | #2E7D5B | connectivity, reticulation, the intervention
@TABLE Loss | #C1462F | damage, removal, collapse, thresholds
@TABLE Muted | #6B7280 | captions, secondary labels, sources
@TABLE Rule | #E2E2DC | hairlines, table borders

Green means connectivity and red means damage on every slide, without exception. Pair
each colour with a label or position as well, since roughly one panelist in twelve
cannot separate the two by hue.

@H Species naming

The study models a generic haustorial leak conductance, not a species. The manuscript
names *Cuscuta* in three roles only: introduction motivation, the pre-symptomatic
time-course literature, and the scope of the Balios et al. 2025 published negative. The
calibrated 18 to 20 percent diversion is a hemiparasite measurement (Jiang et al. 2003).

A species name therefore appears on **slides 2, 16 and A1 only**, and on no methods,
results or model slide.

@PART 2. Slide-by-slide

@SLIDE 1 | Title | before block 1
@FIG figures/board_photos/cuscuta_b.jpg
@F Layout: full-bleed photo darkened to about 35 percent, text overlaid bottom-left
@F Content: full study title at 32 pt over two lines; name, school, adviser at 20 pt Muted
@F Exclude: outline, agenda, objectives

@SLIDE 2 | Opening image | block 1
@FIG figures/board_photos/haustorium.jpg
@F Layout: full-bleed image, one text line bottom-left at 28 pt
@F Line: *Cuscuta*. A holoparasite. It drills.
@F Constraint: the word holoparasite must be present; this is one of three slides permitted a species name

@SLIDE 3 | The negative result | block 2
@F Layout: hero number, centred
@F Hero: 2.6% in Loss red at 140 pt
@F Caption: the modelled sink's share of the safety margin (not "the parasite's")
@F Strip: 0.026 MPa depression | 6.0 MPa needed to cavitate | 0.5 MPa largest ever measured
@F Build: strip appears on click

@SLIDE 4 | Branching against reticulate | block 3
@FIG figures/methodology/fig_reticulation_concept.png
@F Layout: two panels, 50/50
@F Left label: Branching, one route (Loss red)
@F Right label: Reticulate, detour available (Vein green)
@F Footer: Sack et al., midrib cut = -75% conductance; minor veins cut = no detectable penalty
@F Build: left panel, then right on click
@F Blocking: the script points left for branching and right for reticulate; keep those sides on slide 14 as well

@SLIDE 5 | Fragmentation | block 4
@FIG figures/collapse_montage.png
@F Layout: single figure, full width
@F Title: Connectivity does not decay. It shatters.
@F Preferred: figures/collapse.gif, a 6-second loop on a real cohort leaf; confirm playback on the venue machine
@F Fallback: figures/collapse_montage.png if the venue machine will not loop a GIF
@F Regenerate: scripts/make_collapse_gif.py

@SLIDE 6 | Definitions | block 4
@F Layout: three columns
@F Columns: Nodes = vein junctions | Edges = vein segments | Threshold = fraction removed before the giant component halves
@F Footer: operational, not a physical critical point; source-anchored cross-check rho = 0.912
@F Range to state if asked: 421 to 300,633 nodes

@SLIDE 7 | Data and its limitation | block 5
@FIG figures/methodology/fig02_dataset.png
@F Layout: figure left 60 percent, facts right 40 percent
@F Facts: 120 traced networks, 122 species, Matos et al. 2024, Dryad
@F Cohorts: 112 characterisation, 100 percolation, 105 enhancement
@F Boxed in Loss red: 100 of 120 are calibrated crop windows, not whole leaves

@SLIDE 8 | Methods pipeline | block 5
@FIG figures/methodology/fig01_pipeline_revised.png
@F Layout: full-width horizontal flow, title only, no bullets
@F Note: the one slide permitted to be dense; regenerate if internal text falls below 18 pt on screen

@SLIDE 9 | The threshold | block 6
@FIG figures/sigmoid.png
@F Layout: hero number left 40 percent, figure right 60 percent
@F Hero: 0.1998 at 120 pt in Loss red
@F Caption: median critical removed fraction, n = 100
@F Footer: 2,400 Monte Carlo trials per network per mode, fixed seeds
@F Build: none

@SLIDE 10 | Degree-weighted removal | block 6
@FIG figures/sigmoid.png
@FIG figures/sigmoid_targeted.png
@F Layout: two collapse curves side by side on shared axes
@F Numbers: 0.1998 to 0.1685, -15.7 percent, 100 of 100 networks
@F Boxed footer: not an attack; probabilistic weighting, a bounding scenario

@SLIDE 11 | Architecture predicts tolerance | block 7
@FIG figures/cohort_pc_predictors.png
@F Layout: figure top 65 percent, quartile table bottom 35 percent
@F Correlations: mean degree rho = 0.733; fractal dimension rho = 0.496
@F Size-controlled: 0.745 and 0.633, both stronger
@F Model: R-squared = 0.507, F(2,97) = 49.93
@F Build: figure, table on click, correlations on click

@THEAD Reticulation quartile | Loop fraction | Mean degree | Median threshold
@TABLE Q1 least reticulate | 0.616 | 2.320 | 0.1584
@TABLE Q2 | 0.738 | 2.472 | 0.1850
@TABLE Q3 | 0.807 | 2.564 | 0.2087
@TABLE Q4 most reticulate | 0.901 | 2.734 | 0.2308

Q4 minus Q1 is 7.2 percentage points, a 45.7 percent relative gain, monotonic across all
four quartiles. U = 4, delta = 0.987.

@SLIDE 12 | The intervention | block 8
@FIG figures/cohort_suggested.png
@F Layout: figure centred, result overlaid bottom-right
@F Result at 56 pt: 93 improved, 12 unchanged, 0 worse
@F Numbers: 0.2010 to 0.2150, median difference 0.0095, p = 1.7e-18
@F Method footer: Delaunay, parameter-free; capped at cohort P90 mean degree 2.811; common random numbers; 10,000 trials per arm
@F Build: the "0 worse" appears last, on its own click
@F Note: block 8 runs 2:35 and covers this slide and slide 13; do not rush off it

@SLIDE 13 | The intervention, shown | block 8
@FIG figures/methodology/fig_realsuggested_Met_dav.png
@F Layout: before and after, side by side, identical scale
@F Labels: Original | Plus loops, from its own coordinates
@F Alternative if added edges are hard to see: figures/methodology/fig_realsuggested_Cis_ant_zoom_pair.png

@SLIDE 14 | The scope limit | block 9
@FIG figures/locality_boxplots.png
@F Layout: boxplots left 60 percent, numbers right 40 percent
@F Numbers: 0.1998 dispersed, 0.4951 one lesion (2.46x), 0.4511 ten lesions (2.27x); 100 of 100 both
@F In Loss red: rho 0.737 dispersed, 0.151 ten lesions, -0.000 one lesion
@F Footer: claim scoped to dispersed damage
@F Build: the correlation collapse on click

@SLIDE 15 | Scope as a claim | block 9
@F Layout: text only, centred, 44 pt, three lines. The only text-only slide in the deck.
@F Line 1: Reticulation governs tolerance
@F Line 2: to *dispersed* damage.
@F Line 3: Under a single lesion, the effect is gone.
@F Footer: fractal dimension behaves oppositely and survives multi-lesion damage at rho = 0.523

@SLIDE 16 | Close | block 10
@FIG figures/board_photos/cuscuta_b.jpg
@F Layout: three lines, hairline, then two gap lines; small photo thumbnail bottom-right
@F Line 1: about 20 percent of junctions to fragmentation
@F Line 2: reticulation raises that threshold, causally, within-leaf
@F Line 3: conditional on dispersed damage
@F Gap line 1 at 24 pt: Cuscuta-host, no published water potential (Balios et al. 2025)
@F Gap line 2 at 24 pt: holoparasites as a class, none found (this study's search)
@F Constraint: the two gap lines stay separate and neither widens to "parasitic plants"; hemiparasite water relations have been measured, and the 20 percent on slide 3 is one of those measurements
@F Exclude: a Thank you or Questions slide; the conclusion stays on screen through questioning

@PART 3. Builds and animation

Permitted: Appear with no duration, and Fade at 0.2 s or less. Not permitted: Fly In,
Wipe, Zoom, Bounce, Morph, and slide transitions of any kind.

@THEAD Slide | Click | Reveals
@TABLE 3 | 1 | the MPa strip
@TABLE 4 | 1 | the reticulate panel
@TABLE 5 | up to 3 | montage panels left to right
@TABLE 11 | 2 | quartile table, then the correlations
@TABLE 12 | 1 | 93 / 12 / 0
@TABLE 14 | 1 | the correlation collapse

Total build clicks: 9 to 11 depending on slide 5. Every other slide appears whole.
Write the per-slide click count on the notes card.

@PART 4. Figures

@H Figures required, all verified present

@THEAD Slide | Path
@TABLE 1, 16 | figures/board_photos/cuscuta_b.jpg
@TABLE 2 | figures/board_photos/haustorium.jpg
@TABLE 4 | figures/methodology/fig_reticulation_concept.png
@TABLE 5 | figures/collapse.gif, figures/collapse_montage.png
@TABLE 7 | figures/methodology/fig02_dataset.png
@TABLE 8 | figures/methodology/fig01_pipeline_revised.png
@TABLE 9, 10 | figures/sigmoid.png, figures/sigmoid_targeted.png
@TABLE 11 | figures/cohort_pc_predictors.png
@TABLE 12 | figures/cohort_suggested.png
@TABLE 13 | figures/methodology/fig_realsuggested_Met_dav.png
@TABLE 14 | figures/locality_boxplots.png
@TABLE A2 | figures/methodology/fig12_stats_tree.png
@TABLE A3 | figures/calibration_grid.png
@TABLE A4 | figures/sink_demo.png, figures/sink_surface.png
@TABLE A6 | figures/finite_size_fixedD.png

@H The collapse animation

`figures/collapse.gif` is generated by `scripts/make_collapse_gif.py`. It runs on a real
cohort leaf rather than the synthetic mesh, and it draws the giant connected component
in Vein green with everything detached from it in grey. That colour split is the whole
point: with one colour for all surviving veins, the eye reads progressive thinning
rather than fragmentation. Removal is nested from a single seeded permutation, so the
sequence is one sweep rather than unrelated draws. Roughly 6 seconds, 1.1 MB, holds on
the intact network at the start and the shattered state at the end.

The threshold line is that leaf's archived value. The animation is a single realisation,
so its own crossing sits slightly later; the archived number is a median over 2,400
trials. Say "one run" if asked, not "the threshold".

@H The locality figure

`figures/locality_boxplots.png` is generated by `scripts/make_locality_figure.py` from
`data/criterion_and_locality.csv`, 100 rows, columns `pc_gcc` (dispersed), `pc_disc1`
(one lesion) and `pc_disc10` (ten lesions). Re-run that script if the underlying data
changes; it prints the medians and ratios it drew.

Each network is also drawn as a faint line carried across the three conditions, because
the claim is that every network moved the same way rather than that the distributions
differ on average, and only the paired lines show that. The 2.46x and 2.27x printed on
it are median per-network ratios, not ratios of the medians; the two definitions differ
in the third decimal and the per-network one is what the manuscript reports.

@H Preparing the rest

Check each figure full-screen from three metres. If the axis labels cannot be read,
regenerate at larger type rather than scaling the image, which only enlarges blurred
text. Set before regenerating: font.size 16, axes.labelsize 18, axes.titlesize 20,
tick labelsize 15, legend.fontsize 15, savefig.dpi 200, bbox tight, facecolor #FAFAF7.

Remove figure-internal titles, which duplicate the slide title, along with unused
gridlines and single-entry legends. Recolour series to #2E7D5B and #C1462F. Write slide
copies to `figures/slides/` and never overwrite a manuscript figure. Export PNG at 200
dpi or higher; JPEG artefacts around thin vein lines read as tracing noise.

@PART 5. Appendix slides

Hidden from the main flow with right-click, Hide Slide. Reached during questioning by
typing the slide number and Enter. Write the numbers on the notes card.

@THEAD Slide | Contents | Question it answers
@TABLE A1 | sink scoping card, contents below | which parasite are you modelling
@TABLE A2 | figures/methodology/fig12_stats_tree.png | why Spearman and not Pearson
@TABLE A3 | figures/calibration_grid.png | how were connectivity and D separated
@TABLE A4 | figures/sink_demo.png and figures/sink_surface.png | show the sink model
@TABLE A5 | cavitation threshold sweep | is zero embolised robust
@TABLE A6 | figures/finite_size_fixedD.png | is this a phase transition
@TABLE A7 | limitations table, contents below | what are your limitations

@H A1, sink scoping card

@BULLET Modelled: a generic haustorial leak conductance, K_h = 0.0392, giving 20.0 percent withdrawal
@BULLET Anchor: Jiang et al. 2003, a hemiparasite; no holoparasite flux fraction has been measured
@BULLET Gradient: about 1.5 MPa, stipulated, declared as a delimitation
@BULLET Attachment in nature: Cuscuta to stems, petioles and pedicels; Orobanche to roots; the networks here are leaf laminae
@BULLET In Loss red: a haustorial node inside a lamina is a modelling device, declared as one

@H A5, cavitation threshold sweep

@THEAD Cavitation threshold | Onset gradient
@TABLE -1.00 MPa | 1.1 MPa
@TABLE -2.00 MPa | 6.0 MPa
@TABLE -3.00 MPa | 9.5 MPa

Zero vessels embolised holds from 0 to 3.0 MPa but inverts at a -1.00 MPa threshold, so
the result is specific to thresholds at or below about -1.10 MPa within the swept range.

@H A7, limitations

@BULLET No phylogenetic correction; species are treated as independent when they are not
@BULLET No multiple-comparison correction; the analysis is exploratory over a pre-specified predictor set
@BULLET 100 of 120 files are crop windows; no petiole flag exists in the deposit
@BULLET No construction-cost, mechanical or photosynthetic term in the enhancement experiment
@BULLET R-squared 0.507; about half the variance in the threshold is unmeasured
@BULLET K_leaf validation rho = 0.187, p = 0.073, underpowered and xylem-only
@BULLET Zero vessels embolised is threshold-dependent and inverts at -1.00 MPa
@BULLET Betweenness-weighted removal exists on the synthetic reference network only
@BULLET Bootstrap resample capped at 50,000 trials, so intervals on longer runs are conservative

@PART 6. Build order and checks

@H Order

@BULLET 1. Slides 12, 14, 15
@BULLET 2. Slides 3 and 2
@BULLET 3. Slides 9, 10, 11
@BULLET 4. Slides 4, 5, 6, 7, 8
@BULLET 5. Slides 1 and 16
@BULLET 6. Appendix A1 and A7 first, then A2 to A6
@BULLET 7. Remove one element from every slide
@BULLET 8. Rehearse against a timer, aloud and standing

@H Checks before the defense

@BULLET Species names appear on slides 2, 16 and A1 only
@BULLET Slide 16 keeps its two gap lines separate; neither says parasitic plants
@BULLET Slide 3 caption reads the modelled sink, not the parasite
@BULLET figures/locality_boxplots.png placed on slide 14
@BULLET Exported to PPTX and PDF, on a USB stick and in cloud storage
@BULLET Fonts embedded, all characters
@BULLET Opened once on a machine other than the one it was built on
@BULLET Every figure legible from three metres; no slide over six lines
@BULLET Click counts and appendix slide numbers written on the notes card
@BULLET Presenter view tested; notes are three-word cues, not sentences
@BULLET Slide 5 GIF confirmed to loop on the venue machine, or replaced with figures/collapse_montage.png
@BULLET No slide says attack, hydraulic collapse, validated, or leaves where it should say leaf venation networks

@PART 7. Related documents

@THEAD Document | Contents
@TABLE DEFENSE_SCRIPT.pdf | the spoken script; rebuild with scripts/make_defense_script_pdf.py
@TABLE PRESENTATION_SCRIPT.md | the full 40-question bank
@TABLE STUDY_MASTERY_GUIDE.md | concepts, Part 5 do-not-claim, Part 8 fast facts
@TABLE DEFENSE_PANEL_PREP.md | the ten questions the adviser flagged
@TABLE MANUSCRIPT_REVISED_SECTIONS.md | canonical figure numbering and captions
@TABLE rrl/E_parasitic_plants_haustoria.md | evidence behind the species-naming rule
"""


def register_fonts() -> None:
    faces = {
        "Body": "arial.ttf", "Body-Bold": "arialbd.ttf",
        "Body-Italic": "ariali.ttf", "Body-BoldItalic": "arialbi.ttf",
        "Mono": "consola.ttf",
    }
    for name, filename in faces.items():
        path = FONT_DIR / filename
        if not path.exists():
            raise SystemExit(f"missing font: {path}")
        pdfmetrics.registerFont(TTFont(name, str(path)))
    pdfmetrics.registerFontFamily(
        "Body", normal="Body", bold="Body-Bold",
        italic="Body-Italic", boldItalic="Body-BoldItalic")


def inline(text: str) -> str:
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"<i>\1</i>", text)
    text = re.sub(r"`([^`]+?)`",
                  r'<font name="Mono" size="8.5">\1</font>', text)
    return text


def build_styles() -> dict[str, ParagraphStyle]:
    body = ParagraphStyle(
        "body", fontName="Body", fontSize=9.5, leading=13.5,
        textColor=INK, alignment=TA_LEFT, spaceAfter=8)
    return {
        "body": body,
        "title": ParagraphStyle(
            "title", parent=body, fontName="Body-Bold", fontSize=21,
            leading=25, alignment=TA_CENTER, spaceAfter=6),
        "sub": ParagraphStyle(
            "sub", parent=body, fontSize=8.5, leading=12,
            textColor=MUTED, alignment=TA_CENTER, spaceAfter=3),
        "part": ParagraphStyle(
            "part", parent=body, fontName="Body-Bold", fontSize=14,
            leading=18, spaceAfter=10, keepWithNext=1),
        "h": ParagraphStyle(
            "h", parent=body, fontName="Body-Bold", fontSize=10.5,
            leading=14, spaceBefore=10, spaceAfter=5, keepWithNext=1),
        "slide": ParagraphStyle(
            "slide", parent=body, fontName="Body-Bold", fontSize=11,
            leading=15, textColor=VEIN, spaceBefore=12, spaceAfter=3,
            keepWithNext=1),
        "field": ParagraphStyle(
            "field", parent=body, fontSize=9.5, leading=13,
            leftIndent=12, spaceAfter=2),
        "fig": ParagraphStyle(
            "fig", parent=body, fontName="Mono", fontSize=8.5, leading=12,
            textColor=LOSS, leftIndent=12, spaceAfter=2),
        "bullet": ParagraphStyle(
            "bullet", parent=body, leftIndent=16, bulletIndent=4,
            spaceAfter=3),
        "cell": ParagraphStyle(
            "cell", parent=body, fontSize=9, leading=12.5, spaceAfter=0),
        "cellhead": ParagraphStyle(
            "cellhead", parent=body, fontName="Body-Bold", fontSize=9,
            leading=12.5, textColor=MUTED, spaceAfter=0),
    }


class Hairline(Table):
    def __init__(self, width: float):
        super().__init__([[""]], colWidths=[width], rowHeights=[1])
        self.setStyle(TableStyle([
            ("LINEABOVE", (0, 0), (-1, 0), 0.6, RULE),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))


def make_table(rows, width, st):
    ncols = max(len(c) for c, _ in rows)
    data, heads = [], []
    for i, (cells, is_head) in enumerate(rows):
        cells = cells + [""] * (ncols - len(cells))
        style = st["cellhead"] if is_head else st["cell"]
        data.append([Paragraph(inline(c), style) for c in cells])
        if is_head:
            heads.append(i)
    if ncols == 2:
        widths = [width * 0.34, width * 0.66]
    elif ncols == 3:
        widths = [width * 0.22, width * 0.30, width * 0.48]
    elif ncols == 4:
        widths = [width * 0.31, width * 0.23, width * 0.23, width * 0.23]
    else:
        widths = [width / ncols] * ncols
    tbl = Table(data, colWidths=widths, hAlign="LEFT", repeatRows=len(heads))
    cmds = [("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 3.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
            ("LEFTPADDING", (0, 0), (0, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("LINEBELOW", (0, 0), (-1, -2), 0.4, RULE)]
    for i in heads:
        cmds.append(("LINEBELOW", (0, i), (-1, i), 0.8, MUTED))
    tbl.setStyle(TableStyle(cmds))
    return tbl


def parse(src, st, width):
    flow, pending, para = [], [], []
    missing, declared = [], []

    def flush_para():
        nonlocal para
        if para:
            flow.append(Paragraph(inline(" ".join(para)), st["body"]))
            para = []

    def flush_table():
        nonlocal pending
        if pending:
            flow.append(make_table(pending, width, st))
            flow.append(Spacer(1, 9))
            pending = []

    for raw in src.strip("\n").split("\n"):
        s = raw.strip()
        if not s:
            flush_para()
            flush_table()
            continue

        if s.startswith("@TABLE ") or s.startswith("@THEAD "):
            flush_para()
            pending.append(([c.strip() for c in s.split(" ", 1)[1].split("|")],
                            s.startswith("@THEAD ")))
            continue
        flush_table()

        if s.startswith("@TITLE "):
            flush_para()
            flow.append(Paragraph(inline(s[7:]), st["title"]))
        elif s.startswith("@SUB "):
            flush_para()
            flow.append(Paragraph(inline(s[5:]), st["sub"]))
        elif s == "@RULE":
            flush_para()
            flow.extend([Spacer(1, 9), Hairline(width), Spacer(1, 12)])
        elif s.startswith("@PART "):
            flush_para()
            flow.append(PageBreak())
            flow.append(Paragraph(inline(s[6:]), st["part"]))
            flow.extend([Hairline(width), Spacer(1, 10)])
        elif s.startswith("@H "):
            flush_para()
            flow.append(Paragraph(inline(s[3:]), st["h"]))
        elif s.startswith("@SLIDE "):
            flush_para()
            num, title, block = [p.strip() for p in s[7:].split("|")]
            flow.append(CondPageBreak(1.1 * inch))
            flow.append(Paragraph(
                f"SLIDE {num} &nbsp; {inline(title)}"
                f'&nbsp;&nbsp;<font name="Body" size="8.5" color="#6B7280">'
                f"{block}</font>", st["slide"]))
        elif s.startswith("@F "):
            flush_para()
            label, _, rest = s[3:].partition(":")
            flow.append(Paragraph(
                f"<b>{inline(label)}</b>&nbsp; {inline(rest.strip())}",
                st["field"]))
        elif s.startswith("@FIG "):
            flush_para()
            rel = s[5:].strip()
            if rel in TO_GENERATE:
                declared.append(rel)
                flow.append(Paragraph(
                    f"{rel} &nbsp;&nbsp;[TO GENERATE]", st["fig"]))
            else:
                if not (ROOT / rel).exists():
                    missing.append(rel)
                flow.append(Paragraph(rel, st["fig"]))
        elif s.startswith("@BULLET "):
            flush_para()
            flow.append(Paragraph(inline(s[8:]), st["bullet"],
                                  bulletText="\u2022"))
        else:
            para.append(s)

    flush_para()
    flush_table()
    return flow, missing, declared


def decorate(canvas, doc):
    canvas.saveState()
    canvas.setFont("Body", 8)
    canvas.setFillColor(MUTED)
    if doc.page > 1:
        canvas.drawString(MARGIN_X, MARGIN_BOT * 0.55, DOC_TITLE)
    canvas.drawRightString(letter[0] - MARGIN_X, MARGIN_BOT * 0.55,
                           str(doc.page))
    canvas.restoreState()


def main() -> int:
    register_fonts()
    st = build_styles()
    width = letter[0] - 2 * MARGIN_X
    flow, missing, declared = parse(GUIDE, st, width)
    if missing:
        raise SystemExit("ERROR: figure paths do not resolve:\n  "
                         + "\n  ".join(missing))

    doc = BaseDocTemplate(
        str(OUT), pagesize=letter,
        leftMargin=MARGIN_X, rightMargin=MARGIN_X,
        topMargin=MARGIN_TOP, bottomMargin=MARGIN_BOT,
        title=DOC_TITLE, author="Nicko Fajardo")
    doc.addPageTemplates([PageTemplate(
        id="body",
        frames=[Frame(MARGIN_X, MARGIN_BOT, width,
                      letter[1] - MARGIN_TOP - MARGIN_BOT,
                      leftPadding=0, rightPadding=0,
                      topPadding=0, bottomPadding=0)],
        onPage=decorate)])
    doc.build(flow)
    print(f"wrote {OUT}")
    print(f"  {doc.page} pages, letter portrait")
    print("  all referenced figure paths resolve")
    for rel in declared:
        print(f"  still to generate: {rel}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
