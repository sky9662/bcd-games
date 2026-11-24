#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# Copyright 2026 thebcd69 (BCD)
# BCD Material: additional terms under GPL-3.0 section 7 apply; see LICENSE-BCD.md.
"""The app's frame-rate limit holds a Windows Vulkan game's presents (build 703; tools/patch-wine-vulkan-fps-cap.py and
madeira_vk_fps_cap_pace in build/win32u-unix/vulkan_ios.c).

Checks:
  1. the patch applies once to Wine's committed win32u/vulkan.c (a second run only says so), adds one line right before the host's
     present and nothing else, and fails by name when its anchor moved;
  2. with the frame ring, suboptimal and 32-bit Vulkan patches, the four apply in every order with the same result;
  3. the pacing, compiled from vulkan_ios.c against a controlled clock and real Mach waits: 60, 40 and 30 FPS hold a fast game to the limit; no limit
     (vsync modes 0 and 2), MADEIRA_VK_FPS_CAP=0 and a link without the app's getter never wait; a game slower than the limit
     never waits either;
  4. wiring: the helper sits before Wine's vulkan.c in vulkan_ios.c, and CI runs this check and then the patch before win32u-unix
     is built.

    tests/host/check-vk-fps-cap.py [--require-wine]     WINE_SRC=<wine tree> to name another tree
"""
import itertools
import os
import subprocess
import sys
import tempfile
from pathlib import Path

R = Path(__file__).resolve().parents[2]
REQUIRE = "--require-wine" in sys.argv
ok = True


def check(what, cond, detail=""):
    global ok
    print(("ok   " if cond else "FAIL ") + what + (("\n     " + str(detail)[-1500:]) if detail and not cond else ""))
    ok = ok and bool(cond)


import importlib.util
spec = importlib.util.spec_from_file_location("wow64", R / "tools/patch-wine-vulkan-wow64.py")
wow64 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wow64)
RELS = [rel for rel, _, _ in wow64.FILES]
if "dlls/win32u/vulkan.c" not in RELS:
    RELS.append("dlls/win32u/vulkan.c")
wine = Path(os.environ.get("WINE_SRC", R / "wine"))


def pristine(rel):
    if (wine / ".git").exists() or (wine / rel).is_file():
        r = subprocess.run(["git", "-C", str(wine), "show", "HEAD:" + rel], capture_output=True, text=True)
        if r.returncode == 0 and r.stdout:
            return r.stdout
        if (wine / rel).is_file():
            return (wine / rel).read_text()
    bare = Path.home() / "madeira-local/kaynak/wine.git"
    if bare.is_dir():
        pin = subprocess.run(["git", "-C", str(R), "ls-tree", "HEAD", "wine"], capture_output=True, text=True).stdout.split()
        if len(pin) >= 3:
            r = subprocess.run(["git", "-C", str(bare), "show", f"{pin[2]}:{rel}"], capture_output=True, text=True)
            if r.returncode == 0 and r.stdout:
                return r.stdout
    return None


def run_script(name, cwd):
    return subprocess.run([sys.executable, str(R / "tools" / name)], cwd=cwd, capture_output=True, text=True)


tool = R / "tools/patch-wine-vulkan-fps-cap.py"
check("BCD's header on the patch script", tool.read_text().startswith("#!/usr/bin/env python3\n# SPDX-License-Identifier: GPL-3.0-only\n# Copyright 2026 thebcd69 (BCD)"))
anchor = "    res = device->p_vkQueuePresentKHR( queue->host.queue, present_info );\n"
line = "    madeira_vk_fps_cap_pace();   /* madeira-bcd fps cap (Vulkan) (tools/patch-wine-vulkan-fps-cap.py): the app's frame-rate limit */\n"

