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

These were the first two accepted whole edits; later owner-evaluated examples below add further evidence but not a statistically meaningful automatic-success benchmark.

## Arrangement-continuity revision from Fallen Sentience (2026-10-31)

Owner feedback to A: "acceptable, but a little odd": the piano began unexpectedly even though the background beat aligned. A was **not rejected**. A revised B was permitted to run **2:30–3:30**, skipped a shorter same-arrangement passage, and was explicitly **approved** with the feedback "cannot even hear it." B is 3:09.492, one join whose edited-output crossfade starts at 0:55.900 (not the erroneous 0:55.780 quoted earlier).

**Required manual check for future cuts:** compare multi-second contexts before and after the join for instrument entrances, phrase/buildup logic, vocal/lead continuity and section role; a matching drum groove alone is insufficient. Try a smaller repeated-phrase removal within the same musical arrangement when an early-to-late jump suddenly changes the texture. Do not relax the user's duration cap unless explicitly authorized. First offer just A, then revise only on feedback.

The song-specific exploratory scan used wider skip durations and ~4-second phase/waveform contexts. The existing `analysis/suggest_one_cut.py` accepts `--target 210 --tolerance 35` to broaden a *user-authorized* 3:30 search; it still cannot detect arrangement changes. Optional `scripts/inspect_join.py --source ... --manifest ... --variant ...` reproduces numeric overlap and edge QC with checksum enforcement. Numeric scores **do not** certify acceptance; compare A (~0.781) vs B (~0.786). Full details: [arrangement continuity](arrangement_continuity.md) and [human evaluation](../examples/fallen_sentience/evaluation.json).

## New human-verified examples: Neogravity A and Seraphim A → B (2026-10-31)

- [**Realm of Neogravity A**](../examples/realm_of_neogravity/README.md): owner-approved single join at edited output **1:29.010**, MP3 **2:25.737**, preserving the intro and entire ending; no new algorithm or extra variants required.
- [**Seraphim A/B**](../examples/seraphim/README.md): A was **rejected** for an abrupt held-string-like note at **1:15.000**, although its rhythm and geometry fit. B moved **both** splice points roughly **7.2 seconds later within the same repeated musical phrase**, retaining approximately the same skipped length and the same **2:21.322** output. B's fade begins at **1:22.200**. The owner explicitly **approved B**.

**Revision rule:** If the overall structural jump makes musical sense but a particular instrumental note, sustain or lead entrance sounds abrupt, first **slide the paired splice windows along the repeated passage** (maintain nearly the same removed interval) to find a corresponding harmonic/phrase moment. Re-evaluate **several seconds of active instrumentation** around both source windows and phase-align the short overlap; don't only line up drums or optimize instantaneous waveform correlation. This can solve a localized musical discontinuity **without** exceeding the original duration cap. A longer, safer cut is a fallback only with owner permission. Store both rejected and accepted geometries and the owner's actual feedback; technical QC never overrides listening.

## Vocal/bass-heavy song finding: Never Look Back A → B → C (2026-10-31)

[Exact case and owner feedback](../examples/never_look_back/README.md). One A first was followed correctly: A was rejected for an obvious level and backing-instrument jump near its 1:32.816 join; only then did the owner allow **1:30–3:30**, and B was made at 2:25.345 (acceptable but bass jump faintly audible). After that specific feedback, C moved both splice windows ~10 seconds later within a repeated arrangement. C's join was at 2:35.680, resulting in a 3:18.312 MP3, and the owner explicitly chose C.

**Refinement:** Check bass waveform/envelope over about a second *around* both source windows, not just the overlap: B had short 120 ms bass correlation ~0.96, yet only ~0.24 contextual correlation across ~1.2 s in the 35–170 Hz band. C retained ~0.95 short-overlap correlation and improved long-context correlation to ~0.91. Compare voice, backing instruments, and phrase position too: a long-context bass score alone does not prove a seam sounds good. Do **not** add a fixed correlation gate based on this single case.

The default stays **one A first** and **≤2:30** absent user-authorized relaxation. C only followed B feedback, not speculative batch generation. Preserve the owner-status distinction A rejected / B acceptable / C approved. The original recording remains external; the manifest contains the source SHA-256 and exact sample-domain geometry.
