from typing import List
from pydantic import BaseModel, Field
from app.schemas.product import ProductInput


class OptimizeRequest(BaseModel):
    products: List[ProductInput] = Field(..., min_length=1)


class BoxCatalogOut(BaseModel):
    id: str
    name: str
    length: float
    width: float
    height: float
    max_weight: float
    base_cost: float

    class Config:
        from_attributes = True
