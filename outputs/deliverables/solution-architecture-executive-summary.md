# PAI Packaging Automation PoC — Executive Summary

**Engagement:** Adobe PAI Interview — R162394 Senior Platform & AI Engineer
**Author:** Paul Prae
**Date:** March 20, 2026
**Repository:** https://github.com/praeducer/pai-take-home-exercise

---

## What Was Built

A fully functional AI-native packaging automation pipeline that accepts a structured SKU brief (JSON) and produces multi-format, regionally adapted packaging images — 24 high-quality variants across 4 global markets for $2.21. The pipeline chains three AI model calls per image (brand profiling → prompt enhancement → image generation) plus Pillow text overlay compositing, delivering organized outputs to S3 with full run manifests. Infrastructure is provisioned via a CloudFormation stack (`pai-exercise`), the user interface is 8 Claude Code custom skills, and the entire system is orchestrated from a single JSON brief.

The pipeline was designed and built by Claude (Sonnet 4.6 / Opus 4.6) under human architectural direction — every Python module, test, CloudFormation resource, and CI workflow. This mirrors the AI-native development philosophy the pipeline itself embodies: the same toolchain that runs the pipeline built it.

---

## System Architecture

```
SKU Brief (JSON)
    └─► Claude Code skill /run-pipeline
            └─► Claude Sonnet 4.6 (tool_use) — brand profile  [once per brief]
            └─► Claude Sonnet 4.6 — prompt enhancement         [per image]
            └─► Amazon Nova Canvas v1:0 — image generation     [per image]
            └─► Pillow — text overlay compositing              [per image]
            └─► S3 — {sku_id}/{region}/{format}/{product}.png
            └─► JSON manifest — outputs/runs/ + S3
```

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Image generation | Amazon Nova Canvas v1:0 | Premium packaging imagery ($0.08/image) |
| Dev/test generation | Amazon Titan Image V2:0 | CI-safe fast iteration ($0.01/image) |
| Brand profiling | Claude Sonnet 4.6 (tool_use) | Structured visual direction — once per brief |
| Prompt enhancement | Claude Sonnet 4.6 | Bedrock-optimized prompt from brand profile |
| Text overlay | Pillow (PIL) | Title strip, attribute badges, regulatory footer |
| Storage | Amazon S3 | Organized by SKU / region / format |
| Infrastructure | CloudFormation | S3×2, IAM least-privilege, Budget alarm |
| Interface | Claude Code custom skills | 8 skills — zero CLI boilerplate |

---

## AI Highlights

### Development Process

Claude (Sonnet 4.6 / Opus 4.6) designed and built the pipeline under human architectural direction — every Python module, test, CloudFormation resource, and CI workflow. This mirrors the AI-native development philosophy the pipeline itself demonstrates: the same toolchain that runs the pipeline built it.

### Pipeline Intelligence

- **Brand profiling via tool_use:** Claude Sonnet 4.6 with `tool_choice: {type: "tool"}` generates a structured brand profile (photography style, color palette, cultural elements, negative guidance) once per brief — guaranteed JSON schema, no brittle parsing. All 6 images in a run share this visual direction, ensuring brand coherence.
- **Prompt enhancement:** A second Claude call transforms the brand profile + SKU brief into a Bedrock-optimized image prompt per variant.
- **Nova Canvas premium settings:** cfgScale 8.5 with reinforced negative prompts to minimize AI text hallucination on packaging surfaces — a critical quality concern for real packaging assets.
- **SHA-256 content cache:** Identical prompts return cached images in under 1 second for deterministic demo re-runs.

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Claude Code skills as interface | Zero argparse boilerplate; matches Adobe's AI-native toolchain |
| tool_use for brand profiling | Guaranteed JSON schema; no regex parsing of model output |
| Model tiers (dev / iterate / final) | CI builds never call Bedrock — $0 CI cost; Nova Canvas reserved for quality runs |
| IAM least-privilege + Deny on s3:Delete* | Defense-in-depth; accidental deletions blocked at policy level |
| DeletionPolicy: Retain on Budget/S3 | AWS Budgets doesn't support CF updates — Retain prevents UPDATE_ROLLBACK_COMPLETE |
| SHA-256 content cache | Reproducible demos; avoids re-billing for identical generation requests |

---

## Results

| Metric | Value |
|--------|-------|
| Demo images generated | 24 (4 regions × 2 products × 3 formats) |
| Total PoC cost | ~$2.21 |
| Tests passing | 42 unit tests, 3 integration skipped in CI |
| CI/CD | Green — https://github.com/praeducer/pai-take-home-exercise/actions/runs/23351029169 |
| Tag | v1.2.1 |
| CloudFormation stack | `pai-exercise` — UPDATE_COMPLETE, us-east-1 |

**Production scale projection:** At 1,000 variants/month using Nova Canvas, estimated cost is ~$95/month vs. $5,000–50,000/month for traditional agency creative — 98%+ cost reduction per variant.

---

## Bonus Items Implemented

The following optional ("nice to have") items from the exercise specification were implemented:

- **Approval status tracking:** JSON manifest per run captures model IDs, generation duration, per-image cost, and errors — written to `outputs/runs/` and S3.
- **Brand consistency mechanism:** Claude Sonnet 4.6 brand profile (tool_use) shared across all images in a run ensures visual coherence — a lightweight alternative to post-generation compliance checking.
- **CI/CD:** GitHub Actions pipeline — ruff lint, pytest, pip-audit security scan, and CloudFormation deploy on every push.
- **Multi-tier model selection:** `--model-tier dev|iterate|final` parameter allows cost-controlled iteration without changing code.
