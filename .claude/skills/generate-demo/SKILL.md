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
2. For each brief, run the pipeline:
```bash
for brief in inputs/demo_briefs/*.json; do
  echo "Processing: $brief"
  python src/pipeline/run_pipeline.py "$brief" --model-tier "${MODEL_TIER:-final}"
done
```
3. Download best images from S3 to `outputs/demo/`
4. Report total images generated

## Demo Briefs (created in Phase 5)

| File | Product | Region |
|------|---------|--------|
| `trail-mix-us.json` | Organic Trail Mix (Original + Dark Choc) | us-west |
| `granola-bar-latam.json` | Granola Bar (Original + Honey) | latam |
| `energy-drink-apac.json` | Energy Drink (Citrus + Berry) | apac |
| `protein-bar-eu.json` | Protein Bar (Vanilla + Chocolate) | eu |

## Expected Output

```
Demo generation complete.
4 SKU briefs × 2 products × 3 ratios = 24 images
S3: s3://{output_bucket}/
Local: outputs/demo/
```

Use `--model-tier dev` for a fast/cheap validation run. Use `--model-tier final` for the actual demo images.
