from typing import List, Dict, Any
from src.state.pipeline_state import PipelineState
from src.templates.faq_template import TEMPLATE
from src.blocks import BLOCKS
from src.blocks.faq_answers import build_faq_answer

class FaqPageAgent:
    def run(self, state: PipelineState) -> PipelineState:
        if not state.product or not state.questions:
             raise ValueError("ProductData and Questions required for FaqPageAgent")
        
        draft = {}
        # 1. Fill fields from template blocks
        for field in TEMPLATE.fields:
             block_func = BLOCKS[field.block_id]
             # FAQ template only needs 'product'
             draft[field.name] = block_func(state.product)
        
        # 2. Add dynamic questions (Phase 3 logic)
        all_q_objs = state.questions.items
        
        # Simple transform for 'question_bank' output (just categories)
        draft["question_bank"] = all_q_objs
        
        # Use external block for deterministic answers
        draft["faqs"] = [
            {"question": q["question"], "answer": build_faq_answer(state.product, q)} 
            for q in all_q_objs[:5] # Limit to 5 as per plan 2B
        ]
        
        # 3. Add meta
        draft["meta"] = {"generated_by": "FaqPageAgent"}
        
        state.faq_draft = draft
        return state
