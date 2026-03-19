import json

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
    """Optionally enhance image prompt via Claude Sonnet 4.6. Falls back to base_prompt on error."""
    if dry_run:
        return base_prompt
    try:
        message = client.messages.create(
            model="anthropic.claude-sonnet-4-6",
            max_tokens=256,
            system=(
                "You are a packaging design expert. Improve the following image generation "
                "prompt for better visual quality. Return ONLY the improved prompt text, nothing else."
            ),
            messages=[{"role": "user", "content": base_prompt}],
        )
        enhanced = message.content[0].text.strip()
        return enhanced if enhanced else base_prompt
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


def generate_brand_profile(brief: dict, dry_run: bool = False) -> dict:
    """Generate brand-specific visual direction for all images in a pipeline run.

    Called once per brief (not per image). Returns a profile dict consumed by
    build_image_prompt() to ensure visual consistency across all 6 images.
    Falls back to _DEFAULT_BRAND_PROFILE on dry_run or any error.
    """
    if dry_run:
        return _DEFAULT_BRAND_PROFILE.copy()
    try:
        client = get_bedrock_client()
        brand_name = brief.get("brand_name", brief.get("sku_id", "the brand"))
        packaging_type = brief.get("packaging_type", "product packaging")
        cultural_context = brief.get("cultural_context", "")
        region = brief.get("region", "")
        audience = brief.get("audience", "")

        prompt_text = (
            f"Brand: {brand_name}\n"
            f"Packaging type: {packaging_type}\n"
            f"Region: {region}\n"
            f"Target audience: {audience}\n"
            f"Cultural context: {cultural_context}\n\n"
            "Return a JSON object with EXACTLY these keys (no extra keys, no markdown):\n"
            "- photography_style: camera and lighting style for product photography\n"
            "- color_palette: 2-4 specific colors that define the brand identity\n"
            "- regional_visual_elements: cultural/regional visual motifs to include\n"
            "- background_description: background setting for product shots\n"
            "- packaging_hero_shot: how the packaging should be positioned\n"
            "- negative_guidance: visual elements to avoid in ALL images"
        )

        message = client.messages.create(
            model="anthropic.claude-opus-4-6",
            max_tokens=512,
            system="You are a senior CPG brand designer specializing in packaging for global markets. Respond with valid JSON only.",
            messages=[{"role": "user", "content": prompt_text}],
        )
        raw = message.content[0].text.strip()
        # Strip markdown code fences if model adds them
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        profile = json.loads(raw)
        # Ensure all required keys present; fill missing from defaults
        for key in _DEFAULT_BRAND_PROFILE:
            if key not in profile:
                profile[key] = _DEFAULT_BRAND_PROFILE[key]
        return profile
    except Exception:
        return _DEFAULT_BRAND_PROFILE.copy()
