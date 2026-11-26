# Cross-branch IPA builds

Canonical branch: [build/ipa-infrastructure](https://github.com/sky9662/bcd-games/tree/build/ipa-infrastructure). Clean official base `f811dd05a9183cda20ffd3956cb1958cafe654f7`; proven integrated Run #66 source `2fa14a0b1fcdd983f51897ff425e5f2c2ecdf917`. This extracted tree requires its own CI verification. Existing PRs, feature branches, main and the verified IPA remain unchanged.

1. Fetch canonical branch, read AGENTS.md and the two historical build manuals. Compare the requested official release against the infrastructure base and review the CI-only diff; never replace new upstream with an older combined tree.
2. Create a separate build branch, e.g. `build/ipa-validation-touch`, from the matching reviewed infrastructure tree; port only requested feature patches. Keep upstream-facing PRs clean. For future versions, port reviewed infrastructure-only changes onto the matching release and validate again.
3. Generic verifier checks both bundle IDs, version, actual SHA, CRC, executable and PE modules. The clean infrastructure build also rejects the three custom feature markers. For feature builds add the required feature regression and payload markers; never rely solely on generic verification.
4. Run portable preflight and macOS CI. Preserve verified caches but separate feature-dependent compiled cache inputs; branch scope can cause cold misses. Check active runs before dispatch. Write new root causes and verified fixes back here and selectively propagate them.
5. Validate clean infrastructure first, then a separate branch with one isolated feature and a strict corresponding payload check. Do not merge unrelated features or alter existing PRs.

## Read without changing checkout

```powershell
git fetch origin refs/heads/build/ipa-infrastructure:refs/remotes/origin/build/ipa-infrastructure
git show origin/build/ipa-infrastructure:AGENTS.md
git show origin/build/ipa-infrastructure:docs/local-build/IPA-BUILD-RUNBOOK.md
git show origin/build/ipa-infrastructure:docs/local-build/CI-LESSONS.md
git show origin/build/ipa-infrastructure:docs/local-build/CROSS-BRANCH-BUILDS.md
```

Assumes origin is the user's fork. No checkout or merge required.

## Cross-branch discovery

[CODEX-GLOBAL-AGENTS.md](CODEX-GLOBAL-AGENTS.md) is a template for the global Codex instructions. Append a uniquely marked block to the actual global AGENTS.md (CODEX_HOME, otherwise ~/.codex), preserving unrelated rules and checking AGENTS.override.md precedence. Restart Codex and verify the instructions are picked up from a clean checkout. This GitHub document does not install anything on the PC. ChatGPT connector agents must explicitly fetch the canonical branch. A fresh chat or agent without global instructions is not guaranteed to discover it automatically.

## Status

Historical evidence saved; candidate infrastructure extracted; clean CI and isolated feature CI pending. Global PC rule installation pending local access. Do not restart the successful Run #66 target solely to validate the shared branch.
