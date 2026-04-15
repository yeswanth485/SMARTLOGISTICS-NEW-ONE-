from typing import List, Optional
from pydantic import BaseModel, Field


class ProductInput(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    length: float = Field(gt=0.01, description="cm (min 0.01)")
    width: float = Field(gt=0.01, description="cm (min 0.01)")
    height: float = Field(gt=0.01, description="cm (min 0.01)")
    weight: float = Field(gt=0.01, description="kg (min 0.01)")
    quantity: int = Field(default=1, ge=1, le=1000)


class ProductOut(BaseModel):
    id: str
    order_id: str
    name: str
    length: float
    width: float
    height: float
    weight: float
    quantity: int

    class Config:
        from_attributes = True
