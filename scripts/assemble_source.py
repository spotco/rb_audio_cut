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


def main():
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
