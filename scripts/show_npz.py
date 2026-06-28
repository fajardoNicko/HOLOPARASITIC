"""
show_npz.py — pretty-print the contents of a .npz results file.

    C:\\laragon\\bin\\python\\python-3.13\\python.exe scripts\\show_npz.py data\\results.npz
    ...\\python.exe scripts\\show_npz.py data\\results_preview.npz

With no argument it defaults to data/results.npz (the full run), falling back to
the preview file if the full run hasn't finished yet.
"""

import os
import sys
import numpy as np

DEFAULT = os.path.join("data", "results.npz")
PREVIEW = os.path.join("data", "results_preview.npz")


def show(path):
    if not os.path.exists(path):
        print(f"(not found: {path})")
        return
    print(f"\n=== {path} ===")
    with np.load(path, allow_pickle=True) as z:
        names = list(z.keys())
        print(f"{len(names)} arrays: {', '.join(names)}\n")
        for name in names:
            a = z[name]
            print(f"- {name:22s} shape={str(a.shape):12s} dtype={a.dtype}")
            # show full small arrays; head/tail for long 1-D ones
            with np.printoptions(precision=4, suppress=True, threshold=20):
                if a.ndim <= 1 and a.size <= 12:
                    print(f"    {a}")
                elif a.ndim == 1:
                    print(f"    first 6: {a[:6]}")
                    print(f"    last  6: {a[-6:]}")
                else:
                    print(f"{np.array2string(a, prefix='    ')}")
            print()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        target = DEFAULT if os.path.exists(DEFAULT) else PREVIEW
    show(target)
