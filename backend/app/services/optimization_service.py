"""
SmartLogistics – Optimization Service
Orchestrates entire pipeline: GA -> Pack -> Cartonize -> Cost -> AI Analysis -> DB Save
"""
import uuid
from typing import List
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.product import ProductInput
from app.models.order import Order
from app.models.product import Product
from app.models.packing_result import PackingResult
from app.models.box_catalog import BoxCatalog
from app.engines.packing_engine import Item
from app.engines.cartonization_engine import cartonize
from app.engines.packing_engine import capped_expand_products  # Added
from app.engines.genetic_optimizer import optimize_packing_order
from app.services.shipment_service import generate_shipment_options
from app.services.analysis_service import analyze_shipments

async def run_optimization_pipeline(db: AsyncSession, product_inputs: List[ProductInput]) -> dict:
    """Full optimization pipeline."""
    # 1. Create order
    order = Order()
    db.add(order)
    await db.flush()  # to get order.id

    # 2. Add products
    total_actual_weight = 0.0
    products_dicts = []
    
    for p_in in product_inputs:
        num = p_in.quantity
        product = Product(
            order_id=order.id,
            name=p_in.name,
            length=p_in.length,
            width=p_in.width,
            height=p_in.height,
            weight=p_in.weight,
            quantity=p_in.quantity
        )
        db.add(product)
        products_dicts.append(p_in.model_dump())
        total_actual_weight += p_in.weight * num
        
    await db.flush()
    
# Load box catalog first for checks
    result = await db.execute(select(BoxCatalog))
    box_catalog_db = result.scalars().all()
    box_catalog = [
        {
            "name": b.name, "length": b.length, "width": b.width,
            "height": b.height, "max_weight": b.max_weight, "base_cost": b.base_cost
        }
        for b in box_catalog_db
    ]
    max_box_weight = max(b["max_weight"] for b in box_catalog)
    
    if total_actual_weight > max_box_weight * 1.2:  # 20% buffer
        raise ValueError(f"Total weight {total_actual_weight:.1f}kg exceeds largest box capacity {max_box_weight}kg")
    
    # Capped expand: max 200 items to prevent mem/GA explosion
    items: List[Item] = capped_expand_products(products_dicts, max_items=200)
    
    if len(items) == 0:
        raise ValueError("No items after capping - reduce quantities")
    # Convert ORM to dict for engine
    box_catalog = [
        {
            "name": b.name, "length": b.length, "width": b.width,
            "height": b.height, "max_weight": b.max_weight, "base_cost": b.base_cost
        }
        for b in box_catalog_db
    ]

    # 4. Cartonization engine to pick best box structure
    # This internally does a fast FFD pack to check fit
    best_candidate = cartonize(items, box_catalog)
    
    box = best_candidate["box"]
    
    # 5. GA Optimizer to refine packing order for the chosen box
    if len(items) > 1:
        optimized_items = optimize_packing_order(items, box)
    else:
        optimized_items = items
        
    # Re-pack with optimized order
    from app.engines.packing_engine import PackingEngine
    final_engine = PackingEngine(box["length"], box["width"], box["height"])
    final_packing_result = final_engine.pack_items(optimized_items)
    
    # Build dimensions string
    box_dimensions = f'{box["length"]}x{box["width"]}x{box["height"]}'
    
    # 6. Save PackingResult
    db_packing = PackingResult(
        order_id=order.id,
        box_type=box["name"],
        box_dimensions=box_dimensions,
        utilization=final_packing_result["utilization"],
        cost=box["base_cost"],
        items_placed=final_packing_result["placed"],
        items_count=final_packing_result["items_packed"]
    )
    db.add(db_packing)
    await db.flush()

    # 7. Generate Shipments Options (Cost Engine included)
    shipments = await generate_shipment_options(
        db, order.id, box["length"], box["width"], box["height"], total_actual_weight
    )
    
    # 8. AI Analysis
    analysis = await analyze_shipments(db, order.id, shipments)
    
    # 9. Update order total cost
    best_shipment = next(s for s in shipments if s.carrier_name == analysis.best_option)
    order.total_cost = db_packing.cost + best_shipment.estimated_cost
    await db.commit() # Commit all Tx!
    
    await db.refresh(order)
    
    return {
        "order_id": str(order.id),
        "created_at": order.created_at,
        "box_type": db_packing.box_type,
        "box_dimensions": db_packing.box_dimensions,
        "utilization": db_packing.utilization,
        "packing_cost": db_packing.cost,
        "items_count": db_packing.items_count,
        "total_cost": order.total_cost,
        "shipment_options": shipments,
        "best_option": analysis.best_option,
        "reason": analysis.reason,
        "cost_saving": analysis.cost_saving,
        "confidence": analysis.confidence
    }
