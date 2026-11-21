# Turing Complete: opt-in executable-section interval recheck

Status: experimental, device result not yet verified. **No default behavior change.**

## Reproduction

- Game: Steam Turing Complete, new engine, Windows x86-64 executable.
- Device: iPhone Duo / iOS 27.2, BCD 0.1.686.
- Original configuration: `MESA_GL_VERSION_OVERRIDE=4.1`,
  `MESA_GLSL_VERSION_OVERRIDE=410` (Zink/Vulkan).
- Reproduced crash with FEX `MULTIBLOCK=0`, `SMCCHECKS=full`,
  `MADEIRA_NTDLL_XSEC=1` and `MADEIRA_SHARED_SECTION_EXEC=1`
  (each experiment reported as unsuccessful; later results have not been
  provided as full logs).
- Known good comparison: Turing Complete runs in Playport with the two
  Mesa overrides and Vulkan backend.

Relevant original BCD log:

```text
[jit-pool] anon RWX 0x71477e0000 size=0x4000 -> ...
[iOS-xquery] MISS tracker=... addr=0x71477e212f ... alias-table=155/256 refused=0
NoExec instruction in entry block: 71477E212F
[noexec-who] ... now: a view 0x71477e0000+0x4000 ... (section, SEC_COMMIT)
[noexec-who] alias: ... guest/RW/RX view hashes match
[guest-rip] ... state=1000 protect=40 ... type=40000
```

The last line is a Wine query that says MEM_COMMIT,
PAGE_EXECUTE_READWRITE, MEM_MAPPED. It does **not** prove when or why
FEX dropped/missed the executable interval. This experiment separates
that suspected gap from a fault in generated x86 code.

## Implementation

`tools/patch-fex-ios-exec-recheck.py` modifies one
`InvalidationTracker::QueryExecutableRange` ARM64EC query path, under
`FEX_IOS_HOST`, with an anchored, idempotent source transformation.
The host test rejects changed anchors.

`env.MADEIRA_FEX_EXEC_RECHECK = 1` enables a narrowly gated recovery
*only on a missing executable interval*, and only when `VirtualQuery`
confirms `MEM_COMMIT`, `MEM_MAPPED`, unguarded, executable guest memory.
It registers just the missed 4 KiB guest page, under the interval lock,
with matching writable/SMC status. No other mapping is promoted; pages
without actual executable rights still fault. With the variable unset,
the original FEX path is used.

The change is applied only to the temporary ARM64EC FEX build tree,
before xtajit64.dll is built. It does not edit the pinned submodule.
The existing build script resets the patched source after building.

## Trial

1. Install the **unsigned test IPA** after signing it through the user's
   normal installation path. Use the existing Turing Complete installation;
   do not switch Steam branches, reset prefixes or overwrite saves.
2. Restore the known-good Mesa overrides for the game.
3. Add only `env.MADEIRA_FEX_EXEC_RECHECK = 1`.
4. Launch once and inspect `[tc-exec-recheck] restored ...`,
   `[iOS-xquery] MISS`, `NoExec`, the next guest RIP, and the result.
5. If still failing: preserve both the new and previous BCD logs.
   Do not conclude that the repair worked just because a log line appears.

## Follow-ups for upstream review

This is a **diagnostic experiment**, not a proven upstream fix.
If it succeeds, trace the missing/dropped Wine→FEX
`NotifyMapViewOfSection`/`NotifyMemoryProtect`/`InvalidateInterval`
path and put the final fix there, with a reproduction probe for
executable pagefile section views and interval removal/reuse races.
Only then remove the opt-in and consider an upstream PR.
