# PAI Packaging Automation PoC

**Adobe PAI Interview Take-Home Exercise**
**Owner:** Paul Praedunhin (@praeducer)
**SA Engagement:** eng-2026-003
**Target GitHub:** `praeducer/pai-take-home-exercise` (public)

---

## How to Start Every Session

**Always read the master plan first:**

```
Read .claude/plans/00-master-plan.md
```

Then load the current phase plan (`.claude/plans/phase-0N-*.md`) and execute tasks in order. Each task has explicit acceptance criteria — do not move to the next task until criteria pass.

After each phase, save a context snapshot as `phase-0N-complete.md` in the repo root with actual bucket names, model IDs used, function signatures, and any deviations.

---

## Current State

**Phase 5 — Complete. v1.0.0 tagged.**

| Task | Status | Notes |
|------|--------|-------|
| 1 — GitHub repo | ✅ Done | `praeducer/pai-take-home-exercise` public, remote set |
| 2 — Directory structure | ✅ Done | All dirs exist |
| 3 — venv + requirements.txt | ✅ Done | `.venv` and `requirements.txt` created |
| 4 — CloudFormation stack.yaml | ✅ Done | `infra/cloudformation/stack.yaml` deployed |
| 5 — Deploy stack | ✅ Done | Stack deployed, CREATE_COMPLETE |
| 6 — G-001 Bedrock gate | ✅ Done | Nova Canvas + Claude Sonnet 4.6 verified |
| 7 — CLAUDE.md | ✅ Done | |
| 8 — 8 skills scaffolded | ✅ Done | All 8 in `.claude/skills/` |
| 9 — .claude/settings.json hooks | ✅ Done | ruff lint, pytest stop hook, destructive guard |
| 10 — .mcp.json | ✅ Done | aws-iac + aws-knowledge configured |
| 11 — Commit + push | ✅ Done | Public repo hardened, OSS governance committed |

### Environment Status (as of 2026-03-19)

- AWS credentials: `pai-exercise` profile configured → account `<ACCOUNT_ID>` verified
- Python: 3.12, all deps installed in `.venv` (requirements.txt pinned)
- CloudFormation stack: `pai-exercise` — CREATE_COMPLETE, us-east-1
- Bedrock: Nova Canvas (`amazon.nova-canvas-v1:0`) + Claude Sonnet 4.6 verified
- GitHub Actions CI: green (lint + 35 tests + pip-audit)
- v1.0.0 tag: pushed to praeducer/pai-take-home-exercise

---

## Architecture Decisions (Fixed — Do Not Change Without SA Review)

| Decision | Value | Rationale |
|---------|-------|-----------|
| Region | `us-east-1` | Only region with Nova Canvas + Claude Sonnet 4.6 |
| Primary image model | `amazon.nova-canvas-v1:0` | TIFA 0.897, ImageReward 1.250 (arxiv 2506.12103) |
| Dev/fallback model | `amazon.titan-image-generator-v2:0` | us-east-1 available, $0.01/image |
| Text reasoning model | `anthropic.claude-sonnet-4-6` | Via `AnthropicBedrock(aws_region='us-east-1')` |
| Text reasoning package | `anthropic[bedrock]` | Cleaner API than raw boto3 InvokeModel |
| Interface | Claude Code CLI — 8 custom skills | No argparse, no CLI framework |
| IaC | CloudFormation YAML | Self-contained, no npm |
| Language | Python 3.12 | boto3, anthropic, Pillow, pytest, ruff |
| Database | None | Flat JSON manifests only — PostgreSQL is BACKLOG |
| Budget | Unconstrained | Expected total <$25 for PoC |
| MCP transport | `uv tool run` (Python) | NOT npm/npx — AWS MCP servers are Python packages |
| CloudFormation stack name | `pai-exercise` | Used in all phase commands |
| AWS profile | `pai-exercise` | `~/.aws/credentials` named profile |
| Output S3 key pattern | `{sku_id}/{region}/{format}/{filename}` | front_label/, back_label/, wraparound/ |

---

## Skills Reference

8 custom skills live in `.claude/skills/`. Invoke via `/skill-name` in Claude Code.

