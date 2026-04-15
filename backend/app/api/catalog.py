"""
SmartLogistics – Catalog API Routes
"""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import get_db
from app.schemas.order import BoxCatalogOut
from app.models.box_catalog import BoxCatalog

router = APIRouter(prefix="/catalog", tags=["Catalog"])

@router.get("/boxes", response_model=List[BoxCatalogOut])
async def get_box_catalog(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(BoxCatalog))
    boxes = result.scalars().all()
    
    out_list = []
    for b in boxes:
        d = b.__dict__.copy()
        d['id'] = str(d['id'])
        out_list.append(d)
    return out_list
