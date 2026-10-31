# First experiment — 終末を詠う少女

- Source: `source.mp3` (the original unedited 4:33 recording); SHA-256 in `manifest.json`.
- Render recipe: `manifest.json`, consumed by `../../reproduce_edits.py`.
- Human feedback: `evaluation.json` (A accepted; B/C rejected as vocal discontinuities).
- `labels/` contains the original Audacity label exports for A, B and C.
- `song_map.png`: visualization of harmonic self-similarity extracted from original audio.
- Exact reference renders are *not* committed. To recreate them, run `python reproduce_edits.py` at the repository root.
- Reference MP3 hashes in manifest depend on the original encoding environment; exact MP3 byte equality is not required across FFmpeg versions.
