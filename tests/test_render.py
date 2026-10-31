"""Deterministic geometry tests. No real audio file required."""
import json
import unittest
from pathlib import Path

import numpy as np
from reproduce_edits import DEFAULT_MANIFEST, labels_for, render


class RenderTests(unittest.TestCase):
    def test_manifest_splices_and_duration(self):
        d = json.loads(DEFAULT_MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(len(d["variants"]), 3)
        for name, spec in d["variants"].items():
            segments, fades = spec["segments"], spec["crossfades"]
            computed_duration = sum(end-start for start,end in segments)-sum(fades)
            self.assertAlmostEqual(computed_duration, spec["duration_seconds"], places=2, msg=name)
            running = 0.0
            times = []
            for i, (start, end) in enumerate(segments):
                if i:
                    times.append(running-fades[i-1])
                    running -= fades[i-1]
                running += end-start
            for actual, expected in zip(times, spec["junction_output_seconds"]):
                self.assertAlmostEqual(actual, expected, places=2, msg=name)
            self.assertEqual(len(times), len(fades))
            self.assertEqual(len(labels_for(spec, times).splitlines()), len(times))

    def test_render_linear_fade_and_duration(self):
        sr = 10
        src = np.arange(100, dtype="float32")[:, None]
        pcm, junctions = render(src, sr, [[0,2],[4,6],[8,10]], [0.2,0.1])
        self.assertEqual(len(pcm), 57)
        self.assertEqual(len(junctions), 2)
        self.assertAlmostEqual(junctions[0], 1.8)
        self.assertAlmostEqual(junctions[1], 3.7)

    def test_reject_invalid(self):
        src = np.zeros((100,2), dtype="float32")
        with self.assertRaises(ValueError):
            render(src, 10, [[0,2],[3,5]], [])
        with self.assertRaises(ValueError):
            render(src, 10, [[0,2],[3,5]], [3])
        with self.assertRaises(ValueError):
            render(src, 10, [[0,2],[1,5]], [0.1])


if __name__ == "__main__":
    unittest.main()
