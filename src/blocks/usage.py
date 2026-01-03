from src.models.product import ProductData

def block_usage(product: ProductData) -> str:
    """Returns product.how_to_use."""
    return product.how_to_use
