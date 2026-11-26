#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# Copyright 2026 thebcd69 (BCD)
# BCD Material: additional terms under GPL-3.0 section 7 apply; see LICENSE-BCD.md.
"""Mouse-look and the game's own cursor (round 714, agent A1 S10; feedback 9YXC9N); source checks, nothing runs.

env.MADEIRA_RELATIVE_CURSOR = 1 lets the drawn cursor of a directly started game show in Mouse-look while the program shows
its own cursor (menus) and hide while it hides it (play). Default off, so Mouse-look behaves as before:
  1. the switch is default off and needs the drawn cursor (MADEIRA_DIRECT_CURSOR) to be on;
  2. renderCursor's visibility admits Mouse-look only through the switch, and still needs the program's cursor shown;
  3. the relative finger branch hands the move to stickMoved() (the drawn cursor follows Wine's) only with the switch, outside
     a Windows desktop session, and only for a real move; it still sends the same relative motion and returns;
  4. nothing else that tests Mouse-look changed: the route, the automatic lock, the touch cursor and the tap guards.
"""
import sys
from pathlib import Path

R = Path(__file__).resolve().parents[2]
hw = (R / "app/Madeira/HardwareInput.swift").read_text()
cv = (R / "app/Madeira/ContentView.swift").read_text()
failures = 0


def require(cond, label):
    global failures
    print(("PASS: " if cond else "FAIL: ") + label)
    if not cond:
        failures += 1


require('static let relativeCursorEnabled = directCursorEnabled && flag("MADEIRA_RELATIVE_CURSOR", defaultOn: false)' in hw,
        "the switch is default off (only 1 turns it on) and needs the drawn cursor")
require("&& mouseFocused && shown && (!InputSettings.shared.relative || Self.relativeCursorEnabled)\n" in hw,
        "the drawn cursor shows in Mouse-look only with the switch, and only while the program shows its cursor")
# The custom acceleration integration changes the sensitivity expression, not
# the relative cursor contract. Identify the branch by its actual condition
# and carry calculation; require one candidate and keep the guarded ordering.
def relative_move_ok(source):
    import re
    candidates = re.findall(r"(?m)^        if InputSettings\.shared\.relative \{\n(.*?)(?=^        \})", source, re.S | re.M)
    candidates = [b for b in candidates if "relCarryX += dx * sens" in b and "relCarryY += dy * sens" in b]
    if len(candidates) != 1:
        return False
    branch = candidates[0]
    # A nonzero motion must enclose both calls; cursor follows only after the
    # relative motion and only in the opted-in non-desktop case.
    return re.search(
        r"(?m)^            if ix != 0 \|\| iy != 0 \{\n"
        r"                winios_pointer\(ix, iy, F_MOVE, 0\)\n"
        r"(?:                //[^\n]*\n)*"
        r"                if !desktopMode && HardwareInput\.relativeCursorEnabled \{ HardwareInput\.shared\.stickMoved\(\) \}\n"
        r"            \}\n            return\n$",
        branch,
    ) is not None

require(relative_move_ok(cv),
        "the finger's relative move is sent as before, then (switch on, not a desktop session) the cursor follows Wine's")
if "--self-test" in sys.argv:
    # Mutate the real checkout; no synthetic success or skipped assertions.
    for before, after in (
        ("if !desktopMode && HardwareInput.relativeCursorEnabled { HardwareInput.shared.stickMoved() }",
         "HardwareInput.shared.stickMoved()"),
        ("if ix != 0 || iy != 0 {", "if ix == 0 && iy == 0 {"),
        ("winios_pointer(ix, iy, F_MOVE, 0)", "winios_pointer(ix, iy, F_MOVE | F_ABS, 0)"),
        ("relCarryX += dx * sens", "relCarryX += dx"),
    ):
        require(before in cv and not relative_move_ok(cv.replace(before, after)),
                "negative control rejects " + after)
require(hw.count("relativeCursorEnabled") == 2 and cv.count("relativeCursorEnabled") == 1,
        "the switch is read in those two places only")
require("if InputSettings.shared.relative { return false }" in hw
        and "guard directCursorLive, !InputSettings.shared.relative else { return }" in hw
        and "let relOptIn = InputSettings.shared.relative" in hw
        and "if !desktopMode && !InputSettings.shared.relative {" in cv,
        "the route, the touch cursor, the automatic lock and the tap guards still exclude Mouse-look")
print("\n%s" % ("ALL PASS" if failures == 0 else "%d FAILURE(S)" % failures))
sys.exit(0 if failures == 0 else 1)
