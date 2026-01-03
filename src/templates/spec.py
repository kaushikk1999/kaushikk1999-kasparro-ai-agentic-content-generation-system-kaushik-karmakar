from dataclasses import dataclass
from typing import List, Set, Literal

ALLOWED_FORMATS = {"raw", "bullet", "paragraph"}
FormatType = Literal["raw", "bullet", "paragraph"]

@dataclass(frozen=True)
class FieldSpec:
    name: str
    block_id: str
    format: FormatType

    def __post_init__(self):
        if self.format not in ALLOWED_FORMATS:
            raise ValueError(
                f"Invalid format='{self.format}'. Allowed: {sorted(ALLOWED_FORMATS)}"
            )

@dataclass(frozen=True)
class TemplateSpec:
    template_id: str
    required_inputs: Set[str]
    fields: List[FieldSpec]
    output_type: Literal["faq", "product_page", "comparison"]
