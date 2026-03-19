# Submission Email

**To:** Rahul Krishna Radhakrishnan, Molly Holt
**From:** Paul Prae
**Re:** Interview Submission — Paul Prae (C6393269), R162394 Senior Platform & AI Engineer
**Date:** March 20, 2026

---

Rahul, Molly —

Submission complete for the PAI take-home exercise (R162394). Here's what's delivered:

- **GitHub repository (public, v1.1.0):** https://github.com/praeducer/pai-take-home-exercise
  — README with embedded demo images across 4 global markets, architecture overview, and quick-start guide
- **CI/CD badge (GitHub Actions, green):** https://github.com/praeducer/pai-take-home-exercise/actions
  — Automated lint (ruff), 42 unit tests (pytest), dependency audit (pip-audit) on every push
- **Solution architecture document:** `docs/solution-architecture.md` in the repository
  — Attached separately as `solution-architecture.docx`
- **Demo output:** 24 generated images — one product line (Alpine Harvest Organic Trail Mix) across 4 regional markets (US West, LATAM, APAC, EU), 3 packaging formats each
  — Demonstrates the regional variant automation scenario directly: same `sku_id`, 4 culturally distinct packaging directions, all generated from JSON briefs

The AWS CloudFormation stack (`pai-exercise`) is live in `us-east-1` with Amazon Nova Canvas as the primary image model (premium quality). All S3 outputs are organized by `alpine-harvest-trail-mix/{region}/{format}/{product}.png`.

The pipeline interface is entirely through 8 Claude Code custom skills — no traditional CLI. The brand profile generation uses Claude Opus 4.6 to establish visual direction once per brief, then Claude Sonnet 4.6 enhances format-specific prompts for each of the 6 images per run.

Happy to walk through the implementation live during the interview session.

Best,
Paul Prae
