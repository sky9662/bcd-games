#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Positive and negative controls for the exact OpenGL CI overlay guard."""
import runpy
import subprocess
import tempfile
from pathlib import Path

root = Path(__file__).resolve().parents[2]
check = runpy.run_path(str(root / 'tools/check-wine-gl-optin-tree.py'))['check']
patch = runpy.run_path(str(root / 'tools/patch-wine-gl-null-sync.py'))
with tempfile.TemporaryDirectory() as t:
    w = Path(t)
    p = w / patch['REL']
    p.parent.mkdir(parents=True)
    other = p.parent / 'Makefile.in'

    def git(*a):
        subprocess.run(['git', '-C', str(w), *a], check=True, stdout=subprocess.DEVNULL)

    git('init', '-q')
    git('config', 'user.email', 'test@example.invalid')
    git('config', 'user.name', 'test')
    other.write_text('base\n')
    original = '/* ios_wow_host_ptr */\n' + patch['OLD']
    p.write_text(original)
    git('add', '.')
    git('commit', '-qm', 'base')
    assert check(w, patch), 'pristine pin'
    p.write_text(original.replace(patch['OLD'], patch['NEW']))
    assert check(w, patch), 'exact CI overlay'
    p.write_text(p.read_text() + '/* unexpected */\n')
    assert not check(w, patch), 'unexpected edit in overlay file'
    p.write_text(original.replace(patch['OLD'], patch['NEW']))
    other.write_text('changed\n')
    assert not check(w, patch), 'unexpected edit in other tracked file'
    git('checkout', '--', str(other))
    git('add', str(p))
    assert check(w, patch), 'exact staged overlay'
    p.write_text(original)
    git('add', str(p))
    p.write_text(original.replace('ios_wow_host_ptr', 'missing'))
    assert not check(w, patch), 'fork marker removed'
print('OpenGL opt-in tree: six positive/negative controls passed')
