# BACKLOG — PAI Packaging Automation

Items explicitly deferred from the PoC scope. Prioritized for production evolution.

## Critical Priority — Image Quality, Accuracy & Consistency

Current PoC images are functional but clearly AI-generated — not production-ready. The strategies below are sourced from authoritative vendor documentation and peer-reviewed research, ranked by impact-to-effort ratio.

### Quick Wins (code changes only, no new infrastructure)

- **Add `style: "PHOTOREALISM"` to Nova Canvas API calls** — Nova Canvas has an explicit style preset enum. This single parameter addition directly improves photographic realism for product shots. *(Source: [Nova Canvas Request/Response Structure](https://docs.aws.amazon.com/nova/latest/userguide/image-gen-req-resp-structure.html))*

- **Color-guided generation with brand hex codes** — Nova Canvas supports passing 1-10 hex color values alongside prompts. Extract brand colors from the SKU brief's brand profile and pass via the color-guided generation API to enforce palette adherence across all images in a run. *(Source: [Generating Images with Amazon Nova Canvas](https://docs.aws.amazon.com/nova/latest/userguide/image-generation.html))*

- **Tune cfgScale from 8.5 to 7.0-7.5** — AWS documents 1.1-10.0 range, default 6.5. Our 8.5 is in the oversaturation zone — risks unnatural aesthetics. 7.0-8.0 is the sweet spot for product photography where prompt fidelity matters but natural lighting is needed. *(Source: [Nova Canvas Prompting Best Practices](https://docs.aws.amazon.com/nova/latest/userguide/prompting-image-generation.html))*

- **Restructure prompts as image captions, not commands** — Nova Canvas cannot reason or interpret instructions. "A professional studio photograph of a trail mix pouch on white marble" outperforms "Generate an image of a trail mix package." Order: subject → environment → positioning → lighting → camera → style. *(Source: [Nova Canvas Prompting Best Practices](https://docs.aws.amazon.com/nova/latest/userguide/prompting-image-generation.html))*

- **Remove negation words from ALL prompts (positive AND negative)** — Nova Canvas does not understand "no", "not", "without". Our negative prompt uses phrases like "no text" — the model reads "text" and generates it. Use bare nouns only in `negativeText`: `"text, words, letters"` not `"no text, no words"`. *(Source: [Nova Canvas Prompting Best Practices](https://docs.aws.amazon.com/nova/latest/userguide/prompting-image-generation.html))*

- **Add few-shot examples to prompt enhancement system prompt** — Anthropic recommends 3-5 diverse examples in `<example>` tags. Provide Claude with 2-3 (before, after) prompt pairs showing Nova Canvas's preferred caption style to steer refinement quality. *(Source: [Anthropic Multishot Prompting](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/multishot-prompting))*

- **Use fixed seed for prompt iteration, vary for final selection** — Fix `seed` when testing prompt refinements to isolate wording effects. Once prompts are tuned, generate variations with different seeds and pick the best. Range: 0-2,147,483,646. *(Source: [Nova Canvas Prompting Best Practices](https://docs.aws.amazon.com/nova/latest/userguide/prompting-image-generation.html))*

### Medium Effort (new pipeline steps)

- **Generate N candidates per image, Claude-as-judge selects best** — Use `numberOfImages: 3` per call, then send all candidates to Claude Sonnet 4.6 with multimodal evaluation against brand profile criteria. AWS published this exact reference architecture. Anthropic recommends using their crop tool for region-specific evaluation (product area, background, text zones). *(Sources: [AWS — Generate and Evaluate Images with Nova Canvas and Claude](https://aws.amazon.com/blogs/machine-learning/generate-and-evaluate-images-in-amazon-bedrock-with-amazon-nova-canvas-and-anthropic-claude-3-5-sonnet/), [Claude 4 Best Practices — Improved Vision](https://platform.claude.com/docs/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices))*

- **Automated negative prompt grounding (NPC method)** — After generating, caption the result to identify unwanted elements, then add them to the negative prompt and regenerate. Research shows this yields 54% improvement in compositional accuracy vs. static negative prompt lists. Academic finding: optimizing negative prompts yields more improvement than optimizing positive prompts. *(Sources: [NPC — Automated Negative Prompting, arXiv 2512.07702](https://arxiv.org/abs/2512.07702), [DPO-Diff, arXiv 2407.01606](https://arxiv.org/abs/2407.01606))*

- **Image conditioning for cross-regional layout consistency** — Generate one ideal packaging layout, then use it as a structural reference for all regional variants. Nova Canvas analyzes the reference to create a segmentation mask — output follows the layout while allowing creative freedom per region. Ensures the pouch is positioned identically across US/LATAM/APAC/EU. *(Source: [Generating Images with Amazon Nova Canvas](https://docs.aws.amazon.com/nova/latest/userguide/image-generation.html))*

- **Self-correction chain: generate → evaluate → refine → regenerate** — Anthropic identifies this as the most effective chaining pattern. Build prompt → Claude evaluates against Nova Canvas best practices → Claude outputs refined version → generate → Claude evaluates image against brand criteria → refine and regenerate if below threshold. *(Source: [Claude 4 Best Practices](https://platform.claude.com/docs/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices))*

- **Persistent brand kit JSON per SKU** — Inspired by Adobe GenStudio "Style Kits": bundle reference hex colors, composition descriptions, banned elements, photography direction, and example layouts into a persistent JSON file per brand. Feed as structured context to every generation call. *(Source: [Adobe Firefly for Enterprise](https://business.adobe.com/products/firefly-business.html))*

### Higher Effort (infrastructure or model changes)

- **Nova Canvas inpainting for text overlay regions** — Instead of Pillow alpha compositing (which creates flat text on a potentially 3D surface), use Nova Canvas's native inpainting API to blend text overlay regions naturally. Adobe Mockup uses a similar approach to auto-adjust art to product curves. *(Sources: [Nova Canvas Image Generation](https://docs.aws.amazon.com/nova/latest/userguide/image-generation.html), [Adobe MAX 2025](https://news.adobe.com/news/2025/10/adobe-max-2025-creative-cloud))*

- **Automated quality scoring with HPSv3 or ImageReward** — HPSv3 (2025) achieves 87% win rate vs. previous human preference metrics. ImageReward found distorted/duplicated objects are the #1 failure mode (21.14%). Implement automated scoring in the pipeline: generate → score → reject below threshold → regenerate. *(Sources: [HPSv3, arXiv 2508.03789](https://arxiv.org/abs/2508.03789), [ImageReward, arXiv 2304.05977](https://arxiv.org/abs/2304.05977))*

- **Custom model fine-tuning on approved brand imagery** — Adobe Foundry trains custom models on 10-20 brand reference images for on-brand generation. Nova Canvas supports fine-tuning via Bedrock. Even a small set of approved Alpine Harvest packaging photos would dramatically improve brand consistency. *(Sources: [Adobe Firefly Foundry](https://news.adobe.com/news/2025/10/adobe-max-2025-firefly-foundry), [AWS Bedrock Custom Models](https://docs.aws.amazon.com/bedrock/latest/userguide/custom-models.html))*

- **IP-Adapter + ControlNet patterns for style transfer** — ICAS (2025) combines adaptive style injection with structural conditioning for "superior style consistency and inference efficiency." While Nova Canvas doesn't expose these directly, the principle applies: combine image conditioning (structure) with color-guided generation (style) for maximum consistency. *(Source: [ICAS, arXiv 2504.13224](https://arxiv.org/abs/2504.13224))*

### Research Context

| Finding | Source | Implication |
|---------|--------|------------|
| Scaling the language model (prompt quality) improves alignment more than scaling the diffusion model | Google Imagen research | Investing in better prompts via Claude yields more improvement than switching image models |
| Average Firefly prompt length doubled in 2025 | Adobe Firefly Blog, Feb 2026 | Verbose narrative prompts consistently outperform short ones across all models |
| TIFA: models fail most on counting, spatial relations, multi-object composition | Hu et al., 2023 (arXiv 2303.11897) | Simplify: one subject per image, avoid counting in prompts, minimize spatial complexity |
| Negative prompt optimization > positive prompt optimization for diffusion models | DPO-Diff, 2024 (arXiv 2407.01606) | Invest more effort in negative prompt engineering than positive prompt wordsmithing |
| Soft-TIFA: decompose evaluation into atomic visual primitives | GenEval 2, 2025 (arXiv 2512.16853) | Evaluate color match, object presence, background, composition separately — not holistically |
| Prompt adaptation to model-preferred formats improves quality | arXiv 2502.11477, Feb 2025 | Claude should rewrite prompts into Nova Canvas's caption style, not generic image description |

---

## High Priority (Phase 2 — Production MVP)

- **PostgreSQL on RDS** — structured run history, approval tracking, audit trail; replaces flat JSON manifests in `outputs/runs/`
- **Regulatory compliance database** — real regulatory requirements by region/market (not synthesized placeholder text); integrate with existing compliance data feeds
- **stability.sd3-5-large-v1:0** — SD3.5 Large when us-east-1 availability confirmed; benchmark against Nova Canvas on TIFA and ImageReward metrics
- **Content moderation** — Amazon Rekognition `DetectModerationLabels` on every generated image before S3 storage; block non-compliant outputs
- **CloudTrail audit logging** — S3 and Bedrock API call audit trail for compliance requirements
- **Budget alarm email configurability** — parameterize `PaiBudgetAlarm` subscriber email via CloudFormation parameter instead of hard-coded value

## Medium Priority (Phase 3 — Quality and Scale)

- **Amazon QuickSight dashboard** — analytics on generated images: approval rates, average generation time, cost per SKU, model performance comparison
- **Multi-language localization** — text overlay support for Japanese (CJK), Spanish, French beyond English; requires font bundling and coordinate adjustments per language
- **A/B testing pipeline** — variant comparison framework for packaging decisions; generate N variants per SKU, surface top-K by automated scoring
- **Aspect ratio output validation** — automated check that generated image dimensions exactly match target (dev tier Titan V2 always produces 1024×1024; non-square ratios only correct with Nova Canvas final tier)

## Low Priority (Phase 4 — Production Operations)

- **Lambda + API Gateway** — serverless execution for production auto-scaling; current PoC requires local Python environment
- **Web dashboard UI** — non-technical marketing stakeholder interface for triggering runs, reviewing outputs, and approving packaging candidates
- **Brand asset library integration** — DAM (Digital Asset Management) connector to pull logos and brand guidelines directly into prompt construction
- **Real-time WebSocket progress** — live generation status for long-running batch jobs (24+ images)
- **Kubernetes/ECS deployment** — for multi-tenant, concurrent generation workloads beyond single-user PoC
