from src.state.pipeline_state import PipelineState
from src.templates.comparison_template import TEMPLATE
from src.blocks import BLOCKS

class ComparisonPageAgent:
    def run(self, state: PipelineState) -> PipelineState:
        if not state.product or not state.product_b:
             raise ValueError("ProductData and ProductBData required for ComparisonPageAgent")
        
        draft = {}
        for field in TEMPLATE.fields:
             block_func = BLOCKS[field.block_id]
             
             if field.name == "meta":
                 # Special case: meta block takes product_b
                 draft[field.name] = block_func(state.product_b)
             elif field.name == "comparison":
                 # Comparison block takes (product, product_b)
                 draft[field.name] = block_func(state.product, state.product_b)
             else:
                 # Default fallback (unlikely for this specific template but safe)
                 try:
                    draft[field.name] = block_func(state.product)
                 except TypeError:
                    pass
        
        # Add basic structured data (Phase 1 schema might require product_a/product_b objects too?)
        # Schema stub: {meta, product_a, product_b, comparison}
        # The block only generates 'comparison' (rows) and 'meta' (from product_b)
        
        # We need to fill product_a and product_b summaries for the schema
        draft["product_a"] = {"name": state.product.product_name}
        draft["product_b"] = {
            "name": state.product_b.name,
            "key_ingredients": state.product_b.key_ingredients,
            "benefits": state.product_b.benefits,
            "price": {"currency": "INR", "amount": state.product_b.price_inr}
        }
        
        state.comparison_draft = draft
        return state
