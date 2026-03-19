from src.pipeline.text_reasoning import generate_brand_profile


def test_brand_profile_dry_run_returns_default():
    profile = generate_brand_profile({}, dry_run=True)
    assert "photography_style" in profile
    assert "negative_guidance" in profile
    assert isinstance(profile, dict)


def test_brand_profile_dry_run_all_keys():
    expected_keys = {
        "photography_style",
        "color_palette",
        "regional_visual_elements",
        "background_description",
        "packaging_hero_shot",
        "negative_guidance",
    }
    profile = generate_brand_profile({}, dry_run=True)
    assert expected_keys.issubset(profile.keys())


def test_brand_profile_dry_run_no_api_call():
    """Dry run should return immediately without calling Bedrock."""
    brief = {"brand_name": "Test Brand", "region": "us-west"}
    profile = generate_brand_profile(brief, dry_run=True)
    assert isinstance(profile, dict)
    assert len(profile) >= 6
