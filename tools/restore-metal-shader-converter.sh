#!/bin/bash
# Preserve the hash-verified restoration used by successful run 45028450936.
# The iOS library is distributed under app/Madeira/d3d12/NOTICE.txt.
set -euo pipefail
URL="https://github.com/intraducine/iridium/releases/download/deps-metal-shader-converter-4.0-beta2/metal-shader-converter-4.0-beta2-apple.tar.gz"
ARCHIVE_SHA="f61c5bf4eadb993430642bb32c5642b1ddf2479a97b22ac307564967a4ff69d4"
IOS_SHA="073f903be98e973ff38f4d79f2c48d61ef938754a77b1caedda79c9f05a068c2"
DEST="app/Madeira/d3d12/libmetalirconverter.dylib"
if [[ -f "$DEST" ]] && echo "$IOS_SHA  $DEST" | shasum -a 256 -c -; then
  echo "Pinned iOS converter already present"
  exit 0
fi
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
curl --fail --location --retry 3 --retry-all-errors --silent --show-error "$URL" -o "$TMP/converter.tar.gz"
echo "$ARCHIVE_SHA  $TMP/converter.tar.gz" | shasum -a 256 -c -
mkdir -p "$TMP/unpack"
tar -xzf "$TMP/converter.tar.gz" -C "$TMP/unpack"
FOUND=""
while IFS= read -r -d '' CANDIDATE; do
  if echo "$IOS_SHA  $CANDIDATE" | shasum -a 256 -c --status; then
    FOUND="$CANDIDATE"
    break
  fi
done < <(find "$TMP/unpack" -type f -name 'libmetalirconverter.dylib' -print0)
if [[ -z "$FOUND" ]]; then
  echo "::error::No iOS Metal Shader Converter dylib matches upstream pinned SHA-256"
  exit 1
fi
cp "$FOUND" "$DEST"
echo "$IOS_SHA  $DEST" | shasum -a 256 -c -
echo "Restored pinned iOS Metal Shader Converter library"
