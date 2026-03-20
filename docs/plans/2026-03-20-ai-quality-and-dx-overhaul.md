# AI Quality & Developer Experience Overhaul

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Upgrade AI component quality, fix skill/documentation accuracy, add single-command UX, fix APAC brief, eliminate garbled text in base images, then run full E2E pipeline and update all deliverables.

**Architecture:** Three-layer AI stack — Nova Canvas for images (primary, us-east-1 only), Claude Sonnet 4.6 for both brand profile + prompt enhancement (switching from Opus → same quality, faster, cheaper), Pillow for text compositing. Prompts rewritten as narrative prose for Nova Canvas. Tool use enforces JSON schema.

**Tech Stack:** Python 3.12, `anthropic[bedrock]` SDK, boto3, Nova Canvas v1:0, claude-sonnet-4-6, Pillow, pytest, ruff

---

## Model Decision Rationale (Post-Research)

### Image Generation: Nova Canvas is Correct
- Bedrock available image models in `us-east-1`: **only** `nova-canvas-v1:0` and `titan-image-generator-v2:0`
- Stability AI SD3.5 Large, Stable Image Ultra — `us-west-2` ONLY, incompatible with Claude Sonnet 4.6 requirement
- Nova Canvas: TIFA 0.897, ImageReward 1.250 — best available for us-east-1
- **No model change needed for image generation**

### Text Models: Opus → Sonnet 4.6
- Current code uses `anthropic.claude-opus-4-6` for brand profile (structured JSON, 6 fields)
- Sonnet 4.6 supports `strict: true` tool use, extended thinking, 1M context — equally capable for this task
- Cost: Opus = $5/$25 per MTok; Sonnet = $3/$15 per MTok → 40% input savings
- Bedrock IDs (authoritative, March 2026): `anthropic.claude-sonnet-4-6`, `anthropic.claude-opus-4-6-v1`
- **Switch brand profile to Sonnet 4.6**

### Prompt Caching: Not Available on Bedrock
- Anthropic docs (March 2026): "Amazon Bedrock & Google Vertex AI: Support coming later"
- **Do not implement** — would have zero effect on Bedrock calls

---

## Task 1: Fix Critical Accuracy Issues (Skills + Docs)

**Files:**
- Modify: `.claude/skills/generate-demo/SKILL.md`
- Modify: `.claude/skills/health-check/SKILL.md`
- Modify: `README.md`
- Modify: `CLAUDE.md`

**Step 1: Fix `generate-demo` skill — wrong brief names**

In `.claude/skills/generate-demo/SKILL.md`, the Demo Briefs table lists `granola-bar-latam.json`, `energy-drink-apac.json`, `protein-bar-eu.json` — these do not exist. Actual briefs are `trail-mix-us.json`, `trail-mix-latam.json`, `trail-mix-apac.json`, `trail-mix-eu.json`.

Replace the Demo Briefs table with:
```markdown
| File | Product | Region | Cultural direction |
|------|---------|--------|--------------------|
| `trail-mix-us.json` | Alpine Harvest Trail Mix (Original, Dark Chocolate) | us-west | Pacific NW earth tones, outdoor lifestyle |
| `trail-mix-latam.json` | Alpine Harvest Trail Mix (Original, Tropical Edition) | latam | Golden yellows, terracotta, tropical energy |
| `trail-mix-apac.json` | Alpine Harvest Trail Mix (Original, Mango Coconut) | apac | Vibrant tropical, warm oranges, natural ingredients |
| `trail-mix-eu.json` | Alpine Harvest Trail Mix (Original, Dark Berry) | eu | Scandinavian kraft, moss green, Nordic botanical |
```

Also update the step 3 bash loop to use correct brief names:
```bash
for brief in inputs/demo_briefs/trail-mix-us.json \
             inputs/demo_briefs/trail-mix-latam.json \
             inputs/demo_briefs/trail-mix-apac.json \
             inputs/demo_briefs/trail-mix-eu.json; do
```

**Step 2: Fix `health-check` skill — wrong expected output**

Update expected output section:
- Change "3 models listed" → "4 models listed (nova-canvas, titan-image, claude-sonnet-4-6, claude-opus-4-6-v1)"
- Change expected stack status to include `UPDATE_ROLLBACK_COMPLETE` as valid functional state

**Step 3: Fix README test count and model table**

