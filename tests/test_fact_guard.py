import pytest
from src.agents.parse_product import ParseProductAgent
from src.blocks.ingredients import block_key_ingredients
from src.blocks.benefits import block_benefits
from src.blocks.safety import block_safety

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

def test_fact_guard_ingredients(product):
    allowed = set(product.key_ingredients)
    output = set(block_key_ingredients(product))
    assert output <= allowed

def test_fact_guard_benefits(product):
    allowed = set(product.benefits)
    output = set(block_benefits(product))
    assert output <= allowed

def test_fact_guard_safety(product):
    # Safety block should contain EXACTLY the side effects text with Note prefix
    out = block_safety(product)
    assert out == f"Note: {product.side_effects}"
    assert out.replace("Note: ", "", 1) == product.side_effects
