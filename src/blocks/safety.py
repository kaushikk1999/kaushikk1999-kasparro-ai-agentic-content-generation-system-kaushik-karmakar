from src.models.product import ProductData

def block_safety(product: ProductData) -> str:
    """Must reference only product.side_effects."""
    return f"Note: {product.side_effects}"
