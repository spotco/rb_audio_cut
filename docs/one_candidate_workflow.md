# Single-A-first song shortening protocol

**Default:** user uploads a song and requests shortening to <=2:30 (unless otherwise specified). Produce **one** thoughtful A candidate first, with full MP3, splice audition, manifest and Audacity labels. Stop for listening feedback. Do not preemptively generate B and C.

1. **Validate the source:** exact source SHA-256, sample rate, channel count, decoded duration, target. Work from stereo source PCM and preserve the original ending whenever musically appropriate.
2. **Locate musical repetitions:** analyze phrasing, arrangement, instrumental breaks, recurring rhythms, harmony and waveform repeats. Try the minimum number of cuts. Existing analysis/analyze.py produces chroma/MFCC feature cache and song map. analysis/suggest_one_cut.py ranks repeat-matched **single jumps** near a target duration. Scores are evidence, not listening approval or vocal activity labels.
3. **Check the proposed join:** inspect both source neighborhoods. Prefer instrumental transitions and phrase boundaries. The old seatrus B/C edits sounded bad due to vocals jumping even though structural matches appeared plausible. Compare several seconds before and after each jump; preserve rhythmic buildup and the outro.
4. **Align the overlap properly:** waveform alignment must hold through the crossfade. If fade duration is f, match earlier time (left_end-f) with the later segment's right_start. Do **not** align only left_end to right_start; the overlap can flam transients. Prefer short fades, typically 0.12–0.25 s, but choose by ear and by material.
5. **Render just A:** author a single-variant reproduce_edits.py-compatible manifest with SHA-256, exact source-relative retained intervals, overlap length, expected decoded duration, output-relative crossfade-start label(s). Run scripts/render_one.py to make only the full A MP3, ~7s-before/9s-after audition(s), labels and QA JSON. Enforce the **encoded** MP3 duration <= the user limit. No tempo or pitch modification unless requested.
6. **Get human feedback:** present A and audition(s) for listening. Until feedback, keep status pending. Mark accepted/rejected for the complete edit exactly as owner reports; do not infer independent splice ratings. Make alternate candidates only when requested or in response to specific A criticism.
7. **Store lessons:** commit the source-pinned manifest, labels, descriptive evidence and evaluation; generated cuts, stems, WAV, caches, and source audio are not automatically committed. Never overwrite older owner ratings.

## Example CLI: one-jump discovery

    python -m pip install -r requirements-analysis.txt
    python analysis/analyze.py "/path/to/source.mp3" --outdir out/analysis
    python analysis/suggest_one_cut.py --features out/analysis/features.npz --source "/path/to/source.mp3" --target 150 --out out/analysis/one_cut_suggestions.json

The finder ranks aligned chroma/MFCC contexts plus sub-frame waveform correlation. It is experimental and makes no vocal-continuity or beat/phrase certification. Inspect its shortlist and refine chosen splice boundaries manually before committing a manifest.

Then render a single manifest variant:

    python scripts/render_one.py --manifest examples/flaming_sky/manifest.json --source "/path/to/original.mp3" --outdir out/flaming_sky

## Verified human findings

- **seatrus feat. 愛原圭織 — 終末を詠う少女:** A accepted as a whole; B/C rejected for obvious vocal jumps. Do not trust high structural similarity alone.
- **JinoBeats — Flaming Sky (Embers of Heaven Long Ver.):** A accepted as a whole, 2:28.428, one repeat-matched instrumental jump at output 1:30.880. Owner never listened to B/C. Demonstrates value of attempting a single strong cut before generating multiple variants.

These are two accepted whole edits, not a statistically meaningful automatic-success benchmark.
