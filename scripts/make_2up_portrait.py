# -*- coding: utf-8 -*-
r"""
make_2up_portrait.py -- impose several portrait pages onto one portrait sheet.

Ordinary "2 pages per sheet" printing rotates the sheet to landscape and puts
the pages side by side. This keeps the sheet portrait and stacks them instead:
source page 1 shrunk into the top half, page 2 into the bottom half, page 3
onto the top of the next sheet, and so on.

    C:\laragon\bin\python\python-3.13\python.exe scripts\make_2up_portrait.py IN.pdf

    ... IN.pdf -o OUT.pdf      write somewhere other than IN_2up.pdf
    ... IN.pdf --sheet short   impose onto 8.5 x 11 (default: the source page size)
    ... IN.pdf --grid 2x2      four per sheet instead of two, filled left to right
    ... IN.pdf --title "Appendix G" --title "RAW DATA"   heading atop sheet 1
    ... IN.pdf --no-trim       keep the source margins instead of cropping them
    ... IN.pdf --no-rule       omit the hairlines between the slots

Readability comes from the crop. A page shrunk to half height can only ever be
50% of its original size, which turns 12 pt text into 6 pt. Cropping the white
margins off first means only the inked area has to fit, so the same text lands
nearer 55%. The crop box is the union of every page's content, so the scale is
identical on every sheet and the type does not change size part-way through.

Whether a taller grid costs anything depends on which way the slot is pinched.
A tall narrow source page dropped into a 1x2 grid is limited by slot height and
leaves half the sheet width empty, so going to 2x2 -- which only halves the slot
width -- often prints at exactly the same scale on half as many sheets. The
summary printed at the end reports the scale, so the two can be compared.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pymupdf

MARGIN = 20.0   # blank border around the whole sheet, points
GUTTER = 12.0   # blank strip between neighbouring slots, points
PAD = 6.0       # slack left around the cropped content, points
RULE_GRAY = 0.78
RULE_WIDTH = 0.5
TITLE_FONT = "tibo"    # Times-Bold, matching the appendix heading in the manuscript
TITLE_SIZE = 12.0      # manuscript body size, as the appendix heading is set
TITLE_LEADING = 24.0   # baseline to baseline: double spaced at 12 pt
TITLE_GAP = 14.0       # blank strip under the heading, before the first row


def content_box(doc: pymupdf.Document) -> pymupdf.Rect:
    """Union of the inked area of every page, ignoring full-page backgrounds."""
    page_rect = doc[0].rect
    box = pymupdf.Rect(1e9, 1e9, -1e9, -1e9)
    for page in doc:
        for block in page.get_text("blocks"):
            box |= pymupdf.Rect(block[:4])
        for drawing in page.get_drawings():
            rect = drawing["rect"]
            # A white sheet-sized fill is the exported background, not content.
            if rect.width >= page_rect.width - 1 and rect.height >= page_rect.height - 1:
                continue
            box |= rect
    if box.is_empty or box.x1 < box.x0:
        return pymupdf.Rect(page_rect)
    box = pymupdf.Rect(box.x0 - PAD, box.y0 - PAD, box.x1 + PAD, box.y1 + PAD)
    return box & page_rect


SHEETS = {                    # width x height in inches, portrait
    "short": (8.5, 11.0),     # short bond / US Letter
    "letter": (8.5, 11.0),
    "long": (8.5, 13.0),      # long bond / folio
    "folio": (8.5, 13.0),
    "legal": (8.5, 14.0),
    "a4": (8.27, 11.69),
}


def sheet_size(name: str | None, src: pymupdf.Document) -> pymupdf.Rect:
    """Named sheet, an explicit WxH in inches, or the source page size."""
    if name is None:
        return pymupdf.Rect(src[0].rect)
    key = name.strip().lower()
    if key in SHEETS:
        w, h = SHEETS[key]
    elif "x" in key:
        try:
            w, h = (float(v) for v in key.split("x", 1))
        except ValueError:
            raise SystemExit(f"cannot read sheet size {name!r}; try 8.5x11")
    else:
        raise SystemExit(f"unknown sheet {name!r}; use {', '.join(SHEETS)} or WxH in inches")
    return pymupdf.Rect(0, 0, w * 72, h * 72)


def parse_grid(spec: str) -> tuple[int, int]:
    """COLSxROWS, e.g. 1x2 for two stacked or 2x2 for four to a sheet."""
    try:
        cols, rows = (int(v) for v in spec.strip().lower().split("x", 1))
    except ValueError:
        raise SystemExit(f"cannot read grid {spec!r}; try 1x2 or 2x2")
    if cols < 1 or rows < 1:
        raise SystemExit(f"grid {spec!r} must be at least 1x1")
    return cols, rows


def title_band(lines: list[str] | None) -> float:
    """Height the heading needs at the top of the sheet, gap to the grid included."""
    if not lines:
        return 0.0
    return TITLE_SIZE + TITLE_LEADING * (len(lines) - 1) + TITLE_GAP


def draw_title(page: pymupdf.Page, sheet: pymupdf.Rect, lines: list[str]) -> None:
    """The heading lines, each centred across the sheet, stacked at the top."""
    baseline = MARGIN + TITLE_SIZE
    for line in lines:
        width = pymupdf.get_text_length(line, fontname=TITLE_FONT, fontsize=TITLE_SIZE)
        page.insert_text(
            pymupdf.Point((sheet.width - width) / 2, baseline),
            line, fontname=TITLE_FONT, fontsize=TITLE_SIZE,
        )
        baseline += TITLE_LEADING


class Layout:
    """Where the slots sit on a sheet, given a strip reserved at the top."""

    def __init__(self, sheet: pymupdf.Rect, clip: pymupdf.Rect,
                 cols: int, rows: int, top_inset: float) -> None:
        self.cols, self.rows, self.top = cols, rows, MARGIN + top_inset
        self.slot_w = (sheet.width - 2 * MARGIN - GUTTER * (cols - 1)) / cols
        self.slot_h = (sheet.height - MARGIN - self.top - GUTTER * (rows - 1)) / rows
        if self.slot_w <= 0 or self.slot_h <= 0:
            raise SystemExit(
                f"{cols}x{rows} leaves no room on a "
                f"{sheet.width / 72:.2f} x {sheet.height / 72:.2f} in sheet"
            )
        self.scale = min(self.slot_w / clip.width, self.slot_h / clip.height)
        self.draw_w = clip.width * self.scale
        self.draw_h = clip.height * self.scale

    def slot_rect(self, col: int, row: int) -> pymupdf.Rect:
        # Each page is centred in its own cell, so the columns line up down the
        # sheet and the blank space falls evenly around the block of type.
        x = MARGIN + col * (self.slot_w + GUTTER) + (self.slot_w - self.draw_w) / 2
        y = self.top + row * (self.slot_h + GUTTER) + (self.slot_h - self.draw_h) / 2
        return pymupdf.Rect(x, y, x + self.draw_w, y + self.draw_h)


def build(
    src_path: Path, out_path: Path, trim: bool, rule: bool,
    sheet_name: str | None, grid: tuple[int, int], title: list[str] | None = None,
) -> None:
    src = pymupdf.open(src_path)
    if src.page_count == 0:
        raise SystemExit(f"{src_path} has no pages")

    cols, rows = grid
    per_sheet = cols * rows
    sheet = sheet_size(sheet_name, src)
    clip = content_box(src) if trim else pymupdf.Rect(src[0].rect)

    # The heading opens the appendix, so only the first sheet gives up room to
    # it. Every sheet after it keeps the full height, and so the larger type.
    plain = Layout(sheet, clip, cols, rows, 0.0)
    first_layout = Layout(sheet, clip, cols, rows, title_band(title))

    n_pages = src.page_count
    out = pymupdf.open()
    for first in range(0, n_pages, per_sheet):
        page = out.new_page(width=sheet.width, height=sheet.height)
        lay = first_layout if (first == 0 and title) else plain
        if first == 0 and title:
            draw_title(page, sheet, title)
        placed = min(per_sheet, n_pages - first)
        for slot in range(placed):
            # Row-major, so the sheet is read left to right then down.
            target = lay.slot_rect(slot % cols, slot // cols)
            page.show_pdf_page(target, src, first + slot, clip=clip)
        if rule:
            draw_rules(page, sheet, lay, placed)

    out.save(out_path, garbage=4, deflate=True)
    out.close()
    src.close()

    print(f"wrote {out_path}")
    print(f"  {n_pages} source pages -> {-(-n_pages // per_sheet)} sheets"
          f" at {cols}x{rows} ({per_sheet} per sheet)")
    print(f"  sheet {sheet.width / 72:.2f} x {sheet.height / 72:.2f} in (portrait)")
    print(f"  crop  {clip.width / 72:.2f} x {clip.height / 72:.2f} in of the source page")
    print(f"  scale {plain.scale * 100:.1f}%"
          f"  (12 pt source text prints at {12 * plain.scale:.1f} pt)")
    if title:
        print(f"  sheet 1 carries the heading, so its four pages sit at"
              f" {first_layout.scale * 100:.1f}% ({12 * first_layout.scale:.1f} pt)")


def draw_rules(page: pymupdf.Page, sheet: pymupdf.Rect, lay: Layout, placed: int) -> None:
    """Hairlines in the gutters, drawn only where both neighbours hold a page."""
    cols, rows = lay.cols, lay.rows
    filled = {(slot % cols, slot // cols) for slot in range(placed)}
    gray = (RULE_GRAY,) * 3
    for row in range(1, rows):
        if not any((c, row) in filled for c in range(cols)):
            continue
        y = lay.top + row * (lay.slot_h + GUTTER) - GUTTER / 2
        page.draw_line(
            pymupdf.Point(MARGIN, y), pymupdf.Point(sheet.width - MARGIN, y),
            color=gray, width=RULE_WIDTH,
        )
    for col in range(1, cols):
        x = MARGIN + col * (lay.slot_w + GUTTER) - GUTTER / 2
        for row in range(rows):
            if (col - 1, row) not in filled or (col, row) not in filled:
                continue
            top = lay.top + row * (lay.slot_h + GUTTER)
            page.draw_line(
                pymupdf.Point(x, top), pymupdf.Point(x, top + lay.slot_h),
                color=gray, width=RULE_WIDTH,
            )


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("pdf", type=Path)
    ap.add_argument("-o", "--out", type=Path)
    ap.add_argument("--no-trim", action="store_true", help="keep the source margins")
    ap.add_argument("--no-rule", action="store_true", help="omit the gutter hairlines")
    ap.add_argument(
        "--sheet",
        help=f"output sheet: {', '.join(SHEETS)}, or WxH in inches (default: the source page size)",
    )
    ap.add_argument(
        "--grid", default="1x2",
        help="slots per sheet as COLSxROWS (default 1x2; 2x2 puts four to a sheet)",
    )
    ap.add_argument(
        "--title", action="append", metavar="LINE",
        help="centred heading at the top of the first sheet; repeat for each line",
    )
    args = ap.parse_args(argv)

    if not args.pdf.exists():
        raise SystemExit(f"missing: {args.pdf}")
    grid = parse_grid(args.grid)
    default_name = f"{args.pdf.stem}_{grid[0] * grid[1]}up.pdf"
    out = args.out or args.pdf.with_name(default_name)
    build(
        args.pdf, out, trim=not args.no_trim, rule=not args.no_rule,
        sheet_name=args.sheet, grid=grid, title=args.title,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
