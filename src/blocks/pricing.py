from src.models.product import ProductData

def block_price(product: ProductData) -> dict:
    """Output: {'currency': 'INR', 'amount': product.price_inr}"""
    return {"currency": "INR", "amount": product.price_inr}
