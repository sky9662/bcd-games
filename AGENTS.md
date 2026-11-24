# IPA and CI work

Before building an IPA, changing CI or porting this work to another version, read [the persistent build lessons](docs/local-build/CI-LESSONS.md) and the current branch's handoff. The user explicitly requested that past build failures and successful build methods be retained across versions.

Keep independent feature/CI fixes when upgrading; do not replace a new release tree with an old successful tree. Check active runs before any dispatch or workflow push. Preserve test assertions, distinguish explicit fixture skips from passes, and verify the actual IPA and its source SHA before reporting success.
