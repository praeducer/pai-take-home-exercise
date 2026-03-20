from __future__ import annotations

from src.pipeline.text_reasoning import _DEFAULT_BRAND_PROFILE

_UNIVERSAL_NEGATIVE = (
    "text, words, letters, writing, numbers, printed text, packaging text, "
    "product labels with text, typography, handwriting, captions, watermarks, "
    "blurry, deformed, multiple packages, duplicate, clone, "
    "low quality, cartoon, illustration, CGI render, artificial, fake, "
    "hands, people, cluttered background, busy scene"
)


def _sanitize(value: str, max_len: int = 200) -> str:
    return value.replace("\n", " ").replace("\r", "").strip()[:max_len]


def _product_display(product: dict) -> str:
    name = _sanitize(product["name"])
    flavor = _sanitize(product.get("flavor", ""))
    return f"{name} — {flavor}" if flavor else name


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


_FORMAT_BUILDERS = {
    "1:1": _build_front_label_prompt,
    "9:16": _build_back_label_prompt,
    "16:9": _build_wraparound_prompt,
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
