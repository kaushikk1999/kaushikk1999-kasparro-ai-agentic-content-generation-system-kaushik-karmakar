import pytest
from src.state.pipeline_state import PipelineState, CategorizedQuestions
from src.agents.generate_questions import GenerateQuestionsAgent
from src.agents.parse_product import ParseProductAgent

@pytest.fixture
def populated_state(valid_raw_data):
    product = ParseProductAgent().run(valid_raw_data)
    return PipelineState(product=product)

def test_generate_questions_constraints_strict(populated_state):
    """
    Strict compliance check:
    - >= 15 questions
    - >= 5 categories
    - All questions unique
    - All questions non-empty strings
    """
    agent = GenerateQuestionsAgent()
    new_state = agent.run(populated_state)
    
    assert new_state.questions is not None
    items = new_state.questions.items
    
    # 1. Total >= 15
    assert len(items) >= 15, f"Expected >= 15 questions, got {len(items)}"
    
    # 2. Categories >= 5
    categories = {item["category"] for item in items}
    assert len(categories) >= 5, f"Expected >= 5 categories, got {len(categories)}: {categories}"
    
    # 3. Non-empty
    for idx, item in enumerate(items):
        q = item["question"]
        assert isinstance(q, str), f"Question at index {idx} is not a string"
        assert q.strip() != "", f"Question at index {idx} is empty"
        assert q == q.strip(), f"Question at index {idx} has leading/trailing whitespace"
        
    # 4. Unique
    unique_qs = {item["question"] for item in items}
    assert len(unique_qs) == len(items), "Found duplicate questions"

def test_generate_questions_determinism(populated_state):
    agent = GenerateQuestionsAgent()
    state1 = agent.run(populated_state)
    # Re-run on fresh state
    state2 = agent.run(populated_state)
    
    # Order and content must be identical
    assert state1.questions.items == state2.questions.items
