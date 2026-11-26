#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Run portable clock-controlled Vulkan pacing checks before the macOS build."""
from pathlib import Path
import sys
import tempfile

from vk_fps_cap_harness import check_pacing

failures = 0


def check(what, cond, detail=""):
    global failures
    print(("PASS: " if cond else "FAIL: ") + what)
    if not cond:
        failures += 1
        if detail:
            print(detail)


with tempfile.TemporaryDirectory(prefix="bcd-vk-clock-") as tmp:
    check_pacing(Path(__file__).resolve().parents[2], Path(tmp), check)
sys.exit(bool(failures))
