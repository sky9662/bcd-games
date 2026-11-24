#!/usr/bin/env python3
"""Verify the branch's two unsigned IPA payloads before uploading them."""
import hashlib
import os
from pathlib import Path
import plistlib
import zipfile

expected_sha = os.environ["GITHUB_SHA"]
for name, bundle_id in (("Madeira", "com.thebcd69.bcd"), ("Madeira2", "com.thebcd69.bcd2")):
    paths = list(Path("build-out").glob(f"{name}-*-unsigned.ipa"))
    assert len(paths) == 1, f"Expected exactly one {name} IPA: {paths}"
    path = paths[0]
    with zipfile.ZipFile(path) as ipa:
        assert ipa.testzip() is None, f"Corrupt IPA: {path}"
        app = f"Payload/{name}.app/"
        info = plistlib.loads(ipa.read(app + "Info.plist"))
        assert info["CFBundleIdentifier"] == bundle_id, info
        assert info["CFBundleShortVersionString"] == "0.1.712", info
        assert info["MadeiraCommit"] == expected_sha, info
        binary = ipa.read(app + info["CFBundleExecutable"])
        for marker in (b"BCDTouchAcceleration", b"[profile] one Windows profile"):
            assert marker in binary, f"Missing feature marker {marker!r}: {path}"
        for dll in ("xtajit64.dll", "xtajit64-avx.dll"):
            assert b"[tc-exec-recheck]" in ipa.read(app + "arm64ec-windows/" + dll), f"Unpatched {dll}"
    with path.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    print(f"PASS: {path.name}: {bundle_id}, 0.1.712, {expected_sha}; touch, Turing and Cloud markers present; sha256={digest}")
