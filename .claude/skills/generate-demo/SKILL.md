---
name: generate-demo
description: "Run the pipeline for all demo SKU briefs in inputs/demo_briefs/ using the final model tier. Produces the full demo dataset for README embeds and interview showcase."
argument-hint: "[--model-tier dev|final]"
disable-model-invocation: true
allowed-tools: Bash, Read
---

Generate the full demo dataset for the project showcase.

## Steps

1. Check that `inputs/demo_briefs/` exists and contains JSON files
2. Get the output bucket name:
```bash
aws cloudformation describe-stacks \
  --stack-name pai-exercise \
  --profile pai-exercise \
  --query 'Stacks[0].Outputs[?OutputKey==`OutputBucketName`].OutputValue' \
  --output text
```
3. For each brief, run the pipeline:
```bash
OUTPUT_BUCKET=$(aws cloudformation describe-stacks \
  --stack-name pai-exercise --profile pai-exercise \
  --query 'Stacks[0].Outputs[?OutputKey==`OutputBucketName`].OutputValue' \
  --output text)

for brief in inputs/demo_briefs/trail-mix-us.json inputs/demo_briefs/trail-mix-latam.json inputs/demo_briefs/trail-mix-apac.json inputs/demo_briefs/trail-mix-eu.json; do
  echo "Processing: $brief"
  PAI_OUTPUT_BUCKET="$OUTPUT_BUCKET" \
  uv run python -m src.pipeline.run_pipeline "$brief" \
    --model-tier "${MODEL_TIER:-final}" \
    --profile pai-exercise
done
```
4. Copy best images to `outputs/demo/` for README embedding
5. Report total images generated

## Demo Briefs

| File | Product | Region | Cultural direction |
|------|---------|--------|--------------------|
| `trail-mix-us.json` | Alpine Harvest Trail Mix (Original, Dark Chocolate) | us-west | Pacific NW earth tones, outdoor lifestyle |
| `trail-mix-latam.json` | Alpine Harvest Trail Mix (Original, Tropical Edition) | latam | Golden yellows, terracotta, tropical energy |
| `trail-mix-apac.json` | Alpine Harvest Trail Mix (Original, Mango Coconut) | apac | Vibrant tropical, warm oranges, natural ingredients |
| `trail-mix-eu.json` | Alpine Harvest Trail Mix (Original, Dark Berry) | eu | Scandinavian kraft, moss green, Nordic botanical |

## Expected Output

```
4 briefs × 2 products × 3 ratios = 24 images
Model tier: final ($0.04/image × 24 = ~$0.96)
S3: s3://{output_bucket}/
Local: outputs/results/ (organized by sku/region/format)
```

Use `--model-tier dev` for fast/cheap validation ($0.24 total). Use `--model-tier final` for showcase-quality demo images ($0.96 total).
