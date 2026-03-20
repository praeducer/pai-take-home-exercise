---
name: run-pipeline
description: "Run the PAI packaging image generation pipeline. Accepts an SKU brief JSON file path and produces images in 3 aspect ratios (1:1, 9:16, 16:9) uploaded to S3. Optionally accepts --model-tier (dev|iterate|final) and --dry-run flags."
argument-hint: "<sku-brief-path> [--model-tier dev|iterate|final] [--dry-run]"
allowed-tools: Read, Bash
---

## PAI Exercise Requirements Covered

| Requirement | Status |
|------------|--------|
| SKU brief JSON input (products, region, audience, attributes) | ✅ Validated against `src/schemas/sku_brief_schema.json` |
| ≥2 products/flavors per run | ✅ Processes all products in `brief.products[]` |
| 3 aspect ratios (1:1, 9:16, 16:9) | ✅ front_label, back_label, wraparound per product |
| Text/attributes/regulatory on packaging | ✅ Title strip, attribute badges, footer via Pillow |
| S3 organized by SKU/Region/Format | ✅ `{sku_id}/{region}/{format}/{product_slug}.png` |
| Input assets from S3 (if present) | ✅ `asset_manager.check_s3_asset()` checks input bucket first |
| Manifest/approval logging | ✅ JSON manifest → S3 + `outputs/runs/` |

Run the PAI pipeline for the given SKU brief JSON file.

## Arguments

- `$ARGUMENTS[0]` — path to SKU brief JSON (required). Example: `inputs/sample_sku_brief.json`
- `--model-tier dev|iterate|final` — image quality tier (default: dev)
  - `dev` → amazon.titan-image-generator-v2:0 ($0.01/image, fast)
  - `iterate` → amazon.nova-canvas-v1:0 (quality)
  - `final` → amazon.nova-canvas-v1:0 (quality, higher steps)
- `--dry-run` — skip all Bedrock API calls, validate inputs only, zero cost

## Steps

1. Parse arguments from `$ARGUMENTS`
2. Verify the SKU brief file exists and is valid JSON
3. Run: `PAI_OUTPUT_BUCKET=$(aws cloudformation describe-stacks --stack-name pai-exercise --profile pai-exercise --query 'Stacks[0].Outputs[?OutputKey==`OutputBucketName`].OutputValue' --output text) python -m src.pipeline.run_pipeline "$SKU_BRIEF_PATH" --model-tier "$MODEL_TIER" $DRY_RUN_FLAG`
4. Show output S3 paths and manifest location
5. If dry-run: show what would have been generated

## Expected Output

```
Pipeline run complete.
SKU: trail-mix-original
Products: 2 (Original, Dark Chocolate)
Images generated: 6 (2 products × 3 ratios)
S3 output: s3://pai-packaging-output-XXXX/trail-mix-original/us-west/
Manifest: outputs/runs/2026-03-19T12:00:00_trail-mix-original.json
```

## Error Handling

- Invalid JSON brief → show schema validation error with field name
- Bedrock ThrottlingException → pipeline retries automatically (3 attempts, exponential backoff)
- After 3 failures → falls back to next tier model
