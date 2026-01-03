from typing import List, Dict
from src.state.pipeline_state import PipelineState, CategorizedQuestions

class GenerateQuestionsAgent:
    def run(self, state: PipelineState) -> PipelineState:
        if not state.product:
            raise ValueError("ProductData is required for GenerateQuestionsAgent")
        
        product = state.product
        questions = []
        
        # 1. Informational
        questions.append({"category": "Informational", "question": f"What is {product.product_name}?"})
        questions.append({"category": "Informational", "question": f"How much {product.concentration} does it contain?"})
        questions.append({"category": "Informational", "question": f"What are the key ingredients in {product.product_name}?"})
        
        # 2. Usage
        questions.append({"category": "Usage", "question": "How do I use this product?"})
        questions.append({"category": "Usage", "question": "When should I apply it?"})
        questions.append({"category": "Usage", "question": f"Can I use {product.product_name} with other serums?"})
        
        # 3. Safety
        questions.append({"category": "Safety", "question": "Are there any side effects?"})
        questions.append({"category": "Safety", "question": f"Is {product.product_name} suitable for sensitive skin?"})
        questions.append({"category": "Safety", "question": "What specifically should I watch out for?"})
        
        # 4. Benefits
        for benefit in product.benefits[:2]:
             questions.append({"category": "Benefits", "question": f"Does this help with {benefit.lower()}?"})
        questions.append({"category": "Benefits", "question": "How long until I see results?"})

        # 5. Purchase
        questions.append({"category": "Purchase", "question": f"How much does {product.product_name} cost?"})
        questions.append({"category": "Purchase", "question": "Is there a money-back guarantee?"})
        questions.append({"category": "Purchase", "question": "Where can I buy it?"})

        # 6. Storage (Bonus category to ensure > 5)
        questions.append({"category": "Storage", "question": "How should I store this serum?"})

        # Ensure uniqueness and non-empty
        seen = set()
        unique_questions = []
        for q in questions:
            q_text = q["question"].strip()
            if not q_text:
                continue
            if q_text not in seen:
                seen.add(q_text)
                q["question"] = q_text # Store stripped version
                unique_questions.append(q)

        # Sanity check (though tests cover this)
        if len(unique_questions) < 15:
             # Just in case our list logic changes and we shrink below limit
             # Add generic padding to guarantee contract if needed, 
             # but better to rely on fixed list above being sufficient.
             pass

        state.questions = CategorizedQuestions(items=unique_questions)
        return state
