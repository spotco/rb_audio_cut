#!/usr/bin/env python3
"""Reassemble exact original MP3 from temporary GitHub-transfer base64 chunks.

Does not change or remove chunk files. Checks SHA-256 before accepting output.
"""
import base64
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHUNKS = ROOT / '.source_chunks'
MANIFEST = ROOT / 'examples/seatrus/manifest.json'
SOURCE = ROOT / 'examples/seatrus/source.mp3'



def assemble_new_examples():
    """Assemble each explicitly staged example from its pinned manifest."""
    for folder in sorted(p for p in CHUNKS.iterdir() if p.is_dir()):
        slug = folder.name
        if not slug.replace('_', '').isalnum() or slug != slug.lower():
            raise ValueError(f'Invalid example slug: {slug}')
        info = json.loads((folder / 'index.json').read_text(encoding='utf-8'))
        manifest = json.loads((ROOT / 'examples' / slug / 'manifest.json').read_text(encoding='utf-8'))
        filename = manifest['source_name']
        if not filename or filename != Path(filename).name or '/' in filename or '\\' in filename:
            raise ValueError(f'Unsafe source filename: {filename!r}')
        expected = manifest['source_sha256']
        if info['source_sha256'] != expected or info['source_name'] != filename:
            raise ValueError(f'Source transfer metadata mismatch: {slug}')
        count = info['chunk_count']
        if type(count) is not int or count < 1 or count > 100:
            raise ValueError(f'Invalid source chunk count: {slug}')
        parts = sorted(folder.glob('*.b64'))
        if [p.name for p in parts] != [f'{i:04d}.b64' for i in range(count)]:
            raise RuntimeError(f'Incomplete source transfer chunks: {slug}')
        encoded = ''.join(''.join(p.read_text(encoding='ascii').split()) for p in parts)
        raw = base64.b64decode(encoded, validate=True)
        actual = hashlib.sha256(raw).hexdigest()
        if actual != expected or len(raw) != info['source_size_bytes']:
            raise RuntimeError(f'Source SHA-256 or size mismatch for {slug}: {actual}')
        target = ROOT / 'examples' / slug / filename
        if target.exists():
            if hashlib.sha256(target.read_bytes()).hexdigest() != expected:
                raise RuntimeError(f'Existing source checksum mismatch: {target}')
            print(f'Already verified source: {target}')
        else:
            target.write_bytes(raw)
            print(f'Materialized verified source: {target} ({len(raw)} bytes)')


def main():
    if CHUNKS.is_dir() and any(p.is_dir() for p in CHUNKS.iterdir()):
        assemble_new_examples()
        return
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    expected = manifest['source_sha256']
    if SOURCE.is_file():
        digest = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
        if digest == expected:
            print('Source already present and hash verified:', SOURCE)
            return
        raise RuntimeError(f'Existing source has incorrect SHA-256: {digest}')
    parts = sorted(CHUNKS.glob('*.b64'))
    if len(parts) != 12 or [x.name for x in parts] != [f'{i:04d}.b64' for i in range(12)]:
        raise RuntimeError(f'Expected 12 consecutively numbered source chunks, found {len(parts)}')
    encoded = ''.join(p.read_text(encoding='ascii') for p in parts)
    source = base64.b64decode(encoded, validate=True)
    actual = hashlib.sha256(source).hexdigest()
    if actual != expected:
        raise RuntimeError(f'Assembled MP3 SHA-256 mismatch: {actual} != {expected}')
    SOURCE.parent.mkdir(parents=True, exist_ok=True)
    SOURCE.write_bytes(source)
    print(f'Assembled {len(source)} bytes at {SOURCE}; SHA-256 verified')


if __name__ == '__main__':
    main()
