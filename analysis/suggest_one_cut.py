#!/usr/bin/env python3
"""Find promising single-jump edits from existing spectral analysis features.

This is a shortlist, not an automatic musical-quality/vocal-continuity verdict.
The accepted Flaming Sky A required subsequent phase-aware waveform alignment and
human listening. Generate the feature cache with analysis/analyze.py first.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np


def candidate_geometry(start: float, destination: float, fade: float, duration: float) -> dict:
    """A match is between crossfade *starts*, not the two segment ends.

    The right-source start aligns with (left-source end - fade). As a result,
    edited length is duration - (destination - start), including the overlap.
    """
    if not (0 <= start < start + fade < destination < duration):
        raise ValueError('Not a valid forward jump')
    return {'segments': [[0., round(start + fade, 6)],
                         [round(destination, 6), round(duration, 9)]],
            'crossfades': [fade], 'duration_seconds': round(duration - (destination-start), 6),
            'junction_output_seconds': [round(start, 6)]}


def scan(features: Path, duration: float, target: float = 150.,
         tolerance: float = 12., intro: float = 30., outro: float = 25.,
         top: int = 30) -> list[dict]:
    """Rank repeated context at one-cut offsets near the duration target."""
    if min(duration, target, intro, outro, tolerance) <= 0:
        raise ValueError('Durations and search windows must be positive')
    with np.load(features) as d:
        C, M, times = (d[k] for k in ('C', 'M', 'times'))
    step = float(np.median(np.diff(times)))
    if not np.allclose(np.diff(times), step, atol=step*.01):
        raise ValueError('Feature frames must be uniformly spaced')
    if C.shape[1] != len(times) or M.shape[1] != len(times):
        raise ValueError('Features must match time axis')
    # Repo analysis/analyze.py generates unit-length column vectors, but
    # normalize again to support other compatible feature caches.
    C = C / np.maximum(np.linalg.norm(C, axis=0), 1e-9)
    M = M / np.maximum(np.linalg.norm(M, axis=0), 1e-9)
    minimum_skip = duration - target + .08  # allow encoder padding
    if minimum_skip <= 0:
        raise ValueError('Song is already short enough for a single-cut search')
    off = max(1, round(1.5/step))
    low_k = max(1, int(np.ceil(minimum_skip/step)))
    high_k = int(np.floor((minimum_skip+tolerance)/step))
    picks = []
    for k in range(low_k, high_k+1):
        first = max(off, int(np.ceil(intro/step)))
        last = min(C.shape[1]-off-k,
                   int(np.floor((duration-outro-k*step)/step)))
        if last <= first:
            continue
        indices = np.arange(first, last)
        scores = np.zeros(len(indices), dtype='float32')
        # Compare aligned timbral and harmonic contexts before/after the seam.
        for offset in range(-off, off+1, max(1, off//5)):
            ia = indices + offset
            ib = ia + k
            scores += .35*np.sum(C[:, ia]*C[:, ib], axis=0)
            scores += .65*np.sum(M[:, ia]*M[:, ib], axis=0)
        scores /= len(range(-off, off+1, max(1, off//5)))
        n = min(4, len(scores))
        leaders = np.argpartition(scores, -n)[-n:]
        for pos in leaders:
            picks.append({'score': round(float(scores[pos]), 6),
                          'left_crossfade_start': round(float(times[indices[pos]]), 6),
                          'right_source_start': round(float(times[indices[pos]+k]), 6)})
    picks.sort(key=lambda c: c['score'], reverse=True)
    distinct = []
    for p in picks:
        if all(abs(p['left_crossfade_start'] - x['left_crossfade_start']) > 1.0 or
               abs(p['right_source_start'] - x['right_source_start']) > 1.0
               for x in distinct):
            distinct.append(p)
        if len(distinct) >= top:
            break
    return distinct


def refine_waveform(source: Path, candidates: list[dict],
                    duration: float, fade: float, target: float) -> list[dict]:
    """Resolve sub-frame right-side phase; match a 2-second PCM neighborhood.

    Waveform correlation is supporting evidence only; mixes can differ between
    repeats, and this method contains no vocal detector or musical beat parser.
    """
    from scipy.signal import correlate
    sr = 5512
    raw = subprocess.check_output(['ffmpeg', '-nostdin', '-loglevel', 'error',
                                   '-i', str(source), '-ar', str(sr), '-ac', '1',
                                   '-f', 'f32le', 'pipe:1'])
    mono = np.frombuffer(raw, dtype='<f4')
    margin = round(.45*sr)
    span = round(2*sr)
    refined = []
    for candidate in candidates:
        left = candidate['left_crossfade_start']
        right = candidate['right_source_start']
        a = round((left-1)*sr)
        b = round((right-1)*sr)
        if a < 0 or b < margin or b+span+margin > len(mono):
            continue
        x = mono[a:a+span].astype('float64')
        y = mono[b-margin:b+span+margin].astype('float64')
        cor = correlate(y, x, mode='valid', method='fft')
        squares = np.r_[0., np.cumsum(y*y)]
        denominator = np.sqrt(np.maximum((squares[span:]-squares[:-span])*np.dot(x,x),1e-15))
        score = cor / denominator
        ix = int(np.argmax(score))
        aligned_right = right + (ix-margin)/sr
        try:
            geometry = candidate_geometry(left, aligned_right, fade, duration)
        except ValueError:
            continue
        if geometry['duration_seconds'] > target-.04:
            continue
        refined.append({**candidate, 'right_source_start': round(aligned_right, 6),
                        'waveform_correlation': round(float(score[ix]), 6),
                        'phase_adjustment_seconds': round((ix-margin)/sr, 6),
                        'proposed_geometry': geometry})
    refined.sort(key=lambda c: (.65*c['score'] + .35*max(c['waveform_correlation'],0)),reverse=True)
    return refined


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--features', type=Path, required=True, help='features.npz from analysis/analyze.py')
    ap.add_argument('--source', type=Path, required=True, help='Original audio, for PCM refinement + checksum')
    ap.add_argument('--target', type=float, default=150.)
    ap.add_argument('--tolerance', type=float, default=12., help='How many extra seconds shorter than target to search')
    ap.add_argument('--min-intro', type=float, default=30.)
    ap.add_argument('--min-outro', type=float, default=25.)
    ap.add_argument('--fade', type=float, default=.12)
    ap.add_argument('--out', type=Path, default=Path('out/analysis/one_cut_suggestions.json'))
    args = ap.parse_args()
    import soundfile as sf
    with sf.SoundFile(args.source) as s:
        duration = len(s)/s.samplerate
    picks = scan(args.features, duration, args.target, args.tolerance,
                 args.min_intro, args.min_outro, top=50)
    suggestions = refine_waveform(args.source, picks, duration, args.fade, args.target)
    h = hashlib.sha256()
    with args.source.open('rb') as f:
        for chunk in iter(lambda: f.read(1048576), b''):
            h.update(chunk)
    result = {'source_name': args.source.name, 'source_sha256': h.hexdigest(),
              'source_seconds': duration, 'target_seconds': args.target,
              'status': 'algorithmic_suggestions_only_not_human_approved',
              'caveats': 'No vocal identification or guaranteed musical phrasing; audition before acceptance',
              'candidates': suggestions[:10]}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False)+'\n',encoding='utf-8')
    for i, c in enumerate(result['candidates'], 1):
        print(f"{i:2}: {c['left_crossfade_start']:.3f} -> {c['right_source_start']:.3f}  "
              f"length {c['proposed_geometry']['duration_seconds']:.3f}s  "
              f"context={c['score']:.3f} waveform={c['waveform_correlation']:.3f}")
    print(f'Wrote {args.out}; inspect and audition; not automatically approved.')


if __name__ == '__main__':
    main()
