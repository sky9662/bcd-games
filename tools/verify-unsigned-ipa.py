#!/usr/bin/env python3
"""Verify both unsigned payloads; feature builds must add feature-specific checks."""
import hashlib
import os
from pathlib import Path
import plistlib
import zipfile
expected_sha = os.environ["GITHUB_SHA"]
number = "".join(line.strip() for line in Path("docs/local-build/BUILD-NUMBER").read_text().splitlines() if not line.startswith("#"))
assert number.isdigit(), "Invalid build number"
expected_version = "0.1." + number
baseline = os.environ.get("GITHUB_REF_NAME") == "build/ipa-infrastructure"
for name, bundle_id in (("Madeira", "com.thebcd69.bcd"), ("Madeira2", "com.thebcd69.bcd2")):
    paths = list(Path("build-out").glob(f"{name}-*-unsigned.ipa"))
    assert len(paths) == 1, f"Expected exactly one {name} IPA: {paths}"
    path = paths[0]
    with zipfile.ZipFile(path) as ipa:
        assert ipa.testzip() is None, f"Corrupt IPA: {path}"
        app = f"Payload/{name}.app/"
        info = plistlib.loads(ipa.read(app + "Info.plist"))
        assert info["CFBundleIdentifier"] == bundle_id, info
        assert info["CFBundleShortVersionString"] == expected_version, info
        assert info["MadeiraCommit"] == expected_sha, info
        binary = ipa.read(app + info["CFBundleExecutable"])
        assert binary, "Empty app executable"
        for dll in ("xtajit64.dll", "xtajit64-avx.dll"):
            module = ipa.read(app + "arm64ec-windows/" + dll)
            assert module.startswith(b"MZ"), f"Invalid PE module: {dll}"
            if baseline:
                assert b"[tc-exec-recheck]" not in module, f"Custom Turing patch leaked into {dll}"
        if baseline:
            for marker in (b"BCDTouchAcceleration", b"[profile] one Windows profile"):
                assert marker not in binary, f"Custom feature leaked: {marker!r}"
    with path.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    print(f"PASS: {path.name}: {bundle_id}, {expected_version}, {expected_sha}; sha256={digest}")
