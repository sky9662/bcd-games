#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Accept the pinned OpenGL source plus exactly the CI NULL-sync overlay."""
import runpy
import subprocess
import sys
from pathlib import Path


def check(wine, patch):
    def git(*args):
        return subprocess.check_output(['git', '-C', str(wine), *args])
    rel = patch['REL']
    original = git('show', 'HEAD:' + rel)
    current = (wine / rel).read_bytes()
    changed = git('diff', '--name-only', '-z', 'HEAD', '--', 'dlls/opengl32').split(b'\0')[:-1]
    if b'ios_wow_host_ptr' not in original:
        return False
    if not changed:
        return current == original
    old, new = patch['OLD'].encode(), patch['NEW'].encode()
    return (changed == [rel.encode()] and original.count(old) == 1
            and current == original.replace(old, new, 1))


if __name__ == '__main__':
    patch = runpy.run_path(str(Path(__file__).with_name('patch-wine-gl-null-sync.py')))
    if not check(Path(sys.argv[1]), patch):
        sys.exit('OpenGL source differs from the pin plus the exact NULL-sync overlay')
    print('OpenGL source: pinned tree or exact NULL-sync overlay')
