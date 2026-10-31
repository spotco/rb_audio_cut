# Agent instructions — rb_audio_cut

- Keep A/B/C edit manifest and `evaluation.json` authoritative; do not rewrite the listener feedback based on algorithmic predictions.
- A is accepted as a whole, B/C rejected due to noticeable vocal jumps. Do not declare splice quality from harmonic similarity alone.
- Maintain `reproduce_edits.py` behavior and the original audio SHA-256. Test exact clip geometry and source checksum whenever changing rendering.
- Source and manifest use source-relative seconds; splice labels are edited-output relative and mark **crossfade beginnings**.
- Don't commit generated MP3 cuts, WAV intermediates, caches, or extracted stems. They are derivable and may be large.
- `analysis/legacy/` is a verbatim snapshot of the first experiment and contains `/mnt/data/` paths; do not present it as polished CLI tooling.
- Keep the repository small. Before building sophisticated music intelligence, demonstrate improvements against human-evaluated samples.
- Do not claim an edit is human-approved until the owner listens and confirms it.

## Updated owner preference — one A first (2026-10-31)

- Default for new user-uploaded songs: produce **only one strongest A candidate**, with complete MP3, local audition(s), one edit manifest, Audacity labels, QA; **stop for human feedback**. Do not generate B/C unless A needs work or the owner requests variations.
- Source-relative segments, output-relative crossfade-start labels, preserve outro when practical. Use phase-aligned overlap (earlier source left_end - fade matches later source right_start), not just a time-based cut. Favor instrumental phrasing.
- Do not conflate **Flaming Sky B/C not listened** with the older **seatrus B/C rejected**. Flaming Sky A is owner-accepted **as a whole**, not separately certified at its single join. Preserve exact feedback.
- Read docs/one_candidate_workflow.md and examples/flaming_sky/README.md for the new accepted example. The helper scripts are provisional aids, not automated vocal-continuity gates.

## Fallen Sentience A/B result (owner evaluated, 2026-10-31)

- **A:** technically beat-aligned, 2:17.770, but piano entered unexpectedly at its cross-arrangement jump; owner called it acceptable with a reservation, **not rejected**.
- **B:** **approved and preferred**, 3:09.492, one 120 ms join within the original first energetic section at **0:55.900 edited-output fade start**; owner: "cannot even hear it." B was only made after A feedback and an **explicit** 2:30–3:30 relaxation; normal <=2:30 target remains in force otherwise.
- Prioritize consistency of *active instruments, section role, phrase arc and buildups* over a matched backing beat alone. Inspect several seconds on either side of the **source** join; stereo phase/correlation and click-free output cannot certify musical continuity.
- Do not install an automatic numeric threshold as an arrangement-quality gate. A and B correlations were ~0.781 and ~0.786 despite different human results. Manual owner listening is authoritative.
- `scripts/inspect_join.py` is a reusable source-pinned **diagnostic** (hash, geometry, overlap/RMS/edge), not a voice/instrument detector. See `docs/arrangement_continuity.md` and `examples/fallen_sentience/evaluation.json`.
- **Exact label correction:** the B fade begins at **0:55.900**, not 0:55.780 as mistakenly stated in an earlier chat reply; 0:56.020 is the end of its 120 ms overlap. Preserve the manifest/PCM values.

## Never Look Back A/B/C — vocal and bass-continuity lesson (2026-10-31)

- This is a **different song** from seatrus; preserve its own [exact evaluation](examples/never_look_back/evaluation.json): Never Look Back A rejected (visible/audible loudness and instrumental discontinuity), B **acceptable** despite a faint bass jump, C **approved and chosen**. Do not relabel B rejected or imply B and C were independently proposed before owner feedback.
- Owner explicitly relaxed the goal from ≤2:30 to **1:30–3:30** after A was rejected; C is 3:18.312 (encoded). The next song still defaults to one A and ≤2:30 until instructed otherwise.
- **New low-end lesson:** good matching inside a short 120 ms bass crossfade does not ensure the surrounding bass *phrase* continues. For B, short-fade bass correlation was ~0.96 but 1.2-second 35–170 Hz phrase-context correlation ~0.24; C moved both windows ~10 s later and reached ~0.91 in that longer context while maintaining ~0.95 inside fade. This is diagnostic, not a universal score threshold. Check active backing instruments, vocal phrase and low-end envelope over seconds on both sides.
- Exact source-hash-pinned A/B/C recipe, labels and C byte-exact rendering evidence are in `examples/never_look_back/`. No need to add speculative automatic gates or commit ephemeral analysis scripts/audio files.

## Binary source-audio transfer via GitHub Actions

- When an owner asks to add original MP3s to this public repository and the connected GitHub API cannot accept binary attachments, **do not assume upload is impossible**. Use the demonstrated **Base64 chunks → text-file GitHub connector → GitHub Actions reconstruction** workflow. See [docs/source_audio_transfer.md](docs/source_audio_transfer.md) for complete steps and verification checks.
- Specifically: stage numbered `.source_chunks/<slug>/*.b64` plus `index.json`; `.github/workflows/materialize-source.yml` calls `scripts/assemble_source.py` to reconstruct and verify SHA-256 **and exact size**, commit the source MP3 under `examples/<slug>/`, and delete staging chunks. The Never Look Back source upload proved this end-to-end (GitHub commits `0d11b985` and `b294b777`).
- Always read the existing source-pinned manifest, skip already uploaded matching originals, validate GitHub Actions completion and the final binary, and never claim success after merely staging the chunks. If byte transfer from the current runtime into connector calls is unavailable, report the actual limitation instead of claiming the approach cannot work in general.
