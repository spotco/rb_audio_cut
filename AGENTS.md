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
