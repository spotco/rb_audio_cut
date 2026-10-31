#!/usr/bin/env python3
"""Experimental harmonic/spectral self-similarity extraction for an arbitrary song.

Produces features.npz and song_map.png for inspection. This is candidate evidence,
not an automatic vocal-aware splice selector and not a quality certification.
"""
import argparse
from pathlib import Path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("source", type=Path, help="MP3, FLAC, or WAV")
    p.add_argument("--outdir", type=Path, default=Path("out/analysis"))
    p.add_argument("--resolution", type=float, default=0.25, help="feature interval (seconds)")
    args = p.parse_args()
    if args.resolution <= 0:
        p.error("--resolution must be positive")
    args.outdir.mkdir(parents=True, exist_ok=True)

    import numpy as np
    import librosa
    from scipy import ndimage
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    y, sr = librosa.load(str(args.source), sr=11025, mono=True)
    hop = 512
    rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=hop)[0]
    onset = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop)
    chroma = librosa.feature.chroma_stft(y=y, sr=sr, hop_length=hop, n_fft=4096, tuning=None)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=14, hop_length=hop, n_fft=2048)
    _, beats = librosa.beat.beat_track(onset_envelope=onset, sr=sr, hop_length=hop, trim=False, units="time")
    times = np.arange(0, len(y)/sr, args.resolution)
    index = np.minimum((times*sr/hop).astype(int), chroma.shape[1] - 1)
    C = ndimage.gaussian_filter1d(chroma, 3, axis=1)[:, index]
    M = ndimage.gaussian_filter1d(mfcc, 3, axis=1)[:, index]
    C /= np.linalg.norm(C, axis=0, keepdims=True) + 1e-8
    M = (M - np.mean(M, axis=1, keepdims=True)) / (np.std(M, axis=1, keepdims=True) + 1e-5)
    M /= np.linalg.norm(M, axis=0, keepdims=True) + 1e-8
    similarity = 0.5 * (C.T @ C) + 0.5 * (M.T @ M)
    harmonic = C.T @ C
    np.fill_diagonal(harmonic, 0)

    fig, ax = plt.subplots(3, 1, figsize=(17, 13), gridspec_kw={"height_ratios": [1, 2.5, 1]})
    ax[0].plot(np.arange(len(rms)) * hop / sr, rms, linewidth=.8)
    ax[0].set_ylabel("RMS")
    ax[0].set_xlim(0, len(y)/sr)
    ax[1].imshow(harmonic, origin="lower", extent=[0, times[-1], 0, times[-1]],
                 aspect="auto", cmap="magma", vmin=.4, vmax=1)
    ax[1].set_title("Harmonic similarity")
    ax[1].set_ylabel("Song time (s)")
    ax[1].set_xlabel("Song time (s)")
    ax[2].plot(np.arange(len(onset)) * hop / sr, onset, linewidth=.8)
    ax[2].set_ylabel("Onset")
    ax[2].set_xlim(0, len(y)/sr)
    fig.savefig(args.outdir / "song_map.png", dpi=130, bbox_inches="tight")
    plt.close(fig)
    np.savez_compressed(args.outdir / "features.npz", C=C, M=M, times=times, rms=rms,
                        onset=onset, beats=beats, similarity=similarity, sr=sr, hop=hop)
    print(f"Created {args.outdir/'features.npz'} and {args.outdir/'song_map.png'}")


if __name__ == "__main__":
    main()
