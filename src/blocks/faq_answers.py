from typing import Dict, Any

def build_faq_answer(product: Any, question_obj: Dict[str, str]) -> str:
    """
    Deterministically builds an FAQ answer based on product data.
    """
    cat = (question_obj.get("category") or "").lower()
    q = (question_obj.get("question") or "").lower()

    # 0. explicit rejections/fallbacks (None currently needed, relying on general fallback)

    # 1. Exact/Keyword Mapping to Dataset Fields
    if "usage" in cat or "how to use" in q or "apply" in q:
        return product.how_to_use
    
    if "safety" in cat or "side effect" in q or "tingl" in q:
        return product.side_effects
        
    if "ingredient" in cat or "ingredient" in q:
        return "Key ingredients: " + ", ".join(product.key_ingredients)
        
    if "benefit" in cat or "dark spot" in q or "bright" in q:
        return "Benefits: " + ", ".join(product.benefits)
        
    if "price" in cat or "purchase" in cat or "cost" in q:
        return f"Price: ₹{product.price_inr}"
        
    # 2. General Fallback (Dataset Only - Safe Compliance)
    return "This information is not provided in the product dataset."
