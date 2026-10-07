"""Exercise safe updates using real disposable local Git repositories, without network."""
import contextlib
import io
import subprocess
import tempfile
import unittest
from pathlib import Path
import workspace

class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        base = Path(self.temp.name)
        self.root = base / 'workspace'
        self.root.mkdir()
        self.upstream = base / 'upstream'
        subprocess.run(['git', 'init', '-q', '-b', 'main', str(self.upstream)], check=True)
        workspace.git(self.upstream, 'config', 'user.name', 'Fixture')
        workspace.git(self.upstream, 'config', 'user.email', 'fixture@example.invalid')
        self.commit(self.upstream, 'initial')
        self.entry = dict(path='gb28181-test', branch='main', url=str(self.upstream))
        self.path = self.root / self.entry['path']

    def commit(self, repo, content):
        (repo / 'README.md').write_text(content, encoding='utf-8')
        workspace.git(repo, 'add', 'README.md')
        workspace.git(repo, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', content)

    def sync(self, apply=True):
        with contextlib.redirect_stdout(io.StringIO()):
            workspace.sync(self.root, [self.entry], apply)

    def test_preview_clone_and_fast_forward(self):
        self.sync(False)
        self.assertFalse(self.path.exists())
        self.sync()
        self.commit(self.upstream, 'new upstream')
        self.sync()
        self.assertEqual(workspace.git(self.path, 'rev-parse', 'HEAD'), workspace.git(self.upstream, 'rev-parse', 'HEAD'))

    def test_dirty_branch_and_remote_are_preserved(self):
        self.sync()
        before = workspace.git(self.path, 'rev-parse', 'HEAD')
        local = self.path / 'scratch.txt'
        local.write_text('local work', encoding='utf-8')
        with self.assertRaisesRegex(RuntimeError, 'local changes'):
            self.sync()
        self.assertEqual(local.read_text(), 'local work')
        local.unlink()
        workspace.git(self.path, 'checkout', '-qb', 'feature')
        with self.assertRaisesRegex(RuntimeError, 'expected main'):
            self.sync()
        workspace.git(self.path, 'checkout', 'main')
        workspace.git(self.path, 'remote', 'set-url', 'origin', 'https://example.invalid/unexpected.git')
        with self.assertRaisesRegex(RuntimeError, 'origin does not match'):
            self.sync()
        self.assertEqual(workspace.git(self.path, 'rev-parse', 'HEAD'), before)

    def test_unpublished_and_divergent_commits_are_preserved(self):
        self.sync()
        self.commit(self.path, 'local commit')
        before = workspace.git(self.path, 'rev-parse', 'HEAD')
        with self.assertRaisesRegex(RuntimeError, 'unpublished/divergent'):
            self.sync()
        self.commit(self.upstream, 'remote divergence')
        with self.assertRaisesRegex(RuntimeError, 'unpublished/divergent'):
            self.sync()
        self.assertEqual(workspace.git(self.path, 'rev-parse', 'HEAD'), before)

    def test_path_and_non_repository_are_rejected(self):
        for name in ('../escape', 'gb28181-test/../../escape', '/absolute'):
            with self.assertRaises(RuntimeError):
                workspace.target(self.root, {**self.entry, 'path': name})
        self.path.mkdir()
        with self.assertRaisesRegex(RuntimeError, 'not an independent'):
            self.sync()

    def test_preflight_prevents_partial_clone_for_known_error(self):
        other = {**self.entry, 'path': 'gb28181-other'}
        (self.root / other['path']).mkdir()
        with self.assertRaises(RuntimeError):
            workspace.sync(self.root, [self.entry, other], True)
        self.assertFalse(self.path.exists())

if __name__ == '__main__':
    unittest.main()
