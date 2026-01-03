from typing import Set, List, Any

class FactGuard:
    """
    Deterministic validator to ensure generated outputs only contain 
    facts present in the source dataset.
    """
    
    def __init__(self, product_data):
        self.product = product_data
        self.allowed_ingredients = set(product_data.key_ingredients)
        self.allowed_benefits = set(product_data.benefits)
        # Note: Usage/Safety checks can be exact string matches or containment
        self.usage_text = product_data.how_to_use
        self.safety_text = product_data.side_effects
        self.price = product_data.price_inr
    
    def check_subset(self, items: List[str], allowed: Set[str], context: str):
        """Ensures all items in the list are in the allowed set."""
        for item in items:
            if item not in allowed:
                raise ValueError(f"FactGuard Failure [{context}]: '{item}' is not a known fact. Allowed: {sorted(list(allowed))}")

    def check_exact(self, value: Any, expected: Any, context: str):
        if value != expected:
            raise ValueError(f"FactGuard Failure [{context}]: Value '{value}' does not match expected '{expected}'")

    def validate_product_page(self, data: dict):
        # 1. Details - Ingredients
        if "details" in data and "ingredients" in data["details"]:
            self.check_subset(data["details"]["ingredients"], self.allowed_ingredients, "ProductPage.ingredients")
            
        # 2. Details - Benefits
        if "details" in data and "benefits" in data["details"]:
            self.check_subset(data["details"]["benefits"], self.allowed_benefits, "ProductPage.benefits")
            
        # 3. Pricing
        if "pricing" in data and "amount" in data["pricing"]:
            self.check_exact(data["pricing"]["amount"], self.price, "ProductPage.price")

    def validate_comparison_page(self, data: dict):
        # Scan comparison rows
        if "comparison" in data:
            for row in data["comparison"]:
                attr = row.get("attribute")
                val_a = row.get("product_a_value")
                
                if attr == "Key Ingredients" and isinstance(val_a, list):
                    self.check_subset(val_a, self.allowed_ingredients, "Comparison.ingredients")
                elif attr == "Benefits" and isinstance(val_a, list):
                    self.check_subset(val_a, self.allowed_benefits, "Comparison.benefits")
                elif attr == "Price (INR)":
                    self.check_exact(val_a, self.price, "Comparison.price")

    def validate_faq_page(self, data: dict):
        # 3. FAQ Validation
        # Check that answers don't hallucinate facts or prices
        if "faqs" in data:
            allowed_price = str(self.price)
            
            for item in data["faqs"]:
                ans = item.get("answer", "")
                
                # Simple boolean checks if specific tokens appear
                # 1. No Placeholders
                if "placeholder" in ans.lower():
                    raise ValueError("FactGuard Failure [FAQ]: Generated placeholder found in answer.")

                # 2. Strict Price Check
                if "₹" in ans and allowed_price not in ans:
                     raise ValueError(f"FactGuard Failure [FAQ]: Price mismatch. Answer mentions ₹ but not {allowed_price}")

                # 3. Ingredient Leakage
                if "Key ingredients:" in ans:
                    # Parse out the list part: "Key ingredients: A, B" -> ["A", "B"]
                    try:
                        content = ans.split("Key ingredients:")[1]
                        parts = [x.strip() for x in content.split(",") if x.strip()]
                        # Check if all parts are in allowed ingredients
                        for p in parts:
                            if p not in self.allowed_ingredients:
                                 raise ValueError(f"FactGuard Failure [FAQ]: Ingredient '{p}' not in dataset.")
                    except IndexError:
                        pass # Valid answer format might differ slightly, but split should work if phrase present

                # 4. Benefit Leakage
                if "Benefits:" in ans:
                    try:
                        content = ans.split("Benefits:")[1]
                        parts = [x.strip() for x in content.split(",") if x.strip()]
                        for p in parts:
                            if p not in self.allowed_benefits:
                                 raise ValueError(f"FactGuard Failure [FAQ]: Benefit '{p}' not in dataset.")
                    except IndexError:
                        pass

                # 5. Concentration Check
                if "%" in ans and self.product.concentration not in ans:
                     # Strict check: if a percentage is mentioned, it must be the product concentration
                     raise ValueError(f"FactGuard Failure [FAQ]: Answer mentions % but does not include dataset concentration '{self.product.concentration}'")
