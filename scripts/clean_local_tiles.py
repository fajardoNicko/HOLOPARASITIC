# -*- coding: utf-8 -*-
r"""
clean_local_tiles.py -- prepares one leaf window's hand-held microscope photos for
stitching in Fiji.

The photos are taken with a phone held over the trinocular eyepiece (4x objective), so
every photo has the field of view as a bright circle somewhere in the frame. Each photo
also has its own small rotation (some were taken with the phone sideways), its own
exposure, and a slightly different magnification, because the phone refocuses each time.
For every photo the script

  1. finds the field-of-view circle (Hough transform, then a least-squares fit to the
     edge points);
  2. flattens the uneven lighting (bright centre, dark rim) by dividing each colour
     channel by a smooth surface fitted to the leaf pixels. This also matches brightness
     and colour across photos;
  3. finds the leaf features each photo shares with every photo it overlaps
     (SIFT + RANSAC). It then fits, over all photos at once, one rotation, one
     magnification and one position per photo, plus one lens-distortion term shared by
     all photos (least squares, robust loss);
  4. corrects the distortion, brings every photo to one magnification and one
     orientation, crops the square inside the circle and saves it as a lossless PNG.
     The orientation is the real slide's: the microscope view turned 180 degrees;
  5. writes TileConfiguration.txt for Fiji (Plugins > Stitching > Grid/Collection
     stitching > "Positions from file"), a preview mosaic and a report.

Nothing is drawn, removed, sharpened or contrast-stretched locally. The only changes are
the smooth lighting correction, a smooth geometric correction (rotation, magnification,
lens distortion) and cropping.

    C:\laragon\bin\python\python-3.13\python.exe scripts\clean_local_tiles.py ^
        "LOCAL VALIDATION\Talisay-20261110T023026Z-1-001\Talisay" "LOCAL VALIDATION\Talisay_cleaned"
"""
import argparse
import glob
import json
import os
import pickle
import re

import cv2
import numpy as np
from scipy.optimize import least_squares
from scipy.sparse import lil_matrix

PX_PER_MM = 626.0          # from the 2026-11-10 ruler photo (blurry, about +/-5%)
SQUARE_FRACTION = 0.95     # crop square half-diagonal = this x the smallest circle radius
MAX_PTS_PER_PAIR = 400     # matches per overlapping pair used in the joint fit
SCALE_PRIOR_PX = 100.0     # weak prior on each photo's log-magnification (px of misfit per unit)


def rot(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, -s], [s, c]])


def wrap(a):
    return (a + np.pi) % (2 * np.pi) - np.pi


def kasa(p):
    x, y = p[:, 0], p[:, 1]
    A = np.c_[2 * x, 2 * y, np.ones_like(x)]
    sol = np.linalg.lstsq(A, x * x + y * y, rcond=None)[0]
    cx, cy = sol[0], sol[1]
    return cx, cy, np.sqrt(sol[2] + cx * cx + cy * cy)


