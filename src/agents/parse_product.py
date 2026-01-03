from src.models.product import RawProductInput, ProductData, split_csv, parse_price

class ParseProductAgent:
    def run(self, raw: dict) -> ProductData:
        # Validate raw dict with RawProductInput (reject unknown keys)
        raw_input = RawProductInput(**raw)

        # Normalize and map to ProductData
        return ProductData(
            product_name=raw_input.product_name,
            concentration=raw_input.concentration,
            skin_type=split_csv(raw_input.skin_type),
            key_ingredients=split_csv(raw_input.key_ingredients),
            benefits=split_csv(raw_input.benefits),
            how_to_use=raw_input.how_to_use,
            side_effects=raw_input.side_effects,
            price_inr=parse_price(raw_input.price)
        )
