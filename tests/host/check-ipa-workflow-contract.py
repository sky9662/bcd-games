#!/usr/bin/env python3
"""Check publication modes and the actual unsigned workflow without macOS tools."""
from pathlib import Path

from ipa_workflow_contract import check_publication_workflow

signed = "run: bash tools/sign-and-publish-ota.sh\nbuild-out/Madeira2-0.1.${{ steps.bn.outputs.n }}-unsigned.ipa\n"
unsigned = """run: python3 tools/ota-variants.py package archive build-out 712
run: python3 tools/verify-unsigned-ipa.py
      - name: Upload unsigned BCD test IPAs
        uses: actions/upload-artifact@v4
        name: bcd-shared-unsigned-ipa
        path: |
          build-out/Madeira-*-unsigned.ipa
          build-out/Madeira2-*-unsigned.ipa
        if-no-files-found: error
"""
check_publication_workflow(signed)
check_publication_workflow(unsigned, unsigned=True)
for text, mode in ((unsigned, False), (signed, True), (unsigned + signed, True),
                   (unsigned.replace("build-out/Madeira2-*-unsigned.ipa", "missing.ipa"), True),
                   (unsigned.replace("if-no-files-found: error", "if-no-files-found: ignore"), True),
                   (unsigned + "R2_SECRET_ACCESS_KEY", True)):
    try:
        check_publication_workflow(text, unsigned=mode)
    except (AssertionError, ValueError):
        continue
    raise AssertionError("An invalid publication contract was accepted")
check_publication_workflow((Path(__file__).resolve().parents[2] / ".github/workflows/build-ipa.yml").read_text(), unsigned=True)
print("PASS: OTA and unsigned contracts; wrong modes, missing secondary IPA, ignored upload and signing credentials refused; current workflow valid")
