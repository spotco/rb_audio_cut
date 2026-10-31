#!/usr/bin/env python3
"""Rank structural similarity between two requested candidate splice ranges.

WARNING: scores do not model vocal continuity. The rejected B/C edits also
looked mathematically plausible, so never certify a vocal cut from this alone.
"""
import argparse
from pathlib import Path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("features", type=Path)
    p.add_argument("--from-range", nargs=2, type=float, required=True, metavar=("START", "END"))
    p.add_argument("--to-range", nargs=2, type=float, required=True, metavar=("START", "END"))
    p.add_argument("--window", type=float, default=2)
    args = p.parse_args()
    import numpy as np
    d = np.load(args.features)
    C, M, times = (d[k] for k in ("C", "M", "times"))
    step = float(np.median(np.diff(times)))
    n = max(1, int(round(args.window / step)))

    def score(a, b):
        i, j = int(round(a/step)), int(round(b/step))
        if min(i,j) < n or max(i+n,j+n) > C.shape[1]:
            return None
        ca, cb = C[:, i-n:i+n], C[:, j-n:j+n]
        ma, mb = M[:, i-n:i+n], M[:, j-n:j+n]
        return float(.6*np.mean(np.sum((ca-cb)**2,axis=0)) + .4*np.mean(np.sum((ma-mb)**2,axis=0)))

    out = []
    for a in np.arange(args.from_range[0], args.from_range[1]+step/2, step):
        for b in np.arange(args.to_range[0], args.to_range[1]+step/2, step):
            val = score(a,b)
            if val is not None:
                out.append((val, float(a), float(b)))
    for similarity, source, destination in sorted(out)[:20]:
        print(f"score={similarity:.4f}\t{source:.3f}s -> {destination:.3f}s")


if __name__ == "__main__":
    main()
