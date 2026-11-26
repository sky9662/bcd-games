## Verified successful baseline — Run 66 (2026-11-26 Taipei)

**Build completed; do not restart this target just to monitor it. Device validation remains pending.** [Run #66](https://github.com/sky9662/bcd-games/actions/runs/45652561853), build source `2fa14a0b1fcdd983f51897ff425e5f2c2ecdf917`, both Linux jobs and macOS build succeeded; 880 successful main-job steps, zero failed, 920 listed steps including conditional skips. Started 2026-11-25 16:19:06 UTC, completed 18:07:31 UTC. [Actual artifact 15049313063](https://github.com/sky9662/bcd-games/actions/runs/45652561853/artifacts/15049313063), `bcd-0712-upstream-cloud-unsigned-ipa`, 469103728 bytes, ZIP digest `3ab04f6ed4ed30c1fd98c5de44037c703680c756e99b232dd00e86cc523c97f0`, expires 2026-12-09 18:07:07 UTC. [Build logs artifact](https://github.com/sky9662/bcd-games/actions/runs/45652561853/artifacts/15049468767). Download and retain the actual artifact before expiry. A docs-only commit recording this result does not change the build source SHA.

- `Madeira-0.1.712-unsigned.ipa`, `com.thebcd69.bcd`, SHA256 `a019a9608e56bbd06ffc8e7fd83125a035ad7a46493495937db62ba271881415`.
- `Madeira2-0.1.712-unsigned.ipa`, `com.thebcd69.bcd2`, SHA256 `7e837a019155b83322eb5b511dae8aac501351d77ad534453a095a29d66b1733`.
- Step 915 ran the actual verifier: ZIP CRC, bundle IDs, 0.1.712, MadeiraCommit matching source SHA, BCDTouchAcceleration, [profile] one Windows profile, [tc-exec-recheck] in both xtajit64.dll and xtajit64-avx.dll. Both passed before upload. This is CI evidence, not independent downloaded-byte or physical-device testing.
- Explicit omissions in macOS log: 14 host tests stopped at optional absent fixtures (itch, ea, cluster-logs, steam-cm-transport, system32-x86-tools, external-storage, kk-lsfg, vulkan-wow64, kk-snorm-blend, kk-msl-fail, kk-ms-store-drop, moltenvk-patched, vcruntime-mfc, vcruntime-sources); do not report these as passes. Two narrower document-only exceptions (Vulkan README, Steam Desktop) preserve functional checks. Nonfatal warnings include source-built dxgi/d3d11 differing from upstream committed binaries, expected patched FEX rebuild difference and opengl32-optin.dll delay-import gap for glu32.dll; retain warnings for review, do not silently declare all runtime features validated.
- Cache restore confirmed in logs for native Wine, GnuTLS, FFmpeg, OpenGL libs, KosmicKrisp, MoltenVK, llvm-mingw, DXC (original hash key), LuaJIT, FEX iOS/ARM64EC/WOW64, LLVM 15 iOS, i386 farm, Wine ARM64EC and ICU. Preserve pins and independent changes. This successful SHA is the new reference for future builds; previous baseline remains historical.
- Install only the intended identity via existing signing method, enable JIT as needed, back up both wine/drive_c/users/mythic and mobile before launching; no automatic Cloud conflict resolution. Test touch acceleration, Turing Complete and actual Cloud save coherence on device.
- Pending project follow-up: shared infrastructure branch and cross-branch global agent guidance, as previously approved. The artifact gate is now satisfied; record device validation separately, do not merge features or mutate existing PRs. No infrastructure restructuring performed in this status check.

---

# BCD IPA build runbook — permanent cross-version checklist

Last reviewed: 2026-11-25. Maintainers and coding agents: read this file and [CI-LESSONS.md](CI-LESSONS.md) BEFORE changing or building a BCD version. The user requires that failures from earlier builds be retained and prevented, not rediscovered. This is the complete first-build-to-current run ledger for the 0.1.712 upstream-Cloud branch (#47–62), plus the verified prior IPA baseline. It is not a claim to have audited every historical run of every branch.

## Proven baseline and current checkpoint

- Older successful IPA: [run 45028450936](https://github.com/sky9662/bcd-games/actions/runs/45028450936), source `6ef3ed8f5e6d36a2f81e96d2f9d35cf78391c67b`, artifact [14761973158](https://github.com/sky9662/bcd-games/actions/runs/45028450936/artifacts/14761973158), branch `feature/turing-success-touch-acceleration-ipa`. Preserve its dependency recovery, Xcode/SDK selection, source pins, cache strategy and packaging, not its entire older app tree.
- Current target: `feature/bcd-0712-upstream-cloud-ipa`, artifact `bcd-0712-upstream-cloud-unsigned-ipa`; keep independent touch acceleration, Turing FEX recheck, Madeira profile unification and CI fixes. No changes to main, other PRs, releases or device saves.
- Latest checked [run #62](https://github.com/sky9662/bcd-games/actions/runs/45592898592), source `a34d1b66671179cac73e094c0c484cd6a54fe4d3`: both Linux jobs passed, macOS step 11 queue-gate test and step 12 complete native VideoToolbox test passed, step 34 native Duo interface running, no failed steps at snapshot. DXC/OpenGL actual builds and final IPA pending. A later documentation-only commit does not change these build inputs or retroactively change the run SHA. Follow the active run even if the docs-only head differs. Do not trigger another run for this documentation update.

## Every failed run of this branch

First fatal named step from actual Actions jobs; step numbers change as checks move and do not measure elapsed work. The detailed causes and evidence are in CI-LESSONS.md. "Passed later" means a later run passed that specific gate, not that the full IPA was successful.

| Run | First fatal step | Root cause / prevention | Evidence state |
|---|---|---|---|
| [47](https://github.com/sky9662/bcd-games/actions/runs/45363457250) | 29 Classic parity | BCD-visible branding; seed fresh prefix before one-shot migration; preserve internal identities | Passed later |
| [48](https://github.com/sky9662/bcd-games/actions/runs/45366916878) | 291 Wine sign-in redaction patch | Exact-line workflow assertions failed with identical-script fallback; normalize via workflow_commands.py and audit all analogous checks. Separate KK failure: floating LLVM 23 incompatible; pin LLVM 22 via KK_LLVM_CONFIG | Passed later; KK built/cached |
| [49](https://github.com/sky9662/bcd-games/actions/runs/45382700524) | 325 IPA/OTA contract | Explicit unsigned-mode contract; retain paired upload and forbid signing/publication | Passed later |
| [50](https://github.com/sky9662/bcd-games/actions/runs/45416654858) | 415 Wine Vulkan pacing | Host oversleep polluted timing test; controlled Mach clock plus native wait lower bounds and missing-wait negative control | Passed later |
| [51](https://github.com/sky9662/bcd-games/actions/runs/45429967366) | 433 D3D8/DirectDraw routes | Missing pinned vendor README/license files; restore exact upstream bytes and verify all manifests | Passed later |
| [52](https://github.com/sky9662/bcd-games/actions/runs/45479155786) | 456 Metal Shader Converter headers/dependency | Missing proprietary pinned iOS dylib; restore exact archive and library by SHA-256 early; no stub/macOS substitute | Passed later |
| [53](https://github.com/sky9662/bcd-games/actions/runs/45494579844) | 564 VideoToolbox | Simulated game FPS driven by real host sleeps; controlled Mach/Quartz clock, real async worker | Partial fix; next race exposed |
| [54](https://github.com/sky9662/bcd-games/actions/runs/45506929959) | 10 VideoToolbox | 30 ms extra delay exposed fake model ready too early; gate initial readiness, preserve format/surface/order checks | Passed later |
| [55](https://github.com/sky9662/bcd-games/actions/runs/45508567740) | 630 build-591 engine checks | New SDK ARM accessor macros collide with synthetic context; undefine before stand-ins, audit family; preserve sanitizers | Passed later |
| [56](https://github.com/sky9662/bcd-games/actions/runs/45520810311) | 755 Windows Vulkan | Public export lacks exact untracked README; split documentation-only skip from mandatory packaging/DLL checks | Passed later |
| [57](https://github.com/sky9662/bcd-games/actions/runs/45530002175) | 10 VideoToolbox | Backpressure and phase-4 readiness races; fake-model gating alone insufficient; wait for lifecycle events | Superseded by #62 fix |
| [58](https://github.com/sky9662/bcd-games/actions/runs/45531234472) | 10 VideoToolbox | 130 ms delayed phase missed busy-skip; copy wait gate still too late for decision | Same assertion recurred #61 |
| [59](https://github.com/sky9662/bcd-games/actions/runs/45532286385) | 773 FEX call/return elision | Squashed mirror lacks exact test baseline; restore canonical FEX/DXMT history without changing build HEAD; maintain final overlay order | Passed later #60 |
| [60](https://github.com/sky9662/bcd-games/actions/runs/45542157073) | 819 mandatory opt-in DLLs | DXC HCT generated-header byte comparison failed with ambient formatter; pin clang-format 17.0.1 wheel/executable. Wine OpenGL guard incorrectly rejected its own exact NULL-sync overlay | Source guard passed #61; actual DXC/OpenGL DLL builds pending |
| [61](https://github.com/sky9662/bcd-games/actions/runs/45591200543) | 11 VideoToolbox | Same 130 ms busy=0 assertion twice. Production samples backlog BEFORE copy wait/model. Insert bounded gate at actual serial queue head; require two genuine outstanding frames before release | #62 gate and full native harness passed |
| [62](https://github.com/sky9662/bcd-games/actions/runs/45592898592) | 674 opt-in DLL shadowing | Early DXC now triggers old partial-set heuristic before Wine extras/dcomp; explicit source-only stage and strict final built-set verification | DXC built/verified/cached; fix pending CI |

| [63](https://github.com/sky9662/bcd-games/actions/runs/45610481322) | 91 round 624 log lines | Previous fix changed exact mandatory DLL verifier command from inline to YAML block; restore original step, add separate strict shadow verification | Existing assertion and stage controls checked against repaired workflow; CI pending |

| [65](https://github.com/sky9662/bcd-games/actions/runs/45633943883) | 896 Steam for Windows | Missing untracked docs/STEAM_DESKTOP.md only; explicit documentation exception | DXC restored, OpenGL and all 44 named DLLs verified, FEX lean passed; fix pending CI |

| [66](https://github.com/sky9662/bcd-games/actions/runs/45652561853) | SUCCESS | Both unsigned IPAs verified and uploaded | CI complete; device testing pending |

## Mandatory workflow for every future version

### 1. Before editing or dispatch
- Read AGENTS.md, this runbook, CI-LESSONS.md and relevant feature handoff; fetch current target branch and check all active/queued and successful runs plus actual artifacts. Do not dispatch duplicate work or cancel another build. If a workflow push queues it, follow that run. Docs-only commits with identical build inputs do not require a new build; report the actual build SHA.
- For an upstream upgrade, compare *all* workflow steps, dependencies, submodule pins, cache keys, Xcode/SDK and test inputs against the successful baseline AND the latest repaired workflow. Inventory independent feature fixes and CI fixes as separate patches/commits; transplant/rebase these, not an old entire app tree. Resolve conflicts with evidence. Never blindly replace the repaired workflow with the upstream one.
- Audit source pins and vendor hashes, fixture presence including literal exists/is_file checks, workflow-command assertions and all similar failures together. Do not change production functionality just to pass a test; do not suppress a compiler or package failure.

### 2. Run inexpensive preflight before expensive macOS work

Run from repository root using Linux/WSL where applicable (with correct 4 KiB host pages for guest-instruction test). Preserve native macOS-only checks in CI; unavailable locally is not passed. Run `git diff --check`, shell syntax, Python syntax and inspect staged files. For these paths use:
```sh
python3 tests/host/check-workflow-commands.py
python3 tests/host/check-ipa-workflow-contract.py
python3 tests/host/check-vk-fps-pacing.py
python3 tests/host/check-vulkan-bcd.py --public-source
python3 tests/host/check-host-arm-accessors.py
python3 tests/host/check-vt-interp-clock.py
python3 tests/host/check-gl-optin-tree.py
bash -n tools/build-dxcompiler.sh
bash -n tools/build-wine-extra-dlls.sh
python3 tools/check-vendored-manifests.py --index
python3 tools/ci-preflight-host-fixtures.py --strict
python3 tests/host/check-guest-instruction.py
python3 tests/host/check-swap-diag.py
git diff --check
```
Use `--index` for staged bytes locally; CI checkout uses no flag. Run the queue gate `python3 tests/host/check-vt-interp-queue.py` with clang and libdispatch (macOS or Swift Linux toolchain), and the full native `check-vt-interp.py` on macOS, with 30/130 ms stress cases, before long dependency builds. Preserve profile migration/Steam Cloud/remotecache checks and native ARM fault tests. Do not describe unavailable preflight as completed. Treat strict checks as mandatory, only explicitly recognized missing untracked public fixtures can be documented skips.

### 3. Dependency and cache discipline
- Keep exact FEX/DXMT build HEADs, restore historical test SHAs via `tools/fetch-host-test-baselines.py`, and check canonical history and unchanged HEAD. Maintain Turing independent recheck before final ARM64EC pool overlay.
- Keep hash-verified Metal Shader Converter iOS recovery, all six vendored manifests, KK LLVM 22, LLVM 15.0.7 iOS, current llvm-mingw and actual runner/toolchain requirements. Pin DXC formatter 17.0.1 (macOS universal2 SHA-256 `88b84ef2255a95b4e4aeaf3c207f4f7521e821b6988e91948318ce5ce4665670`, verified against https://pypi.org/project/clang-format/17.0.1/); preserve generated-header exact compare. This pin is not yet proven to solve the full native build.
- Preserve known-good FEX iOS/ARM64EC/WOW64, LLVM iOS, i386 farm, KosmicKrisp and ICU caches; save successful verified components as soon as available. Invalidate only affected cache keys when inputs change. Check actual restore/save logs; GitHub caches are branch-scoped and may miss. Never restore wrong-architecture or stale unchecked binaries.
- Keep DXC restore/build/save after llvm-mingw, require DLL immediately; exact Wine OpenGL overlay guard, PE machine/base/export and final opt-in DLL checks remain mandatory.

### 4. On failure
- Read full first fatal step logs and surrounding context, not merely run conclusion or later diagnostics. Record run number/URL/SHA, precise assertion/command, root cause vs hypothesis, affected files, fix commit, local checks and next CI proof.
- A recurrence of the same assertion requires revisiting actual control flow and a reproducible positive/negative regression, not merely longer sleeps, retries, or threshold relaxation. For async harnesses control game time independently of real worker time; gate before the decision, observe events and use bounded waits. Do not repeat the rejected copy/model gates from #57/#58/#61.
- Audit related failures in one pass; put cheap deterministic checks early and preserve caches. Retry once per proven change, check no active build before workflow push. Report when proof is incomplete; do not invent local tests. Update this ledger after each meaningful new failure or confirmed fix, including future versions.

### 5. Success criteria and device safety
- Green job alone is insufficient. Require actual artifact; run `tools/verify-upstream-cloud-ipa.py` before upload, checking ZIP CRC, both identities `com.thebcd69.bcd` and `com.thebcd69.bcd2`, expected version (0.1.712 now), actual MadeiraCommit, BCDTouchAcceleration and [profile] one Windows profile markers, [tc-exec-recheck] in both xtajit64 DLLs. Update version expectations deliberately for future versions.
- Record actual run/artifact URL, source SHA, real pass/skip evidence, install/sign/JIT steps. Archive the known-good workflow/pins and successful cache metadata for the next upgrade. Do not claim successful device validation without it. Back up both `wine/drive_c/users/mythic` and `mobile`; no automatic conflict resolution or edits to real saves.
- After success, keep this runbook/lessons plus CI fixes in any future build branch. Ensure AGENTS.md and handoff point to them; if a future version starts from clean upstream, explicitly cherry-pick/rebase the documentation and independent CI fixes first. Do not depend on chat memory or task IDs to recover build knowledge.

## Follow-up register (not completed)
- #62 DXC built/verified/cached; next run must prove corrected staged shadow check, actual OpenGL payload, final IPA/artifact and device validation.
- Record per-component cache hit/miss and timings after a successful build; design a separate cheap preflight workflow if useful, without weakening the existing complete suite. Do not promise a fixed build duration; runner availability, cache misses and new upstream changes can introduce new issues.

## Pending project task — shared IPA infrastructure (user approved 2026-11-25)

**Status: pending; successful IPA build and payload verification now confirmed by Run #66. Device testing and infrastructure separation remain pending.** Do not restructure branches, merge feature branches, or modify the active workflow while the current IPA is being built. After the verified artifact is available, use the exact successful source SHA as evidence for separating infrastructure; do not assume a failed run or a source-only check establishes a known-good baseline.

- [x] Record the verified IPA run, artifact, source SHA, test outcomes, explicit skips and confirmed cache restores (Run #66 below; retain source-pinned toolchain metadata).
- [ ] Inventory independent CI fixes and feature-specific changes against the matching official upstream release. Separate mixed commits by reviewing their diffs; do not copy the entire combined feature tree.
- [ ] Create a dedicated `build/ipa-infrastructure` branch from an appropriate upstream base containing only shared build workflow improvements, dependency recovery, source/SDK/toolchain pins, cache strategy, regression tests, verification tools and persistent build documentation. Separate generic infrastructure from feature-specific payload assertions; retain strict checks appropriate to each build.
- [ ] Validate the infrastructure branch independently. Confirm a build without custom features works, and that a separate test branch can inherit infrastructure and one isolated feature without acquiring unrelated features. Record resulting commits, run/artifact evidence and documented migration procedure for later upstream versions.
- [ ] Keep all existing feature/PR branches independent. Never merge features into each other, main or upstream merely to share build fixes; preserve clean upstream-facing PR diffs. Use disposable or explicitly named build/integration branches for test IPAs and selective cherry-picks/rebases of infrastructure fixes. Do not alter existing PR branches without explicit authorization.
- [ ] Establish a cross-branch discovery rule in the Windows Codex global `~/.codex/AGENTS.md` (and other applicable Codex environments) instructing agents working on `sky9662/bcd-games` to read the shared infrastructure branch's `AGENTS.md`, `docs/local-build/IPA-BUILD-RUNBOOK.md` and `CI-LESSONS.md` before any IPA build, even on a fresh upstream branch. Inspect existing global instructions and preserve unrelated rules. Local access and actual installation must be verified; do not claim a GitHub documentation edit configures the user's PC. ChatGPT/GitHub agents should explicitly fetch the canonical shared branch when building.
- [ ] Document the canonical branch and reusable CI commit set, update handoff references, and establish a rule to record future failures in the shared infrastructure branch and selectively propagate fixes to relevant build branches. Keep old independent PRs until upstream accepts them; check upstream acceptance before dropping or replacing a patch.

Acceptance: a new isolated feature can use the already proven build infrastructure without merging other features or requiring the user to explain old failures; separate PR diffs stay clean. No automatic upstream PR, main merge, release replacement or modification of real device saves. The current user request authorizes recording this follow-up, not premature restructuring or starting duplicate builds.

## Run 62 — partial DLL set must not trigger final shadowing check

[Run #62](https://github.com/sky9662/bcd-games/actions/runs/45592898592), source `a34d1b66671179cac73e094c0c484cd6a54fe4d3`, passed the native VideoToolbox gate and full harness, both Linux jobs, DXC 1.9.2609 with clang-format 17.0.1 (x86-64 PE/export/import validation, 20,700,672-byte DLL). DXC cache saved under `dxc-win-x64-v1-fc41befb5d40d13190879585e898d20cb1a6568c94354a77ee3c866b9604e426`; do not change its inputs or key. First fatal macOS step 674: `FAIL of the shipped opt-in DLLs only dcomp is shadowed that way ([])`, repeated on diagnostic retry. Early DXC build now makes the old heuristic any(*-optin.dll) true before Wine extras produce dcomp-optin.dll. No evidence that dcomp compilation failed: it had not run. Explicitly run only the source contract at that stage and defer only the shadow assertion to mandatory final built-set check after Wine extras and ICU, alongside the existing required-DLL check. Preserve exact ['dcomp'] assertion, fail missing sets, no fixture waiver for final payload. Six focused local Python controls (empty, DXC-only, expected dcomp, unexpected ARM64 dcomp, extra shadow, directory impostor) and py_compile passed for the new checker; full repository/native CI pending. OpenGL actual DLL build remains unverified; no IPA. No feature or cache-key changes. Future rule: never infer all artifacts ready from one earlier-produced artifact; use explicit build-stage contracts and mandatory post-build checks.

## Run 63 — preserve existing CI command contracts when adding a verifier

[Run #63](https://github.com/sky9662/bcd-games/actions/runs/45610481322), source `7e8be54669a61b6fe7b995b10f16d8cd3a7433a8`, passed both Linux jobs including all six opt-in shadowing fixture controls, and both native VideoToolbox tests. First fatal macOS step 91 (round 624 log lines): check-kernelbase-optin.py's assertion requires the existing literal single-line `run: python3 tools/check-optin-dlls-shipped.py app/Madeira/arm64ec-windows` and unconditional execution after Wine extras. Run #62 fix inadvertently converted this step to a YAML block, triggering the already-known workflow formatting failure family. Restore its exact original single-line command and add a separate mandatory, unconditional shadowing step immediately after it. Preserve early explicit source-only mode and every payload assertion, do not weaken the existing kernelbase test. Checked the actual prior and repaired workflow against the existing assertion in this repair invocation (old fails, new passes), plus stage-order/command contract and five negative mutations (multiline legacy step, continue-on-error, missing verifier, conditional skip, lost source-only flag). Added corresponding Python workflow controls to existing Linux preflight; actual Python/CI execution is pending, not claimed. No production source, component cache-key or toolchain changes. Before workflow edits, check existing exact-command assertions against the proposed text; prefer adding new steps without changing legacy command shape. DXC cache saved by #62; #63 stopped before restoring it. OpenGL and IPA remain unverified.


## Run 64 — separate read-only guard from overlay replay

[Run #64](https://github.com/sky9662/bcd-games/actions/runs/45615712650), source `1712fba422c441e3c5bca65bd870df0e96762380`, passed both Linux jobs and failed macOS step 887 in check-fex-callret-lean.py. All 19 overlays and subsequent lean behavior checks passed individually; parser rejected the exact read-only Turing guard command as an unknown overlay. Fix `2b4cd4fb8c4ea2832ed6071186afeab68daafd6d` classifies only that exact command separately; real build still executes it, unknown commands still fail, overlay count and order checks remain. Static anchor and strictness checks performed; full checkout/native tests not executed locally. Workflow trigger `f168b0d1bb3a3b994ee93b574cc60ae1bf274da7`; next CI evidence pending. No production or cache changes.

## Run 65 — missing public documentation, not Steam functionality

[Run #65](https://github.com/sky9662/bcd-games/actions/runs/45633943883), source `f168b0d1bb3a3b994ee93b574cc60ae1bf274da7`: both Linux jobs passed; macOS reached step 896 of 920 named steps, 859 successful including #64 FEX lean (887), opt-in source (674), named DLLs (821, all 44), shadowing (822, exactly dcomp), and actual OpenGL DLL build. DXC cache restored. Only `docs/STEAM_DESKTOP.md describes it` failed twice; native functional and wiring assertions passed. This exact document is absent in the public tree. Keep all six terms when present and strict missing-file failure by default; explicit public-export mode allows only this absent untracked document. Tracked missing, malformed, directory, symlink or Git error remain fatal. Standalone checker with eight controls and actual checkout check early in Linux, full Steam test uses same checker with step-scoped env and original command. Next X-Plane, Dock census and clipboard tests reviewed for similar missing-document assertions; none seen. No production or cache-key changes. New checker awaits CI execution; no claim of local execution. Remaining farm/OpenGL/Vulkan/archive/package/IPA checks pending. No IPA yet.
