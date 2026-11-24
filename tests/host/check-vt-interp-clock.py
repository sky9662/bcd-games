#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# Copyright 2026 thebcd69 (BCD)
# BCD Material: additional terms under GPL-3.0 section 7 apply; see LICENSE-BCD.md.
"""Check simulated cadence against the production interpolation decisions."""
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("vti", ROOT / "tools/patch-winemetal-vt-interp.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
pure = mod.BLOCK[mod.BLOCK.index("/* vti-pure-begin"):mod.BLOCK.index("/* vti-pure-end */")]
header = (ROOT / "tests/host/vt_interp_clock.h").read_text()
cc = os.environ.get("CC") or shutil.which("cc") or shutil.which("clang")
assert cc, "A C compiler is required"
source = r'''
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include "clock.h"
''' + pure + r'''
int main(void) {
  const unsigned us[] = {12000, 33000, 40000, 20000};
  const int hz[] = {60, 120, 120, 120}, want[] = {1, 1, 3, 3}, pictures[] = {0, 1, 3, 1};
  for (int i = 0; i < 4; i++) {
    uint64_t before = vti_test_absolute_time();
    usleep(50000); /* a late host must not change the simulated game's rate */
    if (vti_test_absolute_time() != before) return 1;
    vti_test_advance_us(us[i]);
    uint64_t elapsed = vti_test_absolute_time() - before;
    if (elapsed != (uint64_t)us[i] * 1000ull) return 2;
    double dt = (double)elapsed / 1e9;
    if (madeira_vti_count(want[i], dt, hz[i], 0) != pictures[i]) return 3;
    if (madeira_vti_count(want[i], dt, hz[i], 1) != 0) return 4;
  }
  if (fabs(vti_test_seconds() - 1.105) > 1e-9) return 5;
  return 0;
}
'''
with tempfile.TemporaryDirectory(prefix="bcd-vti-clock-") as directory:
    tmp = Path(directory)
    (tmp / "clock.h").write_text(header)
    (tmp / "clock.c").write_text(source)
    def run():
        subprocess.run([cc, "-std=gnu11", "-O1", str(tmp / "clock.c"), "-o", str(tmp / "clock")], check=True)
        return subprocess.run([str(tmp / "clock")]).returncode
    assert run() == 0, "Controlled cadence or production picture decisions failed"
    advance = "atomic_fetch_add(&g_vti_test_ns, us * 1000ull);"
    assert header.count(advance) == 1
    (tmp / "clock.h").write_text(header.replace(advance, "(void)us;"))
    assert run() != 0, "Missing-clock-advance negative control was not rejected"
print("PASS: 12/33/40/20 ms cadence and production picture counts survive host delay; backlog suppresses pictures; missing clock advance rejected")