In `README.md`:
- Repository Structure section says "35 unit tests" — change to "39 unit tests"
- Architecture diagram shows "Claude Sonnet 4.6 prompt enhancement" — update to show both roles:
  - `text_reasoning.py` — Claude Sonnet 4.6: brand profile (once/brief) + prompt enhancement (per image)
- Key Components table: update Text reasoning row to: `anthropic.claude-sonnet-4-6` | Brand profile + prompt enhancement

**Step 4: Fix CLAUDE.md model reference**

Architecture Decisions table says `anthropic.claude-sonnet-4-6` as text reasoning model. Update to note:
- Brand profile: `anthropic.claude-sonnet-4-6` (after Task 2 switch)
- Prompt enhancement: `anthropic.claude-sonnet-4-6`

**Step 5: Commit**
```bash
git add .claude/skills/ README.md CLAUDE.md
git commit -m "fix: correct skill brief names, health-check expectations, README test count and model table"
```

---

## Task 2: Fix APAC Brief (Matcha Green Tea → Mango Coconut)

**Files:**
- Modify: `inputs/demo_briefs/trail-mix-apac.json`

**Problem:** "Matcha Green Tea" flavor + "zen minimalism" + "Japanese tea ceremony" context generates images that look like tea products, not trail mix. Need a flavor that reads clearly as a trail mix variant but with APAC cultural resonance.

**Step 1: Update the APAC brief**

Replace the brief content with a Mango Coconut variant (tropical APAC, clearly a snack/trail mix):

```json
{
  "_meta": {
    "purpose": "Demo brief — Alpine Harvest Organic Trail Mix, APAC market. Tropical Southeast Asian aesthetic with mango coconut variant.",
    "data_origin": "Updated 2026-03-20: Changed from matcha green tea to mango coconut for clearer trail mix category signaling."
  },
  "sku_id": "alpine-harvest-trail-mix",
  "brand_name": "Alpine Harvest",
  "packaging_type": "stand-up resealable pouch",
  "cultural_context": "Southeast Asian tropical vibrancy. Warm golden-orange and deep green palette with mango, coconut palm, and tropical foliage motifs. Fresh, energetic, and natural. Communicates adventure snacking and natural tropical ingredients.",
  "products": [
    {
      "name": "Alpine Harvest Trail Mix",
      "flavor": "Original",
      "description": "Crisp macadamia nuts, cashews, dried pineapple, and toasted coconut flakes for tropical trail energy"
    },
    {
      "name": "Alpine Harvest Trail Mix",
      "flavor": "Mango Coconut",
      "description": "Sun-dried mango chunks, toasted coconut chips, macadamia nuts, and candied ginger — Southeast Asia in every handful"
    }
  ],
  "region": "apac",
  "audience": "active urban consumers 22-38 in Southeast Asia, Australia, and South Korea seeking natural adventure snacks",
  "attributes": ["organic", "non-gmo", "tropical-flavors", "no-preservatives"]
}
```

**Step 2: Schema validate**
```bash
python -c "
import json, jsonschema
s = json.load(open('src/schemas/sku_brief_schema.json'))
b = json.load(open('inputs/demo_briefs/trail-mix-apac.json'))
jsonschema.validate(b, s)
print('PASS')
"
```
Expected: `PASS`

**Step 3: Commit**
```bash
git add inputs/demo_briefs/trail-mix-apac.json
git commit -m "fix(briefs): replace APAC matcha-green-tea with mango-coconut — clearer trail mix category signal"
```

---

## Task 3: Tool Use + Model Switch for `generate_brand_profile`

**Files:**
- Modify: `src/pipeline/text_reasoning.py`
- Modify: `tests/test_text_reasoning.py`

**Why:** Current code asks Claude to "Return valid JSON only" then manually strips markdown fences — brittle. Using `tool_use` with `strict: true` guarantees the JSON schema is always honored. Simultaneously switching from `claude-opus-4-6` to `claude-sonnet-4-6` for brand profile (same capability for structured JSON tasks, 40% cheaper, faster).

**Step 1: Write the new test first (TDD)**

In `tests/test_text_reasoning.py`, add:

```python
def test_brand_profile_default_is_complete():
    """All 6 required keys must be present and non-empty in _DEFAULT_BRAND_PROFILE."""
    required = {
        "photography_style", "color_palette", "regional_visual_elements",
        "background_description", "packaging_hero_shot", "negative_guidance",
    }
    from src.pipeline.text_reasoning import _DEFAULT_BRAND_PROFILE
    assert required == set(_DEFAULT_BRAND_PROFILE.keys())
    # All values are strings
    assert all(isinstance(v, str) for v in _DEFAULT_BRAND_PROFILE.values())
```

