from src.pipeline.prompt_constructor import build_image_prompt, build_text_overlay_content


def test_prompt_contains_product_name(sample_brief, sample_product):
    prompt = build_image_prompt(sample_brief, sample_product, "1:1")
    assert "Test Product" in prompt
    assert len(prompt) > 50


def test_prompt_contains_attributes(sample_brief, sample_product):
    prompt = build_image_prompt(sample_brief, sample_product, "1:1")
    assert "organic" in prompt


def test_prompt_contains_region(sample_brief, sample_product):
    prompt = build_image_prompt(sample_brief, sample_product, "1:1")
    assert "us-west" in prompt


def test_prompt_contains_aspect_ratio(sample_brief, sample_product):
    prompt = build_image_prompt(sample_brief, sample_product, "9:16")
    assert "9:16" in prompt


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
    prompt = build_image_prompt(sample_brief, product, "1:1")
    assert "Plain Product" in prompt
