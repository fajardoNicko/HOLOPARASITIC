# -*- coding: utf-8 -*-
r"""
local_window_boxes.py -- places one same-size window on every stitched local leaf and prints the
crop numbers to type into LeafVeinCNN (Crop panel: Top, Left, Width, Height).

For each LOCAL VALIDATION\<Leaf>_cleaned\<Leaf>_stitched.png it

  1. finds the leaf piece: leaf tissue is textured (cells, veins), while the background past the cut
     edges and the empty corners are smooth. It thresholds the local standard deviation of the
     green channel (Otsu), keeps the largest region and fills its holes;
  2. moves MARGIN_MM in from every edge of the piece, because the blade crushes the tissue next to a cut;
  3. finds the largest axis-aligned square inside what is left.

The common window side W is the smallest of those squares over the four flowering species, rounded
down to 0.1 mm, so every leaf is measured over exactly the same area. Each leaf's W x W square is
placed as centrally as possible inside its piece.

The fern (any folder whose name starts with "Fern") is a strip across the whole pinna. Its long sides
are the pinna's own margins, not cuts, so its window spans the full width, edge to edge, and is cut
to the length that gives the same area, W x W.

Writes window.json and window_preview.png into each folder.

    C:\laragon\bin\python\python-3.13\python.exe scripts\local_window_boxes.py
"""
import glob
import json
import os

import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LV = os.path.join(ROOT, "LOCAL VALIDATION")
PX_PER_MM = 626.0
MARGIN_MM = 0.5
F = 8                       # work at 1/8 size