Run: `pytest tests/test_text_reasoning.py -v`
Expected: 3 existing pass + 1 new pass = 4 passed

**Step 2: Rewrite `generate_brand_profile` to use tool_use**

Replace the function body (keep the `_DEFAULT_BRAND_PROFILE` constant and `get_bedrock_client()` unchanged).

The new `generate_brand_profile` implementation:

```python
_BRAND_PROFILE_TOOL = {
    "name": "set_brand_profile",
    "description": "Set the visual brand profile for CPG packaging generation across all regional variants.",
    "input_schema": {
        "type": "object",
        "properties": {
            "photography_style": {
                "type": "string",
                "description": "Camera angle, lighting style, and photographic treatment for product shots"
            },
            "color_palette": {
                "type": "string",
                "description": "2-4 specific colors defining the brand identity for this region"
            },
            "regional_visual_elements": {
                "type": "string",
                "description": "Cultural and regional visual motifs to include in imagery"
            },
            "background_description": {
                "type": "string",
                "description": "Background setting and environment for product shots"
            },
            "packaging_hero_shot": {
                "type": "string",
                "description": "How the packaging pouch should be positioned and oriented"
            },
            "negative_guidance": {
                "type": "string",
                "description": "Visual elements to avoid in all generated images"
            },
        },
        "required": [
            "photography_style", "color_palette", "regional_visual_elements",
            "background_description", "packaging_hero_shot", "negative_guidance",
        ],
    },
}


def generate_brand_profile(brief: dict, dry_run: bool = False) -> dict:
    """Generate brand-specific visual direction via tool use (guaranteed JSON schema).

    Called once per brief. Returns a profile dict consumed by build_image_prompt()
    for visual consistency across all 6 images per brief.
    Falls back to _DEFAULT_BRAND_PROFILE on dry_run or any error.
    """
    if dry_run:
        return _DEFAULT_BRAND_PROFILE.copy()
    try:
        client = get_bedrock_client()
        brand_name = brief.get("brand_name", brief.get("sku_id", "the brand"))
        prompt_text = (
            f"Brand: {brand_name}\n"
            f"Product type: {brief.get('packaging_type', 'stand-up pouch')}\n"
            f"Region: {brief.get('region', '')}\n"
            f"Audience: {brief.get('audience', '')}\n"
            f"Cultural context: {brief.get('cultural_context', '')}\n\n"
            "Define the visual brand profile for generating packaging photography."
        )
        message = client.messages.create(
            model="anthropic.claude-sonnet-4-6",
            max_tokens=300,
            system="You are a senior CPG brand designer specializing in packaging photography direction for global markets.",
            tools=[_BRAND_PROFILE_TOOL],
            tool_choice={"type": "tool", "name": "set_brand_profile"},
            messages=[{"role": "user", "content": prompt_text}],
        )
        # tool_choice forces exactly one tool_use block — extract input directly
        tool_block = next(b for b in message.content if b.type == "tool_use")
        profile = tool_block.input
        # Fill any missing keys from defaults (defensive)
        for key in _DEFAULT_BRAND_PROFILE:
            if key not in profile:
                profile[key] = _DEFAULT_BRAND_PROFILE[key]
        return profile
    except Exception:
        return _DEFAULT_BRAND_PROFILE.copy()
```

**Step 3: Run tests**
```bash
pytest tests/test_text_reasoning.py -v
```
Expected: 4 passed

**Step 4: Run full suite**
```bash
ruff check src/ tests/ && pytest tests/ -m "not integration" -q
```
Expected: All checks passed, 39 passed, 3 skipped

**Step 5: Commit**
```bash
git add src/pipeline/text_reasoning.py tests/test_text_reasoning.py
git commit -m "feat: tool use + sonnet-4-6 for brand profile — guaranteed JSON schema, 40% cost reduction vs opus"
```

---

## Task 4: Enhance `enhance_prompt_with_reasoning` — Focused Nova Canvas Guidance

**Files:**
- Modify: `src/pipeline/text_reasoning.py`

**Why:** Current system prompt is generic ("packaging design expert, improve for visual quality"). Nova Canvas responds best to prompts with specific photographic direction. The enhancement should be targeted at packaging photography for a trail mix product, not generic improvement.

