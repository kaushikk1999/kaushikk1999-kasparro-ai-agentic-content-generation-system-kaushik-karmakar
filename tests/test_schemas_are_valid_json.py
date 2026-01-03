import json
import pytest
from jsonschema.validators import Draft202012Validator

SCHEMA_FILES = [
    "src/schemas/faq_schema.json",
    "src/schemas/product_page_schema.json",
    "src/schemas/comparison_page_schema.json",
]

@pytest.mark.parametrize("schema_path", SCHEMA_FILES)
def test_schema_validity(schema_path):
    # 1. Valid JSON?
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)
    
    # 2. Valid JSON Schema?
    Draft202012Validator.check_schema(schema)
