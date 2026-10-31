"""Tests for the optional PCM overlap inspector."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
import soundfile as sf

from scripts.inspect_join import inspect


class InspectJoinTests(unittest.TestCase):
    def test_repeated_waveform_geometry_and_checksum(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            sr = 8000
            t = np.arange(4*sr)/sr
            y = np.column_stack([np.sin(2*np.pi*10*t), np.cos(2*np.pi*10*t)]).astype('float32')
            source = root/'source.wav'
            sf.write(source, y, sr, subtype='FLOAT')
            manifest = root/'manifest.json'
            spec = {
                'source_name': source.name, 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                'source_seconds': 4.0, 'sample_rate_hz': sr,
                'variants': {'A': {
                    'segments': [[0, 1.6], [2.0, 4.0]], 'crossfades': [.1],
                    'duration_seconds': 3.5, 'junction_output_seconds': [1.5],
                }},
            }
            manifest.write_text(json.dumps(spec))
            result = inspect(source, manifest, 'A')
            self.assertTrue(all(result['checks'].values()))
            self.assertAlmostEqual(result['splices'][0]['edited_crossfade_start_seconds'], 1.5)
            self.assertGreater(result['splices'][0]['overlap_stereo_correlation'], .99)
            self.assertIn('no threshold', result['interpretation'])

    def test_mismatched_source_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root/'source.wav'
            sf.write(source, np.zeros((8000,2),dtype='float32'), 8000, subtype='FLOAT')
            manifest = root/'manifest.json'
            manifest.write_text(json.dumps({
                'source_sha256': '0'*64, 'source_seconds': 1, 'sample_rate_hz': 8000,
                'variants': {'A': {'segments': [[0,.5],[.7,1]], 'crossfades':[.1],
                                   'duration_seconds': .7, 'junction_output_seconds':[.4]}}
            }))
            with self.assertRaisesRegex(ValueError, 'SHA-256 mismatch'):
                inspect(source, manifest, 'A')


if __name__ == '__main__':
    unittest.main()
