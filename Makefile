# PAI Packaging Automation PoC — Single-command operations
.PHONY: deploy run dry-run run-demo deliverables test lint audit help

# ── Infrastructure ─────────────────────────────────────────────────────────────

# Deploy (or update) the CloudFormation stack — S3, IAM, Budget alarm
deploy:
	aws cloudformation validate-template \
	  --template-body file://infra/cloudformation/stack.yaml \
	  --profile pai-exercise --region us-east-1
	aws cloudformation deploy \
	  --stack-name pai-exercise \
	  --template-file infra/cloudformation/stack.yaml \
	  --capabilities CAPABILITY_NAMED_IAM \
	  --profile pai-exercise \
	  --region us-east-1
	@echo ""
	@echo "=== Stack Outputs ==="
	@aws cloudformation describe-stacks \
	  --stack-name pai-exercise \
	  --profile pai-exercise \
	  --query 'Stacks[0].Outputs' --output table

# ── Pipeline ───────────────────────────────────────────────────────────────────

# Run the pipeline for the sample brief (final tier — Nova Canvas)
run:
	$(eval BUCKET := $(shell aws cloudformation describe-stacks \
	  --stack-name pai-exercise --profile pai-exercise \
	  --region us-east-1 \
	  --query 'Stacks[0].Outputs[?OutputKey==`OutputBucketName`].OutputValue' \
	  --output text 2>/dev/null))
	PAI_OUTPUT_BUCKET=$(BUCKET) \
	python -m src.pipeline.run_pipeline inputs/sample_sku_brief.json \
	  --model-tier final --profile pai-exercise

# Zero-cost dry-run — validates schema, shows what would be generated
dry-run:
	python -m src.pipeline.run_pipeline inputs/sample_sku_brief.json --dry-run

# Run all 4 regional demo briefs (24 images, Nova Canvas final tier)
run-demo:
	$(eval BUCKET := $(shell aws cloudformation describe-stacks \
	  --stack-name pai-exercise --profile pai-exercise \
	  --region us-east-1 \
	  --query 'Stacks[0].Outputs[?OutputKey==`OutputBucketName`].OutputValue' \
	  --output text 2>/dev/null))
	@for brief in inputs/demo_briefs/trail-mix-us.json \
	              inputs/demo_briefs/trail-mix-latam.json \
	              inputs/demo_briefs/trail-mix-apac.json \
	              inputs/demo_briefs/trail-mix-eu.json; do \
	  echo ""; \
	  echo "=== $$brief ==="; \
	  PAI_OUTPUT_BUCKET=$(BUCKET) \
	  python -m src.pipeline.run_pipeline $$brief \
	    --model-tier final --profile pai-exercise; \
	done

# ── Deliverables ──────────────────────────────────────────────────────────────

# Show all PAI exercise deliverables with links
deliverables:
	@echo ""
	@echo "════════════════════════════════════════════════════"
	@echo "  PAI Packaging Automation PoC — Deliverables"
	@echo "════════════════════════════════════════════════════"
	@echo ""
	@echo "GitHub Repository:"
	@echo "  https://github.com/praeducer/pai-take-home-exercise"
	@echo ""
	@echo "CI Status:"
	@echo "  https://github.com/praeducer/pai-take-home-exercise/actions/workflows/ci.yml"
	@echo ""
	@echo "Release Tags:"
	@echo "  v1.2.0: https://github.com/praeducer/pai-take-home-exercise/releases/tag/v1.2.0"
	@echo "  v1.1.0: https://github.com/praeducer/pai-take-home-exercise/releases/tag/v1.1.0"
	@echo "  v1.0.0: https://github.com/praeducer/pai-take-home-exercise/releases/tag/v1.0.0"
	@echo ""
	@echo "PAI Exercise Requirements:"
	@echo "  ✅ SKU brief JSON input    → inputs/sample_sku_brief.json + inputs/demo_briefs/"
	@echo "  ✅ ≥2 products/flavors     → Each brief: 2 products (Original + regional variant)"
	@echo "  ✅ 3 aspect ratios         → front_label (1:1), back_label (9:16), wraparound (16:9)"
	@echo "  ✅ Text/attributes on pkg  → Title strip, attribute badges, regulatory footer"
	@echo "  ✅ S3 organized storage    → {sku_id}/{region}/{format}/{product}.png"
	@echo "  ✅ IaC deployment          → infra/cloudformation/stack.yaml"
	@echo "  ✅ README                  → github.com/praeducer/pai-take-home-exercise#readme"
	@echo "  ✅ CI/CD (bonus)           → GitHub Actions ci.yml + deploy.yml"
	@echo "  ✅ Brand consistency (bonus) → Claude Sonnet 4.6 brand profile per brief"
	@echo "  ✅ Approval logging (bonus) → JSON manifests in S3 + outputs/runs/"
	@echo ""
	@echo "Key Documents:"
	@echo "  Solution Architecture: docs/solution-architecture.md"
	@echo "  UAT Walkthrough:       docs/uat-walkthrough.md"
	@echo "  Submission Email:      outputs/deliverables/submission-email.md"
	@echo ""
	@echo "Local Outputs:"
	@find outputs/results -name "*.png" 2>/dev/null | wc -l | xargs echo "  Generated images (local):"
	@find outputs/demo -name "*.png" 2>/dev/null | wc -l | xargs echo "  Demo images (committed): "

# ── Quality ───────────────────────────────────────────────────────────────────

# Run unit tests (no AWS required)
test:
	python -m pytest tests/ -q -m "not integration"

# Run all tests including integration (requires AWS credentials)
test-all:
	AWS_PROFILE=pai-exercise python -m pytest tests/ -q

# Lint with ruff
lint:
	ruff check src/ tests/

# Security audit
audit:
	pip-audit -r requirements.txt

# ── Help ──────────────────────────────────────────────────────────────────────

help:
	@echo ""
	@echo "PAI Pipeline Commands:"
	@echo "  make deploy       Deploy CloudFormation stack (S3, IAM, Budget)"
	@echo "  make run          Run pipeline: sample brief, final tier, S3 upload"
	@echo "  make dry-run      Validate inputs only — zero cost, zero AWS calls"
	@echo "  make run-demo     Run all 4 regional demo briefs (24 images)"
	@echo "  make deliverables Show all exercise deliverables with links"
	@echo "  make test         Unit tests (no AWS required)"
	@echo "  make test-all     All tests including live AWS integration"
	@echo "  make lint         ruff check"
	@echo "  make audit        pip-audit security scan"
	@echo ""
