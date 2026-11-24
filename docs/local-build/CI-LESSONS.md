# IPA build lessons — read before the next version

Recorded 2026-11-24 at the user's request. Keep these independent CI fixes when porting features to a newer release. Do not transplant an older whole release tree just because it built successfully.

## Verified successful baseline

- Run: https://github.com/sky9662/bcd-games/actions/runs/45028450936
- Source: `6ef3ed8f5e6d36a2f81e96d2f9d35cf78391c67b`, branch `feature/turing-success-touch-acceleration-ipa`.
- Actual IPA artifact: `bcd-turing-complete-fex-unsigned-ipa`, artifact ID `14761973158`, 452,299,768 bytes, uploaded 2026-11-22.
- Its workflow has 272 named steps and references 69 distinct host checks. The initial 0.1.712 upstream-Cloud workflow has 909 named steps and references 802 checks. A successful older IPA does not establish that the expanded newer suite passes.
- Preserve the proven Xcode/SDK selection, Debug archive, Wine/FEX/DXMT source pins, Dock-only public-submodule fallback, dependency caches, Turing DLL marker checks, and unsigned two-identity packaging. Compare individual changes against this baseline; do not downgrade the new app tree to it.

## Failures and prevention

| Evidence | Root cause | Fix / next-version rule |
| --- | --- | --- |
| Run `45363457250`, parity check | The newly ported profile-migration log said `Files › Madeira`, while this app is BCD. | Use `Files › BCD` in visible text; retain internal support-directory and bundle identities. Run the branding/source check before requesting another expensive build. |
| Source inspection of fresh installation | `ProfileUnification.run()` was called before the template created `system.reg`, so its one-shot startup invocation could miss the new prefix. | Seed the prefix before profile migration, before background/view startup. Keep the regression in `check-profile-unification.py`. Never test against real device saves automatically. |
| Run `45366916878`, sign-in-value mirror check | An exact test-command/newline assertion did not recognize `test || ci-optional-fixture-check.py test`. The compiled helper and complete mirror ASan checks themselves passed. | Use `tests/host/workflow_commands.py` for workflow ordering, exact-line and command-count assertions. Normalize only a fallback that retries the identical script and arguments. Cover block and inline YAML `run:` commands. Do not remove ordering or runtime assertions. |
| Same source audit | Adjacent guest-log, Dock and other checks had the same raw-string assumption; four diagnostic checks counted the test twice because of its fallback. | Audit the complete referenced suite for the same pattern in one pass, rather than spending a new macOS build on each occurrence. Keep `check-workflow-commands.py` positive and negative controls in the Linux preflight. |
| Run `45366916878`, KosmicKrisp build | Homebrew's unversioned LLVM was 23; the pinned SPIRV translator supports LLVM 21/22. The optional step warned and omitted KosmicKrisp. | Install `llvm@22` for that component and export its `llvm-config` as `KK_LLVM_CONFIG`; do not change the global Wine/FEX toolchain to fix this one library. Verify the library actually built; a warning/omission is not proof of preserved functionality. |
| Existing upstream fixture omissions | The public release omits some documentation and fork-only log-intake files. Some DXMT tests also require an unavailable overlay baseline. | Preserve strict fixture classification and explicit warnings. An absent fixture is **not a passing regression**. Never use this fallback for compiler failures, DLL checks or IPA verification; never fabricate missing fixtures. |

## Before dispatching or pushing a workflow change

1. Read the current handoff and this file. Inspect the target branch SHA, active/queued runs and actual artifacts. A workflow push can already start the build; never immediately add a manual dispatch. Do not cancel other builds.
2. Compare the new workflow with the verified successful baseline, including the number of tests and toolchain versions. Check formatting assertions across the whole suite when adding fixture guards. Fix the family of proven failures together.
3. Run `python3 tests/host/check-workflow-commands.py`, `python3 tools/ci-preflight-host-fixtures.py --strict`, syntax checks and `git diff --check`. Put new, focused regression checks early on the appropriate runner. Source checks on Windows are not Swift/C/iOS execution evidence.
4. Keep Xcode/SDK selection, source pins, compatibility patches and cache keys unless evidence requires a specific change. Record component compiler majors: a floating Homebrew formula can change while app source remains the same. GitHub caches are branch-scoped; a new feature branch may have to rebuild dependencies even when another feature branch built them before.
5. On failure, read the failed step's full log. Distinguish a wrong workflow assertion, missing optional fixture, unsupported compiler and actual compiler/runtime failure. Preserve successful caches before retrying. Check for an active or successful matching run again immediately before starting another.
6. Require the expected IPA artifact, not just a green job. Verify both payloads' bundle IDs, version and `MadeiraCommit`, ZIP integrity, touch-acceleration symbol, Cloud-migration log marker, and `[tc-exec-recheck]` in both shipped FEX DLLs. `tools/verify-upstream-cloud-ipa.py` performs this for the 0.1.712 test build; update its version expectation deliberately for future versions.
7. Report the actual run URL, artifact URL, source SHA and real test results, including explicit skips. Before any device test, back up **both** `wine/drive_c/users/mythic` and `mobile`. A per-file newer timestamp is not proof of a coherent game save set; do not automatically resolve Steam Cloud conflicts.

## Current status at this entry

The two 2026-11-24 runs above failed before App archive and produced no target IPA. The startup/branding fix is commit `a44732d4e3617b9c41aee4bc4d4eda16950893bd`; its macOS migration, branding and touch/players steps completed successfully. Workflow-normalization coverage and the component-specific LLVM selection require the next full CI run. Replace this paragraph with final run/artifact evidence after verification; do not claim success in advance.

Work stays on `feature/bcd-0712-upstream-cloud-ipa`. Do not change main, existing PR branches, releases, upstream PRs or device saves.
