#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Require the complete built DLL sets and their exact opt-in shadowing contract."""
import argparse
from pathlib import Path
import tempfile


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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('ec', nargs='?', type=Path)
    parser.add_argument('aa', nargs='?', type=Path)
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.ec is None or args.aa is None:
        parser.error('both built DLL directories are required')
    ok, detail = validate(args.ec, args.aa)
    print(('PASS: ' if ok else 'FAIL: ') + detail)
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
