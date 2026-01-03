import json
import pytest
from pydantic import ValidationError
from src.agents.parse_product import ParseProductAgent
from src.models.product import RawProductInput, ProductData



def test_parse_valid_product(valid_raw_data):
    agent = ParseProductAgent()
    product = agent.run(valid_raw_data)
    
    assert isinstance(product, ProductData)
    assert product.product_name == "GlowBoost Vitamin C Serum"
    class_skin_type = product.skin_type
    assert "Oily" in class_skin_type
    assert "Combination" in class_skin_type
    assert product.price_inr == 699
    assert product.concentration == "10% Vitamin C"

def test_lists_split_correctly(valid_raw_data):
    agent = ParseProductAgent()
    product = agent.run(valid_raw_data)
    
    assert product.skin_type == ["Oily", "Combination"]
    assert product.key_ingredients == ["Vitamin C", "Hyaluronic Acid"]
    assert product.benefits == ["Brightening", "Fades dark spots"]

def test_lists_strip_whitespace(valid_raw_data):
    valid_raw_data["Skin Type"] = "  Oily ,  Combination  "
    valid_raw_data["Key Ingredients"] = " Vitamin C ,  Hyaluronic Acid "
    valid_raw_data["Benefits"] = " Brightening ,  Fades dark spots  "

    agent = ParseProductAgent()
    product = agent.run(valid_raw_data)

    assert product.skin_type == ["Oily", "Combination"]
    assert product.key_ingredients == ["Vitamin C", "Hyaluronic Acid"]
    assert product.benefits == ["Brightening", "Fades dark spots"]

def test_price_parsed(valid_raw_data):
    agent = ParseProductAgent()
    product = agent.run(valid_raw_data)
    assert product.price_inr == 699

def test_reject_extra_keys(valid_raw_data):
    agent = ParseProductAgent()
    bad = dict(valid_raw_data)
    bad["Extra"] = "nope"
    
    with pytest.raises(ValidationError):
        agent.run(bad)

def test_round_trip_stability(valid_raw_data):
    agent = ParseProductAgent()
    product = agent.run(valid_raw_data)
    
    # Dump to dict
    product_dict = product.model_dump()
    
    # Validate against internal model (ProductData), not RawInput
    # This just ensures the output is a valid ProductData
    restored_product = ProductData(**product_dict)
    assert product == restored_product