Also: `max_tokens=256` can truncate longer prompts. Raise to 400.

**Step 1: Update the system prompt and max_tokens**

Replace the `enhance_prompt_with_reasoning` function:

```python
def enhance_prompt_with_reasoning(
    client: AnthropicBedrock,
    base_prompt: str,
    product: dict,
    dry_run: bool = False,
) -> str:
    """Refine image generation prompt for Nova Canvas photorealism. Falls back to base_prompt on error."""
    if dry_run:
        return base_prompt
    try:
        message = client.messages.create(
            model="anthropic.claude-sonnet-4-6",
            max_tokens=400,
            system=(
                "You are a Nova Canvas prompt engineer specializing in CPG product packaging photography. "
                "Refine the given prompt for photorealistic output: enhance lighting specificity, "
                "add depth-of-field direction, and strengthen the scene composition. "
                "Preserve all product names, brand colors, and cultural references exactly. "
                "Return ONLY the refined prompt text — no preamble, no explanation, no markdown."
            ),
            messages=[{"role": "user", "content": base_prompt}],
        )
        enhanced = message.content[0].text.strip()
        # Truncate to Nova Canvas 1024-char limit
        return enhanced[:1024] if enhanced else base_prompt
    except Exception:
        return base_prompt
```

**Step 2: Run tests**
```bash
pytest tests/ -m "not integration" -q
```
Expected: 39 passed, 3 skipped

**Step 3: Commit**
```bash
git add src/pipeline/text_reasoning.py
git commit -m "fix: targeted Nova Canvas prompt refinement system prompt, 400 max_tokens, 1024-char truncation guard"
```

---

## Task 5: Narrative Prompts + Stronger Negative Prompts + cfgScale

**Files:**
- Modify: `src/pipeline/prompt_constructor.py`
- Modify: `src/pipeline/image_generator.py`
- Modify: `tests/test_prompt_constructor.py`

**Why:**
1. Nova Canvas performs better with narrative scene descriptions than label-value pairs
2. Garbled text appears in base images — need stronger negative prompt targeting packaging text specifically
3. cfgScale 7.5 → 8.5 gives more prompt-adherent composition for controlled product photography

**Step 1: Write tests for new prompt characteristics**

Add to `tests/test_prompt_constructor.py`:

```python
def test_front_label_prompt_is_narrative(sample_brief, sample_product):
    """Prompt should read as a scene description, not a key-value list."""
    prompt, _ = build_image_prompt(sample_brief, sample_product, "1:1")
    # Narrative prompts avoid "Color palette:" style labels
    assert "Color palette:" not in prompt
    assert "Photography style:" not in prompt

def test_negative_prompt_blocks_packaging_text(sample_brief, sample_product):
    """Negative prompt must explicitly block generated packaging text."""
    _, neg = build_image_prompt(sample_brief, sample_product, "1:1")
    assert "printed text" in neg.lower() or "packaging text" in neg.lower()
```

Run: `pytest tests/test_prompt_constructor.py::test_front_label_prompt_is_narrative tests/test_prompt_constructor.py::test_negative_prompt_blocks_packaging_text -v`
Expected: **FAIL** (tests drive the implementation)

**Step 2: Rewrite prompt builders as narrative prose**

Replace the three `_build_*_prompt` functions and `_UNIVERSAL_NEGATIVE` in `prompt_constructor.py`:

