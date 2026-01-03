from src.models.product_b import ProductBData

def block_product_b_meta(product_b: ProductBData) -> dict:
    """
    Explicit fictional marker for Product B to be included in output metadata.
    """
    return {
        "product_b_fictional": True,
        "product_b_name": product_b.name
    }
