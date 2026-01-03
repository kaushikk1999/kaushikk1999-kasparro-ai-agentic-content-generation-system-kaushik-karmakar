from src.templates.spec import TemplateSpec, FieldSpec

TEMPLATE = TemplateSpec(
    template_id="faq_page",
    required_inputs={"product"},
    fields=[
        FieldSpec(name="title", block_id="title", format="raw"),
        FieldSpec(name="ingredients", block_id="key_ingredients", format="bullet"),
        FieldSpec(name="benefits", block_id="benefits", format="bullet"),
        FieldSpec(name="usage", block_id="usage", format="paragraph"),
        FieldSpec(name="safety", block_id="safety", format="paragraph"),
        FieldSpec(name="price", block_id="price", format="raw")
    ],
    output_type="faq"
)
