import json
from pathlib import Path

import jsonschema

SCHEMA_PATH = Path(__file__).parent.parent / "schemas" / "sku_brief_schema.json"


def parse_sku_brief(file_path: str) -> dict:
    """Load and validate SKU brief JSON. Raises jsonschema.ValidationError on invalid."""
    with open(file_path) as f:
        brief = json.load(f)
    validate_sku_brief(brief)
    return brief


def validate_sku_brief(brief: dict) -> bool:
    schema = json.loads(SCHEMA_PATH.read_text())
    jsonschema.validate(brief, schema)
    return True
