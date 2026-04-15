"""
SmartLogistics – Analysis Service
Calls OpenRouter API for carrier recommendation.
"""
import json
import logging
import httpx
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.shipment_option import ShipmentOption
from app.models.shipment_analysis import ShipmentAnalysis
from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

async def analyze_shipments(db: AsyncSession, order_id: str, shipments: List[ShipmentOption]) -> ShipmentAnalysis:
    """Analyze using OpenRouter (GPT-4o-mini) and store result."""
    
    if not settings.OPENROUTER_API_KEY:
        # Fallback if no Key
        logger.warning("No OpenRouter API Key provided. Using fallback logic.")
        best = min(shipments, key=lambda s: s.estimated_cost)
        db_analysis = ShipmentAnalysis(
            order_id=order_id,
            best_option=best.carrier_name,
            reason=f"Selected {best.carrier_name} purely based on lowest cost.",
            cost_saving=0.0,
            confidence=0.5
        )
        db.add(db_analysis)
        await db.flush()
        return db_analysis
        
    payload = _build_prompt(shipments)
    
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:3000",
        "X-Title": "SmartLogistics"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{settings.OPENROUTER_BASE_URL}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            content = data["choices"][0]["message"]["content"]
            
            # Try to parse JSON from AI
            # AI might wrap in markdown ```json ... ```
            content = content.replace("```json", "").replace("```", "").strip()
            result = json.loads(content)
            
            best_carrier = result.get("best_carrier", shipments[0].carrier_name)
            reason = result.get("reason", "Determined optimal by AI.")
            cost_saving = float(result.get("cost_saving", 0.0))
            confidence = float(result.get("confidence", 0.9))
            
            db_analysis = ShipmentAnalysis(
                order_id=order_id,
                best_option=best_carrier,
                reason=reason,
                cost_saving=cost_saving,
                confidence=confidence
            )
            db.add(db_analysis)
            await db.flush()
            return db_analysis
            
    except Exception as e:
        logger.error(f"OpenRouter API call failed: {e}")
        # Fallback
        best = min(shipments, key=lambda s: s.estimated_cost)
        db_analysis = ShipmentAnalysis(
            order_id=order_id,
            best_option=best.carrier_name,
            reason="AI analysis failed. Defaulted to lowest cost option.",
            cost_saving=0.0,
            confidence=0.5
        )
        db.add(db_analysis)
        await db.flush()
        return db_analysis


def _build_prompt(shipments: List[ShipmentOption]) -> dict:
    options_data = []
    for s in shipments:
        options_data.append({
            "carrier": s.carrier_name,
            "cost": s.estimated_cost,
            "delivery_time_days": s.delivery_time,
            "reliability_rating": s.rating,
            "status": s.status
        })
        
    system_msg = """You are a logistics optimization AI.
Given a list of shipment carrier options, pick the BEST overall option.
Consider cost, delivery time, reliability, and status.
Return ONLY valid JSON with exactly these keys:
{
  "best_carrier": "Name of carrier",
  "reason": "Brief explanation of why it is the best balance of cost and reliability (max 2 sentences)",
  "cost_saving": 0.0, // savings compared to the most expensive option
  "confidence": 0.95 // numeric confidence score 0.0-1.0
}
Strictly return JSON and NO OTHER TEXT.
"""
    
    return {
        "model": settings.OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": json.dumps(options_data)}
        ],
        "response_format": {"type": "json_object"},
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "scan_and_optimize_products",
                    "description": "Fastest and best optimizer tool to scan the products data, validate constraints, and optimize the results optimally.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "product_count": {
                                "type": "integer",
                                "description": "Number of products processed"
                            },
                            "optimization_strategy": {
                                "type": "string",
                                "description": "The logic or strategy applied during scanning (e.g. Genetic Algorithm, FFD)"
                            }
                        },
                        "required": ["optimization_strategy"]
                    }
                }
            }
        ]
    }
