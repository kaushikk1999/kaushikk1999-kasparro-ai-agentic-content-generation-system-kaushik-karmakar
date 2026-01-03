from typing import List, Optional
from pydantic import BaseModel, ConfigDict

class ProductBData(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    name: str
    key_ingredients: List[str]
    benefits: List[str]
    price_inr: int

    def price_dict(self) -> dict:
        return {"currency": "INR", "amount": self.price_inr}
