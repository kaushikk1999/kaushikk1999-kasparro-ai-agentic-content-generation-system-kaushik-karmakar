from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any
from src.models.product import ProductData
from src.models.product_b import ProductBData

@dataclass
class CategorizedQuestions:
    items: List[Dict[str, str]] = field(default_factory=list)

@dataclass
class PipelineState:
    raw_product: Optional[Dict[str, Any]] = None
    product: Optional[ProductData] = None
    questions: Optional[CategorizedQuestions] = None
    product_b: Optional[ProductBData] = None
    
    # Draft outputs
    faq_draft: Optional[Dict[str, Any]] = None
    product_page_draft: Optional[Dict[str, Any]] = None
    comparison_draft: Optional[Dict[str, Any]] = None
    
    # Final paths
    output_paths: Dict[str, str] = field(default_factory=dict)
    schema_paths: Dict[str, str] = field(default_factory=dict)
    
    # Validation
    validation_report: Optional[Dict[str, Any]] = None

    # Debug / Testing
    debug_log: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict[str, Any]:
        """Helper for debugging."""
        return {
            "has_raw": self.raw_product is not None,
            "has_product": self.product is not None,
            "has_questions": self.questions is not None and len(self.questions.items) > 0,
            "has_product_b": self.product_b is not None,
            "draft_keys": [
                k for k in ["faq_draft", "product_page_draft", "comparison_draft"]
                if getattr(self, k) is not None
            ]
        }
