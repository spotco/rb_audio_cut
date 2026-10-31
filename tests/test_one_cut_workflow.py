"""Focused tests for the default one-A workflow and Flaming Sky provenance."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
import soundfile as sf

from analysis.suggest_one_cut import candidate_geometry, scan
from scripts.render_one import run

ROOT = Path(__file__).resolve().parents[1]


class SingleCutGeometryTests(unittest.TestCase):
    def test_overlap_phase_and_timeline(self):
        geometry = candidate_geometry(90.88, 246.939, .12, 304.437505669)
        self.assertEqual(geometry['segments'], [[0., 91.0], [246.939, 304.437505669]])
        self.assertEqual(geometry['duration_seconds'], 148.378506)
        self.assertEqual(geometry['junction_output_seconds'], [90.88])

    def test_invalid_geometry(self):
        with self.assertRaises(ValueError):
            candidate_geometry(10, 10.1, .2, 50)

    def test_accepted_manifest_matches_fade_geometry(self):
        m = json.loads((ROOT/'examples/flaming_sky/manifest.json').read_text(encoding='utf8'))
        self.assertEqual(list(m['variants']), ['A_one_repeat_join'])
        v = m['variants']['A_one_repeat_join']
        self.assertAlmostEqual(sum(b-a for a,b in v['segments'])-sum(v['crossfades']),
                               v['duration_seconds'], places=5)
        self.assertLess(v['encoded_duration_seconds'], 150.)
        self.assertEqual(v['junction_output_seconds'], [90.88])
        self.assertEqual(m['source_sha256'], 'a1da2a9c586d37f0e6b370d2e1a2f75e05b062dda4c829957cfd006edf830632')
        e = json.loads((ROOT/'examples/flaming_sky/evaluation.json').read_text())
        self.assertEqual(e['variants']['A_one_repeat_join']['human_result'], 'accepted')
        for other in ('B_two_repeat_joins', 'C_full_intro_three_joins'):
            self.assertEqual(e['variants'][other]['human_result'], 'not_listened')

    def test_feature_scan_prefers_repeat_at_target_gap(self):
        rng = np.random.default_rng(4)
        c = rng.normal(size=(12, 160)).astype('float32')
        m = rng.normal(size=(14, 160)).astype('float32')
        # 61 frames = 15.25 seconds, enough removal for 40s -> <=25s.
        c[:, 81:111] = c[:, 20:50]
        m[:, 81:111] = m[:, 20:50]
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)/'f.npz'
            np.savez(path, C=c, M=m, times=np.arange(160)*.25)
            found = scan(path, duration=40., target=25., tolerance=3.,
                         intro=3., outro=2., top=10)
        self.assertTrue(found)
        self.assertTrue(any(abs(p['right_source_start']-p['left_crossfade_start']-15.25)<.001
                            for p in found))


class SingleCutRenderTests(unittest.TestCase):
    def test_render_audition_labels_and_reject_hash_mismatch(self):
        sr = 8000
        duration = 4.
        t = np.arange(round(sr*duration))/sr
        audio = np.column_stack([.2*np.sin(2*np.pi*220*t), .2*np.sin(2*np.pi*330*t)])
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root/'source.wav'
            sf.write(source, audio, sr, subtype='PCM_16')
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
            manifest = {
                'source_name': 'source.wav', 'source_sha256': digest,
                'source_seconds': duration, 'sample_rate_hz': sr,
                'variants': {'A': {
                    'segments': [[0., 1.5], [2.5, 4.]],
                    'crossfades': [.1], 'duration_seconds': 2.9,
                    'junction_output_seconds': [1.4], 'output': 'A.mp3'}}}
            spec = root/'manifest.json'
            spec.write_text(json.dumps(manifest))
            out = root/'out'
            report = run(spec, None, out, max_seconds=3.5, pre=.5, post=.7)
            self.assertLess(report['encoded_seconds'], 3.5)
            self.assertEqual(report['splice_output_seconds'], [1.4])
            self.assertTrue((out/'auditions/A_splice_1.mp3').exists())
            self.assertTrue((out/'A_splice_auditions.mp3').exists())
            self.assertIn('1.400\t1.400\tSplice 1', (out/'A_audacity_labels.txt').read_text())
            with self.assertRaises(ValueError):
                run(spec, None, root/'bad', max_seconds=2.5)
            manifest['source_sha256'] = '0'*64
            spec.write_text(json.dumps(manifest))
            with self.assertRaises(ValueError):
                run(spec, None, root/'wrong_hash', max_seconds=3.5)


if __name__ == '__main__':
    unittest.main()
