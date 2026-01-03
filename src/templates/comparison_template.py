from src.templates.spec import TemplateSpec, FieldSpec

TEMPLATE = TemplateSpec(
    template_id="comparison_page",
    required_inputs={"product", "product_b"},
    fields=[
        FieldSpec(name="meta", block_id="product_b_meta", format="raw"),
        FieldSpec(name="comparison", block_id="comparison_rows", format="raw")
    ],
    output_type="comparison"
)