```python
_UNIVERSAL_NEGATIVE = (
    "text, words, letters, writing, numbers, printed text, packaging text, "
    "product labels with text, typography, handwriting, captions, watermarks, "
    "blurry, deformed, multiple packages, duplicate, clone, "
    "low quality, cartoon, illustration, CGI render, artificial, fake, "
    "hands, people, cluttered background, busy scene"
)


def _build_front_label_prompt(brief: dict, product: dict, brand_profile: dict) -> str:
    """1:1 — Single package hero shot, clean studio, front-facing."""
    display = _product_display(product)
    pkg = _sanitize(brief.get("packaging_type", "stand-up resealable pouch"))
    attrs = ", ".join(_sanitize(a, 50) for a in brief.get("attributes", [])[:3])
    bg = _sanitize(brand_profile.get("background_description", "clean white studio background, soft diffused shadows"))
    colors = _sanitize(brand_profile.get("color_palette", "neutral earth tones"))
    photo_style = _sanitize(brand_profile.get("photography_style", "professional studio photography, soft box lighting"))
    hero = _sanitize(brand_profile.get("packaging_hero_shot", "front-facing centered, single package"))
    regional = _sanitize(brand_profile.get("regional_visual_elements", ""))

    scene = (
        f"{photo_style} of a {display} {pkg}, {hero}. "
        f"The packaging features {colors} with a {bg}. "
    )
    if attrs:
        scene += f"Product conveys {attrs}. "
    if regional:
        scene += f"Subtle {regional} visual accents. "
    scene += "Square format commercial product photography, no text or labels visible."
    return scene


def _build_back_label_prompt(brief: dict, product: dict, brand_profile: dict) -> str:
    """9:16 — Three-quarter angle, ingredients context, portrait lifestyle."""
    display = _product_display(product)
    pkg = _sanitize(brief.get("packaging_type", "stand-up resealable pouch"))
    desc = _sanitize(product.get("description", ""), 150)
    region = _sanitize(brief.get("region", ""))
    bg = _sanitize(brand_profile.get("background_description", "natural lifestyle surface"))
    colors = _sanitize(brand_profile.get("color_palette", "natural tones"))
    photo_style = _sanitize(brand_profile.get("photography_style", "lifestyle product photography"))
    regional = _sanitize(brand_profile.get("regional_visual_elements", ""))

    scene = (
        f"{photo_style} of a {display} {pkg} at a three-quarter angle. "
        f"{colors} color scheme. "
        f"Ingredients and natural elements softly scattered around the package on a {bg}. "
    )
    if desc:
        scene += f"Product character: {desc}. "
    if regional:
        scene += f"{regional} contextual elements in the background. "
    scene += f"Portrait format for {region} market, aspirational and clean, no text overlay."
    return scene


def _build_wraparound_prompt(brief: dict, product: dict, brand_profile: dict) -> str:
    """16:9 — Wide panoramic, brand story, ingredients tableau."""
    display = _product_display(product)
    pkg = _sanitize(brief.get("packaging_type", "stand-up resealable pouch"))
    desc = _sanitize(product.get("description", ""), 150)
    attrs = ", ".join(_sanitize(a, 50) for a in brief.get("attributes", [])[:3])
    bg = _sanitize(brand_profile.get("background_description", "textured natural wood surface"))
    colors = _sanitize(brand_profile.get("color_palette", "warm earth tones"))
    photo_style = _sanitize(brand_profile.get("photography_style", "editorial overhead photography"))
    regional = _sanitize(brand_profile.get("regional_visual_elements", ""))

    scene = (
        f"Wide cinematic {photo_style} of {display} {pkg} centered in frame. "
        f"Product ingredients artfully arranged around the package — nuts, dried fruits, natural elements. "
        f"{colors} palette, {bg}. "
    )
    if desc:
        scene += f"Brand story: {desc}. "
    if attrs:
        scene += f"Product values: {attrs}. "
    if regional:
        scene += f"{regional} visual motifs woven into composition. "
    scene += "Horizontal panoramic format, premium editorial quality, no visible text."
    return scene
```

**Step 3: Update cfgScale in `image_generator.py`**

Change `"cfgScale": 7.5` → `"cfgScale": 8.5` in the Nova Canvas body.

**Step 4: Run tests to verify**
```bash
pytest tests/test_prompt_constructor.py -v
```
Expected: All 13 tests pass (including the 2 new ones)

**Step 5: Run full suite**
```bash
ruff check src/ tests/ && pytest tests/ -m "not integration" -q
```
Expected: All checks passed, 39+ passed

**Step 6: Commit**
```bash
git add src/pipeline/prompt_constructor.py src/pipeline/image_generator.py tests/test_prompt_constructor.py
git commit -m "feat: narrative Nova Canvas prompts, stronger anti-text negative prompt, cfgScale 7.5→8.5"
```

---

## Task 6: Single-Command UX (Deploy, Run, Deliverables)

**Files:**
- Create: `Makefile` (already may exist — check first)
- Modify: `.claude/skills/run-pipeline/SKILL.md`
- Create: `.claude/skills/show-deliverables/SKILL.md`
- Modify: `CLAUDE.md`

**Step 1: Check if Makefile exists**
```bash
ls C:/dev/pai-take-home-exercise/Makefile 2>/dev/null || echo "not found"
```

