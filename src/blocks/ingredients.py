from typing import List
from src.models.product import ProductData

def block_key_ingredients(product: ProductData) -> List[str]:
    """Returns exactly product.key_ingredients."""
    return list(product.key_ingredients)
