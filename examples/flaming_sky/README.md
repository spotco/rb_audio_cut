# Flaming Sky — accepted one-jump edit (2026-10-31)

Source: JinoBeats — Ʌngelic Mechanism, track 10, Flaming Sky (-Embers of Heaven- Long Ver.).

**Human evaluation:** A_one_repeat_join was accepted. Owner: "A is excellent. Going with this." B/C were **not listened to**, not rejected. A was accepted as an *entire edit*; its one splice was not individually rated.

## Exact approved A geometry

- Original recording: 304.437505669 s; 44,100 Hz stereo; SHA-256 in manifest.json.
- Retained source intervals: 0.000–91.000 and 246.939–304.437505669 s.
- Single linear overlap crossfade: 0.120 s.
- Crossfade starts at **90.880 s on the edited-output timeline**. This is the Audacity label, not the original source's jump time.
- Decoded output: 148.378503 s; reference MP3 duration: 148.428 s.
- Reference MP3 SHA-256: 1e04d4984e110323060bfce4f82f7dbcec6318a43aace69a3ffe424718f7b426.
- Intro and the entire mastered final section remain.

## What we actually did

1. Analyzed the audio's structure using chroma/MFCC/time-frequency plots, onset/rhythm cues and repeating timbral material. Searched for one jump long enough to meet the <=2:30 target.
2. Found repeated neighborhoods around original ~1:31 and ~4:07, then refined waveform alignment near those contexts.
3. Aligned the **earlier crossfade beginning** to the **later source start** (90.880 to 246.939 = 156.059 seconds). The left source segment ends 120 ms later at 91.000. Thus matching persists through the overlap, avoiding doubled/flammed drum transients.
4. Used float32 decoded stereo PCM, round(time * sample_rate) source slicing, a 0.12 s linear overlap, a 24-bit intermediate WAV and libmp3lame -qscale:a 0; no pitch or tempo modification.
5. Generated a 7 s before / 9 s after splice audition, Audacity labels and a checksum/duration QA report. The owner listened to full A and accepted it.

**Important limitation:** waveform correlation / harmonic similarity does *not* detect vocals or guarantee musical continuity. The successful whole-edit rating is not a validated prediction model.

## Reproduce the edit

Keep a local copy of the exact original MP3 (source hash pinned in manifest.json). From repository root:

    python scripts/render_one.py --manifest examples/flaming_sky/manifest.json --source "/path/to/original.mp3" --outdir out/flaming_sky

This produces one complete MP3, a splice audition, the Audacity label and QC JSON. The existing reproduce_edits.py is compatible with this manifest. FFmpeg build variation can alter MP3 hashes; sample positions and source hash remain authoritative.

The original Flaming Sky source file and the generated cuts are not included in this commit. Do not commit rendered MP3s, WAV intermediates, stems or analysis caches.

## Carry forward

For future tracks: first create one strong A candidate with one or the fewest musically sensible instrumental transitions, audition it, and stop for human feedback. Only explore B/C if A needs improvement or the owner explicitly asks. See docs/one_candidate_workflow.md.
