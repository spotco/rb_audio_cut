# rb_audio_cut

Experimental music-shortening tools and a reproducible, human-evaluated first experiment.

**Status (2026-10-31):** Six owner-approved edits across seatrus (A), Flaming Sky (A), Fallen Sentience (B), Realm of Neogravity (A), Seraphim (B), and PSYCHO.TEC- (A). Seraphim A was rejected for an abrupt held-note-like entrance; the owner approved B after shifting the same structural cut ~7.2s later. Fallen Sentience A was acceptable with a reservation; seatrus B/C were rejected for vocal jumps; Flaming Sky B/C were not listened to. Candidate selection remains experimental; listening is the acceptance gate.

## Quick start

Requires Python 3.10+, FFmpeg in `PATH`, and an MP3-capable `soundfile` build.

```sh
python -m pip install -r requirements.txt
python reproduce_edits.py
```

This recreates **all three** candidate MP3s and Audacity-importable splice label files in `out/`. The 4:33 reference source lives at `examples/seatrus/source.mp3`; the cuts are **not** committed because they can be rendered from it.

Print the exact output-timeline splice times without decoding audio:

```sh
python reproduce_edits.py --labels-only
python reproduce_edits.py --labels-only --variants A_structure_and_outro
```

Import labels into Audacity with **File > Import > Labels**. Labels indicate **the start of each overlap crossfade**, not the midpoint. Original source timings and rendered output timings differ.

## Evaluated example: 終末を詠う少女

Song: seatrus feat. 愛原圭織 – 終末を詠う少女. Original duration ~4:33.36, 48 kHz stereo. See [`examples/seatrus/manifest.json`](examples/seatrus/manifest.json) for exact retained source segments, crossfades, outputs, and SHA-256; [`examples/seatrus/evaluation.json`](examples/seatrus/evaluation.json) records the owner's listening feedback.

| Candidate | Output length | Splice starts in output | Human evaluation |
|---|---:|---|---|
| **A_structure_and_outro** | **2:29.120** | **1:03.130, 1:06.730, 2:09.260** | **Accepted**: sounded great; instrumental transitions |
| B_one_splice_229 | 2:28.160 | 0:49.550 | Rejected: obvious vocal jump |
| C_repeated_vocal_214 | 2:13.830 | 0:34.470 | Rejected: obvious vocal jump |

**Lessons:** Harmonic or waveform similarity alone cannot validate vocal continuity. Prefer instrumental-to-instrumental transitions, or clean vocal phrase boundaries if necessary. Avoid cutting mid-syllable or across inconsistent breath, lyric, and articulation. This is one song, not evidence that these rules guarantee success elsewhere. A was accepted as a *whole edit*; its three junctions were not individually rated.

The exact original splice geometry for A is:

| Splice | Source jump | Crossfade |
|---|---|---:|
| 1 | 1:03.250 → 1:16.500 | 0.120 s |
| 2 | 1:20.750 → 2:51.250 | 0.650 s |
| 3 | 3:54.000 → 4:13.500 | 0.220 s |

## Reproducibility

The render is driven by source audio decoded into float32 stereo PCM. Segments are extracted with `round(seconds * sample_rate)` and joined by the original *linear overlap* crossfade. The output is encoded via 24-bit intermediate WAV, `ffmpeg -codec:a libmp3lame -qscale:a 0`. This preserves the methodology of the original A/B/C experiment (no generative audio, tempo changes, or pitch changes). MP3 bytes may differ with FFmpeg versions; source checksum and sample-domain splice times are the stronger reproducibility checks.

The manifest stores the original source SHA-256. `reproduce_edits.py` checks this hash before rendering. Reference output MP3 hashes are also retained for exact-environment comparisons.

```sh
python -m unittest discover -s tests -v
```

## Experimental analysis (optional)

These require additional dependencies and do **not** yet automatically select an acceptable splice:

