"""
SmartLogistics – Cost Engine
Calculates per-carrier shipping costs using:
  - Volumetric weight = (L × W × H) / divisor
  - Chargeable weight = max(actual, volumetric)
  - Per-carrier rate tables with minimum charge
"""
from typing import List, Dict, Any
from app.core.constants import CARRIERS
from app.core.config import get_settings

settings = get_settings()


def calculate_volumetric_weight(
    length: float,
    width: float,
    height: float,
    divisor: int = None,
) -> float:
    """Volumetric weight in kg (dimensions in cm)."""
    div = divisor or settings.VOLUMETRIC_DIVISOR
    return (length * width * height) / div


def calculate_chargeable_weight(
    actual_weight: float,
    volumetric_weight: float,
) -> float:
    """Chargeable weight = higher of actual vs volumetric."""
    return max(actual_weight, volumetric_weight)


def calculate_shipping_costs(
    box_length: float,
    box_width: float,
    box_height: float,
    actual_weight: float,
) -> List[Dict[str, Any]]:
    """
    Calculate shipping cost for every carrier.
    Returns list sorted by estimated_cost ascending.
    """
    vol_weight = calculate_volumetric_weight(box_length, box_width, box_height)
    chargeable = calculate_chargeable_weight(actual_weight, vol_weight)

    results = []
    for carrier in CARRIERS:
        raw_cost = chargeable * carrier["rate_per_kg"]
        cost = max(raw_cost, carrier["min_charge"])
        # Add fuel surcharge (5%)
        cost *= 1.05
        cost = round(cost, 2)

        results.append({
            "carrier_name": carrier["name"],
            "estimated_cost": cost,
            "delivery_time": carrier["base_days"],
            "rating": carrier["reliability"],
            "color": carrier["color"],
            "volumetric_weight": round(vol_weight, 3),
            "actual_weight": round(actual_weight, 3),
            "chargeable_weight": round(chargeable, 3),
        })

    return sorted(results, key=lambda r: r["estimated_cost"])