def leaf_mask(img):
    small = cv2.resize(img, (img.shape[1] // F, img.shape[0] // F), interpolation=cv2.INTER_AREA)
    g = small[..., 1].astype(np.float32)
    c = (small.max(axis=2) > 0).astype(np.float32)
    covered = cv2.erode(c, np.ones((7, 7), np.uint8)) > 0          # stay off the black, unphotographed corners
    k = (9, 9)                                                      # local texture, ignoring black pixels
    nrm = cv2.blur(c, k) + 1e-6
    mean = cv2.blur(g * c, k) / nrm
    sd = np.sqrt(np.maximum(cv2.blur(g * g * c, k) / nrm - mean * mean, 0)) * covered
    reg = cv2.blur(sd, (21, 21)) / (cv2.blur(covered.astype(np.float32), (21, 21)) + 1e-6)   # regional texture level
    # tissue absorbs red light; past the cut edges the light comes straight through, so the smoothed red
    # channel (veins blurred away) is much brighter there
    red = cv2.medianBlur(small[..., 2], 15).astype(np.float32)
    med, hi = np.percentile(red[covered], 50), np.percentile(red[covered], 97)
    dark_enough = red < med + 0.5 * (hi - med)
    textured = reg > 0.35 * np.median(reg[covered & dark_enough])    # rules out dark but smooth vignetted corners
    m = (dark_enough & textured & covered).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(m)
    k = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    m = (lab == k).astype(np.uint8)
    cnts, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    filled = np.zeros_like(m)
    cv2.drawContours(filled, cnts, -1, 1, -1)
    return filled & covered.astype(np.uint8)


def largest_square(valid):
    lo, hi, best = 1, min(valid.shape), None
    while lo <= hi:
        L = (lo + hi) // 2
        er = cv2.erode(valid, np.ones((L, L), np.uint8), anchor=(0, 0), borderType=cv2.BORDER_CONSTANT, borderValue=0)
        if er.any():
            best = L; lo = L + 1
        else:
            hi = L - 1
    return best


def place_square(valid, L):
    er = cv2.erode(valid, np.ones((L, L), np.uint8), anchor=(0, 0), borderType=cv2.BORDER_CONSTANT, borderValue=0)
    ys, xs = np.nonzero(er)
    if not len(ys):
        return None
    cy, cx = np.mean(ys), np.mean(xs)
    j = int(np.argmin((ys - cy) ** 2 + (xs - cx) ** 2))
    return int(xs[j]), int(ys[j])


def main():
    leaves = []
    for d in sorted(glob.glob(os.path.join(LV, "*_cleaned"))):
        leaf = os.path.basename(d)[:-len("_cleaned")]
        p = os.path.join(d, leaf + "_stitched.png")
        if os.path.exists(p):
            leaves.append((leaf, d, p))
    margin = int(round(MARGIN_MM * PX_PER_MM / F))
    info = {}
    for leaf, d, p in leaves:
        img = cv2.imread(p)
        m = leaf_mask(img)
        inner = cv2.erode(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * margin + 1, 2 * margin + 1)))
        info[leaf] = dict(dir=d, img=img, mask=m, inner=inner, sq=largest_square(inner))
        print("%-9s piece %.1f mm^2, largest square %.2f mm (after %.1f mm margin)"
              % (leaf, m.sum() * (F / PX_PER_MM) ** 2, info[leaf]["sq"] * F / PX_PER_MM, MARGIN_MM))
    dicots = [l for l in info if not l.lower().startswith("fern")]
    L = min(info[l]["sq"] for l in dicots)
    W_mm = np.floor(L * F / PX_PER_MM * 10) / 10
    L = int(W_mm * PX_PER_MM / F)
    side_px = int(round(W_mm * PX_PER_MM))
    print("\ncommon window: %.1f x %.1f mm = %d x %d px (%.1f mm^2)" % (W_mm, W_mm, side_px, side_px, W_mm ** 2))
    for leaf, v in info.items():
        img, inner, m = v["img"], v["inner"], v["mask"]
        if leaf.lower().startswith("fern"):
            # strip: full width between the pinna margins, length chosen for the same area
            cols = m.sum(0)
            xs = np.nonzero(cols > 0.5 * cols.max())[0]
            x_lo, x_hi = xs.min() + margin, xs.max() - margin          # stay off the two cut ends
            mid = (x_lo + x_hi) / 2
            width_px = np.median(cols[x_lo:x_hi]) * F
            length_px = int(round(W_mm ** 2 * PX_PER_MM ** 2 / width_px))
            x0 = int(round(mid * F - length_px / 2))
            rows = np.nonzero(m[:, x0 // F:(x0 + length_px) // F].any(1))[0]
            y0, y1 = rows.min() * F, (rows.max() + 1) * F
            box = dict(left=x0, top=int(y0), width=length_px, height=int(y1 - y0))
            note = "strip: full width %.2f mm (margin to margin) x length %.2f mm" % (width_px / PX_PER_MM,
                                                                                    length_px / PX_PER_MM)
        else:
            xy = place_square(inner, L)
            box = dict(left=xy[0] * F, top=xy[1] * F, width=side_px, height=side_px)
            note = "square %.1f x %.1f mm" % (W_mm, W_mm)
        box["mm"] = [round(box["width"] / PX_PER_MM, 2), round(box["height"] / PX_PER_MM, 2)]
        leaf_frac = float(m[box["top"] // F:(box["top"] + box["height"]) // F,
                            box["left"] // F:(box["left"] + box["width"]) // F].mean())
        json.dump(dict(leaf=leaf, px_per_mm=PX_PER_MM, margin_mm=MARGIN_MM, window_side_mm=W_mm, note=note,
                       leafvein_crop=dict(Top=box["top"], Left=box["left"], Width=box["width"], Height=box["height"]),
                       leaf_fraction_in_box=round(leaf_frac, 3)),
                  open(os.path.join(v["dir"], "window.json"), "w"), indent=1)
        prev = cv2.resize(img, (img.shape[1] // 4, img.shape[0] // 4), interpolation=cv2.INTER_AREA)
        cnts, _ = cv2.findContours(cv2.resize(m, (prev.shape[1], prev.shape[0]), interpolation=cv2.INTER_NEAREST),
                                   cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        cv2.drawContours(prev, cnts, -1, (255, 255, 0), 2)
        cv2.rectangle(prev, (box["left"] // 4, box["top"] // 4),
                      ((box["left"] + box["width"]) // 4, (box["top"] + box["height"]) // 4), (0, 0, 255), 4)
        # mask for LeafVeinCNN (white = analyse, black = leave out): the leaf piece, minus spots that are not
        # veins but would look like them: brown lesions (any species) and the dark spore clusters (fern)
        small = cv2.resize(img, (img.shape[1] // F, img.shape[0] // F), interpolation=cv2.INTER_AREA).astype(np.float32)
        b, g, r = [cv2.blur(small[..., i], (5, 5)) for i in range(3)]
        inside = m > 0
        if leaf.lower().startswith("fern"):
            # spore clusters: large, very dark blobs (the fern's midvein is brown, so no brown test here)
            rs = cv2.medianBlur(small[..., 2].astype(np.uint8), 9).astype(np.float32)
            sori = (rs < 0.45 * np.median(rs[inside])) & inside    # 0.45: the midvein (min ~0.46) stays in
            dmg = cv2.morphologyEx(sori.astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
            n_, lab_, st_, _ = cv2.connectedComponentsWithStats(dmg)
            for i_ in range(1, n_):                                 # drop specks smaller than ~0.2 mm across
                if st_[i_, cv2.CC_STAT_AREA] < 30:
                    dmg[lab_ == i_] = 0
            grow_mm = 0.3                                           # ragged rim of each cluster
        else:
            # brown lesion cores only, with a thin rim, so veins running past a spot are not cut
            brown = (r > 0.85 * g) & (g < np.median(g[inside])) & inside
            dmg = cv2.morphologyEx(brown.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
            grow_mm = 0.1
        grow = int(round(grow_mm * PX_PER_MM / F))
        dmg = cv2.dilate(dmg, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * grow + 1, 2 * grow + 1)))
        keep = ((m > 0) & (dmg == 0)).astype(np.uint8) * 255
        keep_full = cv2.resize(keep, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_NEAREST)
        box_area = keep[box["top"] // F:(box["top"] + box["height"]) // F, box["left"] // F:(box["left"] + box["width"]) // F]
        masked_pct = 100 * float((box_area == 0).mean())
        for fin in glob.glob(os.path.join(v["dir"], "*final*.png")):
            if not fin.endswith("_mask.png"):
                cv2.imwrite(fin[:-4] + "_mask.png", keep_full)
        dm = cv2.resize(dmg, (prev.shape[1], prev.shape[0]), interpolation=cv2.INTER_NEAREST)
        cnts, _ = cv2.findContours(dm, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        cv2.drawContours(prev, cnts, -1, (255, 0, 255), 3)
        print("%-9s masked out inside the window: %.1f%%" % (leaf, masked_pct))
        cv2.imwrite(os.path.join(v["dir"], "window_preview.png"), prev)
        print("%-9s %-55s Top %5d  Left %5d  Width %5d  Height %5d   (leaf in box %.0f%%)"
              % (leaf, note, box["top"], box["left"], box["width"], box["height"], 100 * leaf_frac))


if __name__ == "__main__":
    main()
