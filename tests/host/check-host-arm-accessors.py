#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# Copyright 2026 thebcd69 (BCD)
# BCD Material: additional terms under GPL-3.0 section 7 apply; see LICENSE-BCD.md.
"""Run portable fault regressions with preexisting SDK accessor macros."""
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
cc = shutil.which(os.environ.get("CC", "cc"))
assert cc, "A C compiler is required"
with tempfile.TemporaryDirectory(prefix="bcd-arm-sdk-") as directory:
    tmp = Path(directory)
    header = tmp / "sdk.h"
    header.write_text("""
#define __darwin_arm_thread_state64_get_sp(s) ((s).__sp)
#define __darwin_arm_thread_state64_get_pc(s) ((s).__pc)
#define __darwin_arm_thread_state64_set_sp(s, v) ((s).__sp = (v))
#define __darwin_arm_thread_state64_set_pc_fptr(s, v) ((s).__pc = (v))
""")
    # Verify the simulated SDK really conflicts without explicit isolation.
    probe = tmp / "probe.c"
    probe.write_text("typedef struct { unsigned sp; } context;\n"
                     "static unsigned __darwin_arm_thread_state64_get_sp(context s) { return s.sp; }\n")
    bad = subprocess.run([cc, "-include", str(header), "-c", str(probe), "-o", str(tmp / "probe.o")], capture_output=True)
    assert bad.returncode != 0, "SDK macro collision negative control was not rejected"
    wrapper = tmp / "cc"
    wrapper.write_text("#!/bin/sh\nexec " + shlex.quote(cc) + " -include " + shlex.quote(str(header)) + ' "$@"\n')
    wrapper.chmod(0o755)
    env = dict(os.environ, CC=str(wrapper))
    for name in ("check-fault-guard-guest-rip.py", "check-fault-loop-guest-progress.py"):
        result = subprocess.run([sys.executable, str(ROOT / "tests/host" / name)], cwd=ROOT,
                                env=env, capture_output=True, text=True)
        if result.returncode:
            print(result.stdout[-5000:] + result.stderr[-1500:])
        assert result.returncode == 0 and result.stdout.rstrip().endswith("PASS"), name
        print(f"PASS: {name}: SDK macros isolated; {result.stdout.count('ok   ')} source/runtime checks with ASan and UBSan")
print("PASS: preexisting ARM accessor macros reproduced and rejected without isolation")
