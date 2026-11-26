#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Require the complete built DLL sets and their exact opt-in shadowing contract."""
import argparse
from pathlib import Path
import tempfile
import re


def validate(ec, aa):
    ec, aa = Path(ec), Path(aa)
    if not any(p.is_file() for p in ec.glob('*.dll')) or not any(p.is_file() for p in aa.glob('*.dll')):
        return False, 'missing built ARM64EC or ARM64 DLL set'
    shadowed = sorted(f.name[:-10] for f in ec.glob('*-optin.dll')
                      if f.is_file() and (ec / (f.name[:-10] + '.dll')).is_file()
                      and not (aa / (f.name[:-10] + '.dll')).is_file())
    return shadowed == ['dcomp'], 'of the shipped opt-in DLLs only dcomp is shadowed that way (%s)' % shadowed


def self_test():
    with tempfile.TemporaryDirectory() as tmp:
        ec, aa = Path(tmp) / 'ec', Path(tmp) / 'aa'
        ec.mkdir(); aa.mkdir()
        assert not validate(ec, aa)[0], 'empty sets must fail'
        for p in (ec / 'dcomp.dll', aa / 'ntdll.dll', ec / 'dxcompiler-optin.dll'):
            p.touch()
        assert not validate(ec, aa)[0], 'DXC-only partial build must fail final validation'
        (ec / 'dcomp-optin.dll').touch()
        assert validate(ec, aa)[0], 'complete expected shadowing must pass'
        (aa / 'dcomp.dll').touch()
        assert not validate(ec, aa)[0], 'unexpected ARM64 dcomp must fail'
        (aa / 'dcomp.dll').unlink()
        (ec / 'extra.dll').touch(); (ec / 'extra-optin.dll').touch()
        assert not validate(ec, aa)[0], 'unexpected additional shadow must fail'
        (ec / 'extra-optin.dll').unlink()
        (ec / 'dcomp-optin.dll').unlink(); (ec / 'dcomp-optin.dll').mkdir()
        assert not validate(ec, aa)[0], 'directory masquerading as DLL must fail'
    print('PASS: six strict opt-in shadowing controls (including DXC-only partial build)')


def workflow_contract(text):
    names = (
        'Check opt-in DLLs',
        'Build extra Wine DLLs for arm64ec',
        'Build ICU and ship it as icuuc-optin.dll and icuin-optin.dll',
        'Verify the opt-in DLLs the lists and rules name',
        'Verify complete opt-in DLL shadowing',
    )
    blocks = []
    for name in names:
        marker = '      - name: ' + name + '\n'
        if text.count(marker) != 1:
            return False
        start = text.index(marker)
        end = text.find('\n      - name: ', start + len(marker))
        blocks.append((start, text[start:] if end == -1 else text[start:end]))
    if any(a[0] >= b[0] for a, b in zip(blocks, blocks[1:])):
        return False
    commands = (
        'python3 tests/host/check-optin-dlls.py --source-only || python3 tools/ci-optional-fixture-check.py tests/host/check-optin-dlls.py --source-only',
        'python3 tools/check-optin-dlls-shipped.py app/Madeira/arm64ec-windows',
        'python3 tools/check-optin-shadowing.py app/Madeira/arm64ec-windows app/Madeira/aarch64-windows',
    )
    for index, command in zip((0, 3, 4), commands):
        if '        run: ' + command not in blocks[index][1].splitlines():
            return False
    return all(not re.search(r'^        (?:if|continue-on-error):', blocks[i][1], re.M) for i in (3, 4))


def workflow_self_test():
    text = (Path(__file__).resolve().parents[1] / '.github/workflows/build-ipa.yml').read_text()
    assert workflow_contract(text), 'staged opt-in workflow contract'
    marker = '      - name: Verify complete opt-in DLL shadowing\n'
    command = '        run: python3 tools/check-optin-dlls-shipped.py app/Madeira/arm64ec-windows'
    mutations = (
        text.replace(command, command.replace('run: ', 'run: |\n          '), 1),
        text.replace(marker, marker + '        continue-on-error: true\n', 1),
        text.replace(marker, '      - name: Removed shadowing verification\n', 1),
        text.replace(marker, marker + '        if: false\n', 1),
        text.replace('check-optin-dlls.py --source-only ||', 'check-optin-dlls.py ||', 1),
    )
    assert all(not workflow_contract(bad) for bad in mutations), 'workflow negative controls'
    print('PASS: staged opt-in workflow and five negative controls')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('ec', nargs='?', type=Path)
    parser.add_argument('aa', nargs='?', type=Path)
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    if args.self_test:
        self_test()
        workflow_self_test()
        return 0
    if args.ec is None or args.aa is None:
        parser.error('both built DLL directories are required')
    ok, detail = validate(args.ec, args.aa)
    print(('PASS: ' if ok else 'FAIL: ') + detail)
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
