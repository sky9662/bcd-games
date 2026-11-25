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
