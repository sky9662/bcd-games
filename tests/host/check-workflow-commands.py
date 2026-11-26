#!/usr/bin/env python3
"""Keep strict workflow guards visible unless they retry the identical test."""
import unittest

from workflow_commands import workflow_commands


class WorkflowCommandsChecks(unittest.TestCase):
    def test_block_command_keeps_patch_order(self):
        before = "          python3 tests/host/check-a.py\n          python3 tools/patch-a.py wine\n"
        guarded = before.replace("check-a.py\n", "check-a.py || python3 tools/ci-optional-fixture-check.py tests/host/check-a.py\n")
        self.assertEqual(workflow_commands(guarded), before)

    def test_inline_command_keeps_required_arguments(self):
        before = "        run: python3 tests/host/check-a.py --require-swift\n"
        guarded = before.rstrip("\n") + " || python3 tools/ci-optional-fixture-check.py tests/host/check-a.py --require-swift\n"
        self.assertEqual(workflow_commands(guarded), before)

    def test_different_test_or_arguments_remain_visible(self):
        for fallback in ("tests/host/check-b.py --require-swift", "tests/host/check-a.py"):
            command = "        run: python3 tests/host/check-a.py --require-swift || python3 tools/ci-optional-fixture-check.py " + fallback + "\n"
            self.assertEqual(workflow_commands(command), command)

    def test_other_fallbacks_and_comments_remain_visible(self):
        for command in ("          python3 tests/host/check-a.py || true\n", "# python3 tests/host/check-a.py || python3 tools/ci-optional-fixture-check.py tests/host/check-a.py\n"):
            self.assertEqual(workflow_commands(command), command)


if __name__ == "__main__":
    unittest.main()
