from typing import List, Any, TypedDict
from src.models.product import ProductData
from src.models.product_b import ProductBData

class ComparisonRow(TypedDict):
    attribute: str
    product_a_value: Any
    product_b_value: Any

def block_comparison_rows(a: ProductData, b: ProductBData) -> List[ComparisonRow]:
    """Field-by-field rows (minimum set)."""
    return [
        {
            "attribute": "Name",
            "product_a_value": a.product_name,
            "product_b_value": b.name
        },
        {
            "attribute": "Key Ingredients",
            "product_a_value": a.key_ingredients,
            "product_b_value": b.key_ingredients
        },
        {
            "attribute": "Benefits",
            "product_a_value": a.benefits,
            "product_b_value": b.benefits
        },
        {
            "attribute": "Price (INR)",
            "product_a_value": a.price_inr,
            "product_b_value": b.price_inr
        }
    ]
