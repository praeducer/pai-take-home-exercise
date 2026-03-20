# UAT Walkthrough — PAI Packaging Automation PoC

**Prepared for:** Paul Prae — interview preparation, stakeholder demo, and quality gate
**System:** Adobe PAI Take-Home Exercise — R162394 Senior Platform & AI Engineer
**Version:** v1.2.0
**Last verified:** 2026-03-20

> **How to use this document**
> Work top to bottom. Each section has a ✅ checkbox, a link to open, and the exact expected result.
> All links are live and verified. Completing the full walkthrough takes ~20 minutes and confirms every component is operational. Re-run any time after a code change to confirm nothing regressed.

---

## Pre-Flight Checklist

Before starting, confirm you have these ready:

| Requirement | Check |
|-------------|-------|
| AWS CLI authenticated: `aws sts get-caller-identity --profile pai-exercise` returns account ID | ☐ |
| GitHub logged in as `praeducer` | ☐ |
| Python env active: `python -c "import boto3, anthropic, PIL; print('OK')"` returns `OK` | ☐ |
| Working directory: `cd C:/dev/pai-take-home-exercise` | ☐ |

---

## Section 1 — GitHub.com Artifacts

These are the externally visible deliverables. An interviewer reviewing your submission will check these links.

---

### 1.1 Repository — Main Page & README

**What it is:** The public face of the submission. Contains embedded demo images, architecture overview, and quick-start guide.

