#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Check Steam Desktop documentation with a narrow public-export exception."""
import argparse
import subprocess
import tempfile
from pathlib import Path

DOC = 'docs/STEAM_DESKTOP.md'
WORDS = ('Steam for Windows', 'Steam Desktop', 'steam_client_win64',
         'MADEIRA_STEAM_DESKTOP_SESSION', '[steam-desktop]', 'pool = 1152')


def verdict(root, public_source=False):
    path = Path(root) / DOC
    if path.is_symlink():
        return 'fail'
    if path.is_file():
        return 'pass' if all(word in path.read_text() for word in WORDS) else 'fail'
    if path.exists() or not public_source:
        return 'fail'
    git = subprocess.run(['git', 'ls-files', '--error-unmatch', '--', DOC],
                         cwd=root, capture_output=True)
    return 'skip' if git.returncode == 1 else 'fail'


def self_test():
    with tempfile.TemporaryDirectory() as t:
        root = Path(t)
        subprocess.run(['git', 'init', '-q', str(root)], check=True)
        doc = root / DOC
        doc.parent.mkdir()
        assert verdict(root) == 'fail'
        assert verdict(root, True) == 'skip'
        doc.write_text(' '.join(WORDS))
        assert verdict(root) == verdict(root, True) == 'pass'
        doc.write_text('incomplete')
        assert verdict(root, True) == 'fail'
        doc.unlink()
        doc.mkdir()
        assert verdict(root, True) == 'fail'
        doc.rmdir()
        doc.symlink_to(root / 'missing')
        assert verdict(root, True) == 'fail'
        doc.unlink()
        doc.write_text(' '.join(WORDS))
        subprocess.run(['git', 'add', '--', DOC], cwd=root, check=True)
        doc.unlink()
        assert verdict(root, True) == 'fail'
    with tempfile.TemporaryDirectory() as t:
        assert verdict(Path(t), True) == 'fail'
    print('PASS: Steam Desktop documentation policy (eight controls)')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--public-source', action='store_true')
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    if args.self_test:
        self_test()
    status = verdict(Path(__file__).resolve().parents[1], args.public_source)
    if status == 'skip':
        print('SKIP: documentation assertion only: public export omits untracked ' + DOC)
    else:
        print(status.upper() + ': ' + DOC)
    return int(status == 'fail')


if __name__ == '__main__':
    raise SystemExit(main())
