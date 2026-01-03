from typing import Dict, Any

def assemble_faq_page(draft: Dict[str, Any]) -> Dict[str, Any]:
    """
    Assembles the final FAQ page structure strictly matching the schema.
    Sanitizes inputs by selecting only allowed keys.
    """
    # Schema: title, ingredients, benefits, usage, safety, price, question_bank, faqs, meta
    return {
        "title": draft.get("title", ""),
        "ingredients": draft.get("ingredients", []),
        "benefits": draft.get("benefits", []),
        "usage": draft.get("usage", ""),
        "safety": draft.get("safety", ""),
        "price": draft.get("price", {"currency": "INR", "amount": 0}),
        "question_bank": draft.get("question_bank", []),
        "faqs": draft.get("faqs", []),
        "meta": draft.get("meta", {"generated_by": "FaqPageAgent"})
    }

def assemble_product_page(draft: Dict[str, Any]) -> Dict[str, Any]:
    """
    Assembles the final Product page structure strictly matching the schema.
    """
    # Schema: meta, hero, details, usage, safety, pricing
    return {
        "meta": draft.get("meta", {"generated_by": "ProductPageAgent"}),
        "hero": draft.get("hero", {"title": ""}),
        "details": draft.get("details", {"ingredients": [], "benefits": []}),
        "usage": draft.get("usage", ""),
        "safety": draft.get("safety", ""),
        "pricing": draft.get("pricing", {"currency": "INR", "amount": 0})
    }

def assemble_comparison_page(draft: Dict[str, Any]) -> Dict[str, Any]:
    """
    Assembles the final Comparison page structure strictly matching the schema.
    """
    # Schema: meta, comparison, product_a, product_b
    return {
        "meta": draft.get("meta", {
            "product_b_fictional": True, # Enforce this
            "product_b_name": "Fictional Product B"
        }),
        "comparison": draft.get("comparison", []),
        "product_a": draft.get("product_a", {"name": ""}),
        "product_b": draft.get("product_b", {
            "name": "", 
            "key_ingredients": [], 
            "benefits": [], 
            "price": {"currency": "INR", "amount": 0}
        })
    }
