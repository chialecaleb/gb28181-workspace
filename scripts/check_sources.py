"""Verify complete, byte-identical shared standards against the reviewed manifest."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIRS = ('docs/standards/GBT28181-2022', 'docs/standards/GB35114-2017')

def check(root):
    entries = json.loads((root / 'docs/standards/sources.json').read_text(encoding='utf-8'))['files']
    errors, seen = [], set()
    for entry in entries:
        name = entry['path']
        if name in seen:
            errors.append('Duplicate source: ' + name)
        seen.add(name)
        path = (root / name).resolve()
        if not path.is_relative_to(root.resolve()) or not any(name.startswith(d + '/') for d in SOURCE_DIRS):
            errors.append('Source path escapes source directories: ' + name)
            continue
        if not path.is_file():
            errors.append('Missing source: ' + name)
        elif path.stat().st_size != entry['bytes'] or hashlib.sha256(path.read_bytes()).hexdigest() != entry['sha256']:
            errors.append('Source content changed: ' + name)
    actual = {p.relative_to(root).as_posix() for d in SOURCE_DIRS for p in (root / d).rglob('*') if p.is_file()}
    errors.extend('Unlisted source: ' + name for name in sorted(actual - seen))
    return errors, len(seen)

def main():
    errors, count = check(ROOT)
    if errors:
        print('\n'.join(errors))
        return 1
    print(f'PASS: {count} source assets match their recorded SHA-256 and size')
    return 0

if __name__ == '__main__':
    sys.exit(main())
