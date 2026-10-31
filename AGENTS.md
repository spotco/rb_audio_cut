# Agent instructions — rb_audio_cut

- Keep A/B/C edit manifest and `evaluation.json` authoritative; do not rewrite the listener feedback based on algorithmic predictions.
- A is accepted as a whole, B/C rejected due to noticeable vocal jumps. Do not declare splice quality from harmonic similarity alone.
- Maintain `reproduce_edits.py` behavior and the original audio SHA-256. Test exact clip geometry and source checksum whenever changing rendering.
- Source and manifest use source-relative seconds; splice labels are edited-output relative and mark **crossfade beginnings**.
- Don't commit generated MP3 cuts, WAV intermediates, caches, or extracted stems. They are derivable and may be large.
- `analysis/legacy/` is a verbatim snapshot of the first experiment and contains `/mnt/data/` paths; do not present it as polished CLI tooling.
- Keep the repository small. Before building sophisticated music intelligence, demonstrate improvements against human-evaluated samples.
- Do not claim an edit is human-approved until the owner listens and confirms it.