**Step 2: Update/create Makefile with single commands**

Add/update these targets:

```makefile
# PAI Pipeline — Single-command operations
.PHONY: deploy run-demo dry-run deliverables test lint

# One-command deploy: validate + deploy CloudFormation stack
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
	@echo "=== Stack Outputs ==="
	aws cloudformation describe-stacks \
	  --stack-name pai-exercise \
	  --profile pai-exercise \
	  --query 'Stacks[0].Outputs' --output table

# One-command pipeline run (US West brief, final tier)
run:
	PAI_OUTPUT_BUCKET=$$(aws cloudformation describe-stacks \
	  --stack-name pai-exercise --profile pai-exercise \
	  --query 'Stacks[0].Outputs[?OutputKey==`OutputBucketName`].OutputValue' \
	  --output text) \
	python -m src.pipeline.run_pipeline inputs/sample_sku_brief.json \
	  --model-tier final --profile pai-exercise

# Zero-cost dry-run
dry-run:
	python -m src.pipeline.run_pipeline inputs/sample_sku_brief.json --dry-run

# Run all 4 demo briefs
run-demo:
	$(eval BUCKET := $(shell aws cloudformation describe-stacks \
	  --stack-name pai-exercise --profile pai-exercise \
	  --query 'Stacks[0].Outputs[?OutputKey==`OutputBucketName`].OutputValue' \
	  --output text))
	@for brief in inputs/demo_briefs/trail-mix-us.json \
	              inputs/demo_briefs/trail-mix-latam.json \
	              inputs/demo_briefs/trail-mix-apac.json \
	              inputs/demo_briefs/trail-mix-eu.json; do \
	  echo "=== $$brief ==="; \
	  PAI_OUTPUT_BUCKET=$(BUCKET) \
	  python -m src.pipeline.run_pipeline $$brief \
	    --model-tier final --profile pai-exercise; \
	done

# Show all deliverables
deliverables:
	@echo "========================================"
	@echo "PAI Packaging Automation PoC Deliverables"
	@echo "========================================"
	@echo ""
	@echo "GitHub Repository:"
	@echo "  https://github.com/praeducer/pai-take-home-exercise"
	@echo ""
	@echo "CI Status:"
	@echo "  https://github.com/praeducer/pai-take-home-exercise/actions/workflows/ci.yml"
	@echo ""
	@echo "Release Tags:"
	@echo "  v1.1.0: https://github.com/praeducer/pai-take-home-exercise/releases/tag/v1.1.0"
	@echo "  v1.0.0: https://github.com/praeducer/pai-take-home-exercise/releases/tag/v1.0.0"
	@echo ""
	@echo "Key Documents:"
	@echo "  README:              https://github.com/praeducer/pai-take-home-exercise#readme"
	@echo "  Solution Architecture: docs/solution-architecture.md"
	@echo "  UAT Walkthrough:     docs/uat-walkthrough.md"
	@echo "  Submission Email:    outputs/deliverables/submission-email.md"
	@echo ""
	@echo "Local Outputs:"
	@find outputs/results -name "*.png" | wc -l | xargs -I{} echo "  Generated images (local): {}"
	@find outputs/demo -name "*.png" | wc -l | xargs -I{} echo "  Demo images (committed):  {}"
	@aws s3 ls s3://$$(aws cloudformation describe-stacks \
	  --stack-name pai-exercise --profile pai-exercise \
	  --query 'Stacks[0].Outputs[?OutputKey==`OutputBucketName`].OutputValue' \
	  --output text)/ --recursive --profile pai-exercise 2>/dev/null \
	  | grep ".png" | wc -l | xargs -I{} echo "  S3 images:                {}"

# Development
test:
	python -m pytest tests/ -q -m "not integration"

lint:
	ruff check src/ tests/
```

**Step 3: Create `/show-deliverables` skill**

Create `.claude/skills/show-deliverables/SKILL.md`:

