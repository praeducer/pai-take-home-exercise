import json

import jsonschema
import pytest

from src.pipeline.sku_parser import parse_sku_brief, validate_sku_brief


def test_valid_brief(sample_brief, tmp_path):
    brief_file = tmp_path / "brief.json"
    brief_file.write_text(json.dumps(sample_brief))
    result = parse_sku_brief(str(brief_file))
    assert result["sku_id"] == "test-product-001"
    assert len(result["products"]) == 2


def test_invalid_brief_missing_sku_id(tmp_path):
    invalid = {
        "products": [
            {"name": "x", "description": "y"},
            {"name": "z", "description": "w"},
        ],
        "region": "us",
        "audience": "a",
        "attributes": [],
    }
    brief_file = tmp_path / "invalid.json"
    brief_file.write_text(json.dumps(invalid))
    with pytest.raises(jsonschema.ValidationError):
        parse_sku_brief(str(brief_file))


def test_brief_requires_two_products(tmp_path):
    one_product = {
        "sku_id": "x",
        "products": [{"name": "a", "description": "b"}],
        "region": "r",
        "audience": "a",
        "attributes": [],
    }
    brief_file = tmp_path / "one_product.json"
    brief_file.write_text(json.dumps(one_product))
    with pytest.raises(jsonschema.ValidationError):
        parse_sku_brief(str(brief_file))


def test_validate_returns_true(sample_brief):
    assert validate_sku_brief(sample_brief) is True