| Skill | Purpose | Note |
|-------|---------|------|
| `/run-pipeline` | Run full pipeline from SKU brief JSON | Disable model invocation |
| `/pipeline-status` | Show recent runs from local manifest files | Read-only |
| `/view-results` | List/download generated images from S3 | Read-only |
| `/deploy` | CloudFormation deploy | Disable model invocation |
| `/teardown` | CloudFormation destroy | Disable model invocation + confirm |
| `/health-check` | Verify AWS resources and Bedrock access | Read-only |
| `/run-tests` | Execute full test suite | Read-only |
| `/generate-demo` | Run pipeline with all demo SKU briefs | Disable model invocation |

Skills are fully implemented in `.claude/skills/` as of Phase 5.

---

## Hooks

Hooks are configured in `.claude/settings.json`:

- **PostToolUse (Edit/Write):** Auto-lints edited `.py` files with `ruff check`
- **Stop:** Runs `pytest tests/ -q` — warns if tests fail (blocking enabled after Phase 4)
- **PreToolUse (Bash):** Requires explicit confirmation for destructive AWS commands and sensitive secret-read operations

---

## MCP Servers

Configured in `.mcp.json`. Activate after Phase 1 Task 9 (`uv` must be installed).

- **aws-iac:** CloudFormation and IaC assistance via `uv tool run awslabs.aws-iac-mcp-server@latest`
- **aws-knowledge:** Optional AWS documentation search server if configured for this repo

---

## AWS Configuration

```bash
# Verify AWS auth before any Bedrock/S3 work:
aws sts get-caller-identity --profile pai-exercise
# Expected: account <ACCOUNT_ID>

# CloudFormation stack:
aws cloudformation describe-stacks --stack-name pai-exercise --profile pai-exercise

# Bedrock model access check (models auto-enable on first invocation — see docs/aws-setup.md):
aws bedrock list-foundation-models --region us-east-1 --profile pai-exercise | grep -E "nova-canvas|titan-image|claude-sonnet"
```

---

## Phase Execution Order

```
Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → [Phase 6 optional]
Foundation  Core     Quality  CI/CD    Docs/Demo  Enhancements
```

**P2 = Minimum Demo State.** If time-constrained, P3 = full exercise requirements met. P4-P5 = polish and CI/CD differentiation.

---

## Reference Files in This Repo

| File | Purpose |
|------|---------|
| `.claude/plans/00-master-plan.md` | Master plan — global acceptance criteria, phase dependency graph |
| `.claude/plans/phase-01-foundation.md` | Phase 1 — AWS infra, Claude Code scaffolding |
| `.claude/plans/phase-02-core-pipeline.md` | Phase 2 — Working pipeline → first images in S3 |
| `.claude/plans/phase-03-output-quality.md` | Phase 3 — All 3 aspect ratios, caching, dry-run |
| `.claude/plans/phase-04-cicd-testing.md` | Phase 4 — GitHub Actions, test suite |
| `.claude/plans/phase-05-docs-demo.md` | Phase 5 — README, demo data, v1.0.0 tag |
| `.claude/plans/phase-06-enhancements.md` | Phase 6 — Brand + regulatory checks (optional) |
| `inputs/PAI-Take_Home_Exercise.md` | Original exercise spec — source of truth |
| `inputs/paul-prae-profile.md` | Developer profile — skill context for code style |

## SA Deliverables (Read-Only Reference)

Full SA artifacts (local only, not committed to this repo):
- `knowledge_base/requirements.json` — FR-001 through FR-015, SC-001 through SC-006
- `knowledge_base/architecture.json` — C-001 through C-012, WA scores (6.8/10)
- `knowledge_base/security_review.json` — STRIDE threats, IAM design
- `knowledge_base/estimate.json` — AI-assisted hours
- `knowledge_base/project_plan.json` — 6 phases, 5 gates
- `outputs/eng-2026-003/proposal.md` — Full technical proposal

---

## Backlog (Do Not Implement in PoC)

These are explicitly out-of-scope. Document in `BACKLOG.md`:
- PostgreSQL on RDS for run history
- Lambda + API Gateway for production auto-scaling
- QuickSight dashboard
- Real regulatory compliance database
- A/B testing pipeline
- stability.sd3-5-large-v1:0 (unavailable in us-east-1)
