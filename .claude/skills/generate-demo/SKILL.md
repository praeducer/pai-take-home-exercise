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

for brief in inputs/demo_briefs/*.json; do
  echo "Processing: $brief"
  PAI_OUTPUT_BUCKET="$OUTPUT_BUCKET" \
  python -m src.pipeline.run_pipeline "$brief" \
    --model-tier "${MODEL_TIER:-final}" \
    --profile pai-exercise
done
```
4. Copy best images to `outputs/demo/` for README embedding
5. Report total images generated

## Demo Briefs

| File | Product | Region | Attributes |
|------|---------|--------|-----------|
| `trail-mix-us.json` | Organic Trail Mix (Original, Dark Chocolate) | us-west | organic, non-gmo, high-protein, gluten-free |
| `granola-bar-latam.json` | Granola Energy Bar (Honey Oat, Tropical Fruit) | latam | whole-grain, natural-flavors, no-preservatives |
| `energy-drink-apac.json` | Natural Energy Drink (Original Citrus, Green Tea) | apac | natural-caffeine, vitamin-b, sugar-free |
| `protein-bar-eu.json` | Plant Protein Bar (Vanilla Almond, Cocoa Hazelnut) | eu | vegan, 20g-protein, gluten-free |

## Expected Output

```
4 briefs × 2 products × 3 ratios = 24 images
Model tier: final ($0.04/image × 24 = ~$0.96)
S3: s3://{output_bucket}/
Local: outputs/results/ (organized by sku/region/format)
```

Use `--model-tier dev` for fast/cheap validation ($0.24 total). Use `--model-tier final` for showcase-quality demo images ($0.96 total).
