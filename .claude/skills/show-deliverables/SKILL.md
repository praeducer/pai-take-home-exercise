---
name: show-deliverables
description: "Display all PAI exercise deliverables with verified links and exercise requirement coverage. Use before or during the interview to navigate the submission."
argument-hint: ""
allowed-tools: Bash, Read
---

Show all PAI take-home exercise deliverables.

## Steps

Run:
```bash
make deliverables
```

Then provide this navigation guide for the interview:

## Interview Navigation Map

| What to Demo | Command | Link |
|-------------|---------|------|
| Schema validation + dry-run | `make dry-run` | — |
| Live pipeline run (US brief) | `make run` | — |
| All 4 regional variants | `make run-demo` | — |
| S3 output structure | `/view-results alpine-harvest-trail-mix` | AWS Console S3 link in UAT |
| CI green status | — | https://github.com/praeducer/pai-take-home-exercise/actions/workflows/ci.yml |
| IaC deployment | `make deploy` | CF Console link in UAT |
| Test suite | `make test` | — |
| Solution Architecture | — | `docs/solution-architecture.md` |
| UAT Walkthrough (all links) | — | `docs/uat-walkthrough.md` |
| Pipeline status/history | `/pipeline-status` | — |

## PAI Exercise Requirements Coverage

| Exercise Requirement | How it's met |
|---------------------|-------------|
| Accept SKU brief JSON | `inputs/sample_sku_brief.json` — validated against JSON Schema |
| ≥2 products/flavors | `trail-mix-us.json`: Original + Dark Chocolate |
| 3 aspect ratios | front_label (1:1 / 1024×1024), back_label (9:16 / 576×1024), wraparound (16:9 / 1024×576) |
| Display text/attributes/regulatory | Pillow RGBA overlay: title strip, attribute badges, regulatory footer |
| S3 organized by SKU/Region/Format | `alpine-harvest-trail-mix/us-west/front_label/original.png` |
| IaC (CloudFormation/Terraform) | `infra/cloudformation/stack.yaml` — S3×2, IAM role, Budget alarm |
| README | https://github.com/praeducer/pai-take-home-exercise |
| Input assets from S3 | `asset_manager.check_s3_asset()` checks input bucket before generating |
| CI/CD (bonus) | GitHub Actions: ci.yml (lint+test+audit) + deploy.yml (CF deploy) |
| Brand compliance (bonus) | Claude Sonnet 4.6 `generate_brand_profile()` — once per brief, 6 visual dimensions |
| Approval logging (bonus) | JSON manifests: S3 `{sku_id}/{region}/manifest.json` + local `outputs/runs/` |
