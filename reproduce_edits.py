#!/usr/bin/env python3
"""Reproduce manifest-defined music edits using source PCM and linear crossfades.

The original A/B/C renderer algorithm is deliberately preserved (including its
sample rounding, fade endpoints, PCM_24 intermediate and libmp3lame -qscale:a 0).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf

DEFAULT_MANIFEST = Path(__file__).parent / "examples" / "seatrus" / "manifest.json"


def fmt(seconds: float) -> str:
    return f"{int(seconds // 60)}:{seconds % 60:06.3f}"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def render(source_audio: np.ndarray, sr: int, segments: list, fades: list) -> tuple[np.ndarray, list]:
    if not segments or len(fades) != len(segments) - 1:
        raise ValueError("Each join must have one crossfade duration")
    duration = len(source_audio) / sr
    last = -1.0
    for start, end in segments:
        if not 0 <= start < end <= duration + 1 / sr or start < last:
            raise ValueError(f"Invalid or out-of-order source segment: {[start, end]}")
        last = end
    pieces = [source_audio[int(round(a * sr)):int(round(b * sr))].copy()
              for a, b in segments]
    if any(not len(p) for p in pieces):
        raise ValueError("A segment is empty")
    result = pieces[0]
    junctions = []
    for i, piece in enumerate(pieces[1:]):
        n = int(round(fades[i] * sr))
        previous_length = len(result)
        if n < 0 or n > min(previous_length, len(piece)):
            raise ValueError("Invalid crossfade duration")
        if n:
            t = np.linspace(0, 1, n, endpoint=True, dtype="float32")[:, None]
            overlap = result[-n:] * (1 - t) + piece[:n] * t
            result = np.concatenate([result[:-n], overlap, piece[n:]], axis=0)
        else:
            result = np.concatenate([result, piece], axis=0)
        junctions.append((previous_length - n) / sr)
    return result, junctions


def labels_for(spec: dict, junctions: list[float]) -> str:
    labels = []
    for i, (t, fade) in enumerate(zip(junctions, spec["crossfades"]), 1):
        left = spec["segments"][i - 1][1]
        right = spec["segments"][i][0]
        labels.append(f"{t:.3f}\t{t:.3f}\tSplice {i}: source {left:.2f}s to {right:.2f}s (crossfade {fade:.2f}s)")
    return "\n".join(labels) + ("\n" if labels else "")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--source", type=Path, help="Path to original MP3 (overrides manifest relative path)")
    parser.add_argument("--outdir", type=Path, default=Path("out"))
    parser.add_argument("--variants", nargs="+", help="Manifest variant names (defaults to all)")
    parser.add_argument("--labels-only", action="store_true", help="Print joins and write Audacity labels without decoding")
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    keys = args.variants or list(manifest["variants"])
    for key in keys:
        if key not in manifest["variants"]:
            parser.error(f"Unknown variant {key}; options: {', '.join(manifest['variants'])}")
    args.outdir.mkdir(parents=True, exist_ok=True)
    source = args.source or args.manifest.parent / manifest["source_name"]
    if args.labels_only:
        audio, sr = None, None
    else:
        if not source.is_file():
            parser.error(f"Source not found: {source}. Pass --source PATH.")
        expected_hash = manifest.get("source_sha256")
        if expected_hash and sha256_file(source) != expected_hash:
            parser.error(f"Source SHA-256 mismatch: {source}")
        if not shutil.which("ffmpeg"):
            parser.error("ffmpeg executable not found in PATH")
        audio, sr = sf.read(source, dtype="float32", always_2d=True)
        if abs(len(audio) / sr - manifest["source_seconds"]) > 0.1:
            parser.error("Source duration differs from manifest")
        print(f"Source: {source} ({len(audio)/sr:.3f}s, {sr} Hz)")

    for key in keys:
        spec = manifest["variants"][key]
        if args.labels_only:
            junctions = spec["junction_output_seconds"]
        else:
            pcm, junctions = render(audio, sr, spec["segments"], spec["crossfades"])
            if abs(len(pcm)/sr - spec["duration_seconds"]) > 0.002:
                raise ValueError(f"Duration mismatch: {key}")
            for actual, expected in zip(junctions, spec["junction_output_seconds"]):
                if abs(actual - expected) > 0.002:
                    raise ValueError(f"Junction mismatch: {key}")
            with tempfile.TemporaryDirectory() as temp_dir:
                wav = Path(temp_dir) / "render.wav"
                sf.write(wav, pcm, sr, subtype="PCM_24")
                target = args.outdir / spec["output"]
                subprocess.run(["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-i", str(wav),
                                "-codec:a", "libmp3lame", "-qscale:a", "0", str(target)], check=True)
            print(f"{key}: {fmt(len(pcm)/sr)} -> {target}")
        for i, t in enumerate(junctions, 1):
            print(f"  splice {i}: {fmt(t)} (crossfade begins)")
        label_path = args.outdir / (key + "_audacity_labels.txt")
        label_path.write_text(labels_for(spec, junctions), encoding="utf-8")
        print(f"  labels: {label_path}")


if __name__ == "__main__":
    main()
