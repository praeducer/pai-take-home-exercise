# Demo Script — 5-Minute Flow

**Goal:** Show an interviewer a working end-to-end AI packaging generation pipeline.
**Setup:** Claude Code open in `C:\dev\pai-take-home-exercise`, AWS profile `pai-exercise` active.

---

## Step 1: Architecture Overview (1 minute)

Open README on github.com/praeducer/pai-take-home-exercise — point to embedded images.

> "This is an AI packaging design pipeline: you put a JSON product brief in one end, and get
> production-ready packaging images in 3 aspect ratios out the other. The whole thing runs through
> Claude Code skills — no argparse, no web server."

Point to key components:
- Nova Canvas model (TIFA 0.897 — published benchmark in the README)
- Claude Sonnet 4.6 for prompt enhancement via `anthropic[bedrock]`
- Pillow for text overlay compositing (title strip, attribute badges, regulatory footer)
- CloudFormation for infrastructure (S3×2, IAM, Budget alarm)
- GitHub Actions CI/CD with SHA-pinned actions

---

## Step 2: Show the Code (1 minute)

Open three files:

**`src/pipeline/run_pipeline.py`** — 120 lines
> "This is the orchestrator. For each product × each aspect ratio: build prompt, enhance with Claude,
> generate image, composite text overlay, save locally, upload to S3. Error-tolerant loop — one
> failed product doesn't abort the whole run."

**`inputs/sample_sku_brief.json`** — the input contract
> "The interface is a simple JSON brief. Brand, products, region, audience, attributes. The schema
> validates it at parse time."

**`infra/cloudformation/stack.yaml`** — 130 lines
> "This deploys everything: two S3 buckets, one IAM role with least-privilege plus explicit deny
> on Delete* and iam:*, and a Budget alarm. CAPABILITY_NAMED_IAM because the role has an explicit
> name."

---

## Step 3: Run the Pipeline (2 minutes)

```
/run-pipeline inputs/sample_sku_brief.json --model-tier dev
```

While it runs (first run ~45s, cached runs ~0.006s):
> "Titan V2 dev tier — $0.01/image, fast for iteration. Switch to `--model-tier final` for
> Nova Canvas quality. Six images: 2 products × 3 ratios (1:1 front label, 9:16 back label,
> 16:9 wraparound). Content-addressed SHA-256 cache means reruns are instant."

After completion:
> "Six images saved locally to `outputs/results/` and uploaded to S3. The manifest in
> `outputs/runs/` records run_id, model used, duration, and any errors."

---

## Step 4: View Results (30 seconds)

```
/view-results organic-trail-mix-us
```

Or open the PNG files in `outputs/results/organic-trail-mix-us/us-west/front_label/`.

> "Title strip is the product name. Attribute badges are the four label claims from the brief.
> Regulatory footer is synthesized placeholder text — real compliance database is in the backlog."

---

## Step 5: Show CI/CD (30 seconds)

Open GitHub Actions tab: github.com/praeducer/pai-take-home-exercise/actions

> "Green on every push. Three jobs: ruff lint, pytest (35 unit tests, 1 integration test skipped
> in CI), pip-audit with severity high. CloudFormation deploy runs on main merge. SHA-pinned
> actions close the supply chain risk from the threat model."

Point to `phase-04-complete.md` in the repo root for the specific SHA hashes used.

---

## Anticipated Questions

**Q: Why not SD3.5 Large?**
A: Only available in us-west-2. Nova Canvas is in us-east-1 — the only region with both Nova Canvas and Claude Sonnet 4.6. Benchmarks are in `docs/design-decisions.md`.

**Q: Why Claude Code skills instead of a CLI?**
A: Zero UI development time. The hooks enforce code quality automatically — ruff on every `.py` edit, pytest on stop. It's an AI-native interface that aligns with GenStudio's product direction.

**Q: What would production look like?**
A: Lambda + API Gateway for auto-scaling, PostgreSQL on RDS for run history, Rekognition for content moderation, OIDC instead of static credentials in CI. All documented in `BACKLOG.md`.

**Q: Is the text overlay production quality?**
A: For English product names ≤30 chars, yes — it's readable and correctly positioned. Multi-language (CJK, etc.) requires font bundling and coordinate tuning — that's in the backlog.
