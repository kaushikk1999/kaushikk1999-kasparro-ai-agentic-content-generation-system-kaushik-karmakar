import json
import os
from typing import Dict, Any, List
from src.state.pipeline_state import PipelineState
from src.validators.schema_validate import SchemaValidator
from src.validators.fact_guard import FactGuard

class ValidatorAgent:
    def run(self, state: PipelineState) -> PipelineState:
        # Configuration
        errors = []
        
        # 1. Schema Validation (Draft 2020-12)
        # We iterate over the output paths stored in state
        for key, output_path in state.output_paths.items():
            if key not in state.schema_paths:
                continue

            schema_path = state.schema_paths[key]
            
            if not os.path.exists(output_path):
                errors.append(f"Output file missing: {output_path}")
                continue
            
            if not os.path.exists(schema_path):
                errors.append(f"Schema file missing: {schema_path}")
                continue

            try:
                # Use strict SchemaValidator
                SchemaValidator.validate_file(output_path, schema_path)
            except Exception as e:
                # Fail Fast: Raise immediately
                raise RuntimeError(f"VALIDATION FATAL: {str(e)}")

        # 2. Fact Guard (Product Consistency)
        if state.product:
            try:
                guard = FactGuard(state.product)
                
                # Check each generated file
                # Map internal keys to Guard methods
                
                # FAQ
                if "faq_draft" in state.output_paths:
                    path = state.output_paths["faq_draft"]
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    guard.validate_faq_page(data)
                    
                # Product Page
                if "product_page_draft" in state.output_paths:
                    path = state.output_paths["product_page_draft"]
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    guard.validate_product_page(data)
                    
                # Comparison Page
                if "comparison_draft" in state.output_paths:
                    path = state.output_paths["comparison_draft"]
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    guard.validate_comparison_page(data)
                    
            except Exception as e:
                # Fail Fast on content violation
                raise RuntimeError(f"CONTENT VIOLATION: {str(e)}")
        else:
             print("[WARNING] Skipping FactGuard: No product data found in state.")

        # If we get here, everything passed
        state.validation_report = {
            "passed": True,
            "errors": []
        }
        return state
