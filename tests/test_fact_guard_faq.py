import pytest
from src.validators.fact_guard import FactGuard
from src.models.product import ProductData

@pytest.fixture
def product():
    return ProductData(
        product_name="Glow",
        concentration="10%",
        key_ingredients=["A", "B"],
        benefits=["X", "Y"],
        skin_type=["All"],
        how_to_use="Use it",
        side_effects="None",
        price_inr=100
    )

def test_faq_valid(product):
    guard = FactGuard(product)
    valid_data = {
        "faqs": [
            {"answer": "Key ingredients: A, B"},
            {"answer": "Price: ₹100"}
        ]
    }
    # Should not raise
    guard.validate_faq_page(valid_data)

def test_faq_placeholder_fail(product):
    guard = FactGuard(product)
    bad_data = {"faqs": [{"answer": "This is a Generated answer placeholder."}]}
    with pytest.raises(ValueError, match="placeholder"):
        guard.validate_faq_page(bad_data)

def test_faq_ingredient_fail(product):
    guard = FactGuard(product)
    bad_data = {"faqs": [{"answer": "Key ingredients: A, Z"}]} # Z is not allowed
    with pytest.raises(ValueError, match="Ingredient 'Z' not in dataset"):
        guard.validate_faq_page(bad_data)

def test_faq_price_fail(product):
    guard = FactGuard(product)
    bad_data = {"faqs": [{"answer": "Price: ₹999"}]} # 100 is expected
    with pytest.raises(ValueError, match="Price mismatch"):
        guard.validate_faq_page(bad_data)
