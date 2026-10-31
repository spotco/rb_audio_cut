# Xeveir and Xeron — Seraphim (B approved; A rejected)

**Human evaluation (2026-10-31):** A was rejected for a sudden string-like note at its splice; revised **B was approved** after listening: “yep - B is good. crazy work. what's the difference?” The suspected held-string instrument was the owner's perceptual description, **not** an independently verified isolated stem.

| Variant | Output MP3 | Output splice fade starts | Human result |
| --- | --- | --- | --- |
| A_one_repeat_join | **2:21.322** | **1:15.000** | **Rejected**: abrupt held-string-like note despite fitting structure |
| B_later_in_repeat_join | **2:21.322** | **1:22.200** | **Approved** |

## Exact source-pinned geometry

Source length **282.543900227s**, 44.1 kHz stereo; exact source SHA-256 in [manifest.json](manifest.json).

- **A (rejected):** retain original **0–75.120s** and **216.271–282.543900227s**; 120ms overlap starts at output **75.000s** (source 75.000 → 216.271). PCM duration 141.272902s.
- **B (approved):** retain original **0–82.320s** and **223.467–282.543900227s**; 120ms overlap starts at output **82.200s** (source 82.200 → 223.467). PCM duration 141.276893424s.
- B moves both ends of the same structural jump **~7.2 seconds later** along a repeated high-energy passage. A's repeated offset was 141.271s; B's was 141.267s (~4ms phase adjustment). The removed duration stays essentially unchanged, so the edit remains under **2:30** without the owner's optional longer allowance.
- Both keep the original opening and ending. No pitch or tempo change.
- Both passed sample alignment/encoded duration/PCM edge checks, but A's **musical** result was rejected. A's low-frequency overlap correlation was ~0.839, B's ~0.849; these figures are diagnostic, **not** musical-quality evidence. Avoid claiming the held-note source was objectively identified.

## Workflow learning from owner feedback

When a user says a splice is **structurally right but one note or instrument suddenly jumps out**, first shift **both** splice windows together along the repeated phrase, while keeping the same skipped musical offset. Evaluate sustained leads, harmonic tails and multi-second musical phrasing at the new time as well as beat alignment. Then refine short-overlap phase (here 120ms; ~4ms offset correction). **Only** if this does not work, consider a shorter same-arrangement deletion or ask whether to relax the duration limit. Never use a numerical correlation threshold as proof that the musical transition will be acceptable.

## Reproduce A or approved B

With the **exact original source** (hash pinned in the manifest) and current repository renderer:

```sh
python scripts/render_one.py \
  --manifest examples/seraphim/manifest.json \
  --variant B_later_in_repeat_join \
  --source "/path/to/Xeveir and Xeron - -JKCD002- Seraphim - 04 Seraphim.mp3" \
  --outdir out/seraphim_B --max-seconds 150
```

To regenerate rejected A for comparison, use `--variant A_one_repeat_join` and a different `--outdir`. Each run produces only its chosen variant, its 7s-before/9s-after audition, an output-relative Audacity label and QC JSON. Reference MP3 SHA-256 values are recorded in the manifest; MP3 encoders may give different file hashes. Labels: [A](A_one_repeat_join_audacity_labels.txt), [B](B_later_in_repeat_join_audacity_labels.txt).

Neither the source recording nor rendered MP3s, WAV intermediates, or caches are committed.
