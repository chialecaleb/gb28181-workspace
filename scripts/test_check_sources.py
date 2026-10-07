"""Source integrity failures must not be silently accepted."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
import check_sources

class SourceTests(unittest.TestCase):
    def test_integrity_and_completeness(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            asset = root / 'docs/standards/GBT28181-2022/sample.pdf'
            asset.parent.mkdir(parents=True)
            asset.write_bytes(b'synthetic fixture')
            manifest = root / 'docs/standards/sources.json'
            entry = dict(path=asset.relative_to(root).as_posix(), bytes=asset.stat().st_size,
                         sha256=hashlib.sha256(asset.read_bytes()).hexdigest())
            manifest.write_text(json.dumps({'files': [entry]}), encoding='utf-8')
            self.assertEqual(check_sources.check(root)[0], [])
            asset.write_bytes(b'changed')
            self.assertTrue(any('changed' in e for e in check_sources.check(root)[0]))
            asset.unlink()
            self.assertTrue(any('Missing' in e for e in check_sources.check(root)[0]))
            (asset.parent / 'extra.png').write_bytes(b'extra')
            self.assertTrue(any('Unlisted' in e for e in check_sources.check(root)[0]))
            entry['path'] = '../outside.pdf'
            manifest.write_text(json.dumps({'files': [entry, entry]}), encoding='utf-8')
            errors = check_sources.check(root)[0]
            self.assertTrue(any('escapes' in e for e in errors))
            self.assertTrue(any('Duplicate' in e for e in errors))

if __name__ == '__main__':
    unittest.main()
