import pytest
import json
import os

OUTPUT_PATH = "outputs/comparison_page.json"

def test_comparison_product_b_structure():
    """
    Step 1C: Hard test to ensure product_b is structured.
    """
    if not os.path.exists(OUTPUT_PATH):
        pytest.skip(f"Output file {OUTPUT_PATH} missing")

    with open(OUTPUT_PATH, 'r') as f:
        data = json.load(f)

    pb = data.get("product_b", {})
    
    # Assert keys exist
    assert "name" in pb, "product_b.name missing"
    assert "key_ingredients" in pb, "product_b.key_ingredients missing"
    assert "benefits" in pb, "product_b.benefits missing"
    assert "price" in pb, "product_b.price missing"

    # Assert types and values
    assert isinstance(pb["key_ingredients"], list), "key_ingredients must be a list"
    assert len(pb["key_ingredients"]) >= 1, "key_ingredients must not be empty"
    
    assert isinstance(pb["benefits"], list), "benefits must be a list"
    assert len(pb["benefits"]) >= 1, "benefits must not be empty"

    assert isinstance(pb["price"], dict), "price must be an object"
    assert pb["price"]["currency"] == "INR", "currency must be INR"
    assert isinstance(pb["price"]["amount"], int), "amount must be integer"

    # Assert Meta
    meta = data.get("meta", {})
    assert meta.get("product_b_fictional") is True, "product_b_fictional must be True"
