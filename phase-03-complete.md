# Phase 3 Complete

**Date:** 2026-03-19

**Aspect ratio dimensions used:**
- 1:1: 1024×1024 ✓ (front_label)
- 9:16: 576×1024 ✓ (back_label) — note: Titan V2 generates at 1024×1024 (square only); Nova Canvas generates natively at 576×1024
- 16:9: 1024×576 ✓ (wraparound) — same note as 9:16 for Titan V2

**Note on Titan V2 non-square ratios:** Titan V2 (`amazon.titan-image-generator-v2:0`) only supports square dimensions. `image_generator.py` detects this and uses 1024×1024 for Titan when a non-square ratio is requested. Nova Canvas supports all 3 native dimensions. For production quality non-square images use `--model-tier iterate` or `--model-tier final`.

**Pillow layout decisions:**
- 1:1 (1024×1024): title at y=52px, attrs at y=717px, reg at y=922px
- 9:16 (576×1024): title at y=51px, attrs at y=666px, reg at y=922px
- 16:9 (1024×576): title at y=29px, attrs at y=346px, reg at y=507px

**S3 key pattern confirmed:** `{sku_id}/{region}/{format_name}/{product_slug}.png`
**Cache location:** `~/.cache/pai-pipeline/`
**Cache performance:** First run ~11.7s (Titan V2 API call); second run 0.006s (cache hit, ~1950x speedup)
**Full run duration:** ~73.9s for 6 images (dev tier, no cache)
**Manifest format:** 9-field JSON (run_id, timestamp, sku_id, region, models_used, images_generated, dry_run, errors, duration_seconds)

**Note:** Phase 3 tasks were implemented as part of Phase 2 — `run_pipeline.py` was written with `RATIO_FORMAT_MAP` and all 3 ratios from the start. Caching was also included in `image_generator.py` from Phase 2.

**Deviations:**
- All 3 ratios implemented during Phase 2 (combined phases)
- Titan V2 uses 1024×1024 for all ratios (square-only model); Nova Canvas uses native dimensions
