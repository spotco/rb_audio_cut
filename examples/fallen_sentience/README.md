# Fallen Sentience — B approved; A acceptable with a flaw

**2026-10-31 evaluation:** Titanium Ʌngel — *Ʌngelic Mechanism*, track 02, Fallen Sentience. Original: **3:42.551**, 44,100 Hz stereo. The input SHA-256 is pinned in [manifest.json](manifest.json); original audio and generated MP3s are **not** committed.

| Variant | Encoded duration | Edited-output crossfade begins | Human result |
| --- | ---: | ---: | --- |
| A_one_repeat_join | **2:17.770** | **0:49.875** | Acceptable, but an unexpected piano entrance makes the join audible despite matching background beat |
| B_one_first_section_repeat_join | **3:09.492** | **0:55.900** | **Approved and preferred.** Owner: "very nice, consider B approved. cannot even hear it." |

A is **not** retroactively classified as rejected. B was requested *after* evaluating A; the user explicitly allowed 2:30–3:30 for a cleaner edit. This does **not** change the default <=2:30 limit for new songs.

## Edit and diagnosis

Both versions use a **single 120 ms linear overlap**, phase-aligned from the start of the overlap, preserving the intro and the unmodified original ending. No pitch/tempo changes.

- **A:** retain original **0–49.995** and **134.702577–222.551179** seconds, deleting ~84.828 seconds of timeline. Jumping from the first rhythmic section into the later piano-led section produced the surprising piano arrival.
- **B:** retain original **0–56.020** and **89.003455–222.551179** seconds, deleting ~33.103 seconds of timeline. B skips a repeated phrase **within the first energetic arrangement**, keeping the later piano material in the song's normal development.

**Source-to-source overlap match:** A begins at source **49.875 → 134.702577**; B begins at source **55.900 → 89.003455**. These are crossfade *starts*, not the earlier segment's end. B's fade ends at edited **0:56.020**.

**Timestamp correction:** A previous chat reply mistakenly called B's edited-output crossfade start **0:55.780**. The actual rendered PCM, [B's Audacity label](B_one_first_section_repeat_join_audacity_labels.txt), and manifest all establish **0:55.900**.

The stereo overlap correlation was approximately **0.781 for A** and **0.786 for B**. Both passed technical continuity checks, yet only B was described by the listener as imperceptible. Numeric beat/phase agreement does not validate active-instrumentation continuity, phrasing, or arrangement progression.

## Reproduce

Using the exact original MP3 (SHA-256 pinned in manifest), from repository root:

```sh
python scripts/render_one.py --manifest examples/fallen_sentience/manifest.json --variant A_one_repeat_join --source "/path/to/original.mp3" --outdir out/fallen_sentience_A --max-seconds 150
python scripts/render_one.py --manifest examples/fallen_sentience/manifest.json --variant B_one_first_section_repeat_join --source "/path/to/original.mp3" --outdir out/fallen_sentience_B --max-seconds 210
python scripts/inspect_join.py --manifest examples/fallen_sentience/manifest.json --variant B_one_first_section_repeat_join --source "/path/to/original.mp3"
```

The renderer reproduces MP3s, 7-second-before/9-second-after audition clips, and output-relative Audacity labels. [evaluation.json](evaluation.json) retains the owner's verbatim feedback. MP3 SHA may differ by FFmpeg/LAME version; source SHA and decoded sample geometry are authoritative.

## Carry forward

Compare several seconds of **active musical texture** on both sides of a join (piano, lead, vocals, fills, buildup), not just a matched drum loop or a 120 ms overlap. For an owner-approved longer limit, prefer a smaller **within-arrangement** repeated-passage deletion if it preserves the song's development. Do not overfit the automatic score to these two examples. See [arrangement continuity workflow](../../docs/arrangement_continuity.md).
