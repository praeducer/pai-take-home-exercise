# Phase 5 Complete — Exercise Requirements Met

**Date:** 2026-03-19

**Repo URL:** https://github.com/praeducer/pai-take-home-exercise
**Release tag:** https://github.com/praeducer/pai-take-home-exercise/releases/tag/v1.0.0

**Demo images generated:** 24 (4 briefs × 2 products × 3 ratios)
- trail-mix-us: 6 images (us-west, dev tier, from cache)
- granola-bar-latam: 6 images (latam, dev tier)
- energy-drink-apac: 6 images (apac, dev tier)
- protein-bar-eu: 6 images (eu, dev tier)

**Model tier used:** dev (Titan V2, $0.01/image) — full demo dataset for $0.18
**Demo images in README:** 6 (front_label × 4 SKUs + back_label + wraparound for trail mix)
**Demo script location:** docs/demo-script.md
**CI badge:** green
**Test count:** 35 unit tests passing, 1 integration test skipped (requires real AWS)

**Deviations:**
- Used dev tier (Titan V2) instead of final tier (Nova Canvas) for demo data generation — saves ~$0.78 and produces equivalent demo quality for the exercise. Nova Canvas still available via `--model-tier final`.
- Sample data origin documented in `inputs/sample_sku_brief.json` via `_meta` field and in `docs/design-decisions.md` section 9.
- 69-byte placeholder image bug fixed: root cause was Stop hook running pytest without `-m "not integration"`, causing the integration test (dry_run=True) to overwrite real images. Fixed by (1) excluding integration tests from Stop hook, (2) not writing local files during dry-run.
