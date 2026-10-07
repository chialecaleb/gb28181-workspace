"""Inspect or safely fast-forward independent product repositories; never reset local work."""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def git(path, *args):
    result = subprocess.run(['git', '-C', str(path), *args], text=True, encoding='utf-8',
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or 'Git command failed')
    return result.stdout.strip()

def target(root, entry):
    name = entry['path']
    if not re.fullmatch(r'gb28181-[a-z0-9-]+', name) or entry['branch'] != 'main':
        raise RuntimeError('Invalid product directory or branch')
    path = root / name
    if path.is_symlink() or path.resolve().parent != root.resolve():
        raise RuntimeError('Product directory escapes workspace or is a symlink')
    return path

def normalized(url):
    return url.rstrip('/').removesuffix('.git')

def inspect(root, entry):
    path = target(root, entry)
    if not path.exists():
        return path, 'missing'
    if not path.is_dir() or not (path / '.git').exists():
        raise RuntimeError(f'{entry["path"]}: existing directory is not an independent Git repository')
    if Path(git(path, 'rev-parse', '--show-toplevel')).resolve() != path.resolve():
        raise RuntimeError('Unexpected Git root')
    if normalized(git(path, 'remote', 'get-url', 'origin')) != normalized(entry['url']):
        raise RuntimeError(f'{entry["path"]}: origin does not match repos.json')
    branch = git(path, 'symbolic-ref', '--quiet', '--short', 'HEAD')
    if branch != entry['branch']:
        raise RuntimeError(f'{entry["path"]}: on {branch}; expected main, no automatic checkout')
    if git(path, 'status', '--porcelain', '--untracked-files=all'):
        raise RuntimeError(f'{entry["path"]}: local changes; no automatic stash/reset')
    return path, 'clean main'

def sync(root, entries, apply=False):
    # Preflight all local state before any network or working-tree mutation.
    planned = [(entry, *inspect(root, entry)) for entry in entries]
    for entry, path, state in planned:
        action = 'clone main' if state == 'missing' else 'fetch and fast-forward main'
        print(f'{entry["path"]}: {action}' + ('' if apply else ' (preview)'))
        if not apply:
            continue
        if state == 'missing':
            subprocess.run(['git', 'clone', '--branch', entry['branch'], '--single-branch', '--', entry['url'], str(path)], check=True)
        else:
            git(path, 'fetch', '--prune', 'origin')
            ahead, behind = map(int, git(path, 'rev-list', '--left-right', '--count', 'HEAD...refs/remotes/origin/main').split())
            if ahead:
                raise RuntimeError(f'{entry["path"]}: local main has {ahead} unpublished/divergent commits; retained unchanged')
            if behind:
                git(path, 'merge', '--ff-only', 'refs/remotes/origin/main')
        print(f'{entry["path"]}: {git(path, "rev-parse", "HEAD")}')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['status', 'sync'])
    parser.add_argument('--apply', action='store_true', help='explicitly execute sync; default is preview')
    args = parser.parse_args()
    if args.apply and args.command != 'sync':
        parser.error('--apply is only valid for sync')
    entries = json.loads((ROOT / 'repos.json').read_text(encoding='utf-8'))['repositories']
    if len({e['path'] for e in entries}) != len(entries):
        parser.error('Duplicate product directory in repos.json')
    try:
        if args.command == 'sync':
            sync(ROOT, entries, args.apply)
        else:
            errors = []
            for entry in entries:
                try:
                    path, state = inspect(ROOT, entry)
                    sha = git(path, 'rev-parse', '--short', 'HEAD') if state != 'missing' else '-'
                    print(f'{entry["path"]}: {state}; {sha}')
                except RuntimeError as error:
                    errors.append(str(error))
                    print('ATTENTION:', error)
            return bool(errors)
    except (RuntimeError, subprocess.CalledProcessError) as error:
        print('STOP:', error, file=sys.stderr)
        return 1
    return 0

if __name__ == '__main__':
    sys.exit(main())
