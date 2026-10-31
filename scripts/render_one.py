#!/usr/bin/env python3
"""Render one manifest variant, its splice auditions, Audacity labels, and QC.

This wraps reproduce_edits.render rather than introducing a second edit engine.
Never treats a candidate as human-accepted on the strength of numeric QC.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from reproduce_edits import labels_for, render, sha256_file  # noqa: E402


def encode_mp3(samples: np.ndarray, sr: int, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        wav = Path(td) / 'audio.wav'
        sf.write(wav, samples, sr, subtype='PCM_24')
        subprocess.run(['ffmpeg', '-nostdin', '-y', '-loglevel', 'error', '-i', str(wav),
                        '-codec:a', 'libmp3lame', '-qscale:a', '0', str(destination)], check=True)


def mp3_duration(path: Path) -> float:
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries',
                    'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1',
                    str(path)], text=True).strip())


def run(manifest_path: Path, source: Path | None, outdir: Path,
        variant: str | None = None, max_seconds: float = 150.,
        pre: float = 7., post: float = 9.) -> dict:
    if min(pre, post, max_seconds) <= 0:
        raise ValueError('Preview windows and duration limit must be positive')
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    options = manifest['variants']
    if variant is None:
        if len(options) != 1:
            raise ValueError('Multiple variants: specify --variant; single-A is the default workflow')
        variant = next(iter(options))
    if variant not in options:
        raise ValueError(f'Unknown variant {variant!r}')
    spec = options[variant]
    source = source or manifest_path.parent / manifest['source_name']
    if sha256_file(source) != manifest['source_sha256']:
        raise ValueError('Source SHA-256 mismatch; will not render from a different recording')
    audio, sr = sf.read(source, dtype='float32', always_2d=True)
    if sr != manifest['sample_rate_hz'] or abs(len(audio)/sr - manifest['source_seconds']) > .01:
        raise ValueError('Source sample rate / decoded duration mismatch')
    result, junctions = render(audio, sr, spec['segments'], spec['crossfades'])
    decoded_seconds = len(result) / sr
    if abs(decoded_seconds - spec['duration_seconds']) > .002:
        raise ValueError('Rendered PCM duration disagrees with manifest')
    if len(junctions) != len(spec['junction_output_seconds']) or any(
            abs(a-b) > .002 for a,b in zip(junctions, spec['junction_output_seconds'])):
        raise ValueError('Rendered splice times disagree with manifest')
    outdir.mkdir(parents=True, exist_ok=True)
    output = outdir / spec['output']
    encode_mp3(result, sr, output)
    encoded_seconds = mp3_duration(output)
    if encoded_seconds > max_seconds:
        output.unlink(missing_ok=True)
        raise ValueError(f'Encoded file {encoded_seconds:.3f}s exceeds {max_seconds:.3f}s')
    label_file = outdir / (variant + '_audacity_labels.txt')
    label_file.write_text(labels_for(spec, junctions), encoding='utf-8')
    clips = []
    audition_labels = []
    montage_seconds = 0.
    audition_paths = []
    for idx, t in enumerate(junctions, 1):
        first = max(0, round((t - pre) * sr))
        last = min(len(result), round((t + post) * sr))
        clip = result[first:last]
        individual = outdir / 'auditions' / f'{variant}_splice_{idx}.mp3'
        encode_mp3(clip, sr, individual)
        audition_paths.append(individual.name)
        audition_t = montage_seconds + t - first / sr
        audition_labels.append(f'{audition_t:.3f}\t{audition_t:.3f}\tSplice {idx}: edited output {t:.3f}s (fade begins)')
        clips.append(clip)
        montage_seconds += len(clip) / sr
        if idx < len(junctions):
            silence = np.zeros((round(1.25 * sr), result.shape[1]), dtype='float32')
            clips.append(silence)
            montage_seconds += len(silence) / sr
    montage = outdir / (variant + '_splice_auditions.mp3')
    if clips:
        encode_mp3(np.concatenate(clips, axis=0), sr, montage)
    (outdir / (variant + '_audition_labels.txt')).write_text(
        '\n'.join(audition_labels) + ('\n' if audition_labels else ''), encoding='utf-8')
    report = {
        'variant': variant, 'source_sha256': manifest['source_sha256'],
        'human_approval': 'not_determined_by_this_tool',
        'decoded_seconds': decoded_seconds, 'encoded_seconds': encoded_seconds,
        'output_sha256': sha256_file(output),
        'splice_output_seconds': junctions, 'audition_individual': audition_paths,
        'audition_montage': montage.name if clips else None,
        'audacity_labels': label_file.name, 'max_seconds': max_seconds,
        'checks': 'passed: source hash, manifest geometry, MP3 duration',
    }
    (outdir / (variant + '_qc.json')).write_text(json.dumps(report, indent=2) + '\n')
    return report


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--manifest', type=Path, required=True)
    ap.add_argument('--source', type=Path, help='Original audio; defaults to manifest-relative source_name')
    ap.add_argument('--outdir', type=Path, default=Path('out/single'))
    ap.add_argument('--variant', help='Optional when manifest contains only one variant')
    ap.add_argument('--max-seconds', type=float, default=150.)
    ap.add_argument('--pre', type=float, default=7.)
    ap.add_argument('--post', type=float, default=9.)
    args = ap.parse_args()
    report = run(args.manifest, args.source, args.outdir, args.variant,
                 args.max_seconds, args.pre, args.post)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
