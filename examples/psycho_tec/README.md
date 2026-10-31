# PSYCHO.TEC- — approved Candidate A (2026-10-31)

**Source:** TeKno.loji — *JKCD006 PSYCHO.TEC- E.P.*, track 04, *PSYCHO.TEC-*.

**Owner evaluation:** **A approved**. Exact feedback: “psycotec  A approved - nice work.” Approval is for the **complete edit**. Only Candidate A was produced; no B/C were generated or evaluated.

## Source-pinned edit

| Property | Value |
| --- | --- |
| Original recording | **6:06.123311** (366.123310658 seconds), 44,100 Hz stereo |
| Edited MP3 (encoded container) | **2:25.633** (145.632653 seconds) |
| Edited PCM | **145.580702948 seconds** (6,420,109 samples/channel) |
| Retained original audio | **0–82.045** seconds; **302.467596–366.123310658** seconds |
| Source interval omitted | **82.045–302.467596** seconds |
| Edited-output splice | **1:21.925** (start of overlap, exactly sample 3,612,892) |
| Source match | left crossfade starts at **81.924989** seconds → later source at **302.467596** seconds |
| Crossfade | **120 ms**, linear PCM overlap, **5,292 samples** |
| Source SHA-256 | `ea4b202046cbd7f96699021f2adf8a04d9e89b1f0c6336437f61628f72cd9e25` |
| Reference MP3 SHA-256 | `2fde44a44de2a38c05fe81e0db0ac38bea619fad8b8db49612f82ec81f0cd034` |

The original opening, late energetic section, and mastered ending are retained. A single splice joins a repeated high-energy rhythmic phrase across the skipped middle section. The editor inspected multi-second spectral/phrase context, bass/drum timing and short-window stereo waveform alignment, including sustained instrument continuity concerns learned from Seraphim. Correlation (~0.762) is a technical diagnostic, **not** an algorithmic approval score; the owner's listening result is authoritative.

The [source-pinned manifest](manifest.json) also records the *exact sample indices* of both retained pieces and the overlap. [Audacity labels](A_one_repeat_join_audacity_labels.txt) identify the **start** of the overlap on the **edited** timeline, not the end of the earlier source region. The [QC report](A_one_repeat_join_qc.json) records geometry, original-file checksum, output checksum and the verification.

## Reproduce

Install Python 3.10+, NumPy, an MP3-capable soundfile build and FFmpeg as described in the repository root, and obtain the **exact original audio recording** matching the manifest's SHA-256. Run from repository root:

```sh
python scripts/render_one.py \
  --manifest examples/psycho_tec/manifest.json \
  --variant A_one_repeat_join \
  --source "/path/to/TeKno.loji - -JKCD006- PSYCHO.TEC- E.P. - 04 PSYCHO.TEC-.mp3" \
  --outdir out/psycho_tec_A --max-seconds 150
```

This makes the full A MP3, the ~7s-before / 9s-after splice audition, output-relative Audacity labels and JSON QC. Exact geometry uses source float32 stereo PCM with `round(seconds * sample_rate)` slicing, a 120ms linear overlap, 24-bit intermediate WAV and `libmp3lame -qscale:a 0`, with no pitch or tempo changes.

**Byte-exact local reproduction was independently checked:** regenerating this edit from the source and the committed splice geometry produced the same SHA-256 `2fde44a44de2a38c05fe81e0db0ac38bea619fad8b8db49612f82ec81f0cd034` and 4,883,005-byte output. FFmpeg/LAME version differences can change encoded MP3 bytes, so source checksum, PCM geometry and decoded duration remain the portable reproducibility tests.

## Lessons / limits

This was a one-candidate approval at the default **≤2:30** target. Unlike Seraphim A, no objectionable held-note entrance was reported by the owner. It reinforces selecting musically coherent sections and phase-aligned overlap, but doesn't establish a new generalized matching threshold or require a new tool. Maintain the [one-candidate workflow](../../docs/one_candidate_workflow.md); do not generate variants automatically.

The original source MP3, edited MP3, auditions, WAV intermediates and analysis caches are **not** committed.