def small_v(img, f=4):
    small = cv2.resize(img, (img.shape[1] // f, img.shape[0] // f), interpolation=cv2.INTER_AREA)
    return cv2.GaussianBlur(small.max(axis=2), (0, 0), 1.5)


def rough_radius(img, f=4):
    v = small_v(img, f)
    _, m = cv2.threshold(v, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (21, 21)))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(m)
    k = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    return np.sqrt(stats[k, cv2.CC_STAT_AREA] / np.pi) * f


def find_circle(img, r_guess, f=4):
    """Centre and radius (full-resolution px) of the field-of-view circle."""
    v = small_v(img, f)
    cs = cv2.HoughCircles(v, cv2.HOUGH_GRADIENT, dp=1, minDist=10000, param1=60, param2=20,
                          minRadius=int(0.85 * r_guess / f), maxRadius=int(1.15 * r_guess / f))
    cx, cy, r = cs[0][0]
    e = cv2.Canny(v, 30, 60)
    ys, xs = np.nonzero(e)
    for tol in (4.0, 2.5):
        d = np.hypot(xs - cx, ys - cy) - r
        k = np.abs(d) < tol
        cx, cy, r = kasa(np.c_[xs[k], ys[k]].astype(float))
    return (cx + 0.5) * f - 0.5, (cy + 0.5) * f - 0.5, r * f


def flat_field_model(img, cx, cy, R):
    """Smooth log-brightness surface per channel, fitted to leaf pixels at 1/4 size."""
    f = 4
    h, w = img.shape[:2]
    small = cv2.resize(img, (w // f, h // f), interpolation=cv2.INTER_AREA).astype(np.float32)
    ys, xs = np.mgrid[0:h // f, 0:w // f].astype(np.float32)
    X = ((xs + 0.5) * f - 0.5 - cx) / R
    Y = ((ys + 0.5) * f - 0.5 - cy) / R
    white = (small.min(axis=2) > 170) & (small.max(axis=2) - small.min(axis=2) < 45)
    mask = (np.hypot(X, Y) < 0.93) & ~white & (small.max(axis=2) > 25)

    def terms(X, Y):
        return np.stack([np.ones_like(X), X, Y, X * X, Y * Y, X * Y, (X * X + Y * Y) ** 2], -1)

    Phi = terms(X[mask], Y[mask])
    full = terms(X, Y)
    surf, b0 = [], []
    for ch in range(3):
        z = np.log(small[..., ch][mask] + 1.0)
        keep = np.ones(len(z), bool)
        for _ in range(3):
            beta = np.linalg.lstsq(Phi[keep], z[keep], rcond=None)[0]
            res = z - Phi @ beta
            s = 1.4826 * np.median(np.abs(res[keep] - np.median(res[keep])))
            keep = np.abs(res) < 2.5 * s
        surf.append(full @ beta - beta[0])          # relative surface, 0 at the circle centre
        b0.append(beta[0])
    return np.stack(surf, -1).astype(np.float32), np.exp(np.array(b0)) - 1.0   # surface at 1/4 size


def match_all(flat, circ, min_inliers):
    sift = cv2.SIFT_create(nfeatures=6000)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    feats = []
    for fl, (cx, cy, R) in zip(flat, circ):
        g = clahe.apply(cv2.resize(fl[..., 1], (fl.shape[1] // 2, fl.shape[0] // 2), interpolation=cv2.INTER_AREA))
        mask = np.zeros(g.shape, np.uint8)
        cv2.circle(mask, (int(round((cx + 0.5) / 2 - 0.5)), int(round((cy + 0.5) / 2 - 0.5))),
                   int(0.92 * R / 2), 255, -1)
        kp, des = sift.detectAndCompute(g, mask)
        pts = np.array([k.pt for k in kp], np.float64) * 2 + 0.5 - np.array([cx, cy])
        feats.append((pts, des.astype(np.float32)))
    flann = cv2.FlannBasedMatcher(dict(algorithm=1, trees=5), dict(checks=64))
    edges = []
    n = len(flat)
    for i in range(n):
        for j in range(i + 1, n):
            pi, di = feats[i]; pj, dj = feats[j]
            mm = [m for m, m2 in (x for x in flann.knnMatch(dj, di, k=2) if len(x) == 2)
                  if m.distance < 0.75 * m2.distance]
            if len(mm) < min_inliers:
                continue
            src = pj[[m.queryIdx for m in mm]]; dst = pi[[m.trainIdx for m in mm]]
            M, inl = cv2.estimateAffinePartial2D(src, dst, method=cv2.RANSAC, ransacReprojThreshold=10.0,
                                                 maxIters=10000, confidence=0.999)
            if M is None:
                continue
            inl = inl.ravel().astype(bool)
            scale = float(np.hypot(M[0, 0], M[1, 0]))
            if inl.sum() >= min_inliers and 0.92 < scale < 1.08:
                edges.append(dict(i=i, j=j, phi=float(np.arctan2(M[1, 0], M[0, 0])), scale=scale,
                                  n=int(inl.sum()), pi=dst[inl], pj=src[inl], weak=False))
    # second pass, only between groups that are still apart (rows taken too far apart overlap
    # only at the circle edges): full resolution, more features, looser ratio test
    groups = components(n, [e for e in edges if e["n"] >= 40])     # a link of < 40 matches is too thin alone
    have = {(e["i"], e["j"]) for e in edges}
    if len(groups) > 1:
        sift2 = cv2.SIFT_create(nfeatures=15000, contrastThreshold=0.02)
        clahe2 = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        f2 = {}
        for k, (fl, (cx, cy, R)) in enumerate(zip(flat, circ)):
            g = clahe2.apply(fl[..., 1])
            mask = np.zeros(g.shape, np.uint8)
            cv2.circle(mask, (int(round(cx)), int(round(cy))), int(0.95 * R), 255, -1)
            kp, des = sift2.detectAndCompute(g, mask)
            f2[k] = (np.array([q.pt for q in kp], np.float64) - np.array([cx, cy]), des)
        gid = {k: gi for gi, g in enumerate(groups) for k in g}
        for i in range(n):
            for j in range(i + 1, n):
                if gid[i] == gid[j] or (i, j) in have:
                    continue
                pi, di = f2[i]; pj, dj = f2[j]
                if di is None or dj is None or len(di) < 50 or len(dj) < 50:
                    continue
                mm = [m for m, m2 in (x for x in flann.knnMatch(dj, di, k=2) if len(x) == 2)
                      if m.distance < 0.8 * m2.distance]
                if len(mm) < 20:
                    continue
                src = pj[[m.queryIdx for m in mm]]; dst = pi[[m.trainIdx for m in mm]]
                M, inl = cv2.estimateAffinePartial2D(src, dst, method=cv2.RANSAC, ransacReprojThreshold=10.0,
                                                     maxIters=20000, confidence=0.999)
                if M is None:
                    continue
                inl = inl.ravel().astype(bool)
                scale = float(np.hypot(M[0, 0], M[1, 0]))
                if inl.sum() >= 20 and 0.85 < scale < 1.18:
                    edges.append(dict(i=i, j=j, phi=float(np.arctan2(M[1, 0], M[0, 0])), scale=scale,
                                      n=int(inl.sum()), pi=dst[inl], pj=src[inl], weak=True))
                    print("  second pass linked %d-%d (%d matches)" % (i + 1, j + 1, inl.sum()))
    return edges


def initial_solve(n, edges):
    """Rotations, log-magnifications and positions from the pairwise fits (linear)."""
    W = np.zeros((n, n))
    for e in edges:
        W[e["i"], e["j"]] = W[e["j"], e["i"]] = e["n"]
    ref = int(np.argmax(W.sum(1)))
    theta = np.full(n, np.nan); theta[ref] = 0.0
    seen = {ref}
    while True:
        best = None
        for e in edges:
            for a_, b_, sgn in ((e["i"], e["j"], 1), (e["j"], e["i"], -1)):
                if a_ in seen and b_ not in seen and (best is None or e["n"] > best[0]):
                    best = (e["n"], a_, b_, sgn * e["phi"])
        if best is None:
            break
        _, a_, b_, ph = best
        theta[b_] = theta[a_] + ph
        seen.add(b_)
    idx = sorted(seen)
    col = {k: c for c, k in enumerate(idx)}
    E = [e for e in edges if e["i"] in seen and e["j"] in seen]

    def lsq(vals):          # x_j - x_i = val_ij, x_ref = 0
        A = np.zeros((len(E) + 1, len(idx))); b = np.zeros((len(E) + 1,) + np.shape(vals[0]))
        for r, (e, v) in enumerate(zip(E, vals)):
            w = np.sqrt(e["n"]); A[r, col[e["j"]]] = w; A[r, col[e["i"]]] = -w; b[r] = w * v
        A[-1, col[ref]] = 100.0
        return np.linalg.lstsq(A, b, rcond=None)[0]

    for _ in range(2):
        d = lsq([wrap(e["phi"] - (theta[e["j"]] - theta[e["i"]])) for e in E])
        for k in idx:
            theta[k] += d[col[k]]
    logs = np.full(n, np.nan)
    ls = lsq([np.log(e["scale"]) for e in E])          # s_j / s_i = scale_ij
    for k in idx:
        logs[k] = ls[col[k]]
    T = lsq([(np.exp(logs[e["i"]]) * rot(theta[e["i"]]) @ e["pi"].T
              - np.exp(logs[e["j"]]) * rot(theta[e["j"]]) @ e["pj"].T).mean(axis=1) for e in E])
    t = np.full((n, 2), np.nan)
    for k in idx:
        t[k] = T[col[k]]
    return ref, idx, theta, logs, t


def components(n, edges):
    adj = {k: set() for k in range(n)}
    for e in edges:
        adj[e["i"]].add(e["j"]); adj[e["j"]].add(e["i"])
    seen, groups = set(), []
    for s in range(n):
        if s in seen:
            continue
        stack, g = [s], []
        while stack:
            k = stack.pop()
            if k not in seen:
                seen.add(k); g.append(k); stack += list(adj[k])
        groups.append(sorted(g))
    return sorted(groups, key=len, reverse=True)


def undistort(p, k1, k2, R0):
    r2 = (p ** 2).sum(-1, keepdims=True) / R0 ** 2
    return p * (1 + k1 * r2 + k2 * r2 * r2)


def joint_fit(n, ref, idx, edges, theta, logs, t, R0, rng):
    """Least-squares fit of all photos at once, plus a shared radial distortion term."""
    col = {k: c for c, k in enumerate([k for k in idx if k != ref])}
    m = len(col)
    pairs = []
    for e in edges:
        if e["i"] in idx and e["j"] in idx:
            sel = rng.permutation(len(e["pi"]))[:MAX_PTS_PER_PAIR]
            pairs.append((e["i"], e["j"], e["pi"][sel], e["pj"][sel]))
    npts = sum(len(p[2]) for p in pairs)

    def unpack(x):
        th, ls, tt = theta.copy(), logs.copy(), t.copy()
        for k, c in col.items():
            th[k], ls[k], tt[k] = x[4 * c], x[4 * c + 1], x[4 * c + 2: 4 * c + 4]
        return th, ls, tt, x[4 * m], x[4 * m + 1]

    def place(k, p, th, ls, tt, k1, k2):
        return np.exp(ls[k]) * (undistort(p, k1, k2, R0) @ rot(th[k]).T) + tt[k]

    def resid(x):
        th, ls, tt, k1, k2 = unpack(x)
        # misfit measured in the photos' own pixels (divided by the pair's magnification), so a group of
        # photos cannot lower its misfit just by shrinking
        out = [(place(i, pi, th, ls, tt, k1, k2) - place(j, pj, th, ls, tt, k1, k2)) / np.exp(0.5 * (ls[i] + ls[j]))
               for i, j, pi, pj in pairs]
        # weak prior: magnification stays near the reference photo's (stops a loosely tied photo from
        # shrinking towards zero, which would fake a perfect fit)
        prior = SCALE_PRIOR_PX * np.array([ls[k] for k in col])
        return np.concatenate([np.concatenate(out).ravel(), prior])

    x0 = np.zeros(4 * m + 2)
    for k, c in col.items():
        x0[4 * c: 4 * c + 4] = [theta[k], logs[k], t[k, 0], t[k, 1]]
    J = lil_matrix((2 * npts + m, 4 * m + 2), dtype=int)
    r0 = 0
    for i, j, pi, pj in pairs:
        rows = slice(r0, r0 + 2 * len(pi))
        for k in (i, j):
            if k in col:
                J[rows, 4 * col[k]: 4 * col[k] + 4] = 1
        J[rows, 4 * m:] = 1
        r0 += 2 * len(pi)
    for k, c in col.items():
        J[2 * npts + c, 4 * c + 1] = 1
    before = np.sqrt((resid(x0)[:2 * npts] ** 2).reshape(-1, 2).sum(1))
    sol = least_squares(resid, x0, jac_sparsity=J, loss="soft_l1", f_scale=6.0, x_scale="jac", max_nfev=200)
    after = np.sqrt((sol.fun[:2 * npts] ** 2).reshape(-1, 2).sum(1))
    th, ls, tt, k1, k2 = unpack(sol.x)
    per_pair = []
    r0 = 0
    for i, j, pi, pj in pairs:
        d = after[r0: r0 + len(pi)]
        per_pair.append((i, j, len(pi), float(np.sqrt(np.mean(d ** 2))), float(np.median(d))))
        r0 += len(pi)
    return th, ls, tt, k1, k2, before, after, per_pair


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--min-inliers", type=int, default=25)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    files = sorted(glob.glob(os.path.join(a.src, "*.jp*g")) + glob.glob(os.path.join(a.src, "*.png")),
                   key=lambda p: tuple(int(x) for x in re.findall(r"\d+", os.path.basename(p))))
    names = [str(k + 1) for k in range(len(files))]    # shot order (file names 1..n, or camera timestamps)
    n = len(files)
    print("photos:", n)

    # ---- 1-2: circle + lighting -------------------------------------------------------
    imgs = [cv2.imread(p, cv2.IMREAD_COLOR) for p in files]
    r_guess = float(np.median([rough_radius(im) for im in imgs]))
    circ = [find_circle(im, r_guess) for im in imgs]
    R0 = float(np.median([c[2] for c in circ]))
    surfs, levels = zip(*[flat_field_model(im, *c) for im, c in zip(imgs, circ)])
    target = np.median(np.array(levels), axis=0)
    flat = []
    for k in range(n):                                  # one photo at a time, to keep memory low
        img = imgs[k]
        # (clipped: outside the circle the fitted surface extrapolates wildly, and that area is never used)
        gain = np.exp(-np.clip(cv2.resize(surfs[k], (img.shape[1], img.shape[0]), interpolation=cv2.INTER_LINEAR),
                               -6, 6))
        gain *= (target / levels[k])[None, None, :].astype(np.float32)
        flat.append(np.clip(img.astype(np.float32) * gain, 0, 255).astype(np.uint8))
        imgs[k] = np.empty((img.shape[0], img.shape[1], 0), np.uint8)   # keep only the shape
        del gain
    del surfs

    # ---- 3: matching (cached) and the joint fit --------------------------------------
    cache = os.path.join(a.out, "_matches.pkl")
    key = ("v3", names, [tuple(np.round(c, 1)) for c in circ])
    edges = None
    if os.path.exists(cache):
        ck, ce = pickle.load(open(cache, "rb"))
        if ck == key:
            edges = ce
    if edges is None:
        edges = match_all(flat, circ, a.min_inliers)
        pickle.dump((key, edges), open(cache, "wb"))
    print("overlapping pairs:", len(edges))
    ref, idx, theta, logs, t = initial_solve(n, edges)
    theta, logs, t, k1, k2, before, after, per_pair = joint_fit(n, ref, idx, edges, theta, logs, t, R0,
                                                                np.random.default_rng(1))
    # a pair whose matches disagree with every other pair is a false match: drop it, fit again
    cut = max(15.0, 4 * float(np.median(after)))
    bad = set()
    for i, j, _, _, md in sorted(per_pair, key=lambda r: -r[4]):
        if md > cut:                                      # never drop a pair that is the only link
            rest = [e for e in edges if (e["i"], e["j"]) not in bad | {(i, j)}]
            if len(components(n, rest)) == len(components(n, edges)):
                bad.add((i, j))
            else:
                print("pair %s-%s fits poorly but is the only link between two groups: kept" % (names[i], names[j]))
    if bad:
        print("dropped pairs that disagree with the rest:", ", ".join("%s-%s" % (names[i], names[j]) for i, j in bad))
        edges = [e for e in edges if (e["i"], e["j"]) not in bad]
        ref, idx, theta, logs, t = initial_solve(n, edges)
        theta, logs, t, k1, k2, _, after, per_pair = joint_fit(n, ref, idx, edges, theta, logs, t, R0,
                                                               np.random.default_rng(1))
    groups = components(n, edges)
    lost = [names[k] for k in range(n) if k not in idx]
    if lost:
        print("NOT CONNECTED to the main group:", ", ".join(lost))
        print("separate groups:", "  ".join("[" + " ".join(names[k] for k in g) + "]" for g in groups))
    c = float(np.nanmedian(logs[idx]))                    # the median photo keeps its magnification
    logs = logs - c
    t = t / np.exp(c)
    print("feature misfit: before %.1f px median / after %.1f px median, %.1f px 95th pct"
          % (np.median(before), np.median(after), np.percentile(after, 95)))
    print("lens distortion k1 = %.4f, k2 = %.4f (shift at the circle edge %.0f px)"
          % (k1, k2, R0 * (k1 + k2)))

    # ---- orientation: rows level with the stage axes, portrait photos ~ microscope view, then +180 deg
    C = t[idx]
    D = np.linalg.norm(C[:, None] - C[None], axis=2) + np.eye(len(idx)) * 1e9
    step = float(np.median(D.min(1)))
    angs = [np.arctan2(*(t[j] - t[i])[::-1]) for i, j, *_ in per_pair if np.linalg.norm(t[j] - t[i]) < 1.3 * step]
    alpha = float(np.angle(np.exp(4j * np.array(angs)).sum()) / 4) if angs else 0.0
    portrait = [k for k in idx if imgs[k].shape[0] > imgs[k].shape[1]]
    best_q = min(range(4), key=lambda q: np.abs(wrap(theta[portrait] - alpha - q * np.pi / 2)).sum())
    slide = -alpha - best_q * np.pi / 2 + np.pi         # mosaic frame -> real slide frame
    psi = theta + slide
    F = (rot(slide) @ t[idx].T).T

    # ---- 4-5: undistort, scale, rotate, crop, save -----------------------------------
    reach = min(np.exp(logs[k]) * np.linalg.norm(undistort(np.array([circ[k][2], 0.0]), k1, k2, R0)) for k in idx)
    s = int(np.floor(np.sqrt(2) * reach * SQUARE_FRACTION)) // 2 * 2
    tl = F - s / 2.0
    tl -= tl.min(0)
    if tl.max() > 15 * s:
        raise SystemExit("fit failed: the mosaic came out %.0f tiles wide; check report and matches" % (tl.max() / s))
    gy, gx = np.mgrid[0:s, 0:s].astype(np.float64)
    q = np.stack([gx - s / 2.0 + 0.5, gy - s / 2.0 + 0.5], -1).reshape(-1, 2)
    cfg = ["# Define the number of dimensions we are working on", "dim = 2", "",
           "# Define the image coordinates"]
    tiles_rep = []
    for k in idx:
        cx, cy, Rk = circ[k]
        v = (q @ rot(psi[k])) / np.exp(logs[k])           # undistorted photo coordinates
        p = v.copy()
        for _ in range(8):                                # invert the radial model
            r2 = (p ** 2).sum(1, keepdims=True) / R0 ** 2
            p = v / (1 + k1 * r2 + k2 * r2 * r2)
        mx = (p[:, 0] + cx).reshape(s, s).astype(np.float32)
        my = (p[:, 1] + cy).reshape(s, s).astype(np.float32)
        tile = cv2.remap(flat[k], mx, my, cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT)
        outside = float((np.hypot(p[:, 0], p[:, 1]) > Rk).mean())
        fn = "tile_%02d.png" % int(names[k])
        cv2.imwrite(os.path.join(a.out, fn), tile)
        x, y = tl[idx.index(k)]
        cfg.append("%s; ; (%.1f, %.1f)" % (fn, x, y))
        tiles_rep.append(dict(photo=os.path.basename(files[k]), tile=fn, circle_radius_px=round(Rk, 1),
                              magnification=round(float(np.exp(logs[k])), 4),
                              rotation_deg=round(float(np.degrees(wrap(psi[k]))), 2),
                              x=round(float(x), 1), y=round(float(y), 1), frac_outside_circle=round(outside, 4)))
    open(os.path.join(a.out, "TileConfiguration.txt"), "w").write("\n".join(cfg) + "\n")

    # ---- 6: full-resolution stitch from the whole circles ---------------------------------
    # Each photo contributes its whole circle, weighted (1 - r^2)^2 so the sharp, evenly lit centre
    # counts most and the rim fades out. Whole circles cover rows that are too far apart for the
    # squares above to touch.
    Reff = {k: float(np.exp(logs[k]) * np.linalg.norm(undistort(np.array([circ[k][2], 0.0]), k1, k2, R0)))
            for k in idx}
    lo = np.floor(np.min([F[idx.index(k)] - Reff[k] for k in idx], axis=0)) - 4
    hi = np.ceil(np.max([F[idx.index(k)] + Reff[k] for k in idx], axis=0)) + 4
    Wf, Hf = int(hi[0] - lo[0]), int(hi[1] - lo[1])
    acc = np.zeros((Hf, Wf, 3), np.float32); wacc = np.zeros((Hf, Wf), np.float32)
    centres = {}
    for k in idx:
        cx, cy, Rk = circ[k]
        c0 = F[idx.index(k)] - lo
        centres[k] = c0
        x0, y0 = int(np.floor(c0[0] - Reff[k])), int(np.floor(c0[1] - Reff[k]))
        Dk = int(np.ceil(2 * Reff[k])) + 3
        gy, gx = np.mgrid[0:Dk, 0:Dk].astype(np.float64)
        q = np.stack([gx + x0 - c0[0], gy + y0 - c0[1]], -1).reshape(-1, 2)
        v = (q @ rot(psi[k])) / np.exp(logs[k])
        p = v.copy()
        for _ in range(8):
            r2 = (p ** 2).sum(1, keepdims=True) / R0 ** 2
            p = v / (1 + k1 * r2 + k2 * r2 * r2)
        rr = (np.hypot(p[:, 0], p[:, 1]) / Rk).reshape(Dk, Dk)
        w = (np.clip(1 - rr ** 2, 0, 1) ** 2).astype(np.float32)
        w[rr > 0.97] = 0
        mx = (p[:, 0] + cx).reshape(Dk, Dk).astype(np.float32)
        my = (p[:, 1] + cy).reshape(Dk, Dk).astype(np.float32)
        tile = cv2.remap(flat[k], mx, my, cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT).astype(np.float32)
        acc[y0:y0 + Dk, x0:x0 + Dk] += tile * w[..., None]
        wacc[y0:y0 + Dk, x0:x0 + Dk] += w
    stitched = (acc / np.maximum(wacc, 1e-6)[..., None]).clip(0, 255).astype(np.uint8)
    stitched[wacc <= 0] = 0
    del acc
    leaf = re.sub(r"_cleaned$", "", os.path.basename(os.path.normpath(a.out)))
    stitched_fn = "%s_stitched.png" % leaf
    cv2.imwrite(os.path.join(a.out, stitched_fn), stitched)

    # largest square covered by leaf everywhere (no gaps, no background past the cut edges), at 1/8 size
    f8 = 8
    small = cv2.resize(stitched, (Wf // f8, Hf // f8), interpolation=cv2.INTER_AREA)
    cov = cv2.resize((wacc > 0).astype(np.uint8), (Wf // f8, Hf // f8), interpolation=cv2.INTER_NEAREST) > 0
    bright = ((small[..., 2] > 225) & (small[..., 1] > 225)).astype(np.uint8)
    bright = cv2.morphologyEx(bright, cv2.MORPH_OPEN, np.ones((15, 15), np.uint8)) > 0
    valid = (cov & ~bright).astype(np.uint8)
    lo_s, hi_s, best = 1, min(valid.shape), None
    while lo_s <= hi_s:
        L = (lo_s + hi_s) // 2
        er = cv2.erode(valid, np.ones((L, L), np.uint8), anchor=(0, 0), borderType=cv2.BORDER_CONSTANT, borderValue=0)
        ys_, xs_ = np.nonzero(er)
        if len(ys_):
            cy_, cx_ = np.mean(ys_), np.mean(xs_)                 # most central placement
            j = int(np.argmin((ys_ - cy_) ** 2 + (xs_ - cx_) ** 2))
            best = (L, int(xs_[j]), int(ys_[j])); lo_s = L + 1
        else:
            hi_s = L - 1
    sq = None
    if best:
        L, bx, by = best
        sq = dict(left=bx * f8 + f8, top=by * f8 + f8, width=(L - 2) * f8, height=(L - 2) * f8)
        sq["mm"] = round(sq["width"] / PX_PER_MM, 2)

    # previews (1/4 size): plain, and with photo numbers and the largest clean square
    f = 4
    prev = cv2.resize(stitched, (Wf // f, Hf // f), interpolation=cv2.INTER_AREA)
    cv2.imwrite(os.path.join(a.out, "preview_mosaic.png"), prev)
    for k in idx:
        x0, y0 = centres[k] / f
        cv2.putText(prev, names[k], (int(x0 - 20), int(y0 + 15)), cv2.FONT_HERSHEY_SIMPLEX,
                    1.4, (0, 0, 255), 3, cv2.LINE_AA)
    if sq:
        cv2.rectangle(prev, (sq["left"] // f, sq["top"] // f),
                      ((sq["left"] + sq["width"]) // f, (sq["top"] + sq["height"]) // f), (0, 0, 255), 3)
    cv2.imwrite(os.path.join(a.out, "preview_numbered.png"), prev)

    mos = np.array([Wf, Hf]) / PX_PER_MM
    rep = dict(photos=n, connected=len(idx), not_connected=lost, reference_photo=names[ref],
               px_per_mm=PX_PER_MM, square_px=s, square_mm=s / PX_PER_MM,
               field_diameter_mm=2 * R0 / PX_PER_MM, median_step_mm=step / PX_PER_MM,
               mosaic_mm=[round(float(m_), 2) for m_ in mos], stitched=stitched_fn,
               stitched_px=[Wf, Hf], largest_clean_square=sq,
               distortion_k1=k1, distortion_k2=k2,
               misfit_px=dict(before_median=float(np.median(before)), after_median=float(np.median(after)),
                              after_p95=float(np.percentile(after, 95))),
               pairs=[dict(a=names[i], b=names[j], points=m_, rms_px=round(r, 2), median_px=round(md, 2))
                      for i, j, m_, r, md in per_pair],
               tiles=tiles_rep)
    json.dump(rep, open(os.path.join(a.out, "report.json"), "w"), indent=1)
    print("magnification range %.3f-%.3f; rotations applied %.0f to %.0f deg"
          % (min(r["magnification"] for r in tiles_rep), max(r["magnification"] for r in tiles_rep),
             min(r["rotation_deg"] for r in tiles_rep), max(r["rotation_deg"] for r in tiles_rep)))
    print("square %d px = %.2f mm; field %.2f mm; median step %.2f mm; mosaic %.1f x %.1f mm"
          % (s, s / PX_PER_MM, 2 * R0 / PX_PER_MM, step / PX_PER_MM, mos[0], mos[1]))
    worst = max(per_pair, key=lambda r: r[3])
    print("worst pair %s-%s: RMS %.1f px" % (names[worst[0]], names[worst[1]], worst[3]))
    bad = [r["tile"] for r in tiles_rep if r["frac_outside_circle"] > 0]
    if bad:
        print("tiles reaching outside their circle:", bad)
    print("stitched (whole circles): %s, %d x %d px" % (stitched_fn, Wf, Hf))
    if sq:
        print("largest square with leaf everywhere: %.2f mm (%d px); LeafVeinCNN crop Top %d Left %d Width %d Height %d"
              % (sq["mm"], sq["width"], sq["top"], sq["left"], sq["width"], sq["height"]))
    print("SAVED", a.out)


if __name__ == "__main__":
    main()
