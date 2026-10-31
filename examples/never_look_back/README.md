# Never Look Back — A rejected, B acceptable, C approved (2026-10-31)

**Track:** BSLick — Never Look Back (feat. Ari<3), from *The Grand Eggspress OST*.

The owner explicitly selected **C** after comparing three sequential candidates. A was rejected for an obvious level and instrumentation jump; B was acceptable despite a subtle bass jump; C was approved as the preferred full edit. Do not reinterpret these judgments or treat analytical scores as approvals.

| Version | Encoded MP3 | Fade start (edited output) | Source retained before/after jump | Owner verdict |
| --- | ---: | ---: | --- | --- |
| A | 2:21.168 | 1:32.816 | 0–92.936 / 255.672–303.979 s | **Rejected**: loudness and background instruments jump |
| B | 3:18.144 | 2:25.345 | 0–145.465 / 251.220–303.979 s | **Acceptable**, subtle bass change |
| **C** | **3:18.312** | **2:35.680** | **0–155.800 / 261.394–303.979 s** | **Approved, preferred** |

Every candidate retains the **original opening and ending**, with just one 120 ms linear stereo crossfade. No stretch, pitch shift, source separation, volume normalization, or multiband processing was applied. The three geometries and sample indices are in [manifest.json](manifest.json); exact owner's words are in [evaluation.json](evaluation.json). Audacity labels refer to the **beginning** of the overlap on the edited timeline.

## What changed and why

- **A → B:** the first splice at 1:32.816 in A joined a visibly and audibly louder, different instrumental arrangement. Beat and crossfade alignment were not sufficient. After explicit permission to use 1:30–3:30, move the single structural splice to later, more closely matched backing sections.
- **B → C:** B's bass overlapped neatly *within the 120 ms fade* (low-end correlation ~0.96), yet the owner heard the bass pattern jump. Looking at **approximately 1.2 seconds of 35–170 Hz context** showed B's surrounding bass correspondence was only ~0.24. Moving both source junctions ~10 s later, in the same repeated arrangement, improved this context measure to ~0.91 (with ~0.95 bass overlap correlation). C retained approximately the same edited length and the owner preferred it.
- **Selection lesson:** for bass-heavy/vocal music, compare pre/post phrase-scale low-frequency patterns, level/envelope, vocals, and full backing instruments. Similarity through a short crossfade is only local. The metrics here are diagnostic and **not** validated quality thresholds. Listener approval remains the gate.
- **Workflow:** A was generated alone first. B was offered only after A rejection and the duration relaxation; C only after feedback that B's bass was mildly audible. This is *not* a request to routinely generate three candidates.

## Reproduction

Original source file is **not committed**; use the exact supplied recording, SHA-256:
`09ac8101ecad8fd46e122e3de151bf800da2fdeea2acf4290e03147047566f1f`

Format: 48,000 Hz stereo, 303.978666667 s decoded, 5,742,217 bytes. Run from repository root with Python/NumPy/soundfile/FFmpeg installed:

```sh
python scripts/render_one.py \
  --manifest examples/never_look_back/manifest.json \
  --variant C_later_bass_coherent_repeat_join \
  --source "/path/to/BSlick - Never Look Back (feat. Ari-3) - from The Grand Eggspress OST.mp3" \
  --outdir out/never_look_back_C --max-seconds 210 --pre 10 --post 12
```

Use `--variant A_vocal_phrase_boundary` with `--max-seconds 150`, or `--variant B_same_arrangement_repeat_join` with `--max-seconds 210` to reproduce earlier edits. Default preview durations in `render_one.py` are 7 s before/9 s after; the delivered C splice audition used 10 s before/12 s after.

**Verification:** Independently decoded the source, reconstructed C with the repository's exact linear-overlap geometry, encoded using PCM_24 + `libmp3lame -qscale:a 0`, and compared the result with the delivered C MP3: **byte-for-byte identical**, 5,296,316 bytes, SHA-256 `0d834edc5ad5ac897019e685d5518c1239556eff26eae10443e5757bdb047033`, 198.312 s encoded. See [qc.json](qc.json). Different encoder versions may produce different MP3 bytes even when the source samples and geometry match.

Only the manifest, evaluation, QC, labels and lessons are committed; not the source audio, rendered MP3s, audition clips, analysis caches or exploratory hardcoded scripts.
