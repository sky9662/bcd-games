#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Exercise the native harness's queue gate with the production count function."""
import os
from pathlib import Path
import platform
import shutil
import subprocess
import tempfile

root = Path(__file__).resolve().parents[2]
host = root / "tests/host"
src = (root / "tools/patch-winemetal-vt-interp.py").read_text()
start = src.index("static int madeira_vti_count(")
end = src.index("\n}", start) + 2
harness = (host / "vt_interp_harness.m").read_text()
assert harness.index("vti_test_hold_worker(madeira_vti_queue())") < harness.index("dispatch_semaphore_signal(gate)")
assert "atomic_load(&g_vti.outstanding) == 2" in harness
assert "busy_after > busy0" in harness
cc = os.environ.get("CC") or shutil.which("clang")
assert cc, "clang is required"
with tempfile.TemporaryDirectory(prefix="bcd-vti-queue-") as t:
    tmp = Path(t)
    (tmp / "vti_count.h").write_text(src[start:end] + "\n")
    flags = []
    if platform.system() == "Linux":
        swift = shutil.which("swift")
        assert swift, "Linux dispatch test requires Swift's libdispatch"
        lib = Path(swift).resolve().parent.parent / "lib/swift"
        flags = ["-I" + str(lib), "-L" + str(lib / "linux"),
                 "-Wl,-rpath," + str(lib / "linux"), "-ldispatch", "-lBlocksRuntime"]
    subprocess.run([cc, "-std=gnu11", "-fblocks", "-Wall", "-Wextra", "-Werror",
                    "-I" + t, "-I" + str(host), str(host / "vt_interp_queue_gate_test.c"),
                    "-o", str(tmp / "test")] + flags, check=True)
    subprocess.run([str(tmp / "test")], check=True, timeout=30)
