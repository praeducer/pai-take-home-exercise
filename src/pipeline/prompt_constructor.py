from __future__ import annotations

_UNIVERSAL_NEGATIVE = (
    "text, words, letters, writing, numbers, labels with text, typography, "
    "watermarks, blurry, deformed, multiple packages, duplicate, clone, "
    "low quality, cartoon, illustration, CGI render, artificial, fake"
)


def _sanitize(value: str, max_len: int = 200) -> str:
    return value.replace("\n", " ").replace("\r", "").strip()[:max_len]


def _product_display(product: dict) -> str:
    name = _sanitize(product["name"])
    flavor = _sanitize(product.get("flavor", ""))
    return f"{name} — {flavor}" if flavor else name


def _build_front_label_prompt(brief: dict, product: dict, brand_profile: dict) -> str:
    """1:1 — Single package centered, front-facing hero shot, clean studio."""
    display = _product_display(product)
    packaging_type = _sanitize(brief.get("packaging_type", "product packaging"))
    attributes = ", ".join(_sanitize(a, 50) for a in brief.get("attributes", []))
    audience = _sanitize(brief.get("audience", ""))
    bg = _sanitize(brand_profile.get("background_description", "clean white studio background"))
    colors = _sanitize(brand_profile.get("color_palette", "neutral tones"))
    photo_style = _sanitize(brand_profile.get("photography_style", "professional studio lighting"))
    hero = _sanitize(brand_profile.get("packaging_hero_shot", "front-facing centered"))
    regional = _sanitize(brand_profile.get("regional_visual_elements", ""))

    return (
        f"Professional product packaging photograph of {display} in a {packaging_type}. "
        f"{hero}, single package only. "
        f"Color palette: {colors}. "
        f"Background: {bg}. "
        f"Photography style: {photo_style}. "
        f"Key product attributes: {attributes}. "
        f"Target audience: {audience}. "
        + (f"Visual elements: {regional}. " if regional else "")
        + "Square format, clean commercial product photography."
    )


def _build_back_label_prompt(brief: dict, product: dict, brand_profile: dict) -> str:
    """9:16 — 3/4 angle, ingredients/texture visible, portrait, lifestyle context."""
    display = _product_display(product)
    packaging_type = _sanitize(brief.get("packaging_type", "product packaging"))
    description = _sanitize(product.get("description", ""))
    region = _sanitize(brief.get("region", ""))
    bg = _sanitize(brand_profile.get("background_description", "natural lifestyle setting"))
    colors = _sanitize(brand_profile.get("color_palette", "natural tones"))
    photo_style = _sanitize(brand_profile.get("photography_style", "lifestyle product photography"))
    regional = _sanitize(brand_profile.get("regional_visual_elements", ""))

    return (
        f"Lifestyle product photography of {display} in a {packaging_type}, three-quarter angle view. "
        f"Product ingredients and texture visible around the package. "
        f"Portrait orientation. "
        f"{description}. "
        f"Region: {region}. "
        f"Color palette: {colors}. "
        f"Background: {bg}. "
        f"Photography style: {photo_style}. "
        + (f"Regional visual elements: {regional}. " if regional else "")
        + "Vertical format, aspirational lifestyle context."
    )


def _build_wraparound_prompt(brief: dict, product: dict, brand_profile: dict) -> str:
    """16:9 — Wide panoramic, ingredients scattered around package, brand story."""
    display = _product_display(product)
    packaging_type = _sanitize(brief.get("packaging_type", "product packaging"))
    description = _sanitize(product.get("description", ""))
    attributes = ", ".join(_sanitize(a, 50) for a in brief.get("attributes", []))
    audience = _sanitize(brief.get("audience", ""))
    bg = _sanitize(brand_profile.get("background_description", "textured natural surface"))
    colors = _sanitize(brand_profile.get("color_palette", "warm earth tones"))
    photo_style = _sanitize(brand_profile.get("photography_style", "editorial product photography"))
    regional = _sanitize(brand_profile.get("regional_visual_elements", ""))

    return (
        f"Wide panoramic brand story photograph featuring {display} in a {packaging_type}. "
        f"Package prominently placed, with product ingredients and natural elements artfully scattered around it. "
        f"Horizontal wide-angle composition. "
        f"{description}. "
        f"Brand story: {attributes}. "
        f"Target audience: {audience}. "
        f"Color palette: {colors}. "
        f"Background: {bg}. "
        f"Photography style: {photo_style}. "
        + (f"Regional visual motifs: {regional}. " if regional else "")
        + "Cinematic horizontal format, premium editorial quality."
    )


_FORMAT_BUILDERS = {
    "1:1": _build_front_label_prompt,
    "9:16": _build_back_label_prompt,
    "16:9": _build_wraparound_prompt,
}

_DEFAULT_BRAND_PROFILE: dict = {
    "photography_style": "clean studio product photography, professional lighting",
    "color_palette": "neutral earth tones, white background",
    "regional_visual_elements": "",
    "background_description": "clean white studio background, soft shadows",
    "packaging_hero_shot": "front-facing centered product shot",
    "negative_guidance": "",
}


def build_image_prompt(
    brief: dict,
    product: dict,
    aspect_ratio: str,
    brand_profile: dict | None = None,
) -> tuple[str, str]:
    """Build format-specific positive and negative image prompts.

    Returns (positive_prompt, negative_prompt) tuple.
    Dispatches to format-specific builder based on aspect_ratio.
    """
    profile = brand_profile or _DEFAULT_BRAND_PROFILE
    builder = _FORMAT_BUILDERS.get(aspect_ratio, _build_front_label_prompt)
    positive = builder(brief, product, profile)

    extra_negative = _sanitize(profile.get("negative_guidance", ""), 300)
    negative = _UNIVERSAL_NEGATIVE
    if extra_negative:
        negative = f"{negative}, {extra_negative}"

    return positive, negative


def build_text_overlay_content(brief: dict, product: dict) -> dict:
    """Return structured text content for Pillow overlay."""
    name = _sanitize(product["name"])
    flavor = _sanitize(product.get("flavor", ""))
    title = f"{name}\n{flavor}" if flavor else name
    attributes = brief.get("attributes", [])
    regulatory_text = "Contains: See ingredients list. For more information visit our website."
    return {
        "title": title,
        "attributes": [_sanitize(a, 50) for a in attributes[:4]],
        "regulatory_text": regulatory_text,
    }
