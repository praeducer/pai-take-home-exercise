# BACKLOG — PAI Packaging Automation

Items explicitly deferred from the PoC scope. Prioritized for production evolution.

## High Priority (Phase 2 — Production MVP)

- **PostgreSQL on RDS** — structured run history, approval tracking, audit trail; replaces flat JSON manifests in `outputs/runs/`
- **Regulatory compliance database** — real regulatory requirements by region/market (not synthesized placeholder text); integrate with existing compliance data feeds
- **stability.sd3-5-large-v1:0** — SD3.5 Large when us-east-1 availability confirmed; benchmark against Nova Canvas on TIFA and ImageReward metrics
- **Content moderation** — Amazon Rekognition `DetectModerationLabels` on every generated image before S3 storage; block non-compliant outputs
- **CloudTrail audit logging** — S3 and Bedrock API call audit trail for compliance requirements
- **Budget alarm email configurability** — parameterize `PaiBudgetAlarm` subscriber email via CloudFormation parameter instead of hard-coded value (AWS Budgets limitation: cannot update subscriber in-place via CF after initial creation)

## Medium Priority (Phase 3 — Quality and Scale)

- **Amazon QuickSight dashboard** — analytics on generated images: approval rates, average generation time, cost per SKU, model performance comparison
- **Multi-language localization** — text overlay support for Japanese (CJK), Spanish, French beyond English; requires font bundling and coordinate adjustments per language
- **Fine-tuned image models** — brand-specific style consistency trained on Adobe GenStudio brand assets; reduces post-generation editing time
- **A/B testing pipeline** — variant comparison framework for packaging decisions; generate N variants per SKU, surface top-K by automated scoring
- **Aspect ratio output validation** — automated check that generated image dimensions exactly match target (dev tier Titan V2 always produces 1024×1024; non-square ratios only correct with Nova Canvas final tier)

## Low Priority (Phase 4 — Production Operations)

- **Lambda + API Gateway** — serverless execution for production auto-scaling; current PoC requires local Python environment
- **Web dashboard UI** — non-technical marketing stakeholder interface for triggering runs, reviewing outputs, and approving packaging candidates
- **Brand asset library integration** — DAM (Digital Asset Management) connector to pull logos and brand guidelines directly into prompt construction
- **Real-time WebSocket progress** — live generation status for long-running batch jobs (24+ images)
- **Kubernetes/ECS deployment** — for multi-tenant, concurrent generation workloads beyond single-user PoC
