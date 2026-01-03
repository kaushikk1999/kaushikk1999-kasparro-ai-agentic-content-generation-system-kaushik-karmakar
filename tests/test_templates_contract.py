import pytest
from src.blocks import BLOCKS
from src.templates.faq_template import TEMPLATE as FAQ_TEMPLATE
from src.templates.product_template import TEMPLATE as PROD_TEMPLATE
from src.templates.comparison_template import TEMPLATE as COMP_TEMPLATE

TEMPLATES = [FAQ_TEMPLATE, PROD_TEMPLATE, COMP_TEMPLATE]

@pytest.mark.parametrize("template", TEMPLATES)
def test_template_basics(template):
    assert template.template_id
    assert template.output_type in ["faq", "product_page", "comparison"]

def test_faq_template_structure():
    assert "product" in FAQ_TEMPLATE.required_inputs
    for field in FAQ_TEMPLATE.fields:
        assert field.block_id in BLOCKS

def test_product_template_structure():
    assert "product" in PROD_TEMPLATE.required_inputs
    for field in PROD_TEMPLATE.fields:
        assert field.block_id in BLOCKS

def test_comparison_template_structure():
    assert "product" in COMP_TEMPLATE.required_inputs
    assert "product_b" in COMP_TEMPLATE.required_inputs
    for field in COMP_TEMPLATE.fields:
        assert field.block_id in BLOCKS

def test_comparison_template_has_comparison_field():
    field_names = [f.name for f in COMP_TEMPLATE.fields]
    assert "comparison" in field_names
    assert "comparison_data" not in field_names

@pytest.mark.parametrize("template", TEMPLATES)
def test_template_formats_allowed(template):
    from src.templates.spec import ALLOWED_FORMATS
    for field in template.fields:
        assert field.format in ALLOWED_FORMATS
