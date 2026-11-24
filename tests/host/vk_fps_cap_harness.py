# SPDX-License-Identifier: GPL-3.0-only
# Copyright 2026 thebcd69 (BCD)
# BCD Material: additional terms under GPL-3.0 section 7 apply; see LICENSE-BCD.md.
"""Exercise the unchanged Vulkan pacing function with deterministic and real clocks."""
import os
import subprocess
import sys


def check_pacing(root, tmp, check, *, real_clock=False):
    # Compile the production pacing function; control only the Mach clock API.
    vk_ios = (root / "build/win32u-unix/vulkan_ios.c").read_text()
    start = vk_ios.index("#include <mach/mach_time.h>\nextern int madeira_get_vsync_locked(void) __attribute__((weak_import));")
    body = vk_ios[start:vk_ios.index("\n}\n", vk_ios.index("static __attribute__((unused)) void madeira_vk_fps_cap_pace(void)")) + 3]
    fake = tmp / "fake" / "mach"
    fake.mkdir(parents=True)
    (fake / "mach_time.h").write_text(r"""
#include <stdint.h>
#include <stdlib.h>
typedef struct { uint32_t numer, denom; } mach_timebase_info_data_t;
static uint64_t bcd_clock_ticks = 1000000000;
static uint32_t bcd_numer(void) { const char *v = getenv("TEST_NUMER"); return v ? (uint32_t)atoi(v) : 125; }
static uint32_t bcd_denom(void) { const char *v = getenv("TEST_DENOM"); return v ? (uint32_t)atoi(v) : 3; }
static int mach_timebase_info(mach_timebase_info_data_t *tb) { tb->numer = bcd_numer(); tb->denom = bcd_denom(); return 0; }
static uint64_t mach_absolute_time(void) { return bcd_clock_ticks; }
static inline int mach_wait_until(uint64_t deadline) { if (deadline < bcd_clock_ticks) abort(); bcd_clock_ticks = deadline; return 0; }
static void bcd_work_us(unsigned int us) { bcd_clock_ticks += (uint64_t)us * 1000 * bcd_denom() / bcd_numer(); }
static double bcd_now_ms(void) { return (double)bcd_clock_ticks * bcd_numer() / bcd_denom() / 1e6; }
""")
    (tmp / "pace.c").write_text("#include <stdio.h>\n#include <stdlib.h>\n#include <stdint.h>\n#include <time.h>\n#include <unistd.h>\n" + body + r'''
#ifdef BCD_TEST_CLOCK
static double now_ms(void) { return bcd_now_ms(); }
#define WORK_US(us) bcd_work_us(us)
#else
static double now_ms(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return t.tv_sec * 1e3 + t.tv_nsec / 1e6; }
#define WORK_US(us) usleep(us)
#endif
int main(int argc, char **argv) {
  int frames = atoi(argv[1]), work_us = atoi(argv[2]);
  double t0 = now_ms(), waited = 0;
  for (int i = 0; i < frames; i++) {
    if (work_us) WORK_US(work_us);
    if (argc > 3 && i == 2) WORK_US(100000);
    double a = now_ms();
    madeira_vk_fps_cap_pace();
    waited += now_ms() - a;
    if (argc > 3) printf("frame %.6f\n", now_ms() - t0);
  }
  printf("%.3f %.3f\n", (now_ms() - t0) / frames, waited / frames);
  return 0;
}
''')
    # round 707 (A2 F12): the governor's fixed frame cap (server_ios.c's ios_fps_cap), set here from TEST_CAP
    (tmp / "getter.c").write_text('#include <stdlib.h>\nint madeira_get_vsync_locked(void) { const char *m = getenv("TEST_MODE"); return m ? atoi(m) : 1; }\n'
                                  'volatile int ios_fps_cap;\n__attribute__((constructor)) static void cap(void) { const char *c = getenv("TEST_CAP"); ios_fps_cap = c ? atoi(c) : 0; }\n')
    cc = os.environ.get("CC", "cc")
    weak = [] if sys.platform == "darwin" else ["-Dweak_import=weak"]
    unresolved = ["-Wl,-U,_madeira_get_vsync_locked", "-Wl,-U,_ios_fps_cap"] if sys.platform == "darwin" else []
    common = [cc, "-O1", "-Wall", "-Werror"]
    fake_flags = ["-DBCD_TEST_CLOCK", "-I", str(fake.parent), *weak]
    builds = [subprocess.run([*common, *fake_flags, "-o", str(tmp / "pace"), str(tmp / "pace.c"), str(tmp / "getter.c")], capture_output=True, text=True),
              subprocess.run([*common, *fake_flags, "-o", str(tmp / "pace-nogetter"), str(tmp / "pace.c"), *unresolved], capture_output=True, text=True)]
    check("production pacing compiles against a controlled Mach clock, with and without the app's getter", all(b.returncode == 0 for b in builds), "\n".join(b.stderr for b in builds))
    if all(b.returncode == 0 for b in builds):
        def timed(binary, frames, work_us, **env):
            e = {k: v for k, v in os.environ.items() if not k.startswith(("MADEIRA_", "TEST_"))}
            e.update(env)
            r = subprocess.run([str(tmp / binary), str(frames), str(work_us)], capture_output=True, text=True, env=e)
            mean, waited = (float(x) for x in r.stdout.split())
            return mean, waited, r.stderr

        # Exact clock tests retain upper bounds; OS scheduling cannot change this clock.
        # The first frame starts the grid without a wait, so N frames take N - 1 periods
        held = lambda mean, frames, period: period * (frames - 1) / frames * 0.97 <= mean <= period * (frames - 1) / frames + 2.5
        m60, _, log = timed("pace", 31, 0, TEST_MODE="1")
        check(f"60 FPS: a fast game is held to 16.7 ms a frame ({m60:.2f} ms over 31 frames)", held(m60, 31, 1000 / 60))
        check("...and the log says once that the limit holds Vulkan presents", log.count("[winios-vk] the frame-rate limit holds Vulkan presents") == 1, log)
        m40, _, _ = timed("pace", 21, 0, TEST_MODE="4")
        check(f"40 FPS: 25 ms ({m40:.2f} ms over 21 frames)", held(m40, 21, 25.0))
        m30, _, _ = timed("pace", 16, 0, TEST_MODE="3")
        check(f"30 FPS: 33.3 ms ({m30:.2f} ms over 16 frames)", held(m30, 16, 1000 / 30))
        free = [timed("pace", 50, 0, TEST_MODE=m)[0] for m in ("0", "2")]
        check(f"no limit (vsync modes 0 and 2): no wait ({free[0]:.3f}, {free[1]:.3f} ms)", all(x < 1.0 for x in free))
        # round 707 (A2 F12): the fixed frame cap holds a Vulkan game too, the lower of it and the limit
        c25, _, _ = timed("pace", 16, 0, TEST_MODE="0", TEST_CAP="25")
        check(f"a frame cap of 25 with no limit: 40 ms ({c25:.2f} ms over 16 frames)", held(c25, 16, 40.0))
        c25l, _, _ = timed("pace", 16, 0, TEST_MODE="1", TEST_CAP="25")
        check(f"a frame cap of 25 under the 60 FPS limit: the lower rate, 40 ms ({c25l:.2f} ms)", held(c25l, 16, 40.0))
        c60l, _, _ = timed("pace", 16, 0, TEST_MODE="3", TEST_CAP="60")
        check(f"a frame cap of 60 under the 30 FPS limit: 33.3 ms ({c60l:.2f} ms)", held(c60l, 16, 1000 / 30))
        cbad = timed("pace", 50, 0, TEST_MODE="0", TEST_CAP="5")[0]
        check(f"a cap outside 10...120 is none: no wait ({cbad:.3f} ms)", cbad < 1.0)
        off, _, log = timed("pace", 50, 0, TEST_MODE="1", MADEIRA_VK_FPS_CAP="0")
        check(f"MADEIRA_VK_FPS_CAP=0: no wait ({off:.3f} ms), and the log says so", off < 1.0 and "does not hold" in log, log)
        nog, _, _ = timed("pace-nogetter", 50, 0)
        check(f"a link without the app's getter: no wait ({nog:.3f} ms)", nog < 1.0)
        _, slow_wait, _ = timed("pace", 20, 25000, TEST_MODE="1")
        check(f"a game slower than the limit (25 ms a frame) never waits ({slow_wait:.3f} ms a frame)", slow_wait < 1.0)
        m_mid, mid_wait, _ = timed("pace", 31, 8000, TEST_MODE="1")
        check(f"a faster game (8 ms of work a frame) is held to 16.7 ms ({m_mid:.2f} ms, {mid_wait:.2f} ms waited a frame)",
              held(m_mid, 31, 1000 / 60) and mid_wait > 2.0)

        for numer, denom in (("1", "1"), ("125", "3")):
            mean, _, _ = timed("pace", 31, 0, TEST_MODE="1", TEST_NUMER=numer, TEST_DENOM=denom)
            expected = (1000 / 60) * 30 / 31
            check(f"Mach timebase {numer}/{denom}: exact 60 FPS grid", abs(mean - expected) < 0.002)
        env = {k: v for k, v in os.environ.items() if not k.startswith(("MADEIRA_", "TEST_"))}
        env["TEST_MODE"] = "1"
        late = subprocess.run([str(tmp / "pace"), "5", "0", "late"], capture_output=True, text=True, env=env, check=True)
        times = [float(line.split()[1]) for line in late.stdout.splitlines() if line.startswith("frame ")]
        check("a frame 100 ms late resets the grid; later frames wait one period, never repay the delay",
              len(times) == 5 and abs(times[0]) < 0.002 and abs(times[2] - times[1] - 100) < 0.002
              and all(abs(times[i] - times[i - 1] - 1000 / 60) < 0.002 for i in (1, 3, 4)), times)
        mutant = tmp / "pace-no-wait.c"
        original = (tmp / "pace.c").read_text()
        assert original.count("mach_wait_until( deadline )") == 1
        mutant.write_text(original.replace("mach_wait_until( deadline )", "(void)deadline"))
        negative = subprocess.run([*common, *fake_flags, "-o", str(tmp / "pace-no-wait"), str(mutant), str(tmp / "getter.c")], capture_output=True, text=True)
        check("negative control compiles", negative.returncode == 0, negative.stderr)
        if negative.returncode == 0:
            mean, _, _ = timed("pace-no-wait", 31, 0, TEST_MODE="1")
            check("negative control: deleting the wait is rejected by the frame-rate contract", not held(mean, 31, 1000 / 60))

        if real_clock:
            native = subprocess.run([*common, "-o", str(tmp / "pace-real"), str(tmp / "pace.c"), str(tmp / "getter.c")], capture_output=True, text=True)
            check("production pacing compiles against the real Mach clock", native.returncode == 0, native.stderr)
            if native.returncode == 0:
                for mode, frames, period in (("1", 31, 1000 / 60), ("4", 21, 25.0), ("3", 16, 1000 / 30)):
                    mean, waited, _ = timed("pace-real", frames, 0, TEST_MODE=mode)
                    # Mach waits may resume late on a shared runner (Apple TN2169).
                    # The limiter must never present faster than its requested cap;
                    # exact upper bounds and unnecessary waits are checked above.
                    check(f"real Mach clock, mode {mode}: cap holds ({mean:.2f} ms; {waited:.2f} ms waited)",
                          mean >= period * (frames - 1) / frames * 0.97 and waited > 0)
