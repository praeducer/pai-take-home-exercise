import pytest


@pytest.fixture
def sample_brief():
    return {
        "sku_id": "test-product-001",
        "products": [
            {"name": "Test Product", "flavor": "Original", "description": "A test product description"},
            {"name": "Test Product", "flavor": "Vanilla", "description": "Vanilla variant description"},
        ],
        "region": "us-west",
        "audience": "test audience",
        "attributes": ["organic", "non-gmo", "test-attr"],
    }


@pytest.fixture
def sample_product(sample_brief):
    return sample_brief["products"][0]
