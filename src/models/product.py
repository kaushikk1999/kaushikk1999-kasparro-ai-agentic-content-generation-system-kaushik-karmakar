from typing import List
from pydantic import BaseModel, Field, field_validator, ConfigDict

def split_csv(value: str) -> List[str]:
    """Splits a comma-separated string into a list of strings, stripping whitespace."""
    if not value:
        return []
    return [item.strip() for item in value.split(',') if item.strip()]

def parse_price(value: str) -> int:
    """Parses a price string (e.g., '₹699') into an integer (e.g., 699)."""
    digits = ''.join(filter(str.isdigit, value))
    return int(digits) if digits else 0

class RawProductInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    product_name: str = Field(alias="Product Name")
    concentration: str = Field(alias="Concentration")
    skin_type: str = Field(alias="Skin Type")
    key_ingredients: str = Field(alias="Key Ingredients")
    benefits: str = Field(alias="Benefits")
    how_to_use: str = Field(alias="How to Use")
    side_effects: str = Field(alias="Side Effects")
    price: str = Field(alias="Price")

class ProductData(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    product_name: str
    concentration: str
    skin_type: List[str]
    key_ingredients: List[str]
    benefits: List[str]
    how_to_use: str
    side_effects: str
    price_inr: int

