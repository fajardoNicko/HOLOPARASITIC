r"""
fix_sink_surface_summary.py — recompute the derived summary fields of
data/sink_surface.json from its own cells.

The first production run of `run_sink_surface.py` summarised the surface with a
single "largest multiple with no threshold" taken across all cells, which is
wrong when a threshold appears in one row (the least reticulate network) while
the other rows still never collapse. The generator has since been corrected; this
script applies the same correction to an already-computed surface so the 20-minute
run does not have to be repeated. Running it on a surface produced by the current
generator is a no-op.

    C:\laragon\bin\python\python-3.13\python.exe scripts\fix_sink_surface_summary.py
"""

import os
import sys
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import config

path = os.path.join(config.PATHS.data, "sink_surface.json")
doc = json.load(open(path, encoding="utf-8"))

by_mult = {}
for c in doc["cells"]:
    by_mult.setdefault(c["k_h_multiple_of_calibrated"], []).append(
        c["threshold_exists"])
mults = sorted(by_mult)

min_mult = next((m for m in mults if any(by_mult[m])), None)
all_mult = next((m for m in mults if all(by_mult[m])), None)
max_no = None
for m in mults:
    if any(by_mult[m]):
        break
    max_no = m

doc.pop("largest_k_h_multiple_with_NO_threshold", None)
doc["smallest_k_h_multiple_with_a_threshold"] = min_mult
doc["smallest_k_h_multiple_with_a_threshold_in_every_row"] = all_mult
doc["largest_k_h_multiple_with_NO_threshold_in_any_row"] = max_no
doc["threshold_exists_by_multiple"] = {
    str(m): {"n_rows_with_threshold": int(sum(by_mult[m])),
             "n_rows": len(by_mult[m])} for m in mults}

json.dump(doc, open(path, "w", encoding="utf-8"), indent=2)
print(f"no threshold in ANY row up to {max_no}x the calibrated K_h; "
      f"first threshold at {min_mult}x; threshold in every row at {all_mult}x")
print("updated", path)
