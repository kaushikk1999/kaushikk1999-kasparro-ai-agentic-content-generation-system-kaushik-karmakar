from src.state.pipeline_state import PipelineState
from src.templates.product_template import TEMPLATE
from src.blocks import BLOCKS

class ProductPageAgent:
    def run(self, state: PipelineState) -> PipelineState:
        if not state.product:
             raise ValueError("ProductData required for ProductPageAgent")
        
        # 1. Run all blocks to get raw values
        # We manually call blocks or use the template fields. 
        # Using template fields is safer if we want to respect the contract, 
        # but we need to map them to the new schema structure.
        
        # Helper: get value by field name from template execution
        raw_values = {}
        for field in TEMPLATE.fields:
             block_func = BLOCKS[field.block_id]
             raw_values[field.name] = block_func(state.product)
        
        # 2. Assemble Strict Schema Structure
        # Schema: meta, hero, details, usage, safety, pricing
        
        final_draft = {
            "meta": {"generated_by": "ProductPageAgent"},
            "hero": {
                "title": raw_values.get("title")
            },
            "details": {
                "ingredients": raw_values.get("ingredients"),
                "benefits": raw_values.get("benefits")
            },
            "usage": raw_values.get("usage"),
            "safety": raw_values.get("safety"),
            "pricing": raw_values.get("price")  # Schema calls it 'pricing', block/template calls it 'price'
        }

        state.product_page_draft = final_draft
        return state