with tempfile.TemporaryDirectory(prefix="bcd-vk-fps-cap-") as tmp_name:
    tmp = Path(tmp_name)
    files = {rel: pristine(rel) for rel in RELS}
    if any(v is None for v in files.values()):
        print("SKIP: no Wine sources (check out the wine submodule, or set WINE_SRC)" if not REQUIRE else "FAIL: no Wine sources")
        if REQUIRE:
            ok = False
    else:
        w32 = files["dlls/win32u/vulkan.c"]

        def tree(name):
            for rel, text in files.items():
                p = tmp / name / "wine" / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(text)
            return tmp / name

        a = tree("a")
        r1, r2 = run_script(tool.name, a), run_script(tool.name, a)
        patched = (a / "wine/dlls/win32u/vulkan.c").read_text()
        check("the patch applies once; a second run only says it is there",
              r1.returncode == 0 and "frame-rate limit patched" in r1.stdout and r2.returncode == 0 and "already patched" in r2.stdout,
              r1.stdout + r1.stderr + r2.stdout + r2.stderr)
        check("one line, right before the host's present, and nothing else", patched == w32.replace(anchor, line + anchor, 1) and w32.count(anchor) == 1)
        bad = tmp / "bad"
        (bad / "wine/dlls/win32u").mkdir(parents=True)
        (bad / "wine/dlls/win32u/vulkan.c").write_text(w32.replace(anchor, anchor.replace("present_info )", "info )")))
        r = run_script(tool.name, bad)
        check("an anchor that moved fails by name", r.returncode != 0 and "anchor found 0 times" in (r.stdout + r.stderr), r.stdout + r.stderr)
        names = [tool.name, "patch-wine-vulkan-frame-ring.py", "patch-wine-vulkan-suboptimal.py", "patch-wine-vulkan-wow64.py"]
        results, errors = set(), []
        for k, order in enumerate(itertools.permutations(names)):
            t = tree(f"order{k}")
            for n in order:
                r = run_script(n, t)
                if r.returncode != 0:
                    errors.append(f"{order}: {n}: {r.stdout}{r.stderr}")
            out = (t / "wine/dlls/win32u/vulkan.c").read_text()
            results.add(out)
            if not all(m in out for m in ("madeira-bcd fps cap (Vulkan)", "madeira-bcd frame ring (Vulkan)", "ignore_host_suboptimal", "host_alloc")):
                errors.append(f"{order}: a change is missing")
            if not (out.index("madeira_vk_fps_cap_pace();") < out.index(anchor) < out.index("madeira-bcd frame ring (Vulkan)")):
                errors.append(f"{order}: the limit is not before the present, or the ring not after it")
        check("with the frame ring, suboptimal and 32-bit Vulkan patches, all 24 orders apply and give the same win32u/vulkan.c",
              not errors and len(results) == 1, "\n".join(errors[:6]))

    # Clock-controlled logic checks plus a real Mach wait integration check.
    from vk_fps_cap_harness import check_pacing
    check_pacing(R, tmp, check, real_clock=True)

# 4. wiring
vk_ios = (R / "build/win32u-unix/vulkan_ios.c").read_text()
check("vulkan_ios.c: the helper comes before Wine's vulkan.c and the dlopen / dlsym redefinitions",
      vk_ios.index("static __attribute__((unused)) void madeira_vk_fps_cap_pace(void)") < vk_ios.index("#define dlopen( name, flags )")
      < vk_ios.index('#include "../../wine/dlls/win32u/vulkan.c"'))
wf = (R / ".github/workflows/build-ipa.yml").read_text()
check("CI: this check, then the patch and its marker, before win32u-unix is built",
      "python3 tests/host/check-vk-fps-cap.py --require-wine" in wf
      and wf.index("python3 tests/host/check-vk-fps-cap.py --require-wine") < wf.index("python3 tools/patch-wine-vulkan-fps-cap.py")
      < wf.index('grep -q "madeira-bcd fps cap (Vulkan)" wine/dlls/win32u/vulkan.c') < wf.index("- name: Build win32u-unix"))

print("PASS: the frame-rate limit for Vulkan presents" if ok else "FAIL: the frame-rate limit for Vulkan presents")
sys.exit(0 if ok else 1)
