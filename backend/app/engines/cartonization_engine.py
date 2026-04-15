"""
SmartLogistics – Cartonization Engine
Selects the optimal box from the catalog for a given set of items.
Scoring: 60% cost weight + 40% utilization score
"""
from typing import List, Dict, Any, Optional
from app.engines.packing_engine import PackingEngine, Item, sort_items_by_volume


def cartonize(
    items: List[Item],
    box_catalog: List[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    """
    Try each box in catalog (smallest to largest).
    Score each viable box and return the optimal one.
    Returns: {box, packing_result, score}
    """
    # Sort boxes smallest volume first
    sorted_boxes = sorted(
        box_catalog,
        key=lambda b: b["length"] * b["width"] * b["height"],
    )

    total_weight = sum(i.weight for i in items)
    sorted_items = sort_items_by_volume(items)

    candidates = []

    for box in sorted_boxes:
        # Weight check
        if total_weight > box["max_weight"]:
            continue

        engine = PackingEngine(box["length"], box["width"], box["height"])
        result = engine.pack_items(sorted_items[:])  # shallow copy list

        # Accept box if all items fit
        if not result["failed"]:
            utilization = result["utilization"]
            cost = float(box["base_cost"])

            # Normalised cost score (lower cost = higher score)
            max_cost = max(b["base_cost"] for b in sorted_boxes)
            cost_score = 1.0 - (cost / max_cost)

            # Utilization score (higher = better)
            util_score = utilization / 100.0

            # Combined score
            score = 0.60 * cost_score + 0.40 * util_score

            candidates.append({
                "box": box,
                "packing_result": result,
                "score": score,
                "cost": cost,
                "utilization": utilization,
            })

    if not candidates:
        # Fallback: use the largest box
        largest = sorted_boxes[-1]
        engine = PackingEngine(largest["length"], largest["width"], largest["height"])
        result = engine.pack_items(sorted_items[:])
        return {
            "box": largest,
            "packing_result": result,
            "score": 0.0,
            "cost": largest["base_cost"],
            "utilization": result["utilization"],
        }

    # Return highest scored candidate
    return max(candidates, key=lambda c: c["score"])
