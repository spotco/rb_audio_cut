#!/usr/bin/env python3
"""Inspect source-pinned splice geometry and PCM continuity, not musical quality.

Correlation cannot identify changed instruments, vocal phrasing, or style jumps.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from reproduce_edits import render, sha256_file  # noqa: E402


def inspect(source: Path, manifest_path: Path, variant: str) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    if variant not in manifest['variants']:
        raise ValueError(f'Unknown variant {variant!r}')
    if sha256_file(source) != manifest['source_sha256']:
        raise ValueError('Source SHA-256 mismatch')
    data, sr = sf.read(source, dtype='float32', always_2d=True)
    if sr != manifest['sample_rate_hz'] or abs(len(data)/sr - manifest['source_seconds']) > .01:
        raise ValueError('Source PCM metadata mismatch')
    spec = manifest['variants'][variant]
    rendered, junctions = render(data, sr, spec['segments'], spec['crossfades'])
    checks = {
        'source_sha256': True,
        'source_metadata': True,
        'output_duration': abs(len(rendered)/sr - spec['duration_seconds']) <= .002,
        'splice_times': len(junctions) == len(spec['junction_output_seconds']) and all(
            abs(a-b) <= .002 for a,b in zip(junctions, spec['junction_output_seconds'])),
        'original_ending': abs(spec['segments'][-1][1] - len(data)/sr) < 1/sr,
    }
    splices = []
    for i, (t, fade) in enumerate(zip(junctions, spec['crossfades'])):
        n = round(fade*sr)
        a = round(spec['segments'][i][1]*sr) - n
        b = round(spec['segments'][i+1][0]*sr)
        left = data[a:a+n].astype('float64')
        right = data[b:b+n].astype('float64')
        if n == 0 or len(left) != n or len(right) != n:
            raise ValueError('Crossfade interval cannot be inspected')
        denominator = np.linalg.norm(left)*np.linalg.norm(right)
        correlation = float(np.sum(left*right)/denominator) if denominator else None
        rl = float(np.sqrt(np.mean(left**2)))
        rr = float(np.sqrt(np.mean(right**2)))
        db = float(20*np.log10(rl/rr)) if rl > 0 and rr > 0 else None
        start = round(t*sr)
        end = start+n
        local = np.abs(np.diff(rendered[max(0,start-round(.75*sr)):min(len(rendered),end+round(.75*sr))],axis=0))
        p999 = float(np.quantile(local, .999)) if len(local) else None
        boundary_steps = [float(np.max(np.abs(rendered[k]-rendered[k-1])))
                          for k in (start, end) if 0 < k < len(rendered)]
        splices.append({
            'index': i+1, 'edited_crossfade_start_seconds': t,
            'left_source_overlap_start_seconds': a/sr,
            'right_source_overlap_start_seconds': b/sr,
            'crossfade_seconds': n/sr,
            'overlap_stereo_correlation': correlation,
            'overlap_rms_difference_db': db,
            'edge_max_sample_deltas': boundary_steps,
            'nearby_difference_p999': p999,
            'edge_steps_below_local_p999': bool(boundary_steps and p999 is not None
                                                and max(boundary_steps) < p999),
        })
    return {
        'source_sha256': manifest['source_sha256'],
        'variant': variant,
        'decoded_output_seconds': len(rendered)/sr,
        'checks': checks,
        'splices': splices,
        'interpretation': ('Technical geometry / continuity evidence only; no threshold '
                           'certifies arrangement, melody, vocals, or listening quality.'),
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--manifest', type=Path, required=True)
    p.add_argument('--variant', required=True)
    p.add_argument('--out', type=Path)
    args = p.parse_args()
    report = inspect(args.source, args.manifest, args.variant)
    if not all(report['checks'].values()):
        raise SystemExit(f'Failed structural checks: {report["checks"]}')
    message = json.dumps(report, ensure_ascii=False, indent=2) + '\n'
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(message, encoding='utf-8')
    print(message, end='')


if __name__ == '__main__':
    main()
