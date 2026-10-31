#!/usr/bin/env python3
"""Rank novelty peaks (candidate section boundaries) from analyze.py features."""
import argparse
from pathlib import Path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("features", type=Path)
    args = p.parse_args()
    import numpy as np
    from scipy import ndimage, signal
    data = np.load(args.features)
    C, M, times = (data[x] for x in ("C", "M", "times"))
    step = float(np.median(np.diff(times)))
    features = np.vstack([C*.7, M*.3])
    features = ndimage.gaussian_filter1d(features, 1, axis=1)
    for window in (2, 4, 8):
        n = max(1, int(round(window / step)))
        values = []
        for i in range(n, len(times)-n):
            lhs = np.mean(features[:, i-n:i], axis=1)
            rhs = np.mean(features[:, i:i+n], axis=1)
            values.append(np.linalg.norm(lhs-rhs))
        peaks, _ = signal.find_peaks(np.array(values), distance=max(1, int(5 / step)), prominence=.02)
        top = sorted(((float(values[j]), float(times[j+n])) for j in peaks), reverse=True)[:20]
        print(f"window {window}s: {[(round(score, 3), round(at, 2)) for score, at in top]}")


if __name__ == "__main__":
    main()
