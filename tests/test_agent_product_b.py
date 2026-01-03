from src.state.pipeline_state import PipelineState
from src.agents.generate_product_b import ProductBGeneratorAgent

def test_generate_product_b():
    agent = ProductBGeneratorAgent()
    state = PipelineState()
    new_state = agent.run(state)
    
    assert new_state.product_b is not None
    assert new_state.product_b.name == "Fictional Product B"
    assert len(new_state.product_b.key_ingredients) > 0
    assert new_state.product_b.price_inr > 0
