# Submission Email

**To:** [INTERVIEWER_NAME_1], [INTERVIEWER_NAME_2]
**From:** Paul Prae
**Re:** Interview Submission — Paul Prae ([CANDIDATE_ID]), R162394 Senior Platform & AI Engineer
**Date:** [SUBMISSION_DATE]

---

[INTERVIEWER_NAME_1], [INTERVIEWER_NAME_2] —

Submission complete for the PAI take-home exercise (R162394). Here's what's delivered:

- **GitHub repository (public, v1.2.0):** https://github.com/praeducer/pai-take-home-exercise
  — README with embedded demo images across 4 global markets, architecture overview, and quick-start guide
- **CI/CD (GitHub Actions, green):** https://github.com/praeducer/pai-take-home-exercise/actions
  — Automated lint (ruff), 46 tests (43 pass + 3 integration skipped in CI), dependency audit (pip-audit) on every push
- **Solution architecture document:** [`docs/solution-architecture.md`](https://github.com/praeducer/pai-take-home-exercise/blob/main/docs/solution-architecture.md)
  — Also attached separately as `solution-architecture.docx`
- **Demo output:** 24 generated images — Alpine Harvest Organic Trail Mix across 4 regional markets (US West, LATAM, APAC, EU), 2 products × 3 packaging formats each
  — Same `sku_id`, 4 culturally distinct packaging directions, all generated from JSON briefs in `inputs/demo_briefs/`

**Technical highlights:**

- **Multi-step AI pipeline:** 3 AI calls per image (brand profiling → prompt enhancement → image generation) plus text overlay compositing — not a single-prompt approach
- **Brand profile via tool use:** Claude Sonnet 4.6 with `tool_choice` generates structured visual direction (photography style, color palette, cultural elements) once per brief — guaranteed JSON schema, no brittle parsing
- **Nova Canvas premium:** cfgScale 8.5 with strengthened negative prompts to minimize AI text hallucination on packaging surfaces
- **8 Claude Code custom skills** replace all CLI interaction — zero argparse boilerplate
- **CloudFormation stack** (`pai-exercise`) live in us-east-1: S3×2, IAM least-privilege, Budget alarm

Happy to walk through the implementation live during the interview session.

Best,
Paul Prae
