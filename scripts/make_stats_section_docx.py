"""Render the Statistical Analysis rewrite as a paste-ready Word document.

Reads STATISTICAL_ANALYSIS_REWRITE.md (everything from '## Statistical Analysis'
onward) and lays it out in the manuscript's style: Times New Roman 12, double
spaced, 0.5" first-line indent on body text, centred italic formulas, and an
indented 'where' block after each formula.
"""

import re
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_LINE_SPACING, WD_ALIGN_PARAGRAPH

SRC = r"c:\Users\Nicko\HOLOPARASITIC\STATISTICAL_ANALYSIS_REWRITE.md"
OUT = r"c:\Users\Nicko\HOLOPARASITIC\STATISTICAL_ANALYSIS_REWRITE.docx"


def para(doc, text, *, bold=False, italic=False, align=None,
         first_line=0.0, left=0.0, size=12, spacing=WD_LINE_SPACING.DOUBLE):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.line_spacing_rule = spacing
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.left_indent = Inches(left)
    pf.first_line_indent = Inches(first_line)
    if align is not None:
        p.alignment = align
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    return p


def main():
    body = open(SRC, encoding="utf-8").read()
    body = body[body.index("## Statistical Analysis"):]
    lines = body.splitlines()

    doc = Document()
    doc.styles["Normal"].font.name = "Times New Roman"
    doc.styles["Normal"].font.size = Pt(12)
    for s in doc.sections:
        s.top_margin = s.bottom_margin = s.left_margin = s.right_margin = Inches(1)

    i, in_formula = 0, False
    while i < len(lines):
        raw = lines[i]
        line = raw.strip()

        if line.startswith("```"):
            in_formula = not in_formula
            i += 1
            continue

        if in_formula:
            if line:
                para(doc, line, italic=True,
                     align=WD_ALIGN_PARAGRAPH.CENTER,
                     spacing=WD_LINE_SPACING.SINGLE)
            else:
                para(doc, "", spacing=WD_LINE_SPACING.SINGLE)
            i += 1
            continue

        if line.startswith("## "):
            para(doc, line[3:], bold=True)
        elif line.startswith("### "):
            para(doc, "", spacing=WD_LINE_SPACING.SINGLE)
            para(doc, line[4:], bold=True)
        elif line == "where":
            para(doc, "where", left=0.5, spacing=WD_LINE_SPACING.SINGLE)
        elif raw.startswith("    ") and line:
            # variable definition inside a 'where' block
            para(doc, re.sub(r"\s{2,}", "  ", line), left=1.0, size=11,
                 spacing=WD_LINE_SPACING.SINGLE)
        elif line:
            # body paragraph: join wrapped lines until a blank line
            buf = [line]
            while i + 1 < len(lines) and lines[i + 1].strip() and \
                    not lines[i + 1].startswith(("#", "```", "    ")):
                i += 1
                buf.append(lines[i].strip())
            para(doc, " ".join(buf), first_line=0.5,
                 align=WD_ALIGN_PARAGRAPH.JUSTIFY)
        else:
            para(doc, "", spacing=WD_LINE_SPACING.SINGLE)
        i += 1

    doc.save(OUT)
    print(f"wrote {OUT} ({len(doc.paragraphs)} paragraphs)")


if __name__ == "__main__":
    main()
