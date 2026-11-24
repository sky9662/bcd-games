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
Use the existing authenticated local git/gh session. Fetch the work branch, check its latest SHA and existing runs before starting a new run. The branch-specific workflow push may already have queued a run. Avoid duplicate runs; no cancellation of other builds. 
```powershell
gh run list --repo sky9662/bcd-games --branch feature/bcd-0712-upstream-cloud-ipa --limit 10
# Only if no active or successful matching build exists:
gh workflow run build-ipa.yml --repo sky9662/bcd-games --ref feature/bcd-0712-upstream-cloud-ipa
```
Use GitHub's macOS runner for IPA, not native Windows Xcode. Preserve the prior successful pipeline, Xcode/SDK selection, submodule fallback, FEX patch, artifact reuse and preflight handling. Review the current workflow rather than rewriting it. Validate the profile parser, migration test, existing Cloud, fetch and remotecache regressions; verify startup ordering, fresh-prefix handling and baseline reset. Fix actual errors on this branch only. If a run fails, inspect failed job logs, correct root cause, commit and retry. Do not silently skip tests or mark missing fixtures as passes.
Expected artifact: bcd-0712-upstream-cloud-unsigned-ipa. Verify IPA exists and includes both prior feature changes and Cloud migration. Report actual run URL, artifact URL, SHA, test outcomes, installation instructions, and backup warning. No upstream PR, main changes, release replacement or device-save modifications. Current handoff does NOT assert CI or IPA success.