```sh
python -m pip install -r requirements-analysis.txt
python analysis/analyze.py examples/seatrus/source.mp3
python analysis/scan_sections.py out/analysis/features.npz
python analysis/match.py out/analysis/features.npz --from-range 63 64 --to-range 76 77
```

`analysis/analyze.py` creates a similarity map and cached features. `analysis/scan_sections.py` proposes structural boundaries; `analysis/match.py` ranks potential musical similarities in two user-specified windows. The original exploratory scripts, with hardcoded `/mnt/data/` paths, remain under `analysis/legacy/` strictly for provenance; use the parameterized scripts for new songs. A reference [`song_map.png`](examples/seatrus/song_map.png) is included.

## Default workflow: one A first

After the Flaming Sky listening evaluation, **produce one carefully chosen A candidate, then stop for feedback**. Do not generate B/C until A is rejected or the owner requests alternatives. Include the full MP3, splice audition(s), an exact source-pinned manifest, Audacity labels, and QC. Favor instrumental repeat-matched jumps with crossfade-phase alignment; numerical similarity is *not* vocal-continuity or human acceptance.

- [Single-candidate protocol](docs/one_candidate_workflow.md) — reproducible future workflow and guardrails.
- [Approved PSYCHO.TEC- A](examples/psycho_tec/README.md) — single repeat-matched energetic-section join at edited output **1:21.925**, MP3 **2:25.633**; source-hash-pinned recipe, labels, QC and owner evaluation.
- [Approved Realm of Neogravity A](examples/realm_of_neogravity/README.md) — one join at edited 1:29.010, MP3 2:25.737.
- [Seraphim A rejected / B approved](examples/seraphim/README.md) — move *both* splice windows ~7.2s later to avoid a protruding sustained note without changing the output duration (B 2:21.322).

- [Approved Fallen Sentience B / A comparison](examples/fallen_sentience/README.md) — A's beat matched but piano entrance was surprising; B's within-arrangement splice was inaudible to the owner, at 3:09.492 with explicitly relaxed duration.
- [Arrangement continuity checklist](docs/arrangement_continuity.md) — examine active instrumentation and several-second phrase arcs, not just rhythmic or waveform similarity.
- [Optional join inspector](scripts/inspect_join.py) — source-pinned stereo overlap/edge diagnostics; not a musical quality gate.
- [Accepted Flaming Sky edit](examples/flaming_sky/README.md) — owner-approved A: **2:28.428**, one join at edited-output 1:30.880. B/C not listened to.
- [Single-cut suggestion tool](analysis/suggest_one_cut.py) — experimental structural shortlist from analysis feature cache, refined by waveform alignment.
- [Single-variant renderer](scripts/render_one.py) — one MP3, splice auditions, labels, and exact source/duration QC.

For a source audio that you own or otherwise have permission to use, start with:

```sh
python -m pip install -r requirements-analysis.txt
python analysis/analyze.py "/path/to/song.mp3" --outdir out/analysis
python analysis/suggest_one_cut.py --features out/analysis/features.npz --source "/path/to/song.mp3" --target 150
# Review one promising join, then author a one-variant manifest.
python scripts/render_one.py --manifest examples/flaming_sky/manifest.json --source "/path/to/flaming-sky-source.mp3" --outdir out/flaming_sky
```

As in the first experiment, do **not** commit generated cut MP3s, temporary WAVs, stems, or caches.

## Next steps

1. Evaluate on 2–3 more songs with explicit listening feedback, retaining accepted/rejected splice metadata.
2. Explore vocal activity and vocal-phrase boundaries (e.g. source separation), and apply large penalties to active-vocal joins.
3. Improve the single-A suggestion/preview/label workflow on additional human-evaluated songs, without treating algorithmic scores as approval.
4. Prefer few coherent edits over mechanically matching the target length; listener acceptance is the quality gate.

## Rights

The example source recording is included at the repository owner's request for reproduction. Its inclusion **does not grant redistribution or other rights** to third parties. Public hosting of copyrighted audio may require permission from the relevant rights holders.
