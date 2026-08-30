# -*- coding: utf-8 -*-
r"""
make_discussion_sop_docx.py -- render DISCUSSION_SOP_ALIGNED.md as a Word document with real
tables and embedded figures.

The markdown file is the source of truth; this script only typesets it, so the
two can never drift. Re-run it after any edit to the markdown.

  * headings           -> Word heading styles
  * markdown tables    -> real Word tables (Table Grid, bold header row)
  * **Figure N** blocks -> APA layout: label, italic title, IMAGE, then the note
  * **Table N** blocks  -> APA layout: label, italic title, then the table
  * inline **bold**, *italic*, `code` are rendered as runs
  * body text is double-spaced Times New Roman 12 pt; tables are single-spaced

    python scripts/make_discussion_sop_docx.py

Writes DISCUSSION_SOP_ALIGNED.docx.  ASCII-only stdout.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.shared import Pt, Inches, RGBColor

SRC = ROOT / "DISCUSSION_SOP_ALIGNED.md"
OUT = ROOT / "DISCUSSION_SOP_ALIGNED.docx"

# Figure number -> image file, from the crosswalk at the top of the markdown.
FIGURES = {
    1: "figures/methodology/fig01_pipeline_revised.png",
    2: "figures/graph_real_Cis_ant.png",
    3: "figures/graph_synthetic.png",
    4: "figures/sigmoid.png",
    5: "figures/sigmoid_targeted.png",
    6: "figures/collapse_montage.png",
    7: "figures/sink_demo.png",
    8: "figures/cohort_pc_predictors.png",
    9: "figures/calibration_grid.png",
    10: "figures/cohort_suggested.png",
    11: "figures/methodology/fig_realsuggested_Met_dav.png",
    12: "figures/sink_surface.png",
    13: "figures/finite_size_fixedD.png",
    14: "figures/dynamics.png",
}

MAX_IMG_WIDTH_IN = 6.0
INK = RGBColor(0x20, 0x30, 0x3A)

# split a markdown table row on pipes that are not escaped as \|
CELL_SPLIT = re.compile(r"(?<!\\)\|")
INLINE = re.compile(r"(\*\*.+?\*\*|\*[^*]+?\*|`[^`]+?`)")


def add_runs(par, text: str, base_italic: bool = False):
    """Render inline **bold**, *italic* and `code` into runs."""
    text = text.replace(r"\|", "|").replace(r"\*", "*")
    for piece in INLINE.split(text):
        if not piece:
            continue
        if piece.startswith("**") and piece.endswith("**") and len(piece) > 4:
            r = par.add_run(piece[2:-2]); r.bold = True; r.italic = base_italic
        elif piece.startswith("*") and piece.endswith("*") and len(piece) > 2:
            r = par.add_run(piece[1:-1]); r.italic = True
        elif piece.startswith("`") and piece.endswith("`") and len(piece) > 2:
            r = par.add_run(piece[1:-1]); r.font.name = "Consolas"
            r.font.size = Pt(10)
        else:
            r = par.add_run(piece); r.italic = base_italic
    return par


def body(doc, text, *, italic=False, space_after=6, spacing=2.0, style=None):
    p = doc.add_paragraph(style=style)
    add_runs(p, text, base_italic=italic)
    pf = p.paragraph_format
    pf.space_after = Pt(space_after)
    pf.line_spacing = spacing
    return p


def is_table_line(s: str) -> bool:
    return s.lstrip().startswith("|") and s.rstrip().endswith("|")


def is_separator(cells) -> bool:
    return all(re.fullmatch(r":?-{2,}:?", c.strip()) for c in cells if c.strip())


def parse_row(line: str):
    parts = CELL_SPLIT.split(line.strip())
    if parts and not parts[0].strip():
        parts = parts[1:]
    if parts and not parts[-1].strip():
        parts = parts[:-1]
    return [c.strip() for c in parts]


def add_table(doc, rows):
    header, data = rows[0], rows[1:]
    t = doc.add_table(rows=len(rows), cols=len(header))
    t.style = "Table Grid"
    for j, cell in enumerate(header):
        par = t.rows[0].cells[j].paragraphs[0]
        add_runs(par, cell)
        for r in par.runs:
            r.bold = True
        par.paragraph_format.line_spacing = 1.0
        par.paragraph_format.space_after = Pt(0)
    for i, row in enumerate(data, start=1):
        for j in range(len(header)):
            par = t.rows[i].cells[j].paragraphs[0]
            add_runs(par, row[j] if j < len(row) else "")
            par.paragraph_format.line_spacing = 1.0
            par.paragraph_format.space_after = Pt(0)
    for row in t.rows:
        for cell in row.cells:
            for par in cell.paragraphs:
                for r in par.runs:
                    r.font.size = Pt(9)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)
    return t


def add_image(doc, fignum):
    rel = FIGURES.get(fignum)
    if not rel:
        return False
    path = ROOT / rel
    if not path.exists():
        p = doc.add_paragraph()
        r = p.add_run(f"[figure file not found: {rel}]")
        r.italic = True
        return False
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(6)
    p.add_run().add_picture(str(path), width=Inches(MAX_IMG_WIDTH_IN))
    return True


def main() -> None:
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass

    lines = SRC.read_text(encoding="utf-8").split("\n")
    doc = Document()

    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(12)

    i = 0
    pending_fig = None          # figure number awaiting its image
    n_tables = n_figs = n_imgs = 0
    in_code = False
    code_buf = []

    while i < len(lines):
        raw = lines[i]
        line = raw.rstrip()
        stripped = line.strip()

        # ---- fenced code ---------------------------------------------------
        if stripped.startswith("```"):
            if in_code:
                p = doc.add_paragraph()
                r = p.add_run("\n".join(code_buf))
                r.font.name = "Consolas"; r.font.size = Pt(9)
                p.paragraph_format.line_spacing = 1.0
                code_buf, in_code = [], False
            else:
                in_code = True
            i += 1
            continue
        if in_code:
            code_buf.append(raw)
            i += 1
            continue

        # ---- blank ---------------------------------------------------------
        if not stripped:
            i += 1
            continue

        # ---- horizontal rule ----------------------------------------------
        if re.fullmatch(r"-{3,}", stripped):
            if i + 1 < len(lines) and re.fullmatch(r"-{3,}", lines[i + 1].strip()):
                doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
                i += 2
                continue
            i += 1
            continue

        # ---- headings ------------------------------------------------------
        m = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if m:
            level = min(len(m.group(1)), 4)
            h = doc.add_heading(level=level)
            add_runs(h, m.group(2))
            for r in h.runs:
                r.font.color.rgb = INK
            i += 1
            continue

        # ---- tables --------------------------------------------------------
        if is_table_line(line):
            block = []
            while i < len(lines) and is_table_line(lines[i]):
                block.append(parse_row(lines[i]))
                i += 1
            block = [r for r in block if not is_separator(r)]
            if block:
                add_table(doc, block)
                n_tables += 1
            continue

        # ---- Table / Figure caption labels ---------------------------------
        cap = re.fullmatch(r"\*\*(Table|Figure) (\d+)\*\*(.*)", stripped)
        if cap:
            kind, num, tail = cap.group(1), int(cap.group(2)), cap.group(3)
            p = doc.add_paragraph()
            r = p.add_run(f"{kind} {num}")
            r.bold = True
            if tail.strip():
                add_runs(p, " " + tail.strip())
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.0
            # The italic caption title follows, and may wrap over several
            # source lines; consume the whole block up to the blank line so the
            # title is not split around the image.
            if i + 1 < len(lines) and lines[i + 1].strip().startswith("*"):
                title, k = [], i + 1
                while k < len(lines) and lines[k].strip():
                    title.append(lines[k].strip())
                    k += 1
                t = doc.add_paragraph()
                add_runs(t, " ".join(title))
                t.paragraph_format.space_after = Pt(6)
                t.paragraph_format.line_spacing = 1.0
                i = k - 1
            if kind == "Figure":
                n_figs += 1
                if add_image(doc, num):
                    n_imgs += 1
            i += 1
            continue

        # ---- bullets and numbered lists -------------------------------------
        b = re.match(r"^[-*]\s+(.*)$", stripped)
        if b:
            body(doc, b.group(1), spacing=1.15, space_after=3,
                 style="List Bullet")
            i += 1
            continue
        nb = re.match(r"^(\d+)\.\s+(.*)$", stripped)
        if nb:
            body(doc, nb.group(2), spacing=1.15, space_after=3,
                 style="List Number")
            i += 1
            continue

        # ---- blockquote ------------------------------------------------------
        if stripped.startswith(">"):
            q = body(doc, stripped.lstrip("> ").strip(), spacing=1.15,
                     space_after=4)
            q.paragraph_format.left_indent = Inches(0.4)
            i += 1
            continue

        # ---- ordinary paragraph, joining wrapped lines ----------------------
        para = [stripped]
        i += 1
        while i < len(lines):
            nxt = lines[i].strip()
            if (not nxt or is_table_line(lines[i]) or nxt.startswith("#")
                    or nxt.startswith(">") or nxt.startswith("```")
                    or re.fullmatch(r"-{3,}", nxt)
                    or re.match(r"^\*\*(Table|Figure) \d+\*\*", nxt)
                    or re.match(r"^[-*]\s+", nxt) or re.match(r"^\d+\.\s+", nxt)):
                break
            para.append(nxt)
            i += 1
        text = " ".join(para)
        is_note = text.startswith("*Note.*")
        body(doc, text, spacing=1.0 if is_note else 2.0,
             space_after=10 if is_note else 6)

    target = OUT
    try:
        doc.save(target)
    except PermissionError:
        # the document is open in Word; write beside it rather than failing
        target = OUT.with_name(OUT.stem + "_NEW" + OUT.suffix)
        doc.save(target)
        print("NOTE: %s is locked (open in Word?), so this run wrote %s instead."
              % (OUT.name, target.name))
        print("      Close the document and re-run to overwrite the original.")
    print("wrote %s" % target.name)
    print("  tables rendered : %d" % n_tables)
    print("  figure captions : %d" % n_figs)
    print("  images embedded : %d" % n_imgs)
    missing = [n for n in sorted(FIGURES) if not (ROOT / FIGURES[n]).exists()]
    if missing:
        print("  MISSING IMAGE FILES for figures: %s" % missing)


if __name__ == "__main__":
    main()
