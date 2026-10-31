# Jouxl Eterna — Realm of Neogravity (A approved)

**Human evaluation (2026-10-31): approved.** After hearing A, the owner said: “candidate A is great.” This is approval of the **whole edit**, not independent certification of a splice classifier.

## Source and exact A geometry

- Original: **5:56.013401**, 44,100 Hz, stereo. Exact source name, size and SHA-256 are in [manifest.json](manifest.json).
- Retain source **0.000–89.130s** and **299.337278912–356.013401361s**.
- Single **120 ms** linear overlap; left fade begins at **89.010s edited output**, aligns with right source **299.337278912s**. This beginning is what the Audacity label marks.
- Removed source interval: **89.130–299.337278912s**; offset skipped across fade starts is **210.327278912s**.
- Rendered PCM duration **145.686122449s**; reference encoded MP3 container duration **145.737143s (2:25.737)**.
- Original opening and full original outro retained. Original tempo/pitch unchanged.
- At the evaluated join, rhythmic/synth repeat matching and a short overlap worked; the owner accepted the result. This does **not** mean that a waveform correlation score is sufficient to assess other songs.

## Reproduce from the original MP3

From the repository root with Python, soundfile, NumPy and FFmpeg installed:

```sh
python scripts/render_one.py \
  --manifest examples/realm_of_neogravity/manifest.json \
  --variant A_one_repeat_join \
  --source "/path/to/Jouxl Eterna - -JKCD004- Realm of Neogravity E.P. - 05 Realm of Neogravity.mp3" \
  --outdir out/realm_of_neogravity_A --max-seconds 150
```

The renderer checks source SHA-256, duration and splice geometry, writes **one** MP3, its ~7s-before/~9s-after splice audition, Audacity labels and QC JSON. Use [A's Audacity labels](A_one_repeat_join_audacity_labels.txt) to inspect the exact output-timeline crossfade beginning. Encoder versions may change output MP3 bytes; the sample-domain geometry and source checksum are authoritative. Reference output SHA-256 and exact frame indices are in the manifest.

No source MP3, rendered MP3, intermediate WAV, or analysis cache is committed.
