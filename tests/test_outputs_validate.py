import pytest
import json
import os
from src.state.pipeline_state import PipelineState
from src.agents.parse_product import ParseProductAgent
from src.agents.generate_questions import GenerateQuestionsAgent
from src.agents.generate_product_b import ProductBGeneratorAgent
from src.agents.build_faq_page import FaqPageAgent
from src.agents.build_product_page import ProductPageAgent
from src.agents.build_comparison_page import ComparisonPageAgent
from src.agents.write_json import JsonWriterAgent
from src.agents.validate_outputs import ValidatorAgent

@pytest.fixture
def run_pipeline(tmp_path):
    # Setup state
    raw = {
        "Product Name": "GlowBoost Vitamin C Serum",
        "Concentration": "10% Vitamin C",
        "Skin Type": "Oily, Combination",
        "Key Ingredients": "Vitamin C, Hyaluronic Acid",
        "Benefits": "Brightening, Fades dark spots",
        "How to Use": "Apply 2–3 drops in the morning before sunscreen",
        "Side Effects": "Mild tingling for sensitive skin",
        "Price": "₹699"
    }
    
    state = PipelineState(raw_product=raw)
    
    # Run Agents Manually (simulating DAG)
    # 1. Parse
    state.product = ParseProductAgent().run(raw)
    
    # 2. Gens
    state = GenerateQuestionsAgent().run(state)
    state = ProductBGeneratorAgent().run(state)
    
    # 3. Drafts
    state = FaqPageAgent().run(state)
    state = ProductPageAgent().run(state)
    state = ComparisonPageAgent().run(state)
    
    # 4. Write (to tmp using strict writer)
    writer = JsonWriterAgent(output_dir=str(tmp_path))
    state = writer.run(state)
    
    # 5. Config Internal Schema Paths for Validator
    cwd = os.getcwd()
    state.schema_paths = {
        "faq_draft": os.path.join(cwd, "src/schemas/faq_schema.json"),
        "product_page_draft": os.path.join(cwd, "src/schemas/product_page_schema.json"),
        "comparison_draft": os.path.join(cwd, "src/schemas/comparison_page_schema.json")
    }
    
    return state, tmp_path

def test_outputs_exist(run_pipeline):
    state, tmp_path = run_pipeline
    assert os.path.exists(tmp_path / "faq.json")
    assert os.path.exists(tmp_path / "product_page.json")
    assert os.path.exists(tmp_path / "comparison_page.json")

def test_schema_validity(run_pipeline):
    state, tmp_path = run_pipeline
    # ValidatorAgent should pass without error (FactGuard + SchemaValidator)
    agent = ValidatorAgent()
    state = agent.run(state) 
    assert state.validation_report["passed"] is True

def test_faq_constraints(run_pipeline):
    _, tmp_path = run_pipeline
    with open(tmp_path / "faq.json") as f:
        data = json.load(f)
    
    # MinItems Check
    assert len(data["question_bank"]) >= 15
    assert len(data["faqs"]) >= 5
    
    # Content Check
    assert data["title"] == "GlowBoost Vitamin C Serum"
    
def test_comparison_constraints(run_pipeline):
    _, tmp_path = run_pipeline
    with open(tmp_path / "comparison_page.json") as f:
        data = json.load(f)
        
    assert data["meta"]["product_b_fictional"] is True
    assert len(data["comparison"]) >= 4
    assert data["product_b"]["name"] == "Fictional Product B"

def test_product_page_constraints(run_pipeline):
    _, tmp_path = run_pipeline
    with open(tmp_path / "product_page.json") as f:
        data = json.load(f)
        
    assert data["pricing"]["amount"] == 699
    assert data["meta"]["generated_by"] == "ProductPageAgent"
