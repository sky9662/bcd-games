# IPA and CI work

Before building an IPA, changing CI or porting this work to another version, read [the mandatory IPA build runbook](docs/local-build/IPA-BUILD-RUNBOOK.md), [the persistent build lessons](docs/local-build/CI-LESSONS.md), and the current branch's handoff. Carry these documents and independent CI fixes into every new release branch before building. Update the failure ledger after each meaningful new failure or confirmed fix; require real positive/negative evidence for repeated failures. The user explicitly requested that past build failures and successful build methods be retained across versions.

Keep independent feature/CI fixes when upgrading; do not replace a new release tree with an old successful tree. Check active runs before any dispatch or workflow push. Preserve test assertions, distinguish explicit fixture skips from passes, and verify the actual IPA and its source SHA before reporting success.

Documentation-only commits do not invalidate an active build with identical build inputs. Follow that run's actual source SHA, not just the latest documentation SHA. Do not start a new run solely for documentation changes.
