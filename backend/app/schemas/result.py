from typing import List, Optional, Any
from datetime import datetime
from pydantic import BaseModel


class PackingResultOut(BaseModel):
    id: str
    order_id: str
    box_type: str
    box_dimensions: str
    utilization: float
    cost: float
    items_placed: Optional[Any] = None
    items_count: float

    class Config:
        from_attributes = True


class ShipmentOptionOut(BaseModel):
    id: str
    order_id: str
    carrier_name: str
    estimated_cost: float
    delivery_time: int
    rating: float
    status: str
    tracking_id: Optional[str] = None
    color: Optional[str] = None

    class Config:
        from_attributes = True


class ShipmentAnalysisOut(BaseModel):
    id: str
    order_id: str
    best_option: str
    reason: str
    cost_saving: float
    confidence: float

    class Config:
        from_attributes = True


class OptimizeResponse(BaseModel):
    order_id: str
    created_at: datetime
    box_type: str
    box_dimensions: str
    utilization: float
    packing_cost: float
    items_count: float
    total_cost: float
    shipment_options: List[ShipmentOptionOut]
    best_option: str
    reason: str
    cost_saving: float
    confidence: float
