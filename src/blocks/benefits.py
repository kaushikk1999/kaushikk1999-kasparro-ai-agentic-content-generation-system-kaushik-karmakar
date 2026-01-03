from typing import List
from src.models.product import ProductData

def block_benefits(product: ProductData) -> List[str]:
    """Returns exactly product.benefits."""
    return list(product.benefits)
