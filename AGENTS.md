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
