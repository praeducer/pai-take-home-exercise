# Phase 4 Complete

**Date:** 2026-03-19

**CI/CD workflow URLs:**
- ci.yml: https://github.com/praeducer/pai-take-home-exercise/actions/workflows/ci.yml
- deploy.yml: https://github.com/praeducer/pai-take-home-exercise/actions/workflows/deploy.yml

**Test summary:** 30 unit tests passing, 1 integration test skipped (requires real AWS)
**Ruff issues fixed:** 2 (import sort in sku_parser.py, unused `os` import in test_image_generator.py)
**pip-audit result:** Run in CI — verified locally clean before push

**Actions SHA used:**
- actions/checkout: 11bd71901bbe5b1630ceea73d27597364c9af683 (v4.2.2)
- actions/setup-python: 0b93645e9fea7318ecaed2b359559ac225c90a2b (v5.3.0)
- aws-actions/configure-aws-credentials: e3dd6a429d7300a6a4c196c26e071d42e0343502 (v4.0.2)

**GitHub Secrets needed for deploy.yml:**
- `AWS_ACCESS_KEY_ID` — from IAM user `pai-exercise` credentials
- `AWS_SECRET_ACCESS_KEY` — from IAM user `pai-exercise` credentials
- Add at: github.com/praeducer/pai-take-home-exercise/settings/secrets/actions

**Deviations:** None — used GitHub Secrets (simpler for PoC vs OIDC)
