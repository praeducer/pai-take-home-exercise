from src.pipeline.prompt_constructor import build_image_prompt, build_text_overlay_content


def test_prompt_contains_product_name(sample_brief, sample_product):
    prompt, neg = build_image_prompt(sample_brief, sample_product, "1:1")
    assert "Test Product" in prompt
    assert len(prompt) > 50


def test_prompt_contains_attributes(sample_brief, sample_product):
    prompt, neg = build_image_prompt(sample_brief, sample_product, "1:1")
    assert "organic" in prompt


def test_prompt_contains_region(sample_brief, sample_product):
    # region appears in the back-label (9:16) and wraparound (16:9) prompts
    prompt, neg = build_image_prompt(sample_brief, sample_product, "9:16")
    assert "us-west" in prompt


def test_prompt_contains_format_hint(sample_brief, sample_product):
    prompt, _ = build_image_prompt(sample_brief, sample_product, "9:16")
    # Back label (9:16) should mention portrait/vertical composition
    assert any(kw in prompt.lower() for kw in ["portrait", "vertical", "three-quarter", "lifestyle"])


def test_overlay_content_has_regulatory(sample_brief, sample_product):
    content = build_text_overlay_content(sample_brief, sample_product)
    assert "regulatory_text" in content
    assert len(content["regulatory_text"]) > 0


def test_overlay_content_max_four_attributes(sample_brief, sample_product):
    content = build_text_overlay_content(sample_brief, sample_product)
    assert len(content["attributes"]) <= 4


def test_overlay_content_title_includes_flavor(sample_brief, sample_product):
    content = build_text_overlay_content(sample_brief, sample_product)
    assert "Original" in content["title"]


def test_prompt_no_flavor_product(sample_brief):
    product = {"name": "Plain Product", "description": "A product without flavor"}
    prompt, neg = build_image_prompt(sample_brief, product, "1:1")
    assert "Plain Product" in prompt


def test_negative_prompt_contains_text(sample_brief, sample_product):
    _, neg = build_image_prompt(sample_brief, sample_product, "1:1")
    assert "text" in neg.lower()


def test_prompts_differ_by_format(sample_brief, sample_product):
    front_pos, _ = build_image_prompt(sample_brief, sample_product, "1:1")
    back_pos, _ = build_image_prompt(sample_brief, sample_product, "9:16")
    wrap_pos, _ = build_image_prompt(sample_brief, sample_product, "16:9")
    assert front_pos != back_pos
    assert back_pos != wrap_pos
    assert front_pos != wrap_pos


def test_brand_profile_incorporated_in_prompt(sample_brief, sample_product):
    profile = {
        "photography_style": "macro closeup",
        "color_palette": "electric blue",
        "regional_visual_elements": "",
        "background_description": "gradient studio",
        "packaging_hero_shot": "top-down",
        "negative_guidance": "",
    }
    pos, _ = build_image_prompt(sample_brief, sample_product, "1:1", brand_profile=profile)
    assert "macro closeup" in pos or "electric blue" in pos


def test_front_label_prompt_is_narrative(sample_brief, sample_product):
    """Prompt should be narrative prose, not key-value label pairs."""
    prompt, _ = build_image_prompt(sample_brief, sample_product, "1:1")
    assert "Color palette:" not in prompt
    assert "Photography style:" not in prompt
    assert "Background:" not in prompt


def test_negative_prompt_blocks_packaging_text(sample_brief, sample_product):
    """Negative prompt must explicitly block packaging text generation."""
    _, neg = build_image_prompt(sample_brief, sample_product, "1:1")
    assert "printed text" in neg.lower() or "packaging text" in neg.lower()
