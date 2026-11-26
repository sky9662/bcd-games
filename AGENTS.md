# BCD shared IPA infrastructure — mandatory for every build branch

Canonical instructions: `sky9662/bcd-games:build/ipa-infrastructure`. Before any IPA build, read this file, [IPA-BUILD-RUNBOOK.md](docs/local-build/IPA-BUILD-RUNBOOK.md), [CI-LESSONS.md](docs/local-build/CI-LESSONS.md) and [CROSS-BRANCH-BUILDS.md](docs/local-build/CROSS-BRANCH-BUILDS.md) from the current canonical branch head, even when another branch is checked out. Historical integrated-build feature requirements apply only to that feature combination.

Preserve independent feature and upstream PR branches. Never merge unrelated features to get CI fixes. Start dedicated build branches from the matching official release plus reviewed infrastructure-only changes; apply only requested features and their explicit payload checks before upload. Generic verification proves identity, CRC and source SHA, not custom feature correctness. Preserve pinned inputs and cache keys; isolate feature-dependent cache inputs. Run preflight before expensive builds. Record every new root cause and verified correction back here. Do not duplicate active runs, waive compiler/payload failures, or modify main, existing PRs, releases or device saves.

Run #66 is the proven integrated baseline. Independent clean infrastructure CI and isolated-feature CI must be verified separately.