🔗 **[https://github.com/praeducer/pai-take-home-exercise](https://github.com/praeducer/pai-take-home-exercise)**

**Expected when you open it:**
- README renders with 6 embedded Alpine Harvest demo images (4 regions visible)
- CI badge at top-left shows **green / passing**
- Description: "GenAI packaging image generation pipeline..."

☐ README loads with embedded images
☐ CI badge is green

---

### 1.2 Release Tags

**What they are:** Versioned snapshots. v1.0.0 = exercise requirements met. v1.1.0 = image quality overhaul + SA document. v1.2.0 = AI quality overhaul (narrative prompts, tool-use brand profile, Mango Coconut APAC, single-command UX).

🔗 **v1.2.0 (current):** [https://github.com/praeducer/pai-take-home-exercise/releases/tag/v1.2.0](https://github.com/praeducer/pai-take-home-exercise/releases/tag/v1.2.0)
🔗 **v1.1.0:** [https://github.com/praeducer/pai-take-home-exercise/releases/tag/v1.1.0](https://github.com/praeducer/pai-take-home-exercise/releases/tag/v1.1.0)
🔗 **v1.0.0 (baseline):** [https://github.com/praeducer/pai-take-home-exercise/releases/tag/v1.0.0](https://github.com/praeducer/pai-take-home-exercise/releases/tag/v1.0.0)

**Expected:** All 3 tags exist, v1.2.0 is the most recent.

☐ v1.2.0 tag exists
☐ v1.0.0 tag exists

---

### 1.3 CI Workflow — Lint, Test, Audit

**What it is:** Runs on every push. Validates code quality (ruff), correctness (pytest), and security (pip-audit). This is the primary quality gate.

🔗 **All CI runs:** [https://github.com/praeducer/pai-take-home-exercise/actions/workflows/ci.yml](https://github.com/praeducer/pai-take-home-exercise/actions/workflows/ci.yml)
🔗 **Latest run (verified green):** [https://github.com/praeducer/pai-take-home-exercise/actions/runs/23348945425](https://github.com/praeducer/pai-take-home-exercise/actions/runs/23348945425)
🔗 **Workflow definition:** [https://github.com/praeducer/pai-take-home-exercise/blob/main/.github/workflows/ci.yml](https://github.com/praeducer/pai-take-home-exercise/blob/main/.github/workflows/ci.yml)

**Expected in the latest run:**
- ✓ Set up job
- ✓ Install dependencies
- ✓ Lint with ruff
- ✓ Run unit tests (42 passed, 3 skipped)
- ✓ Security audit (pip-audit, zero high vulnerabilities)
- Total duration: ~20 seconds

**To reproduce locally:**
```bash
ruff check src/ tests/
pytest tests/ -v -m "not integration" -q
pip-audit -r requirements.txt
```

☐ Latest CI run shows all steps green
☐ Local ruff returns zero issues
☐ Local pytest shows 42 passed, 3 skipped

---

### 1.4 Deploy Workflow — CloudFormation Update

**What it is:** Runs on every push to `main`. Deploys the CloudFormation stack (`pai-exercise`) to us-east-1. Requires `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` GitHub Secrets.

🔗 **All Deploy runs:** [https://github.com/praeducer/pai-take-home-exercise/actions/workflows/deploy.yml](https://github.com/praeducer/pai-take-home-exercise/actions/workflows/deploy.yml)
🔗 **Workflow definition:** [https://github.com/praeducer/pai-take-home-exercise/blob/main/.github/workflows/deploy.yml](https://github.com/praeducer/pai-take-home-exercise/blob/main/.github/workflows/deploy.yml)

**Expected:** All deploy steps green.

> **Note on CloudFormation stack state:** The AWS stack status shows `UPDATE_ROLLBACK_COMPLETE` — this means a stack update was attempted, the Budget Alarm resource reported a duplicate-name conflict (the alarm already existed from initial creation), and CloudFormation rolled back to the previous known-good state. All functional resources (S3 buckets, IAM role) are intact and operational. The 24 generated images confirm the pipeline worked correctly post-rollback. For interview purposes: the stack is functional; the rollback was a Budget Alarm idempotency issue in the CF template.

☐ Latest Deploy run shows all steps green
☐ Understand the rollback note above (ready to explain to interviewers if asked)

---

### 1.5 Source Code — Pipeline Modules

**What it is:** 8 Python modules forming the end-to-end pipeline. Each module has a single responsibility.

🔗 **[https://github.com/praeducer/pai-take-home-exercise/tree/main/src/pipeline](https://github.com/praeducer/pai-take-home-exercise/tree/main/src/pipeline)**

| Module | Responsibility | Key function |
|--------|---------------|--------------|
| `sku_parser.py` | Load + validate SKU brief JSON against schema | `parse_sku_brief()` |
| `prompt_constructor.py` | Build format-specific (1:1 / 9:16 / 16:9) narrative positive + negative prompts | `build_image_prompt()` → `tuple[str, str]` |
| `text_reasoning.py` | Claude Sonnet 4.6 brand profile via tool_use (once/brief) + prompt enhancement | `generate_brand_profile()`, `enhance_prompt_with_reasoning()` |
| `image_generator.py` | Bedrock image generation with cache, retry, tier fallback | `generate_image()` |
| `text_overlay.py` | Pillow text compositing — brand name, attributes, regulatory | `apply_overlay()` |
| `asset_manager.py` | S3 upload/download, output key builder | `build_output_key()`, `upload_output()` |
| `output_manager.py` | Write JSON run manifest locally and to S3 | `write_manifest()` |
| `run_pipeline.py` | Orchestrator — wires all 7 modules | `run_pipeline()` |

☐ Open 2-3 modules in browser and confirm structure matches table above

---

### 1.6 Test Suite

**What it is:** 45 tests (42 pass, 3 skip, 1 integration deselected). Covers every pipeline module.

🔗 **[https://github.com/praeducer/pai-take-home-exercise/tree/main/tests](https://github.com/praeducer/pai-take-home-exercise/tree/main/tests)**

| Test file | What it covers | Count |
|-----------|---------------|-------|
| `test_sku_parser.py` | Schema validation, missing fields, invalid types | ~6 |
| `test_prompt_constructor.py` | Tuple return, format distinctness, narrative prose, negative prompt blocking text | ~11 |
| `test_image_generator.py` | Dry-run placeholder, cache key, cache hit/miss | ~7 |
| `test_text_overlay.py` | Overlay dimensions, content, format-specific layouts | ~5 |
| `test_asset_manager.py` | Output key format, S3 path structure | ~5 |
| `test_text_reasoning.py` | Brand profile dry-run, default keys, no API call | ~5 |
| `test_output_quality.py` | Manifest structure, output file existence | ~3 |
| `test_integration.py` | Full dry-run pipeline end-to-end (skipped in CI) | 1 |

**Run locally:**
```bash
pytest tests/ -v -m "not integration"
# Expected: 42 passed, 3 skipped, 1 deselected
```

☐ pytest passes locally

---

### 1.7 Claude Code Skills (Interface Layer)

**What it is:** 8 custom skills that replace all CLI/argparse interaction. The sole interface to the pipeline.

🔗 **[https://github.com/praeducer/pai-take-home-exercise/tree/main/.claude/skills](https://github.com/praeducer/pai-take-home-exercise/tree/main/.claude/skills)**

| Skill | Purpose | AWS calls? |
|-------|---------|-----------|
| `/run-pipeline` | Generate images from a SKU brief JSON | Yes — Bedrock + S3 |
| `/generate-demo` | Run all 4 regional demo briefs | Yes — Bedrock + S3 |
| `/pipeline-status` | Show recent runs from local manifests | No — read-only local |
| `/view-results` | List/download S3 images | Yes — S3 read |
| `/health-check` | Verify AWS resources and Bedrock access | Yes — read-only |
| `/deploy` | Deploy CloudFormation stack | Yes — CloudFormation |
| `/teardown` | Destroy CloudFormation stack (requires confirm) | Yes — CloudFormation |
| `/run-tests` | Run pytest suite | No — local only |

☐ Open `.claude/skills/run-pipeline/SKILL.md` — confirm it's a functional skill, not a stub

---

### 1.8 Demo Input Briefs

**What it is:** 4 JSON briefs demonstrating one-brand, 4-region variant automation — the core exercise scenario.

🔗 **[https://github.com/praeducer/pai-take-home-exercise/tree/main/inputs/demo_briefs](https://github.com/praeducer/pai-take-home-exercise/tree/main/inputs/demo_briefs)**

| Brief | Region | Flavors | Cultural direction |
|-------|--------|---------|-------------------|
| `trail-mix-us.json` | us-west | Original, Dark Chocolate | Pacific NW earth tones, outdoor lifestyle |
| `trail-mix-latam.json` | latam | Original, Tropical Edition | Golden yellows, terracotta, tropical energy |
| `trail-mix-apac.json` | apac | Original, Mango Coconut | SE Asian tropical vibrancy, warm sunrise colors |
| `trail-mix-eu.json` | eu | Original, Dark Berry | Scandinavian kraft, moss green, Nordic botanical |

All 4 share `"sku_id": "alpine-harvest-trail-mix"` → S3 paths: `alpine-harvest-trail-mix/{region}/{format}/{product}.png`

☐ Open any brief — confirm `sku_id` is `"alpine-harvest-trail-mix"` and `cultural_context` field is present

---

### 1.9 Solution Architecture Document

**What it is:** 310-line dual-audience SA document (engineers + business executives). Covers all pipeline components, Well-Architected assessment, cost model, and production roadmap.

🔗 **[https://github.com/praeducer/pai-take-home-exercise/blob/main/docs/solution-architecture.md](https://github.com/praeducer/pai-take-home-exercise/blob/main/docs/solution-architecture.md)**

**Key sections to skim:**
- Section 5: Multi-Step Generation Pipeline — explains the 3-AI-call chain per image
- Section 8: Well-Architected Assessment — 8.0/10 overall, per-pillar breakdown
- Section 10: Cost Model — $2.21 PoC, ~$92/month at production scale

☐ Document renders in GitHub with all 11 section headers visible

---

## Section 2 — Local Pipeline Verification

Run these commands locally to confirm the pipeline behaves correctly before the interview.

---

### 2.1 Dry-Run (Zero Cost, Zero AWS Calls)

```bash
cd C:/dev/pai-take-home-exercise
python -m src.pipeline.run_pipeline inputs/sample_sku_brief.json --dry-run
```

**Expected output:**
```
  + Alpine Harvest Trail Mix (Original) 1:1 [dry-run, skipped]
  + Alpine Harvest Trail Mix (Original) 9:16 [dry-run, skipped]
  + Alpine Harvest Trail Mix (Original) 16:9 [dry-run, skipped]
  + Alpine Harvest Trail Mix (Dark Chocolate) 1:1 [dry-run, skipped]
  + Alpine Harvest Trail Mix (Dark Chocolate) 9:16 [dry-run, skipped]
  + Alpine Harvest Trail Mix (Dark Chocolate) 16:9 [dry-run, skipped]

Pipeline complete: 0 images, ~0.04s
```

**Completes in:** <1 second (no network calls)

☐ Dry-run produces 6 "skipped" lines and exits cleanly

---

### 2.2 Local Image Generation (Dev Tier, ~$0.06)

```bash
PAI_OUTPUT_BUCKET=pai-exercise-paipackagingoutputbucket-l4u1ootx9lac \
  python -m src.pipeline.run_pipeline inputs/sample_sku_brief.json \
  --model-tier dev --profile pai-exercise
```

**Expected:** 6 images written to `outputs/results/alpine-harvest-trail-mix/us-west/`
**Duration:** ~15-30 seconds (2nd run uses cache → <2 seconds)

☐ Images appear in `outputs/results/alpine-harvest-trail-mix/us-west/`
☐ Second run is dramatically faster (cache hit logged)

---

### 2.3 Demo Images (Pre-Generated)

These 6 curated images were generated with Nova Canvas premium and are committed to the repo:

```bash
find outputs/demo -name "*.png" | sort
```

**Expected output:**
```
outputs/demo/alpine-harvest-trail-mix/apac/front_label/mango-coconut.png
outputs/demo/alpine-harvest-trail-mix/eu/front_label/original.png
outputs/demo/alpine-harvest-trail-mix/latam/front_label/original.png
outputs/demo/alpine-harvest-trail-mix/us-west/back_label/original.png
outputs/demo/alpine-harvest-trail-mix/us-west/front_label/original.png
outputs/demo/alpine-harvest-trail-mix/us-west/wraparound/dark-chocolate.png
```

☐ All 6 demo images exist locally
☐ Open 1 image per region to confirm visual distinctness

---

## Section 3 — AWS Cloud Resources

All resources are in `us-east-1`. Open AWS Console as the `pai-exercise` IAM user/profile before clicking these links.

---

### 3.1 CloudFormation Stack

**What it is:** Single stack `pai-exercise` provisions all AWS infrastructure as code. Idempotent — re-deployable via CI.

🔗 **[https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks?filteringStatus=active&filteringText=pai-exercise](https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks?filteringStatus=active&filteringText=pai-exercise)**

**CLI alternative:**
```bash
aws cloudformation describe-stacks --stack-name pai-exercise \
  --profile pai-exercise --query 'Stacks[0].{Status:StackStatus,Outputs:Outputs}' --output table
```

**Expected status:** `UPDATE_ROLLBACK_COMPLETE`
**What that means for the interview:** All S3 buckets, IAM role, and Budget alarm are deployed and operational. The `ROLLBACK` suffix means a subsequent `deploy.yml` run tried to update the Budget Alarm, which failed because the alarm already existed. CloudFormation rolled back to the original working state. Zero impact on pipeline functionality.

**Stack outputs to know:**
| Output | Value |
|--------|-------|
| InputBucketName | `pai-exercise-paiassetsinputbucket-vssunkaugllr` |
| OutputBucketName | `pai-exercise-paipackagingoutputbucket-l4u1ootx9lac` |
| PipelineRoleArn | `arn:aws:iam::<ACCOUNT_ID>:role/pai-pipeline-role` |

☐ Stack found in console
☐ Outputs show both bucket names and role ARN

---

### 3.2 S3 — Output Bucket (Generated Images)

**What it is:** 24+ generated PNG images organized by `{sku_id}/{region}/{format}/{product}.png`, plus run manifests.

🔗 **[https://s3.console.aws.amazon.com/s3/buckets/pai-exercise-paipackagingoutputbucket-l4u1ootx9lac?region=us-east-1](https://s3.console.aws.amazon.com/s3/buckets/pai-exercise-paipackagingoutputbucket-l4u1ootx9lac?region=us-east-1)**

**CLI alternative:**
```bash
aws s3 ls s3://pai-exercise-paipackagingoutputbucket-l4u1ootx9lac/alpine-harvest-trail-mix/ \
  --recursive --profile pai-exercise
```

**Expected S3 structure:**
```
alpine-harvest-trail-mix/
  us-west/
    front_label/original.png, dark-chocolate.png
    back_label/original.png, dark-chocolate.png
    wraparound/original.png, dark-chocolate.png
  latam/   (same structure)
  apac/    (same structure — mango-coconut.png)
  eu/      (same structure)
  manifests/  (JSON run logs)
```

**Expected counts:** ≥24 PNG files, ≥4 JSON manifest files

```bash
# Verify counts
aws s3 ls s3://pai-exercise-paipackagingoutputbucket-l4u1ootx9lac/ \
  --recursive --profile pai-exercise | grep "\.png" | wc -l
# Expected: ≥24
```

☐ 24+ PNG images visible in S3
☐ Folder structure matches `{sku_id}/{region}/{format}/` pattern

---

### 3.3 S3 — Input Bucket (Asset Uploads)

**What it is:** Empty input bucket for pre-production assets (logos, brand imagery). Currently unused in PoC — the `asset_manager.py` `check_s3_asset()` function checks here before falling back to prompt-only generation.

🔗 **[https://s3.console.aws.amazon.com/s3/buckets/pai-exercise-paiassetsinputbucket-vssunkaugllr?region=us-east-1](https://s3.console.aws.amazon.com/s3/buckets/pai-exercise-paiassetsinputbucket-vssunkaugllr?region=us-east-1)**

**Expected:** Empty bucket. Block Public Access: enabled. SSE-S3: enabled.

☐ Bucket accessible, Block Public Access confirmed

---

### 3.4 Amazon Bedrock — Model Access

**What it is:** 4 foundation models — all must be `ACTIVE` for the pipeline to function.

🔗 **[https://console.aws.amazon.com/bedrock/home?region=us-east-1#/models](https://console.aws.amazon.com/bedrock/home?region=us-east-1#/models)**

**CLI verification:**
```bash
aws bedrock list-foundation-models --region us-east-1 --profile pai-exercise \
  --query 'modelSummaries[?contains(modelId,`nova-canvas`) || contains(modelId,`titan-image`) || contains(modelId,`claude-sonnet-4-6`) || contains(modelId,`claude-opus-4-6`)].{id:modelId,status:modelLifecycle.status}' \
  --output table
```

**Expected (verified 2026-03-20):**

| Model ID | Role | Status | Cost |
|----------|------|--------|------|
| `amazon.nova-canvas-v1:0` | Primary image generation | ACTIVE | $0.08/image (premium) |
| `amazon.titan-image-generator-v2:0` | Dev/fallback image generation | ACTIVE | $0.01/image |
| `anthropic.claude-sonnet-4-6` | Brand profile (tool_use, once/brief) + prompt enhancement | ACTIVE | ~$0.006/call |
| `anthropic.claude-opus-4-6-v1` | Available (unused — Sonnet handles all text reasoning) | ACTIVE | ~$0.01/call |

☐ All 4 models show ACTIVE
☐ Understand which model is used at each pipeline step (see table above)

---

### 3.5 IAM — Pipeline Role

**What it is:** Least-privilege IAM role used by the pipeline. Grants only what is needed for Bedrock invocation and S3 read/write. Explicitly denies `s3:Delete*` and `iam:*`.

🔗 **[https://console.aws.amazon.com/iam/home#/roles/pai-pipeline-role](https://console.aws.amazon.com/iam/home#/roles/pai-pipeline-role)**

**CLI verification:**
```bash
aws iam get-role --role-name pai-pipeline-role \
  --profile pai-exercise --query 'Role.RoleName'
```

**Key permissions to know for the interview:**
- ✅ `bedrock:InvokeModel` — for all 4 model ARNs
- ✅ `s3:GetObject`, `s3:PutObject`, `s3:ListBucket` — on both buckets
- ❌ `s3:DeleteObject`, `s3:DeleteBucket` — explicitly denied
- ❌ `iam:*` — explicitly denied

☐ Role exists and is accessible

---

### 3.6 AWS Budget Alarm

**What it is:** $25/month budget with alerts at 80% ($20) and 100% ($25). Prevents unexpected cost overruns.

🔗 **[https://console.aws.amazon.com/billing/home#/budgets](https://console.aws.amazon.com/billing/home#/budgets)**

**What to look for:** A budget named `pai-pipeline-budget` (or similar) with $25 monthly limit.

**Note:** The CloudFormation `UPDATE_ROLLBACK_COMPLETE` status was caused by this Budget Alarm. The alarm exists and is active — the CF update failed because you cannot re-create a Budget with the same name (it's idempotent in AWS Budgets). This is a known CF limitation, not a security or cost issue.

☐ Budget alarm visible in Billing console

---

## Section 4 — Interview Talking Points

Use these when presenting the system. Each point is directly verifiable in the sections above.

### The 30-second pitch
> "I built an end-to-end GenAI packaging automation pipeline on AWS Bedrock. You give it a JSON brief for a CPG product, and it generates packaging images in 3 aspect ratios — front label, back label, and wraparound — adapted for any regional market. The demo shows one product line, Alpine Harvest Trail Mix, generating culturally distinct packaging across US West, LATAM, APAC, and EU from the same `sku_id`. The whole interface is 8 Claude Code custom skills. No CLI, no frontend. Claude also wrote all the code."

### The 5 talking points with evidence

| Point | Where to show it |
|-------|-----------------|
| **Regional variant automation** — same `sku_id`, 4 culturally distinct outputs | Demo images in README; 4 briefs in `inputs/demo_briefs/`; S3 structure in Section 3.2 |
| **Multi-step AI chain** — Sonnet 4.6 via tool_use for brand direction, Sonnet 4.6 for prompt refinement, Nova Canvas for generation | `text_reasoning.py` + `prompt_constructor.py` source; Section 5 of SA doc |
| **Production-quality engineering** — 42 tests, CI/CD, CloudFormation IaC, least-privilege IAM | CI run (Section 1.3); Test files (Section 1.6); IAM role (Section 3.5) |
| **AI-native development** — Claude Code IS the interface; Claude wrote all the code | Skills in `.claude/skills/`; CLAUDE.md explaining the workflow |
| **Cost-conscious design** — 3 model tiers, disk caching, $2.21 for 24 production images | `image_generator.py` MODEL_TIERS + CACHE_DIR; SA doc Section 10 |

### Anticipated questions

| Question | Answer |
|----------|--------|
| "Why CloudFormation not CDK?" | Self-contained. No npm dependency. Single YAML file any AWS engineer can read. |
| "Why no database?" | PoC scope. Flat JSON manifests serve the exercise requirements. RDS is first item in BACKLOG.md. |
| "Why Claude Code skills instead of a REST API?" | Zero UI development time. Skills are self-documenting. Matches the AI-native philosophy the exercise calls for. |
| "The stack says UPDATE_ROLLBACK_COMPLETE — is it broken?" | No. S3, IAM, and Bedrock are all operational (24 images generated post-rollback). The rollback was a Budget Alarm idempotency issue in CF, not a resource failure. |
| "How does it ensure visual consistency across the 6 images?" | `generate_brand_profile()` calls Claude Sonnet 4.6 via tool_use once per brief to establish color palette, photography style, and regional visual elements. All 6 images inherit that profile. Using tool_use guarantees schema-conformant JSON without brittle parsing. |
| "Why Sonnet 4.6 instead of Opus for brand profiling?" | Structured tool_use produces identical schema-conformant JSON with either model. Sonnet 4.6 is 40% cheaper and ~2x faster for this task. Opus adds no quality benefit when the output is a constrained JSON schema. |

---

## Section 5 — Regression Checklist

Run this after any code change to confirm nothing broke.

```bash
# 1. Lint
ruff check src/ tests/
# Expected: All checks passed!

# 2. Unit tests
pytest tests/ -v -m "not integration" -q
# Expected: 42 passed, 3 skipped, 1 deselected

# 3. Dry-run pipeline
python -m src.pipeline.run_pipeline inputs/sample_sku_brief.json --dry-run
# Expected: 6 [dry-run, skipped] lines, exits <1s

# 4. Schema validation
python -c "
import json, jsonschema
s = json.load(open('src/schemas/sku_brief_schema.json'))
for f in ['inputs/sample_sku_brief.json'] + [f'inputs/demo_briefs/trail-mix-{r}.json' for r in ['us','latam','apac','eu']]:
    jsonschema.validate(json.load(open(f)), s)
    print(f'valid: {f}')
"
# Expected: 5 "valid: ..." lines
```

---

*Verified 2026-03-20 by Paul Prae. All links tested. All CLI commands confirmed on Windows/Git Bash with `pai-exercise` AWS profile.*
