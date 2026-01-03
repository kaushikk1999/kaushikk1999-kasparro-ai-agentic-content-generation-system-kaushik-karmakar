import json
import pytest
from src.agents.parse_product import ParseProductAgent
from src.models.product_b import ProductBData
from src.blocks.title import block_title
from src.blocks.ingredients import block_key_ingredients
from src.blocks.benefits import block_benefits
from src.blocks.usage import block_usage
from src.blocks.safety import block_safety
from src.blocks.pricing import block_price
from src.blocks.comparison import block_comparison_rows

@pytest.fixture
def product(valid_raw_data):
    # Reuse fixture logic or reload fresh
    raw = {
        "Product Name": "GlowBoost Vitamin C Serum",
        "Concentration": "10% Vitamin C",
        "Skin Type": "Oily, Combination",
        "Key Ingredients": "Vitamin C, Hyaluronic Acid",
        "Benefits": "Brightening, Fades dark spots",
        "How to Use": "Apply 2–3 drops in the morning before sunscreen",
        "Side Effects": "Mild tingling for sensitive skin",
        "Price": "₹699"
    }
    return ParseProductAgent().run(raw)

@pytest.fixture
def product_b():
    return ProductBData(
        name="Fictional Product B",
        key_ingredients=["X"],
        benefits=["Y"],
        price_inr=1
    )

def test_block_title(product):
    assert block_title(product) == "GlowBoost Vitamin C Serum"

def test_block_key_ingredients(product):
    assert block_key_ingredients(product) == ["Vitamin C", "Hyaluronic Acid"]

def test_block_benefits(product):
    assert block_benefits(product) == ["Brightening", "Fades dark spots"]

def test_block_usage(product):
    assert block_usage(product) == "Apply 2–3 drops in the morning before sunscreen"

def test_block_safety(product):
    assert "Mild tingling for sensitive skin" in block_safety(product)

def test_block_price(product):
    assert block_price(product) == {"currency": "INR", "amount": 699}

def test_block_comparison_rows(product, product_b):
    rows = block_comparison_rows(product, product_b)
    assert len(rows) >= 4
    # Check assertions for row structure?
    assert rows[0]["product_a_value"] == "GlowBoost Vitamin C Serum"
    assert rows[0]["product_b_value"] == "Fictional Product B"

from src.blocks.meta import block_product_b_meta

def test_block_product_b_meta(product_b):
    meta = block_product_b_meta(product_b)
    assert meta["product_b_fictional"] is True
    assert meta["product_b_name"] == "Fictional Product B"