```markdown
---
name: show-deliverables
description: "Display all PAI exercise deliverables with verified links for the interview. Shows GitHub repo, CI status, S3 outputs, and local file counts."
argument-hint: ""
allowed-tools: Bash, Read
---

Show all deliverables for the PAI take-home exercise interview.

## Output

Run: `make deliverables`

Then display a structured summary covering each Adobe PAI exercise requirement:

| Exercise Requirement | Deliverable | Status |
|---------------------|------------|--------|
| SKU brief JSON input | `inputs/sample_sku_brief.json` + 4 demo briefs | ✅ |
| ≥2 products/flavors | Each brief has 2 products | ✅ |
| 3 aspect ratios | front_label (1:1), back_label (9:16), wraparound (16:9) | ✅ |
| S3 organized by SKU/Region/Format | `{sku_id}/{region}/{format}/{product}.png` | ✅ |
| CloudFormation IaC | `infra/cloudformation/stack.yaml` — deployed | ✅ |
| README | github.com/praeducer/pai-take-home-exercise | ✅ |
| CI/CD (bonus) | GitHub Actions ci.yml + deploy.yml | ✅ |
| Brand compliance (bonus) | Claude Opus/Sonnet brand profile per brief | ✅ |
| Approval logging (bonus) | JSON manifests in S3 + local outputs/runs/ | ✅ |
```

**Step 4: Commit**
```bash
git add Makefile .claude/skills/show-deliverables/
git commit -m "feat: Makefile single commands (deploy/run/dry-run/run-demo/deliverables) + show-deliverables skill"
```

---

## Task 7: Interview Demo Commands — PAI Exercise Coverage

**Files:**
- Modify: `.claude/skills/run-pipeline/SKILL.md` — add exercise requirement annotations
- Create: `.claude/skills/show-deliverables/SKILL.md` (done in Task 6)
- Review: `.claude/skills/generate-demo/SKILL.md` (fixed in Task 1)

The PAI exercise has these demo-able requirements. Each maps to an existing command:

| Exercise Requirement | Demo Command | What to Show |
|---------------------|-------------|-------------|
| Accept SKU brief JSON | `/run-pipeline inputs/sample_sku_brief.json --dry-run` | Schema validation, 6 items listed |
| Generate for 3 aspect ratios | Show `outputs/results/*/front_label`, `back_label`, `wraparound` | Physical dimension check |
| Store in S3 by SKU/Region/Format | `aws s3 ls s3://.../ --recursive` | Folder structure |
| Text/attributes/regulatory on designs | Open any PNG from `outputs/demo/` | Title strip, badge tags, footer |
| IaC deployment | `/deploy` or `make deploy` | CF stack output |
| CI/CD | GitHub Actions URL | Green checkmarks |
| Manifests/logging (bonus) | `/pipeline-status` | Recent runs table |
| Brand profile consistency (bonus) | `/run-pipeline` non-dry-run | Same visual language across 6 images |

**Step 1: Annotate `run-pipeline` skill with exercise mapping**

Add a section at the top of the Steps section:

```markdown
## Exercise Requirements Covered

This skill demonstrates:
- ✅ **SKU brief JSON input** — parses and validates `inputs/sample_sku_brief.json`
- ✅ **≥2 products/flavors** — processes all products in `brief.products[]`
- ✅ **3 aspect ratios** — front_label (1:1), back_label (9:16), wraparound (16:9)
- ✅ **Text/attributes on packaging** — product name, attribute badges, regulatory footer
- ✅ **S3 organized storage** — `{sku_id}/{region}/{format}/{product}.png`
- ✅ **Manifest logging** — JSON manifest written to S3 + `outputs/runs/`
```

**Step 2: Commit**
```bash
git add .claude/skills/run-pipeline/SKILL.md
git commit -m "docs: annotate run-pipeline skill with PAI exercise requirement coverage"
```

---

## Task 8: End-to-End Pipeline Run + Fresh Demo Images

**Steps:**

**Step 1: Push all previous commits, wait for CI green**
```bash
git push origin main
gh run watch --repo praeducer/pai-take-home-exercise <ci-run-id>
```

**Step 2: Run full demo — all 4 briefs, final tier**
```bash
make run-demo
```
Expected: 24 images, 4 manifests, ~$0.96 total cost

**Step 3: Copy best output images to outputs/demo/ for README**

For each region, copy the best front_label image to `outputs/demo/`:
```bash
# APAC now generates mango-coconut instead of matcha-green-tea
cp outputs/results/alpine-harvest-trail-mix/apac/front_label/mango-coconut.png \
   outputs/demo/alpine-harvest-trail-mix/apac/front_label/mango-coconut.png
# Remove old matcha image from demo
rm -f outputs/demo/alpine-harvest-trail-mix/apac/front_label/matcha-green-tea.png
```

**Step 4: Update README to reference new APAC image**

