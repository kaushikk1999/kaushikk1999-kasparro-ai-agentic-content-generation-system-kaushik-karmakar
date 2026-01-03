import pytest
from src.blocks.faq_answers import build_faq_answer
from src.models.product import ProductData

@pytest.fixture
def mock_product():
    return ProductData(
        product_name="Test Serum",
        concentration="10%",
        key_ingredients=["Vit C", "Aqua"],
        benefits=["Glow", "Hydrate"],
        skin_type=["Oily"],
        how_to_use="Apply daily",
        side_effects="Mild tingling",
        price_inr=500
    )

def test_answer_usage(mock_product):
    q = {"category": "Usage", "question": "How to apply?"}
    ans = build_faq_answer(mock_product, q)
    assert ans == "Apply daily"

def test_answer_ingredients(mock_product):
    q = {"category": "Ingredients", "question": "What is inside?"}
    ans = build_faq_answer(mock_product, q)
    assert "Key ingredients: Vit C, Aqua" in ans

def test_answer_price(mock_product):
    q = {"category": "Price", "question": "Cost?"}
    ans = build_faq_answer(mock_product, q)
    assert "Price: ₹500" in ans

def test_fallback(mock_product):
    q = {"category": "Unknown", "question": "Is it magic?"}
    ans = build_faq_answer(mock_product, q)
    assert "This information is not provided in the product dataset." in ans

def test_answer_storage(mock_product):
    q = {"category": "Storage", "question": "How do I store this?"}
    ans = build_faq_answer(mock_product, q)
    assert ans == "This information is not provided in the product dataset."
    assert "cool, dry place" not in ans
