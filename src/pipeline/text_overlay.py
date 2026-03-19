import io

from PIL import Image, ImageDraw, ImageFont

LAYOUT_1_1 = {
    "title_y_pct": 0.05,
    "title_font_size": 48,
    "attrs_y_pct": 0.70,
    "attr_font_size": 28,
    "regulatory_y_pct": 0.90,
    "reg_font_size": 18,
}
LAYOUT_9_16 = {
    "title_y_pct": 0.05,
    "title_font_size": 44,
    "attrs_y_pct": 0.65,
    "attr_font_size": 26,
    "regulatory_y_pct": 0.90,
    "reg_font_size": 16,
}
LAYOUT_16_9 = {
    "title_y_pct": 0.05,
    "title_font_size": 40,
    "attrs_y_pct": 0.60,
    "attr_font_size": 24,
    "regulatory_y_pct": 0.88,
    "reg_font_size": 16,
}
LAYOUTS = {"1:1": LAYOUT_1_1, "9:16": LAYOUT_9_16, "16:9": LAYOUT_16_9}

# Font search paths — tries system fonts then falls back to Pillow default
_FONT_CANDIDATES = ["arial.ttf", "Arial.ttf", "DejaVuSans.ttf", "LiberationSans-Regular.ttf"]


def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for name in _FONT_CANDIDATES:
        try:
            return ImageFont.truetype(name, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def apply_overlay(image_bytes: bytes, content: dict, aspect_ratio: str = "1:1") -> bytes:
    """Apply text overlay to image. Returns PNG bytes."""
    img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    width, height = img.size

    overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)
    layout = LAYOUTS.get(aspect_ratio, LAYOUT_1_1)

    title_font = _load_font(layout["title_font_size"])
    attr_font = _load_font(layout["attr_font_size"])
    reg_font = _load_font(layout["reg_font_size"])

    # Title with semi-transparent background strip
    title_y = int(height * layout["title_y_pct"])
    title_strip_h = layout["title_font_size"] * 2 + 10
    draw.rectangle(
        [(0, title_y - 5), (width, title_y + title_strip_h)],
        fill=(0, 0, 0, 160),
    )
    draw.text(
        (width // 2, title_y + layout["title_font_size"] // 2),
        content.get("title", ""),
        fill=(255, 255, 255, 255),
        font=title_font,
        anchor="mm",
        align="center",
    )

    # Attribute tags
    attrs = content.get("attributes", [])
    attrs_y = int(height * layout["attrs_y_pct"])
    tag_x = 20
    char_w = max(layout["attr_font_size"] // 2, 1)
    for attr in attrs[:4]:
        tag_text = f"  {attr.upper()}  "
        tag_w = len(tag_text) * char_w
        draw.rectangle(
            [(tag_x - 5, attrs_y - 5), (tag_x + tag_w + 5, attrs_y + layout["attr_font_size"] + 5)],
            fill=(255, 255, 255, 200),
        )
        draw.text((tag_x, attrs_y), tag_text, fill=(0, 0, 0, 255), font=attr_font)
        tag_x += tag_w + 20
        if tag_x > width * 0.85:
            break

    # Regulatory text footer
    reg_y = int(height * layout["regulatory_y_pct"])
    reg_text = content.get("regulatory_text", "")
    draw.rectangle([(0, reg_y - 3), (width, height)], fill=(0, 0, 0, 180))
    draw.text(
        (width // 2, reg_y + layout["reg_font_size"] // 2),
        reg_text,
        fill=(255, 255, 255, 220),
        font=reg_font,
        anchor="mm",
    )

    composited = Image.alpha_composite(img, overlay).convert("RGB")
    output_buf = io.BytesIO()
    composited.save(output_buf, format="PNG")
    return output_buf.getvalue()
