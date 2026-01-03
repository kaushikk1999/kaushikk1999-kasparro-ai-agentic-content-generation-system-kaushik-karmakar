from src.state.pipeline_state import PipelineState
from src.models.product_b import ProductBData

class ProductBGeneratorAgent:
    def run(self, state: PipelineState) -> PipelineState:
        # Deterministic dummy data for Phase 3
        # In a real app, this might come from a DB or another source
        state.product_b = ProductBData(
            name="Fictional Product B",
            key_ingredients=["Water", "Glycerin", "Alcohol Denat"],
            benefits=["Hydration", "Cooling"],
            price_inr=1500
        )
        return state
