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

# Windows Codex handoff: BCD 0.1.712 + Madeira profile unification

## Scope
- Repository: sky9662/bcd-games
- Work branch: feature/bcd-0712-upstream-cloud-ipa
- Tested-feature base: feature/bcd-0712-turing-touch-ipa, commit 64cbe5a6760bb8327ff19cb4ffda837b5fa30c3e
- Preserve all existing feature work (touch mouse acceleration and Turing Complete FEX recheck); no edits to main or existing PR branches, no upstream PR yet.
- Separate PR branches remain pr/touch-mouse-acceleration, pr/turing-complete-compatibility, pr/touch-editor-multiselect-alignment. For future versions transplant the independent changes, not an old entire release tree.

## Cloud port
Source: https://github.com/willfaust/Madeira/blob/v0.2.0/app/Madeira/SteamCloud.swift
Ported ProfileList parsing, profile-first path resolution, ProfileUnification and startup invocation. Kept BCD's Cloud transport and external-storage validation. Added upstream migration tests and a dual-user resolver test; isolated the migration class from existing standalone Cloud/remotecache Swift test slices. See diff against feature/bcd-0712-turing-touch-ipa. Implementation commits precede build workflow commit 98fc2ca4e047c3c323cb6608b13e9e6488feb769.

Observed on device: Turing Complete writes users/mythic; Cloud's same=28 matched users/mobile instead, with counting_signals present only in mobile and cloud. Migration copies old profile into Unix-named profile, keeps original and backs up collisions, resets the Cloud baseline. Per-file modification time is not necessarily a coherent save-set version; back up BOTH user profiles before testing, inspect conflict prompts and verify game progress; don't automatically resolve real cloud conflicts. Do not access or alter device saves.

## Build ownership: Windows Codex
Before building this or a future version, read [the mandatory build runbook](local-build/IPA-BUILD-RUNBOOK.md) and [the recorded CI lessons](local-build/CI-LESSONS.md): verified earlier IPA baseline, whole-suite workflow-assertion fixes, component-specific LLVM selection, cache reuse and non-duplicate dispatch checks. The user explicitly requested that these lessons persist across version upgrades.

Use the existing authenticated local git/gh session. Fetch the work branch, check its latest SHA and existing runs before starting a new run. The branch-specific workflow push may already have queued a run. Avoid duplicate runs; no cancellation of other builds. 
```powershell
gh run list --repo sky9662/bcd-games --branch feature/bcd-0712-upstream-cloud-ipa --limit 10
# Only if no active or successful matching build exists:
gh workflow run build-ipa.yml --repo sky9662/bcd-games --ref feature/bcd-0712-upstream-cloud-ipa
```
Use GitHub's macOS runner for IPA, not native Windows Xcode. Preserve the prior successful pipeline, Xcode/SDK selection, submodule fallback, FEX patch, artifact reuse and preflight handling. Review the current workflow rather than rewriting it. Validate the profile parser, migration test, existing Cloud, fetch and remotecache regressions; verify startup ordering, fresh-prefix handling and baseline reset. Fix actual errors on this branch only. If a run fails, inspect failed job logs, correct root cause, commit and retry. Do not silently skip tests or mark missing fixtures as passes.
Expected artifact: bcd-0712-upstream-cloud-unsigned-ipa. Verify IPA exists and includes both prior feature changes and Cloud migration. Report actual run URL, artifact URL, SHA, test outcomes, installation instructions, and backup warning. No upstream PR, main changes, release replacement or device-save modifications. Current handoff does NOT assert CI or IPA success.


## Resume checkpoint — 2026-11-25, Windows to ChatGPT

User requested handing this work back to ChatGPT because Codex usage is nearly exhausted. Continue directly through GitHub; no remote control of the Windows PC is required. Work only on `feature/bcd-0712-upstream-cloud-ipa` and read `docs/local-build/CI-LESSONS.md` first.

