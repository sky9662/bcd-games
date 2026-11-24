#!/usr/bin/env python3
"""Verify every pinned source manifest entry before allocating macOS.

Use --index locally after git add to check the exact Git blobs without Windows
checkout newline conversion. CI checks the actual checkout bytes by default.
"""
import argparse
import hashlib
import io
from pathlib import Path, PurePosixPath
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--index", action="store_true")
args = parser.parse_args()


def read_files(paths):
    if not args.index:
        result = {}
        for path in paths:
            try:
                result[path] = (ROOT / path).read_bytes()
            except FileNotFoundError:
                result[path] = None
        return result
    response = subprocess.run(["git", "-C", str(ROOT), "cat-file", "--batch"],
                              input="".join(":" + p + "\n" for p in paths).encode(),
                              capture_output=True, check=True)
    stream = io.BytesIO(response.stdout)
    result = {}
    for path in paths:
        header = stream.readline().rstrip(b"\n")
        if header.endswith(b" missing"):
            result[path] = None
            continue
        _, kind, length = header.rsplit(b" ", 2)
        assert kind == b"blob", (path, header)
        data = stream.read(int(length))
        assert len(data) == int(length) and stream.read(1) == b"\n"
        result[path] = data
    return result


tracked = subprocess.check_output(["git", "-C", str(ROOT), "ls-files", "-z"]).decode().split("\0")
manifests = sorted(p for p in tracked if p.endswith("/SHA256SUMS"))
assert manifests, "No tracked source manifests found"
expected = {}
for manifest, data in read_files(manifests).items():
    assert data is not None, f"Missing tracked manifest: {manifest}"
    for line in data.decode().splitlines():
        digest, name = line.split(None, 1)
        name = name.strip().removeprefix("*")
        relative = PurePosixPath(name)
        assert re.fullmatch(r"[0-9a-fA-F]{64}", digest), (manifest, digest)
        assert not relative.is_absolute() and ".." not in relative.parts and ":" not in name and "\n" not in name
        path = (PurePosixPath(manifest).parent / relative).as_posix()
        assert path not in expected, f"Duplicate manifest entry: {path}"
        expected[path] = digest.lower()
failures = []
for path, data in read_files(list(expected)).items():
    if data is None:
        failures.append(f"missing pinned source: {path}")
    elif hashlib.sha256(data).hexdigest() != expected[path]:
        failures.append(f"SHA-256 mismatch: {path}")
for failure in failures:
    print("FAIL: " + failure)
if failures:
    raise SystemExit(1)
print(f"PASS: {len(expected)} pinned files across {len(manifests)} source manifests ({'Git index' if args.index else 'checkout'} bytes)")
