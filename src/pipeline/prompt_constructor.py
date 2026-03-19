def _sanitize(value: str, max_len: int = 200) -> str:
    return value.replace("\n", " ").replace("\r", "").strip()[:max_len]


def build_image_prompt(brief: dict, product: dict, aspect_ratio: str) -> str:
    """Build Bedrock image generation prompt from SKU brief and product."""
    name = _sanitize(product["name"])
    flavor = _sanitize(product.get("flavor", ""))
    description = _sanitize(product["description"])
    attributes = ", ".join(_sanitize(a, 50) for a in brief.get("attributes", []))
    region = _sanitize(brief.get("region", ""))
    audience = _sanitize(brief.get("audience", ""))

    product_display = f"{name} — {flavor}" if flavor else name

    return (
        f"Professional product packaging label design for {product_display}. "
        f"{description}. "
        f"Key attributes: {attributes}. "
        f"Target market: {audience} in {region}. "
        f"Clean, modern packaging design with clear typography. "
        f"High quality commercial product photography style. "
        f"White or light background. Aspect ratio: {aspect_ratio}."
    )


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
