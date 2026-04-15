"""
SmartLogistics – Results API Routes
"""
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import get_db
from app.schemas.result import PackingResultOut, ShipmentOptionOut, ShipmentAnalysisOut
from app.models.packing_result import PackingResult
from app.models.shipment_option import ShipmentOption
from app.models.shipment_analysis import ShipmentAnalysis

router = APIRouter(tags=["Results"])


@router.get("/result/{order_id}", response_model=PackingResultOut)
async def get_packing_result(order_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PackingResult).where(PackingResult.order_id == order_id))
    db_obj = result.scalars().first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="Packing result not found")
    # map explicitly for uuid -> str
    out_dict = db_obj.__dict__.copy()
    out_dict['id'] = str(out_dict['id'])
    out_dict['order_id'] = str(out_dict['order_id'])
    return out_dict


@router.get("/shipment/{order_id}", response_model=List[ShipmentOptionOut])
async def get_shipment_options(order_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ShipmentOption).where(ShipmentOption.order_id == order_id))
    db_objs = result.scalars().all()
    if not db_objs:
        raise HTTPException(status_code=404, detail="Shipment options not found")
    
    out_list = []
    for o in db_objs:
        d = o.__dict__.copy()
        d['id'] = str(d['id'])
        d['order_id'] = str(d['order_id'])
        out_list.append(d)
    return out_list


@router.get("/analysis/{order_id}", response_model=ShipmentAnalysisOut)
async def get_shipment_analysis(order_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ShipmentAnalysis).where(ShipmentAnalysis.order_id == order_id))
    db_obj = result.scalars().first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="Analysis not found")
    out_dict = db_obj.__dict__.copy()
    out_dict['id'] = str(out_dict['id'])
    out_dict['order_id'] = str(out_dict['order_id'])
    return out_dict
