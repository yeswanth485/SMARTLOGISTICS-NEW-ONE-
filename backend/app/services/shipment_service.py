"""
SmartLogistics – Shipment Service
Generates, simulates tracking, and stores shipment options.
"""
import random
import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.engines.cost_engine import calculate_shipping_costs
from app.models.shipment_option import ShipmentOption
from app.core.constants import TRACKING_STATUSES, STATUS_WEIGHTS

async def generate_shipment_options(
    db: AsyncSession,
    order_id: uuid.UUID,
    box_length: float,
    box_width: float,
    box_height: float,
    actual_weight: float
) -> List[ShipmentOption]:
    """Calculate costs, generate fake tracking info, save and return."""
    options_data = calculate_shipping_costs(box_length, box_width, box_height, actual_weight)
    
    shipment_options = []
    
    for opt in options_data:
        # Random status based on weights
        status = random.choices(TRACKING_STATUSES, weights=STATUS_WEIGHTS, k=1)[0]
        
        # Generate random tracking ID
        tracking_prefix = opt["carrier_name"][:3].upper()
        tracking_num = "".join([str(random.randint(0, 9)) for _ in range(9)])
        tracking_id = f"{tracking_prefix}{tracking_num}"
        
        db_opt = ShipmentOption(
            order_id=order_id,
            carrier_name=opt["carrier_name"],
            estimated_cost=opt["estimated_cost"],
            delivery_time=opt["delivery_time"],
            rating=opt["rating"],
            status=status,
            tracking_id=tracking_id,
            color=opt["color"]
        )
        db.add(db_opt)
        shipment_options.append(db_opt)
        
    await db.flush() # flush to get IDs if needed
    
    return shipment_options
