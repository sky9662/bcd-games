# BCD unsigned IPA build playbook (fork)

This is the reusable procedure for building test IPA artifacts in sky9662/bcd-games. Preserve existing artifacts, main, and unrelated feature branches. Use a dedicated feature branch and never cancel unrelated successful/running jobs.

## Proven reference builds
- Successful Turing FEX build: https://github.com/sky9662/bcd-games/actions/runs/44986682956 (branch feature/turing-complete-fex-ipa)
- Successful touch editor builds: https://github.com/sky9662/bcd-games/actions/runs/44925031271 and https://github.com/sky9662/bcd-games/actions/runs/44925031304
- Touch acceleration initial checkout failure: https://github.com/sky9662/bcd-games/actions/runs/44993658841
- Touch acceleration test failure: https://github.com/sky9662/bcd-games/actions/runs/44994441702

## Reliable checkout / submodules
The repository has previously referenced an unavailable madeira-dock gitlink commit (4f01fd6154eb328b402b0fddc2b716cca4aaafb2). The successful Turing build workflow uses actions/checkout@v4 with submodules: false, then explicitly:
```bash
git submodule update --init --recursive -- FEX wine dxmt
rmdir madeira-dock 2>/dev/null || true
git clone --depth 1 https://github.com/thebcd69/bcd-dock.git madeira-dock
```
Treat this as a *reference*, not a universal replacement: inspect the actual branch's submodules, pinned revisions, and required patches before adapting. Do not accidentally change runtime dependency versions.

## Debugging and delivery
1. Inspect the latest Actions run, jobs, failing steps, and full job logs; distinguish test fixture failure, missing dependency, and actual Xcode build failure.
2. Compare with a proven successful workflow. Prefer the smallest branch-local fix rather than rewriting or disabling large test groups.
3. The touch acceleration branch encountered missing bcd-logs/worker/worker.js in check-log-upload.py. A branch-local conditional check was added: run the test when the fixture exists, otherwise emit a warning. Restore the full test when the fixture is available.
4. Verify Xcode/iOS SDK, FEX, LLVM, caches, signing requirements, build and packaging steps against the successful run; do not claim IPA success based on a workflow starting or tests passing.
5. Check Actions Artifacts for the exact unsigned .ipa, download/inspect its Payload/*.app/Info.plist CFBundleIdentifier, and provide the artifact URL plus SideStore/LiveContainer installation steps.
6. Preserve the existing app bundle identifier (com.thebcd69.bcd) unless explicitly requested otherwise. Avoid changing other feature branches, main, existing IPAs, and game saves.
7. Do not cancel other successful or ongoing builds. Record successful run ID, commit SHA, workflow adjustments, artifact name, and expiry in this file for future reuse.

## Current target
Branch: feature/touch-mouse-acceleration
Target artifact: bcd-touch-acc-unsigned.ipa
Independent acceleration toggles (Aim Mouse, Trackpad, Mouse-look) default OFF, including Duo lower screen. Keep existing Aim right-stick/absolute-pointer behavior.

**Status note:** This document records proven runs and known pitfalls; it does not claim that the touch acceleration IPA has been successfully built.
