from src.pipeline.asset_manager import build_output_key


def test_output_key_structure():
    key = build_output_key("trail-mix", "us-west", "front_label", "original.png")
    assert key == "trail-mix/us-west/front_label/original.png"


def test_output_key_with_hyphens():
    key = build_output_key("organic-trail-mix-us", "us-west", "back_label", "dark-chocolate.png")
    parts = key.split("/")
    assert len(parts) == 4
    assert parts[0] == "organic-trail-mix-us"
    assert parts[2] == "back_label"


def test_output_key_wraparound():
    key = build_output_key("energy-drink-apac", "apac", "wraparound", "original-citrus.png")
    assert key == "energy-drink-apac/apac/wraparound/original-citrus.png"


def test_output_key_all_format_names():
    for fmt in ["front_label", "back_label", "wraparound"]:
        key = build_output_key("sku", "region", fmt, "product.png")
        assert fmt in key
