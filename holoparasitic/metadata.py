r"""
metadata.py — the source dataset's own extraction-quality record.

Matos et al. ship UCBG_venation_form_metadata.csv alongside the 120 leaf
networks. It is the only INDEPENDENT statement of how faithful each extracted
network is to the leaf it came from, so it — not our own summary statistics —
is what the inclusion criterion should rest on.

COLUMNS
    sample_name       original image name
    spp_code          6-letter code; identical to the data sub-directory name
    image_resolution  mm per pixel
    version           extraction date
    CNN_image         which CNN pass produced the trace (1/2/3)
    quality           comma-separated flags, decoded below
    OBS               free-text note
    hand_traced       no / partial / full

QUALITY FLAGS. The archive ships no legend, so the meaning below is read off
the OBS text that co-occurs with each flag across all 120 rows (every B row,
every C row and every D row carries a note; the mapping is unambiguous):

    A  clean extraction — no vein-level defect noted            (n=34)
    B  FALSE NEGATIVES: "missing minor veins"                   (n=46)
    C  FALSE POSITIVES: "fake minor veins"                      (n=15)
    D  physical damage to the leaf: tears, folds, not-whole-leaf (n=57)

Why this matters more here than in the source paper: B and C are errors in the
*minor* vein orders, which is where nearly all the anastomoses live. Missing
minor veins depress mean degree and loop fraction; fake ones inflate them. Our
central result is that mean degree — not fractal dimension — sets the
percolation threshold, so B/C error acts directly on the response variable.
Matos et al. could tolerate these flags because they measured vein density and
conductance; we cannot assume the same.

D is different in kind: a torn or folded leaf yields a smaller or partial
network, but the veins that WERE traced are real. D therefore affects extent,
not topology, and is handled by the size screen rather than by exclusion.
"""

from __future__ import annotations

import os
import csv

#: flag -> (short label, what it does to topology)
FLAG_MEANING = {
    "A": ("clean", "no vein-level defect noted"),
    "B": ("missing_veins", "false negatives — depress mean degree & loop fraction"),
    "C": ("fake_veins", "false positives — inflate mean degree & loop fraction"),
    "D": ("damage", "tears/folds/partial leaf — affects extent, not topology"),
}

#: flags that corrupt the topology we measure, and so justify exclusion
TOPOLOGY_CORRUPTING = ("B", "C")

METADATA_FILENAME = "UCBG_venation_form_metadata.csv"


def _flags(quality: str) -> list[str]:
    return [f for f in (quality or "").replace(" ", "").split(",") if f]


def load_metadata(data_dir: str) -> dict[str, dict]:
    """Read the metadata table, keyed by spp_code (== data sub-directory name).

    Looks for the CSV in data_dir and one level up, since the archive nests one
    redundant folder deep when unzipped.
    """
    for cand in (os.path.join(data_dir, METADATA_FILENAME),
                 os.path.join(os.path.dirname(data_dir.rstrip("/\\")),
                              METADATA_FILENAME)):
        if os.path.exists(cand):
            path = cand
            break
    else:
        return {}

    out = {}
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            code = (row.get("spp_code") or "").strip()
            if not code:
                continue
            fl = _flags(row.get("quality", ""))
            out[code] = {
                "spp_code": code,
                "sample_name": (row.get("sample_name") or "").strip(),
                "resolution_mm_px": _float(row.get("image_resolution")),
                "cnn_pass": (row.get("CNN_image") or "").strip(),
                "hand_traced": (row.get("hand_traced") or "").strip(),
                "quality_flags": fl,
                "quality": ",".join(fl),
                "obs": (row.get("OBS") or "").strip(),
                "clean": fl == ["A"],
                "topology_suspect": any(f in TOPOLOGY_CORRUPTING for f in fl),
                "damaged": "D" in fl,
            }
    return out


def _float(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def quality_note(meta: dict | None) -> str:
    """One-line human-readable verdict for a leaf's metadata row."""
    if not meta:
        return "no metadata row"
    labels = [FLAG_MEANING.get(f, (f, ""))[0] for f in meta["quality_flags"]]
    return "+".join(labels) if labels else "unflagged"
