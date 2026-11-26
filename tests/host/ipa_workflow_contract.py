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
    assert "build-out/BCD-0.1.721-TCFix-ACC-Cloud.ipa" in upload
    assert "build-out/BCD2-0.1.721-TCFix-ACC-Cloud.ipa" in upload
    verify = workflow.index("run: python3 tools/verify-upstream-cloud-ipa.py")
    rename = workflow.index("      - name: Rename verified unsigned IPAs to feature-labelled filenames")
    publish = workflow.index("      - name: Upload unsigned BCD 0.1.721 test IPAs")
    assert verify < rename < publish
    stage = workflow[rename:publish]
    assert "mv build-out/Madeira-0.1.721-unsigned.ipa build-out/BCD-0.1.721-TCFix-ACC-Cloud.ipa" in stage
    assert "mv build-out/Madeira2-0.1.721-unsigned.ipa build-out/BCD2-0.1.721-TCFix-ACC-Cloud.ipa" in stage
    assert "if-no-files-found: error" in upload
