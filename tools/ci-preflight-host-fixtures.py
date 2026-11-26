#!/usr/bin/env python3
"""Audit literal host-test file dependencies before expensive IPA builds.

A static audit: does not execute regressions, create missing files, or waive
build/DLL checks. Dynamic or conditional reads require human review.
"""
import argparse
import ast
import re
import runpy
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = re.compile(r'tests/host/[A-Za-z0-9_.-]+\.py')


def source_path(node, known):
    if isinstance(node, ast.Name):
        return known.get(node.id)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        base = source_path(node.left, known)
        if base is not None and isinstance(node.right, ast.Constant) and isinstance(node.right.value, str):
            return base / node.right.value
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
        if node.func.attr in ('resolve', 'absolute') and not node.args:
            return source_path(node.func.value, known)
        if node.func.attr == 'joinpath':
            base = source_path(node.func.value, known)
            if base is not None and all(isinstance(x, ast.Constant) and isinstance(x.value, str) for x in node.args):
                return base.joinpath(*(x.value for x in node.args))
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'Path':
        if len(node.args) == 1 and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
            path = Path(node.args[0].value)
            return path if path.is_absolute() else REPO / path
    if isinstance(node, ast.Attribute) and node.attr == 'parent':
        base = source_path(node.value, known)
        return base.parent if base is not None else None
    return None


def read_calls(node, known):
    for item in ast.walk(node):
        if not isinstance(item, ast.Call) or not isinstance(item.func, ast.Attribute):
            continue
        if item.func.attr not in ('read_text', 'read_bytes', 'is_file', 'exists'):
            continue
        target = source_path(item.func.value, known)
        if target is not None:
            yield item.lineno, target, item.func.attr


def scan(root):
    workflow = root / '.github/workflows/build-ipa.yml'
    if not workflow.is_file():
        raise SystemExit(f'ERROR: workflow absent: {workflow}')
    text = workflow.read_text(encoding='utf-8')
    scripts = sorted(set(SCRIPT.findall(text)))
    results = []
    # Share the exact safe exceptions with the fallback used by individual
    # host checks. Never approve a missing tracked file.
    guard = runpy.run_path(str(root / "tools/ci-optional-fixture-check.py"),
                           run_name="ci_preflight_guard")
    approved = guard["OPTIONAL_TOOLS"] | guard["OPTIONAL_MISSING_DOCS"]
    for name in scripts:
        source = root / name
        if not source.is_file():
            results.append(('FATAL', name, 0, 'script itself is missing'))
            continue
        try:
            tree = ast.parse(source.read_text(encoding='utf-8'), filename=name)
        except SyntaxError as exc:
            results.append(('FATAL', name, exc.lineno or 0, f'Python syntax: {exc.msg}'))
            continue
        known = {key: root for key in ('R', 'ROOT', 'root', 'REPO')}
        # Discover aliases such as series = R / "build/mesa-ios/playport-patches".
        for stmt in tree.body:
            if isinstance(stmt, (ast.Assign, ast.AnnAssign)):
                targets = stmt.targets if isinstance(stmt, ast.Assign) else [stmt.target]
                for target in targets:
                    if isinstance(target, ast.Name):
                        expr = stmt.value
                        pathval = source_path(expr, known) if expr else None
                        if pathval is not None:
                            known[target.id] = pathval
                        elif expr is not None and target.id in known and 'Path(__file__)' not in ast.unparse(expr):
                            known.pop(target.id, None)
        seen = set()
        for stmt in tree.body:
            direct = not isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.If,
                                           ast.For, ast.While, ast.Try, ast.With, ast.ClassDef))
            for line, target, operation in read_calls(stmt, known):
                target = target.resolve(strict=False)
                if not target.is_relative_to(root) or target.is_file():
                    continue
                key = (name, line, str(target))
                if key not in seen:
                    seen.add(key)
                    relative = target.relative_to(root).as_posix()
                    # Generated outputs and submodule contents may be absent
                    # before macOS build steps; report them without a false fail.
                    checked_in = (
                        relative.startswith(('docs/', 'tests/', 'tools/', '.github/'))
                        or (relative.startswith('app/Madeira/')
                            and not relative.startswith('app/Madeira/gl/'))
                        or relative.startswith('build/mesa-ios/playport-patches/')
                    )
                    optional = (
                        (relative.startswith('docs/') and relative.endswith('.md'))
                        or relative.startswith('bcd-logs/')
                        or relative in approved
                    )
                    if optional:
                        # A tracked fixture that vanished from checkout is NOT
                        # optional. This protects against accidentally masking
                        # missing source files or a broken sparse checkout.
                        tracked = subprocess.run(
                            ['git', 'ls-files', '--error-unmatch', '--', relative],
                            cwd=root, capture_output=True).returncode == 0
                        optional = not tracked
                    # A presence test can intentionally assert absence. Report
                    # it for review, never invent a fatal read or waive a check.
                    severity = ('OPTIONAL' if optional else 'REVIEW' if operation in ('is_file', 'exists') else
                                'FATAL' if direct and checked_in else 'REVIEW')
                    results.append((severity, name, line, f'missing literal {operation}: {relative}'))
    return len(scripts), results


def main():
    cli = argparse.ArgumentParser()
    cli.add_argument('--strict', action='store_true', help='fail for definitely missing inputs')
    cli.add_argument('--root', type=Path, default=REPO, help='repository checkout to audit')
    args = cli.parse_args()
    count, issues = scan(args.root.resolve())
    print(f'preflight: inspected {count} host Python scripts referenced by build workflow')
    for severity, source, line, detail in issues[:120]:
        print(f'{severity}: {source}:{line}: {detail}')
    if len(issues) > 120:
        print(f'... {len(issues) - 120} further findings')
    fatals = [issue for issue in issues if issue[0] == 'FATAL']
    optionals = [issue for issue in issues if issue[0] == 'OPTIONAL']
    print(f'preflight: {len(fatals)} definite missing/script issues; '
          f'{len(optionals)} absent optional upstream fixtures; '
          f'{len(issues)-len(fatals)-len(optionals)} conditional or generated reads to review')
    return 1 if fatals and args.strict else 0


if __name__ == '__main__':
    raise SystemExit(main())
