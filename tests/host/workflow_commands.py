# SPDX-License-Identifier: GPL-3.0-only
"""Command text for workflow ordering assertions, including strict fixture guards.

Only remove the fallback suffix when it reruns exactly the same host test with
the same arguments. Other commands and their order remain visible to checks.
This does not execute a fallback or change whether any test passes.
"""


def workflow_commands(text):
    lines = []
    for line in text.splitlines(keepends=True):
        ending = "\n" if line.endswith("\n") else ""
        body = line.removesuffix("\n")
        before, separator, after = body.partition(
            " || python3 tools/ci-optional-fixture-check.py "
        )
        command = before.lstrip()
        # Single-line YAML run entries carry the same strict fallback.
        command = command.removeprefix("run: ")
        if (
            separator
            and command.startswith("python3 tests/host/")
            and after == command.removeprefix("python3 ")
        ):
            body = before
        lines.append(body + ending)
    return "".join(lines)
