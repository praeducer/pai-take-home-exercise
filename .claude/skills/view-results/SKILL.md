---
name: view-results
description: "List generated images in S3 for a given SKU and optionally download them locally. Read-only."
argument-hint: "<sku-id> [region] [--download]"
allowed-tools: Read, Bash
---

Show generated images for a SKU from S3.

## Arguments

- `$ARGUMENTS[0]` — SKU ID (required). Example: `trail-mix-original`
- `$ARGUMENTS[1]` — region filter (optional). Example: `us-west`
- `--download` — download images to `outputs/demo/{sku_id}/` for local viewing

## Steps

1. Get bucket name: `OUTPUT_BUCKET=$(aws cloudformation describe-stacks --stack-name pai-exercise --profile pai-exercise --query 'Stacks[0].Outputs[?OutputKey==`OutputBucketName`].OutputValue' --output text)`
2. Run: `aws s3 ls s3://$OUTPUT_BUCKET/$SKU_ID/ --recursive --profile pai-exercise`
3. Display image list organized by format (front_label, back_label, wraparound)
4. If `--download`: `aws s3 cp s3://$OUTPUT_BUCKET/$SKU_ID/ outputs/demo/$SKU_ID/ --recursive --profile pai-exercise` then open with `start outputs/demo/$SKU_ID/` (Windows)

## Output Format

```
Images for trail-mix-original (us-west):
  front_label/  trail-mix-original_front_1024x1024.png
  back_label/   trail-mix-original_back_576x1024.png
  wraparound/   trail-mix-original_wrap_1024x576.png
  [repeated for each product/flavor]

Manifest: s3://{output_bucket}/trail-mix-original/us-west/manifest.json
```
