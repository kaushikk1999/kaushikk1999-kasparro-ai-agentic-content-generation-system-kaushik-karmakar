from src.models.product import ProductData

def block_title(product: ProductData) -> str:
    """Returns a title derived only from product.product_name."""
    return product.product_name
