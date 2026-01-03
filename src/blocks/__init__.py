from .title import block_title
from .ingredients import block_key_ingredients
from .benefits import block_benefits
from .usage import block_usage
from .safety import block_safety
from .pricing import block_price
from .comparison import block_comparison_rows
from .meta import block_product_b_meta

BLOCKS: dict = {
    "title": block_title,
    "key_ingredients": block_key_ingredients,
    "benefits": block_benefits,
    "usage": block_usage,
    "safety": block_safety,
    "price": block_price,
    "comparison_rows": block_comparison_rows,
    "product_b_meta": block_product_b_meta
}
