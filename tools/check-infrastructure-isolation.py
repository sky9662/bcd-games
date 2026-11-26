#!/usr/bin/env python3
"""Require the original app and feature sources on the canonical branch."""
from pathlib import Path
import subprocess
ROOT = Path(__file__).resolve().parents[1]
BASE = "f811dd05a9183cda20ffd3956cb1958cafe654f7"
if subprocess.run(["git", "cat-file", "-e", BASE + "^{commit}"], cwd=ROOT, capture_output=True).returncode:
    subprocess.run(["git", "fetch", "--depth=1", "origin", BASE], cwd=ROOT, check=True)
subprocess.run(["git", "diff", "--exit-code", BASE, "HEAD", "--", "app", "FEX", "wine", "dxmt", "madeira-dock", "tools/build-xtajit64.sh",
                "tests/host/bcd_aim_checks.swift", "tests/host/check-bcd-players.py", "tests/host/check-bcd-touch-extras.py",
                "tests/host/check-steam-cloud.py", "tests/host/check-steam-remotecache.py"], cwd=ROOT, check=True)
for path in ("app/Madeira/BCDTouchAcceleration.swift", "tools/patch-fex-ios-exec-recheck.py", "tests/host/check-turing-exec-recheck.py", "tests/host/check-profile-unification.py"):
    assert not (ROOT / path).exists(), f"Unexpected custom feature: {path}"
print("PASS: official app, submodule pins and feature sources unchanged")
