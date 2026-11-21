#!/usr/bin/env python3
"""Publish the user's SideStore feed only from actual test IPA releases."""
import argparse
import json
import os
import plistlib
import re
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.request import urlopen, Request
from zipfile import ZipFile

REPO = "sky9662/bcd-games"
BRANCH = "sidestore-feed"
SOURCE_URL = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/source.json"
ICON_URL = f"https://raw.githubusercontent.com/{REPO}/main/app/Madeira/Assets.xcassets/AppIcon.appiconset/AppIcon-1024.png"
IDENTIFIER = "io.github.sky9662.bcd-games.touch-editor"

def request(url):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "BCD-Touch-Editor-Feed"}
    token = os.environ.get("GH_TOKEN")
    if token and url.startswith("https://api.github.com/"):
        headers["Authorization"] = f"Bearer {token}"
    return Request(url, headers=headers)

def previous():
    try:
        raw = subprocess.check_output(["git", "show", f"origin/{BRANCH}:source.json"], text=True)
        old = json.loads(raw)
        if old.get("identifier") == IDENTIFIER: return old
    except (OSError, ValueError, subprocess.CalledProcessError):
        pass
    return {}

def latest_release():
    url = f"https://api.github.com/repos/{REPO}/releases?per_page=40"
    with urlopen(request(url), timeout=30) as res: releases = json.load(res)
    for release in sorted(releases, key=lambda r: r.get("published_at") or "", reverse=True):
        if release.get("draft") or not release.get("tag_name", "").startswith("touch-editor-test-"):
            continue
        assets = [a for a in release.get("assets", []) if
                  re.fullmatch(r"Madeira-[A-Za-z0-9_.+-]+-unsigned\.ipa", a["name"])
                  or a["name"] == "BCD-touch-editor.ipa"]
        if assets: return release, assets[0]
    return None, None

def inspect(url):
    with TemporaryDirectory() as tmp:
        ipa = Path(tmp) / "BCD.ipa"
        with urlopen(request(url), timeout=180) as res, ipa.open("wb") as dst:
            while chunk := res.read(1048576): dst.write(chunk)
        with ZipFile(ipa) as zipped:
            names = [n for n in zipped.namelist()
                     if re.fullmatch(r"Payload/[^/]+\.app/Info\.plist", n)]
            if len(names) != 1: raise RuntimeError("Expected one app Info.plist")
            info = plistlib.loads(zipped.read(names[0]))
        for field in ("CFBundleIdentifier", "CFBundleShortVersionString", "CFBundleVersion"):
            if not isinstance(info.get(field), str) or not info[field]:
                raise RuntimeError(f"Missing IPA field {field}")
        return info, ipa.stat().st_size

def generate(previous_source):
    source = {"name": "BCD Touch Editor – Test Builds", "identifier": IDENTIFIER,
              "sourceURL": SOURCE_URL, "apps": previous_source.get("apps", []), "news": []}
    release, asset = latest_release()
    if asset is None: return source
    info, size = inspect(asset["browser_download_url"])
    if size != asset["size"]: raise RuntimeError("Release IPA size mismatch")
    version = {"version": info["CFBundleShortVersionString"],
               "buildVersion": info["CFBundleVersion"], "date": release["published_at"][:10],
               "localizedDescription": release.get("body") or "BCD touch-editor test",
               "downloadURL": asset["browser_download_url"], "size": size,
               "minOSVersion": info.get("MinimumOSVersion", "18.0")}
    old_versions = []
    if source["apps"] and source["apps"][0].get("bundleIdentifier") == info["CFBundleIdentifier"]:
        old_versions = [v for v in source["apps"][0].get("versions", [])
                        if v.get("downloadURL") != version["downloadURL"]]
    source["apps"] = [{
        "name": "BCD Touch Editor (Test)", "bundleIdentifier": info["CFBundleIdentifier"],
        "developerName": "thebcd69 / sky9662 test fork",
        "subtitle": "Multi-select and smart alignment test build",
        "localizedDescription": "Unofficial BCD touch-editor test build from sky9662/bcd-games.",
        "iconURL": ICON_URL, "category": "games", "beta": True,
        "versions": [version] + old_versions[:4],
    }]
    return source

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    source = generate(previous())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(source, indent=2, ensure_ascii=False) + "\n")
    print("Feed apps:", len(source["apps"]))

if __name__ == "__main__":
    main()
