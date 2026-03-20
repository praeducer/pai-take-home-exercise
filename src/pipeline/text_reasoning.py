from anthropic import AnthropicBedrock


def get_bedrock_client() -> AnthropicBedrock:
    """Return AnthropicBedrock client. aws_region must be explicit — does not read ~/.aws/config."""
    return AnthropicBedrock(
        aws_region="us-east-1"
        # Uses same credential chain as boto3: env vars, ~/.aws/credentials, instance profile
    )


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
        return enhanced[:1024] if enhanced else base_prompt
    except Exception:
        return base_prompt  # Always fall back — text reasoning is enhancement, not critical path


_DEFAULT_BRAND_PROFILE = {
    "photography_style": "clean studio product photography, professional lighting",
    "color_palette": "neutral earth tones, white background",
    "regional_visual_elements": "",
    "background_description": "clean white studio background, soft shadows",
    "packaging_hero_shot": "front-facing centered product shot",
    "negative_guidance": "",
}

_BRAND_PROFILE_TOOL = {
    "name": "set_brand_profile",
    "description": "Set the visual brand profile for CPG packaging photography across all regional variants.",
    "input_schema": {
        "type": "object",
        "properties": {
            "photography_style": {
                "type": "string",
                "description": "Camera angle, lighting style, and photographic treatment for product shots",
            },
            "color_palette": {
                "type": "string",
                "description": "2-4 specific colors defining the brand identity for this region",
            },
            "regional_visual_elements": {
                "type": "string",
                "description": "Cultural and regional visual motifs to include in imagery",
            },
            "background_description": {
                "type": "string",
                "description": "Background setting and environment for product shots",
            },
            "packaging_hero_shot": {
                "type": "string",
                "description": "How the packaging pouch should be positioned and oriented",
            },
            "negative_guidance": {
                "type": "string",
                "description": "Visual elements to avoid in all generated images",
            },
        },
        "required": [
            "photography_style",
            "color_palette",
            "regional_visual_elements",
            "background_description",
            "packaging_hero_shot",
            "negative_guidance",
        ],
    },
}


def generate_brand_profile(brief: dict, dry_run: bool = False) -> dict:
    """Generate brand-specific visual direction via tool use (guaranteed JSON schema).

    Called once per brief (not per image). Returns a profile dict consumed by
    build_image_prompt() for visual consistency across all 6 images.
    Uses claude-sonnet-4-6 with tool_use to guarantee schema conformance.
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
        profile = dict(tool_block.input)
        # Fill any missing keys from defaults (defensive)
        for key in _DEFAULT_BRAND_PROFILE:
            if key not in profile:
                profile[key] = _DEFAULT_BRAND_PROFILE[key]
        return profile
    except Exception:
        return _DEFAULT_BRAND_PROFILE.copy()
