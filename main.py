import json
import os
from src.state.pipeline_state import PipelineState
from src.orchestrator.dag_runner import DagRunner, NodeSpec

# Agents
from src.agents.parse_product import ParseProductAgent
from src.agents.generate_questions import GenerateQuestionsAgent
from src.agents.generate_product_b import ProductBGeneratorAgent
from src.agents.build_faq_page import FaqPageAgent
from src.agents.build_product_page import ProductPageAgent
from src.agents.build_comparison_page import ComparisonPageAgent
from src.agents.write_json import JsonWriterAgent
from src.agents.validate_outputs import ValidatorAgent

def load_input_data(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

class ParseWrapperAgent:
    """Wraps the Phase 1 ParseProductAgent to fit the Phase 3 interface."""
    def run(self, state: PipelineState) -> PipelineState:
        if not state.raw_product:
            raise ValueError("No raw_product to parse")
        agent = ParseProductAgent()
        state.product = agent.run(state.raw_product)
        return state

def main():
    # 1. Setup Initial State
    raw_data = load_input_data("data/product_input.json")
    initial_state = PipelineState(raw_product=raw_data)
    
    # 2. Build DAG
    dag = DagRunner()
    
    # Node 1: Parse
    dag.register(NodeSpec(node_id="parse_product", agent=ParseWrapperAgent()))
    
    # Node 2: Questions (depends on product)
    dag.register(NodeSpec(
        node_id="gen_questions",
        agent=GenerateQuestionsAgent(),
        depends_on=["parse_product"]
    ))
    
    # Node 3: Product B (independent, but let's just depend on parse for consistency)
    dag.register(NodeSpec(
        node_id="gen_product_b",
        agent=ProductBGeneratorAgent(),
        depends_on=["parse_product"]
    ))
    
    # Node 4: Page Drafts
    dag.register(NodeSpec(
        node_id="build_faq",
        agent=FaqPageAgent(),
        depends_on=["parse_product", "gen_questions"]
    ))
    dag.register(NodeSpec(
        node_id="build_product_page",
        agent=ProductPageAgent(),
        depends_on=["parse_product"]
    ))
    dag.register(NodeSpec(
        node_id="build_comparison",
        agent=ComparisonPageAgent(),
        depends_on=["parse_product", "gen_product_b"]
    ))

    # Node 5: Writer
    dag.register(NodeSpec(
        node_id="write_json",
        agent=JsonWriterAgent(output_dir="outputs"),
        depends_on=["build_faq", "build_product_page", "build_comparison"]
    ))

    # Node 6: Validate (depends on writer)
    # Populate schema paths in state for the ValidatorAgent to find
    schema_map = {
        "faq_draft": os.path.abspath("src/schemas/faq_schema.json"),
        "product_page_draft": os.path.abspath("src/schemas/product_page_schema.json"),
        "comparison_draft": os.path.abspath("src/schemas/comparison_page_schema.json")
    }
    initial_state.schema_paths = schema_map # Set heavily needed paths in state

    dag.register(NodeSpec(
        node_id="validate_outputs",
        agent=ValidatorAgent(), # Stateless now
        depends_on=["write_json"]
    ))
    
    # 3. Execution
    final_state = dag.run(initial_state)
    
    # 4. Summary
    print("\n--- Pipeline Summary ---")
    print(f"Product: {final_state.product.product_name}")
    print(f"Questions Generated: {len(final_state.questions.items)}")
    print(f"Questions Generated: {len(final_state.questions.items)}")
    print("Outputs Written:")
    for key, path in final_state.output_paths.items():
        print(f" - {key}: {path}")
    
    if final_state.validation_report:
        print("\n--- Validation Report ---")
        print(f"Passed: {final_state.validation_report['passed']}")
        if not final_state.validation_report['passed']:
             print("Errors:")
             for err in final_state.validation_report['errors']:
                 print(f" - {err}")
             # Fail Hard as per Phase 4 requirement
             raise SystemExit("Validation failed: Pipeline outputs did not meet strict criteria.")
    else:
        print("\n[WARNING] No validation report found!")

if __name__ == "__main__":
    main()
