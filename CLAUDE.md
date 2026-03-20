# PAI Packaging Automation PoC

**Adobe PAI Interview Take-Home Exercise**
**Owner:** Paul Praedunhin (@praeducer)
**Target GitHub:** `praeducer/pai-take-home-exercise` (public)

---

## How to Start Every Session

Read the master plan first: `.claude/plans/00-master-plan.md`

---

## Current State

**Phase 5 — Complete. v1.0.0 tagged.**

- AWS: `pai-exercise` profile, us-east-1, stack CREATE_COMPLETE
- Python 3.12, all deps in `.venv`
- Bedrock: Nova Canvas + Claude Sonnet 4.6 verified
- GitHub Actions CI: green (lint + tests + pip-audit)

---

## Output Conventions

| What | Where | Git tracked? |
|------|-------|-------------|
| Pipeline images | `outputs/results/{sku}/{region}/{format}/` | Yes |
| Run manifests | `outputs/runs/{timestamp}_{sku}.json` | Yes (latest per SKU) |
| Demo images (README) | `outputs/demo/` | Yes |
| **Deliverables & client comms** | **`outputs/deliverables/`** | **Yes — redact PII** |
| Scratch / temp files | `tmp/` | No (gitignored) |
| Plans (all) | `.claude/plans/` | Yes |

**Rules:**
- All deliverables, proposals, emails, and client-facing documents go in `outputs/deliverables/`. Redact PII — leave placeholders like `[INTERVIEWER_NAME]` for the human to fill in.
- All plans go in `.claude/plans/` — never in `docs/plans/` or elsewhere.
- All temporary files go in `tmp/` at the repo root — never in system `/tmp` or other locations outside the repo.
- No files outside this repo should be referenced by absolute path. If external content is needed, copy it into the repo first.

---

## Architecture Decisions (Fixed)

| Decision | Value |
|---------|-------|
| Region | `us-east-1` |
| CloudFormation stack | `pai-exercise` |
| AWS profile | `pai-exercise` |
| Primary image model | `amazon.nova-canvas-v1:0` |
| Dev/fallback model | `amazon.titan-image-generator-v2:0` |
| Text reasoning | `anthropic.claude-sonnet-4-6` via `AnthropicBedrock(aws_region='us-east-1')` |
| Brand profiling | `anthropic.claude-sonnet-4-6` (tool_use for guaranteed JSON) |
| Package | `anthropic[bedrock]` (not raw boto3) |
| Interface | Claude Code CLI — 8 skills in `.claude/skills/` |
| IaC | CloudFormation YAML — self-contained, no npm |
| Language | Python 3.12 |
| Database | None — flat JSON manifests (PostgreSQL in BACKLOG) |
| S3 key pattern | `{sku_id}/{region}/{format}/{filename}` |

---

## AWS Quick Reference

```bash
aws sts get-caller-identity --profile pai-exercise
aws cloudformation describe-stacks --stack-name pai-exercise --profile pai-exercise
```

---

## Reference Files

| File | Purpose |
|------|---------|
| `.claude/plans/00-master-plan.md` | Master plan — acceptance criteria, phase graph |
| `.claude/plans/phase-06-enhancements.md` | Phase 6 — brand + regulatory checks (not yet executed) |
| `inputs/PAI-Take_Home_Exercise.md` | Original exercise spec |
| `docs/design-decisions.md` | Technical decisions with rationale |
| `docs/solution-architecture.md` | Full architecture document |
| `outputs/deliverables/proposal.md` | SA technical architecture brief |
| `outputs/deliverables/submission-email.md` | Submission email draft (PII redacted) |