Replace the README embed:
```markdown
### Alpine Harvest APAC — Mango Coconut (1:1)
![Alpine Harvest APAC Front Label](outputs/demo/alpine-harvest-trail-mix/apac/front_label/mango-coconut.png)
```

**Step 5: Commit outputs + README**
```bash
git add outputs/demo/ outputs/results/ outputs/runs/ README.md
git commit -m "feat: fresh E2E pipeline run — narrative prompts, mango-coconut APAC, cfgScale 8.5, all 4 regions"
git push origin main
```

---

## Task 9: Update All Documentation and Claims

**Files:**
- Modify: `README.md`
- Modify: `docs/solution-architecture.md`
- Modify: `docs/uat-walkthrough.md`
- Modify: `CLAUDE.md`

**Step 1: Update README**
- Update architecture diagram to accurately show:
  - `text_reasoning.py` — Claude Sonnet 4.6 (brand profile via tool_use + prompt enhancement)
  - Image generation → Nova Canvas v1:0 (confirmed best in us-east-1)
  - Note: Stability AI models (SD3.5 Large, Stable Image Ultra) not available in us-east-1
- Fix "35 unit tests" → "39 unit tests"
- Update Design Decisions table to add tool_use and cfgScale entries

**Step 2: Update `docs/solution-architecture.md` AI claims**
- Section on text models: update to show Sonnet 4.6 for both tasks
- Add note on why Opus was replaced (same quality, 40% cheaper for structured JSON)
- Add note on Nova Canvas model selection rationale (Stability AI us-west-2 only)
- Add note on tool_use for guaranteed JSON schema

**Step 3: Update UAT walkthrough with new CI run URLs**
- Get fresh CI URL after E2E run
- Update all links and datestamp

**Step 4: Final CI green check**
```bash
gh run list --repo praeducer/pai-take-home-exercise --workflow ci.yml --limit 1 --json conclusion --jq '.[0].conclusion'
```
Expected: `"success"`

**Step 5: Tag v1.2.0**
```bash
git tag v1.2.0 -m "v1.2.0: AI quality overhaul — narrative prompts, tool-use JSON, Sonnet 4.6 brand profile, single-command UX"
git push origin v1.2.0
```

**Step 6: Commit docs + tag push**
```bash
git add README.md docs/ CLAUDE.md
git commit -m "docs: update all AI claims — Sonnet 4.6 brand profile, Nova Canvas rationale, tool_use, v1.2.0"
git push origin main
```

---

## Pass Criteria

After Task 9, ALL must be true:

- [ ] `ruff check src/ tests/` → exit 0
- [ ] `pytest tests/ -m "not integration"` → 41+ passed (39 existing + 2 new prompt tests)
- [ ] `generate-demo` skill lists correct brief files
- [ ] `generate_brand_profile` uses `tool_use` with `claude-sonnet-4-6`
- [ ] `enhance_prompt_with_reasoning` system prompt is Nova Canvas-specific
- [ ] `_UNIVERSAL_NEGATIVE` includes "printed text, packaging text"
- [ ] `cfgScale` = 8.5 in Nova Canvas calls
- [ ] APAC brief uses `mango-coconut` flavor, no matcha green tea
- [ ] `make deploy`, `make run`, `make dry-run`, `make deliverables` all work
- [ ] `show-deliverables` skill exists and lists all PAI exercise requirements
- [ ] README accurately describes Sonnet 4.6 for text reasoning (not Opus)
- [ ] Latest CI run = `success`
- [ ] v1.2.0 tag pushed

---

## Key Notes for Implementing Agent

1. **Prompt caching is NOT available on AWS Bedrock** — do not attempt to add `cache_control` headers to Bedrock calls
2. **Stability AI models are us-west-2 only** — Nova Canvas is the correct and only high-quality choice for us-east-1
3. **Opus is NOT used for image generation** — Opus was only used for text (brand profile JSON); now switching to Sonnet 4.6
4. **`tool_choice: {"type": "tool", "name": "set_brand_profile"}`** forces exactly one tool call — no need to iterate content blocks looking for tool_use type
5. **Makefile on Windows/Git Bash** — use `$(shell ...)` for subshell evaluation in recipes; test with `bash`
6. **APAC demo image path** — after regeneration, `matcha-green-tea.png` in `outputs/demo/apac/` must be replaced with `mango-coconut.png` and README updated accordingly
