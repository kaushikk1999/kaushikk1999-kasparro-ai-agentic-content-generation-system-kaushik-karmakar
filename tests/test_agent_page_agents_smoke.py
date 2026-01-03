import pytest
from src.state.pipeline_state import PipelineState, CategorizedQuestions
from src.agents.parse_product import ParseProductAgent
from src.agents.generate_product_b import ProductBGeneratorAgent
from src.agents.generate_questions import GenerateQuestionsAgent
from src.agents.build_faq_page import FaqPageAgent
from src.agents.build_product_page import ProductPageAgent
from src.agents.build_comparison_page import ComparisonPageAgent

@pytest.fixture
def full_state(valid_raw_data):
    # Setup state with all deps
    product = ParseProductAgent().run(valid_raw_data)
    state = PipelineState(product=product)
    state = GenerateQuestionsAgent().run(state)
    state = ProductBGeneratorAgent().run(state)
    return state

def test_faq_page_agent(full_state):
    agent = FaqPageAgent()
    new_state = agent.run(full_state)
    assert new_state.faq_draft is not None
    assert "meta" in new_state.faq_draft
    assert "question_bank" in new_state.faq_draft
    assert "faqs" in new_state.faq_draft
    assert len(new_state.faq_draft["faqs"]) >= 5

def test_product_page_agent(full_state):
    agent = ProductPageAgent()
    new_state = agent.run(full_state)
    assert new_state.product_page_draft is not None
    assert "meta" in new_state.product_page_draft
    assert "hero" in new_state.product_page_draft
    # Check a field inside hero
    assert "title" in new_state.product_page_draft["hero"]

def test_comparison_page_agent(full_state):
    agent = ComparisonPageAgent()
    new_state = agent.run(full_state)
    assert new_state.comparison_draft is not None
    assert "meta" in new_state.comparison_draft
    assert "comparison" in new_state.comparison_draft
    assert "product_a" in new_state.comparison_draft
    assert "product_b" in new_state.comparison_draft
    assert len(new_state.comparison_draft["comparison"]) >= 4
