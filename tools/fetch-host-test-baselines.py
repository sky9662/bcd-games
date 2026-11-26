#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# Copyright 2026 thebcd69 (BCD)
# BCD Material: additional terms under GPL-3.0 section 7 apply; see LICENSE-BCD.md.
"""Recover exact upstream test-history objects without changing build pins."""
from pathlib import Path
import runpy
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
for component, helper in (("FEX", "fexpatch_eval.py"), ("dxmt", "dxmt_base.py")):
    module = runpy.run_path(str(ROOT / "tests/host" / helper))
    revision, remote = module["OVERLAY_BASE"], module["BASELINE_REMOTE"]
    checkout = ROOT / component
    def git(*args, **kwargs):
        try:
            return subprocess.run(["git", "-C", str(checkout), *args], check=True, capture_output=True, text=True, **kwargs).stdout.strip()
        except subprocess.CalledProcessError as error:
            print(error.stderr, file=sys.stderr)
            raise
    head = git("rev-parse", "HEAD")
    have = subprocess.run(["git", "-C", str(checkout), "cat-file", "-e", revision + "^{commit}"], capture_output=True)
    if have.returncode:
        git("fetch", "-q", "--depth=1", remote, revision)
    assert git("rev-parse", revision + "^{commit}") == revision
    assert git("rev-parse", "HEAD") == head, "Test-history recovery changed a build pin"
    print(f"PASS: {component} test baseline {revision} from {remote}; build HEAD remains {head}")
