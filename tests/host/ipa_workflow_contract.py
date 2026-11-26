"""Publication-mode assertions shared by cheap preflight and packaging tests."""


def check_publication_workflow(workflow, *, unsigned=False):
    signing = "run: bash tools/sign-and-publish-ota.sh"
    if not unsigned:
        assert workflow.count(signing) == 1, "OTA mode needs exactly one paired signing invocation"
        assert "build-out/Madeira2-0.1.${{ steps.bn.outputs.n }}-unsigned.ipa" in workflow
        return

    assert "sign-and-publish-ota.sh" not in workflow, "Unsigned test builds must not publish OTA"
    for secret in ("R2_ACCOUNT_ID", "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY", "SIGN_P12_PASSWORD", "OTA_MAIL_APP_PASSWORD"):
        assert secret not in workflow, f"Unsigned workflow must not request {secret}"
    assert workflow.count("run: python3 tools/ota-variants.py package ") == 1
    assert workflow.count("run: python3 tools/verify-upstream-cloud-ipa.py") == 1
    upload = workflow[workflow.index("      - name: Upload unsigned BCD 0.1.721 test IPAs"):]
    assert "uses: actions/upload-artifact@v4" in upload
    assert "name: bcd-0721-turing-touch-cloud-unsigned-ipa" in upload
    assert "build-out/Madeira-*-unsigned.ipa" in upload
    assert "build-out/Madeira2-*-unsigned.ipa" in upload
    assert "if-no-files-found: error" in upload
