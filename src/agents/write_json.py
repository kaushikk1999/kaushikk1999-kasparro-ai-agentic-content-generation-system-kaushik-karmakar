import json
import os
from src.state.pipeline_state import PipelineState
from src.agents.assembly import assemble_faq_page, assemble_product_page, assemble_comparison_page

class JsonWriterAgent:
    def __init__(self, output_dir: str = "outputs"):
        self.output_dir = output_dir

    def run(self, state: PipelineState) -> PipelineState:
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        # 1. Assemble strict outputs using the Assembly Layer
        # This converts internal drafts into strictly schema-compliant structures
        
        # FAQ
        if state.faq_draft:
            final_faq = assemble_faq_page(state.faq_draft)
            path = os.path.join(self.output_dir, "faq.json")
            self._write(path, final_faq)
            state.output_paths["faq_draft"] = path
        
        # Product Page
        if state.product_page_draft:
            final_prod = assemble_product_page(state.product_page_draft)
            path = os.path.join(self.output_dir, "product_page.json")
            self._write(path, final_prod)
            state.output_paths["product_page_draft"] = path
            
        # Comparison Page
        if state.comparison_draft:
            final_comp = assemble_comparison_page(state.comparison_draft)
            path = os.path.join(self.output_dir, "comparison_page.json")
            self._write(path, final_comp)
            state.output_paths["comparison_draft"] = path
            
        return state

    def _write(self, path: str, data: dict):
        # Strict requirement: ensure_ascii=False, indent=2
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
