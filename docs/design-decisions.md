# Design Decisions — PAI Packaging Automation PoC

Technical decisions and their rationale for interviewers who want to go deeper.

---

## 1. Model Selection: Nova Canvas over SD3.5 Large

**Decision:** Primary model is `amazon.nova-canvas-v1:0` (Nova Canvas).

**Why not SD3.5 Large:** `stability.sd3-5-large-v1:0` is only available in us-west-2. Nova Canvas is available in us-east-1. No cross-region inference profile exists for SD3.5 Large as of 2026-03. The exercise requires us-east-1 (only region with both Nova Canvas and Claude Sonnet 4.6).

**Nova Canvas benchmark evidence:**
- TIFA score: 0.897 (text-image fidelity alignment)
- ImageReward: 1.250 (human preference alignment)
- Source: Amazon Nova Technical Report (arxiv 2506.12103v1, 2025)
- Built-in inpainting/outpainting for future enhancements

**Dev tier fallback:** `amazon.titan-image-generator-v2:0` ($0.01/image) for fast iteration. Titan V2 limitation: only supports square dimensions (1024×1024); non-square ratios use 1024×1024 with center crop/pad in production.

---

## 2. Interface: Claude Code Skills over argparse

**Decision:** 8 Claude Code custom skills replace all CLI/argparse interaction.

**Why:** Zero UI development time. Better developer experience — invocations are natural language (`/run-pipeline`) rather than memorized flag strings. Hooks enforce code quality automatically (ruff on every `.py` edit, pytest on stop). Positions AI-native tooling as the primary interface pattern, which aligns with Adobe GenStudio's AI-first product vision.

**Tradeoff:** Skills only work within Claude Code sessions — not scriptable in cron jobs or CI pipelines directly. Mitigation: the underlying `python -m src.pipeline.run_pipeline` CLI still works for automation.

---

## 3. Storage: Flat JSON over PostgreSQL

**Decision:** Pipeline manifests stored as flat JSON files (S3 + local `outputs/runs/`). No database.

**Why for PoC:** PostgreSQL adds setup complexity (RDS provisioning, schema migrations, connection pooling) disproportionate to PoC requirements. Flat JSON is sufficient for 10-100 runs per session and produces machine-readable audit records without any additional infrastructure.

**Production path:** PostgreSQL on RDS documented in `BACKLOG.md` High Priority section. Schema design: `runs` table (run_id, sku_id, model_id, duration, cost_usd), `images` table (image_id, run_id, s3_key, format, product_slug).

---

## 4. Text Reasoning: `anthropic[bedrock]` over `boto3 InvokeModel`

**Decision:** `AnthropicBedrock(aws_region='us-east-1')` for Claude Sonnet 4.6 calls.

**Why:** Cleaner messages API vs raw JSON body serialization in boto3. Same IAM `bedrock:InvokeModel` permission. No additional credentials required — uses the same AWS profile as all other boto3 calls.

**Critical caveat:** `AnthropicBedrock` does NOT auto-read `~/.aws/config` for region — `aws_region` must be passed explicitly. Omitting it causes silent fallback to us-west-2 (model not available → `ModelNotReadyException`).

---

## 5. IaC: CloudFormation over Terraform/CDK

**Decision:** CloudFormation YAML (`infra/cloudformation/stack.yaml`).

**Why:** Self-contained, no additional tooling (no npm, no Terraform binary, no CDK synthesis step). Native AWS service with zero extra IAM permissions beyond what boto3 already needs. Sufficient for 3 resources (S3×2, IAM×1). CDK adds Node.js dependency complexity for a PoC with a single small stack.

**Tradeoff:** CloudFormation YAML is more verbose than CDK/Pulumi. For a PoC reviewed by an interviewer, the self-contained nature outweighs the verbosity cost.

---

## 6. CI/CD: Must-Have, Not Nice-To-Have

**Decision:** GitHub Actions `ci.yml` + `deploy.yml` are required deliverables, not bonus work.

**Why:** Demonstrates production engineering maturity that differentiates PoC from a script-in-a-folder. Auto-lint hook catches regressions on every push. `pip-audit --severity high` in CI closes security finding from threat modeling. SHA-pinned actions close supply chain risk (T-015 from STRIDE review). CloudFormation deploy on main push ensures the live stack stays in sync with the repo.

**Deviation from ideal:** Used GitHub Secrets (`AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`) instead of OIDC federation for simplicity in PoC. OIDC (no long-lived credentials in GitHub) is the correct production approach — documented in `BACKLOG.md`.

---

## 7. Text Overlay: Pillow over Server-Side Rendering

**Decision:** Pillow (PIL) for all text compositing (`src/pipeline/text_overlay.py`).

**Why:** Zero additional services. Runs locally and in CI without any rendering environment. Sufficient precision for PoC — title strip, attribute pills, and regulatory footer are all composited correctly using RGBA layers and semi-transparent overlays.

**Production alternative:** ImageMagick + font subsetting, or canvas-based web rendering (Node.js `canvas` or Chromium headless) for pixel-perfect brand typography. Documented in `BACKLOG.md`.

---

## 8. Image Caching: Content-Hash SHA-256 at `~/.cache/pai-pipeline/`

**Decision:** SHA-256 hash of (prompt + width + height + model_id) as the cache key. Cache stored at `~/.cache/pai-pipeline/` as individual PNG files.

**Why:** Avoids re-generation cost during development iterations. Typical development workflow generates the same prompt 10-20 times while tuning overlay layout — caching reduces cost from ~$0.80 to ~$0.04 for a full dev cycle. Cache survives Python process restarts and is cross-run.

**Benchmark:** Second run of 6-image batch completes in ~0.006s vs ~11.7s for first run (~1950x speedup). Cache invalidated automatically when prompt or dimensions change.

---

## 9. Sample Data: Why "Organic Trail Mix"?

**Decision:** The sample SKU brief (`inputs/sample_sku_brief.json`) uses a fictional "Organic Trail Mix" brand with "Original" and "Dark Chocolate" variants.

**Origin:** This data was specified in `.claude/plans/phase-02-core-pipeline.md` Task 2 as the canonical example for pipeline development. The choice was deliberate:
- **Two product variants** satisfy the exercise requirement of demonstrating multi-SKU generation
- **Health-food category** is brand-agnostic and avoids any trademark/IP concerns
- **Common CPG attributes** (organic, non-gmo, high-protein, gluten-free) exercise all four badge types in the text overlay
- **"us-west" region** differs from the AWS deployment region (us-east-1) to verify region-parameterized S3 key paths work correctly

No real brand or product is implied. This is a fictional example representing a typical CPG product brief.

---

## 10. Security: IAM Least Privilege + Explicit Deny

**Decision:** `PaiPipelineRole` uses explicit deny for `s3:Delete*` and `iam:*` in addition to minimum required allows.

**Why:** Explicit denies cannot be overridden by Allow policies at the resource level, providing defense-in-depth. Even if an attacker obtained temporary credentials for this role, they could not delete pipeline outputs or escalate IAM privileges. Design follows STRIDE threat model findings from the SA security review (`C:\dev\solutions-architecture-agent\outputs\eng-2026-003\knowledge_base\security_review.json`).