Last completed run: #59, https://github.com/sky9662/bcd-games/actions/runs/45532286385, source `5b8edd5bf8332bc59710d627d232dc195deca850`. It reached step 773 of roughly 918, then failed fetching the historical FEX test baseline from the squashed mirror. No target IPA has been produced. Reaching 84% of step numbers is not a completion-time guarantee: App archive/package/payload verification have not run yet.

The checkpoint commit accompanying this document restores exact canonical FEX/DXMT test history, removes the old baseline skips, restores both GPU checks, keeps the final ARM64EC exit-overlay ordering while retaining Turing, and fixes the shader-cache host fixture include. Local results and explicit skips are in CI-LESSONS.md. Both build submodule HEADs are unchanged. Main, PR branches, releases and device saves were not changed.

Before doing anything, fetch the latest branch and list its active/queued runs. This workflow push automatically starts one new build; do not immediately dispatch another or cancel other work. Monitor that newest run; if it fails, inspect the full failed-step log, fix the actual cause on this branch, complete portable checks before another workflow push, and repeat until the exact target artifact exists. Windows/WSL can run portable tests; the full app archive still requires macOS/Xcode.

Success requires actual `bcd-0712-upstream-cloud-unsigned-ipa`, both IPA identities/version/source SHA, ZIP integrity, touch acceleration and Cloud migration binary markers, and Turing `[tc-exec-recheck]` in both FEX DLLs. `tools/verify-upstream-cloud-ipa.py` runs before upload. Report run/artifact links, actual source SHA, real tests and explicit skips; do not call a missing fixture a pass. Before device use, back up BOTH `wine/drive_c/users/mythic` and `mobile`; no automatic Cloud-conflict resolution or device-save changes.

User asked about half-hour checks. This Codex environment cannot create a scheduled automation to watch one build through failure/completion; no new half-hour automation was created. Continue the authorized monitor/fix/rebuild work in the receiving chat and state actual background-execution limitations honestly. The earlier one-shot Windows resume schedule has already fired.

## Latest checkpoint — 2026-11-25

Read the [permanent build runbook](local-build/IPA-BUILD-RUNBOOK.md) before all future builds. Run #62 (45592898592, a34d1b66671179cac73e094c0c484cd6a54fe4d3) is active at documentation review, with both Linux jobs and native VideoToolbox queue/full tests green. Follow the active run even if a docs-only commit advances the branch head; no duplicate dispatch. The exact target artifact and actual DXC/OpenGL builds are not yet verified. Update the ledger with future failures and confirmed successes. The earlier #59 checkpoint is historical.

## Approved follow-up after verified IPA

See [shared IPA infrastructure pending task](local-build/IPA-BUILD-RUNBOOK.md#pending-project-task--shared-ipa-infrastructure-user-approved-2026-11-25). Separate CI infrastructure from custom features only after the current IPA is verified; preserve independent PR branches and establish cross-branch Codex discovery. Do not merge branches or interrupt the active build for this task.

## Run #62 completed — next run

DXC 1.9.2609 compiled, verified and cached; native VideoToolbox passed. Run #62 stopped before Wine extras at step 674 because early DXC made a partial DLL set look complete. See runbook/CI lessons. Preserve DXC cache and use explicit source-stage opt-in checks plus mandatory final DLL shadowing and named-DLL verification. New workflow push queues next run; do not dispatch twice. Pending shared infrastructure task remains blocked until verified IPA.

## Run #63 completed — next run

Both Linux jobs and native VideoToolbox passed. Run #63 stopped at step 91: the #62 fix changed the named opt-in DLL verification's exact YAML run command to a multiline block, violating the legacy kernelbase regression. Restore the original command and separate the mandatory shadowing step; early Linux workflow stage controls added. Preserve DXC cache and strict payload checks. New workflow push queues next run; no duplicate dispatch. Infrastructure follow-up remains blocked until verified IPA.

## Run #65 checkpoint

Reached step 896, DXC cache restored, OpenGL built and 44 opt-in DLLs verified. Only absent STEAM_DESKTOP.md assertion failed; narrow explicit public-source documentation exception added with early controls. Preserve strict functional/IPA checks. Next workflow push triggers new run; no duplicate dispatch. Infrastructure follow-up blocked until verified IPA.
