# Submission Email

**To:** [INTERVIEWER_NAME_1], [INTERVIEWER_NAME_2]
**From:** Paul Prae
**Re:** Interview Submission — Paul Prae, R162394 Senior Platform & AI Engineer
**Date:** March 20, 2026

---

[INTERVIEWER_NAME_1], [INTERVIEWER_NAME_2] —

Submission complete for the PAI take-home exercise (R162394). Here's what's delivered:

- **GitHub repository (public):** https://github.com/praeducer/pai-take-home-exercise
  — README with embedded demo images across 4 global markets, architecture overview, and quick-start guide
- **CI/CD badge (GitHub Actions, green):** https://github.com/praeducer/pai-take-home-exercise/actions
  — Automated lint (ruff), 43 unit tests (pytest), dependency audit (pip-audit) on every push
- **Solution architecture document:** `docs/solution-architecture.md` in the repository
  — Attached separately as `solution-architecture.docx`
- **Demo output:** 24 generated images — one product line (Alpine Harvest Organic Trail Mix) across 4 regional markets (US West, LATAM, APAC, EU), 3 packaging formats each
  — Demonstrates the regional variant automation scenario directly: same `sku_id`, 4 culturally distinct packaging directions, all generated from JSON briefs

The AWS CloudFormation stack (`pai-exercise`) is live in `us-east-1` with Amazon Nova Canvas as the primary image model (premium quality). All S3 outputs are organized by `alpine-harvest-trail-mix/{region}/{format}/{product}.png`.

The pipeline interface is entirely through 8 Claude Code custom skills — no traditional CLI. Brand profile generation uses Claude Sonnet 4.6 with structured tool use to establish visual direction once per brief, then prompt enhancement refines format-specific prompts for each of the 6 images per run.

Happy to walk through the implementation live during the interview session.

Best,
Paul Prae
