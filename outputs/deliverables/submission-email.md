# Submission Email

**To:** [INTERVIEWER_NAME_1], [INTERVIEWER_NAME_2]
**From:** Paul Prae
**Re:** Interview Submission — Paul Prae ([CANDIDATE_ID]), R162394 Senior Platform & AI Engineer
**Date:** [SUBMISSION_DATE]

---

[INTERVIEWER_NAME_1], [INTERVIEWER_NAME_2] —

This exercise sits squarely at the intersection of work I've been doing at Modular Earth — building AI-native engineering tools for SAs and engineers — so I genuinely enjoyed going deep on it. Thank you for the opportunity.

Submission complete for the PAI take-home exercise (R162394). Here's what's delivered:

- **GitHub repository (public, v1.2.1):** https://github.com/praeducer/pai-take-home-exercise
  — README with embedded demo images across 4 global markets, architecture overview, and quick-start guide
- **CI/CD (GitHub Actions, green):** https://github.com/praeducer/pai-take-home-exercise/actions/runs/23351029169
  — Automated lint (ruff), 42 tests passing, 3 skipped in CI, dependency audit (pip-audit) on every push
- **Solution architecture document:** [`docs/solution-architecture.md`](https://github.com/praeducer/pai-take-home-exercise/blob/main/docs/solution-architecture.md)
  — Executive summary also attached as `solution-architecture-executive-summary.pdf` (source: [`outputs/deliverables/solution-architecture-executive-summary.md`](https://github.com/praeducer/pai-take-home-exercise/blob/main/outputs/deliverables/solution-architecture-executive-summary.md))
- **Demo output:** 24 generated images — Alpine Harvest Organic Trail Mix across 4 regional markets (US West, LATAM, APAC, EU), 2 products × 3 packaging formats each
  — Same `sku_id`, 4 culturally distinct packaging directions, all generated from JSON briefs in `inputs/demo_briefs/`

**Technical highlights:**

- **Multi-step AI pipeline:** 3 AI calls per image (brand profiling → prompt enhancement → image generation) plus text overlay compositing — not a single-prompt approach
- **Brand profile via tool use:** Claude Sonnet 4.6 with `tool_choice` generates structured visual direction (photography style, color palette, cultural elements) once per brief — guaranteed JSON schema, no brittle parsing
- **Nova Canvas premium:** cfgScale 8.5 with strengthened negative prompts to minimize AI text hallucination on packaging surfaces
- **8 Claude Code custom skills** replace all CLI interaction — zero argparse boilerplate
- **CloudFormation stack** (`pai-exercise`) live in us-east-1: S3×2, IAM least-privilege, Budget alarm
- **Production discipline:** SHA-256 content cache for deterministic demo re-runs; IAM explicit Deny on `s3:Delete*` and `iam:*`; `pip-audit` in every CI build; `DeletionPolicy: Retain` on CloudFormation Budget/S3 to prevent idempotency failures — cost-verified at **$2.21 for all 24 demo images**

Looking forward to the live session — there's more to show than what fits in an email.

Best,
Paul Prae
