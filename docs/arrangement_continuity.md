# Arrangement continuity: the Fallen Sentience A → B lesson

This is a **human-evaluated case**, not an automatic arrangement classifier.

- **A:** 2:17.770, single 120 ms overlap at edited **0:49.875**. Beat/phase and no-click checks passed, overlap stereo correlation ~0.781. Listener found an unexpected piano entrance when the edit jumped into a later arrangement. **Acceptable with reservation**, not formally rejected.
- **B:** 3:09.492, overlap at edited **0:55.900**. Same fade method, correlation ~0.786. B removes a shorter (~33-second) repeated passage inside the *same opening energetic arrangement*, allowing the later piano section to develop normally. Owner **approved B** and reported not hearing the splice.

## Updated human-in-the-loop selection

1. Keep the default **single A first**. Do not generate speculative B/C. After specific feedback, revise only in the requested direction.
2. Match **section, active instrumentation, phrase and longer development**, as well as beat, harmony and waveform alignment. Inspect a few seconds *before and after* both source neighborhoods. Ask whether a piano, vocal, lead or fill appears unnaturally at the seam.
3. Prefer a repeat deletion **within the same arrangement** when a cross-arrangement skip would create an unprepared instrumentation change. Preserve the intro, buildup/breakdown and full outro where musically appropriate.
4. The default limit remains **<=2:30**. Only expand it (as for B's approved **2:30–3:30** window) on user request; don't silently break targets. If the target and natural flow conflict, get feedback.
5. Align the **start of the left overlap** with the incoming source start: left_end - fade → right_start. Verify output-relative Audacity labels at the fade beginning, PCM boundaries, source SHA, stereo, duration and audition clips.
6. Treat stereo correlation and continuity measurements as **diagnostics, not musical-quality gates**. Their near-equality here (A 0.781 vs B 0.786) demonstrates why such a threshold would not have identified the flaw.

The B investigation widened the skip window, compared chroma/MFCC passages with several seconds of context, refined waveform alignment over a ~4-second neighborhood, and checked source PCM / crossfade geometry. Those exploratory scripts were hardcoded to this session and are not generalized production utilities.

**Reusable utility added:** `scripts/inspect_join.py` reproduces checksum-guarded PCM checks, stereo overlap correlation, RMS mismatch and local sample-edge metrics for any manifest-defined variant. It does not judge piano/vocal/arrangement continuity and does not replace listening.

To broaden the repository's existing structural suggestion search under an **explicit** 3:30 maximum, use `analysis/suggest_one_cut.py --features ... --source ... --target 210 --tolerance 35`, then manually inspect longer phrase contexts. Algorithmic ranking is provisional.

See [source-pinned A/B comparison](../examples/fallen_sentience/README.md) and [exact feedback](../examples/fallen_sentience/evaluation.json).

## Never Look Back: short-fade bass match versus phrase-scale bass continuity

The [owner-evaluated A/B/C progression](../examples/never_look_back/README.md) adds a distinct failure mode. A's apparent beat/vocal-boundary match had an obvious **loudness and background instrumentation jump**, visible in Audacity; it was rejected. B moved to better-matched instrumentation after permission to use up to 3:30. B was owner-acceptable, but its bass pattern still jumped slightly. Despite ~0.96 bass waveform correlation *inside* the 120 ms fade, B's ~1.2-second 35–170 Hz neighborhood correlation was only ~0.24. Sliding both source splice windows later within the repeated phrase improved the longer bass-context correlation to ~0.91 and retained ~0.95 fade overlap correlation. The owner **approved C** (3:18.312) over B.

**Add this to manual inspection**: evaluate low-end phrase continuity (envelope, phase/cadence, note identity), levels and active instrumental/vocal content before and after both source windows over multiple beats, not just at overlap. If a splice sounds almost clean but a bass pattern changes, try sliding both endpoints in the repeated phrase while preserving the removal length, as in Seraphim, rather than adding EQ or lengthening the fade. Those correlation values are case-specific **diagnostics**, not validated thresholds or a guarantee of good vocal continuity. Human listening remains authoritative.
