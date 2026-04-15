"""
SmartLogistics – Optimize API Routes
"""
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.exceptions import RequestValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.order import OptimizeRequest
from app.schemas.result import OptimizeResponse
from app.services.csv_service import parse_csv
from app.services.optimization_service import run_optimization_pipeline
import logging
import io

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/optimize", tags=["Optimization"])


@router.post("", response_model=OptimizeResponse)
async def optimize_order(
    request: OptimizeRequest,
    db: AsyncSession = Depends(get_db)
):
    """Run full optimization pipeline on provided JSON products."""
    try:
        return await run_optimization_pipeline(db, request.products)
    except Exception as e:
        logger.exception("Optimization failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload", response_model=OptimizeResponse)
async def optimize_upload(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Run optimization on uploaded CSV file."""
    if not file.filename or not file.filename.lower().endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")
    
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:  # 10MB
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")
    
    try:
        products = await parse_csv(content)
        if not products:
            raise HTTPException(status_code=400, detail="No valid products parsed from CSV.")
        
        # Quick weight check
        total_weight = sum(p.weight * p.quantity for p in products)
        if total_weight > 1000:  # Reasonable limit
            raise HTTPException(status_code=400, detail=f"Total weight {total_weight:.1f}kg too high (max 1000kg)")
            
        return await run_optimization_pipeline(db, products)
    except RequestValidationError as e:
        raise HTTPException(status_code=422, detail="Invalid data in CSV")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Optimization pipeline failed")
        raise HTTPException(status_code=500, detail="Internal optimization error")
