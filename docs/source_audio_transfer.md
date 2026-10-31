# Source MP3 upload through the text-only GitHub connector

**Preferred fallback when the GitHub connector cannot directly upload binary files.** This workflow was demonstrated by the owner with *Never Look Back* on 2026-10-31 (staging commit `0d11b9855df8feac31286dc1c0eca3e6831d029c`, materialization commit `b294b7779778c965c4305092eda629c723cf3eb7`). Do not conclude source upload is impossible solely because GitHub's file-writing connector accepts UTF-8.

## Workflow

1. Confirm the owner has authorized source-audio storage in the **public** repository. Determine the original MP3's exact filename, byte count, and SHA-256 from the working-environment file. Compare them with the already-committed `examples/<slug>/manifest.json`. If the target MP3 already exists, verify its exact hash and skip it.
2. Base64-encode the **original MP3 bytes** without transcoding or shortening. Split the ASCII Base64 into reasonably sized text chunks that fit the connector's per-write limits (the demonstrated Never Look Back transfer used **8** chunks; do not hardcode 8 for larger sources). Ensure chunks are concatenated byte-for-byte in order with no missing characters.
3. Stage only the temporary text under `.source_chunks/<slug>/`: `0000.b64`, `0001.b64`, ..., plus `index.json`:
   ```json
   {
     "source_name": "Exact name from the manifest.mp3",
     "source_sha256": "<64-character sha256 from manifest>",
     "source_size_bytes": 12345678,
     "chunk_count": 8
   }
   ```
   Use the actual size and count. Stage complete batches atomically when possible (e.g. a staging branch and a single merged commit) to avoid repeated incomplete GitHub Actions runs. Never place temporary chunks in the final repository state.
4. When the complete chunk set reaches `main`, `.github/workflows/materialize-source.yml` runs `python scripts/assemble_source.py`. The script discovers staged slugs, checks `index.json` against each source-pinned manifest, reads numbered chunks in sorted order, Base64-decodes them, verifies **both byte size and SHA-256**, and writes the **original** MP3 to `examples/<slug>/<manifest.source_name>`.
5. The workflow commits the reconstructed binary MP3 and deletes `.source_chunks/`. Verify the GitHub Actions run succeeded, the final GitHub tree contains the MP3 with the correct size and source hash, and no chunks remain. If GitHub Actions is blocked or fails, report the incomplete state; do not claim the upload succeeded.
6. Do not modify existing approved edit manifests or human evaluation when transferring source files. Do not commit generated shortened MP3s, splice auditions, intermediate WAVs, or analysis caches.

## Why

This works with the existing GitHub text-file connector and a GitHub Actions runner. It does **not** require a PAT, local `git push` credentials, Git LFS for small MP3s, or a direct binary-upload API. SHA-256 + exact byte count are mandatory; file name/length alone are insufficient.

## Boundaries and common pitfalls

- Use only files explicitly selected by the owner and only if publication rights are confirmed.
- The existing workflow triggers on pushes to `main` touching `.source_chunks/**` (or the workflow file). The connector's per-file size limits and GitHub API rate limits can affect chunk sizing.
- `assemble_source.py` currently permits at most **100** parts per slug; confirm this before staging a larger file. `index.json` and the source-pinned manifest must agree exactly.
- Ensure the upload mechanism actually has access to source bytes. If the current environment cannot pass the encoded bytes into the GitHub connector, **report that operational limitation** rather than fabricating a successful transfer. This procedure describes the validated route, not a guarantee that every runtime can bridge local files to connector calls.
- GitHub's own Git object sizes, repository policies, and Action permissions still apply. Confirm the final post-action commit instead of relying only on a successful staging commit.

Reference: [GitHub Actions reconstruction workflow](../.github/workflows/materialize-source.yml), [source assembler](../scripts/assemble_source.py).
