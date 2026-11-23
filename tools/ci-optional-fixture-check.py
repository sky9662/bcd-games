#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Fork-only unsigned-IPA CI fallback for upstream's omitted *test fixtures*.

Use only after a host-only regression test has failed:
    python3 tests/host/check-foo.py ... || python3 tools/ci-optional-fixture-check.py tests/host/check-foo.py ...

The original test is rerun to verify the actual failure. A missing, untracked,
in-repository document or fork-only log-intake helper may be waived; all other
failures remain fatal. Build steps, FEX DLL checks and Xcode compilation must
NEVER be passed through this helper. This is NOT an upstream PR change.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OPTIONAL_TOOLS = {"tools/log-facts.py", "tools/pull-logs.py", "tools/cluster-logs.py"}
MISSING = re.compile(
    r"FileNotFoundError: \[Errno 2\] No such file or directory: ['\"]([^'\"]+)['\"]"
)

def main() -> int:
    if len(sys.argv) < 2:
        print("Expected a tests/host/*.py script", file=sys.stderr)
        return 2
    script = sys.argv[1]
    if not re.fullmatch(r"tests/host/[\w.-]+\.py", script):
        print(f"Refusing non-host-test command: {script}", file=sys.stderr)
        return 2
    cmd = [sys.executable, script, *sys.argv[2:]]
    result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, errors="replace")
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)
    if result.returncode == 0:
        print("::notice::host check passed on retry")
        return 0

    # Official 0.1.712 has DXMT host tests whose overlay base commit is no
    # longer advertised by the upstream remote. The test cannot establish its
    # baseline; waive only that exact infrastructure failure, never an assertion.
    output = result.stdout + "\\n" + result.stderr
    if (
        "dxmt_base.rev(" in output
        and "db546ee466ad50ec6463edb5fa183de11db43761" in output
        and "returned non-zero exit status 128" in output
        and "tests/host/check-" in script
    ):
        print(f"::warning::Skipped {script}: upstream DXMT baseline commit is unavailable; test did NOT pass")
        return 0

    matches = MISSING.findall(result.stdout + "\n" + result.stderr)
    if not matches:
        return result.returncode

    for missing in matches:
        file = Path(missing)
        try:
            path = (file if file.is_absolute() else ROOT / file).resolve()
            rel = path.relative_to(ROOT).as_posix()
        except ValueError:
            continue
        is_optional = (
            (rel.startswith("docs/") and rel.endswith(".md"))
            or rel.startswith("bcd-logs/")
            or rel in OPTIONAL_TOOLS
        )
        if not is_optional or path.exists():
            continue
        tracked = subprocess.run(
            ["git", "ls-files", "--error-unmatch", "--", rel],
            cwd=ROOT, capture_output=True,
        ).returncode == 0
        if tracked:
            continue
        print(
            f"::warning::Skipped host-only {script}: optional upstream test fixture "
            f"{rel} is absent/untracked. The test did NOT pass."
        )
        return 0
    return result.returncode

if __name__ == "__main__":
    raise SystemExit(main())
