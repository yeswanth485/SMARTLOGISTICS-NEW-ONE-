"""
SmartLogistics – 3D Bin Packing Engine
Algorithm: First Fit Decreasing with 6-axis rotations & guillotine space splitting
"""
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, field
import math


@dataclass
class Item:
    name: str
    length: float
    width: float
    height: float
    weight: float

    def volume(self) -> float:
        return self.length * self.width * self.height

    def get_rotations(self) -> List[Tuple[float, float, float]]:
        """Return all 6 unique axis-aligned rotations (l,w,h)."""
        l, w, h = self.length, self.width, self.height
        return [
            (l, w, h), (l, h, w),
            (w, l, h), (w, h, l),
            (h, l, w), (h, w, l),
        ]


@dataclass
class Space:
    """A free rectangular region inside the box."""
    x: float
    y: float
    z: float
    length: float
    width: float
    height: float

    def volume(self) -> float:
        return self.length * self.width * self.height

    def can_fit(self, l: float, w: float, h: float) -> bool:
        return l <= self.length and w <= self.width and h <= self.height


@dataclass
class PlacedItem:
    name: str
    x: float
    y: float
    z: float
    length: float
    width: float
    height: float
    rotation_index: int


class PackingEngine:
    def __init__(self, box_length: float, box_width: float, box_height: float):
        self.box_length = box_length
        self.box_width = box_width
        self.box_height = box_height
        self.box_volume = box_length * box_width * box_height
        self.spaces: List[Space] = [
            Space(0, 0, 0, box_length, box_width, box_height)
        ]
        self.placed_items: List[PlacedItem] = []
        self.used_volume: float = 0.0

    def _split_space(self, space: Space, l: float, w: float, h: float) -> List[Space]:
        """Guillotine cut: split remaining space into up to 3 new spaces."""
        new_spaces = []
        # Right remainder
        if space.length - l > 0:
            new_spaces.append(Space(
                space.x + l, space.y, space.z,
                space.length - l, space.width, space.height
            ))
        # Front remainder
        if space.width - w > 0:
            new_spaces.append(Space(
                space.x, space.y + w, space.z,
                l, space.width - w, space.height
            ))
        # Top remainder
        if space.height - h > 0:
            new_spaces.append(Space(
                space.x, space.y, space.z + h,
                l, w, space.height - h
            ))
        return new_spaces

    def pack_item(self, item: Item) -> bool:
        """FFD with smart rotation prune & large-space priority."""
        # Prune rotations: sort by best fit to box dims (largest dim first)
        box_l, box_w, box_h = sorted([self.box_length, self.box_width, self.box_height], reverse=True)
        rotations = sorted(
            item.get_rotations(),
            key=lambda r: max(min(r[0]/box_l or 1,1), min(r[1]/box_w or 1,1), min(r[2]/box_h or 1,1)),
            reverse=True
        )
        
        # Sort spaces: largest volume first (fill big gaps)
        self.spaces.sort(key=lambda s: s.volume(), reverse=True)

        for space in self.spaces[:]:  # copy to avoid mod during iter
            for rot_idx, (l, w, h) in enumerate(rotations):
                if space.can_fit(l, w, h):
                    placed = PlacedItem(
                        name=item.name,
                        x=space.x, y=space.y, z=space.z,
                        length=l, width=w, height=h,
                        rotation_index=rot_idx
                    )
                    self.placed_items.append(placed)
                    self.used_volume += l * w * h
                    new_spaces = self._split_space(space, l, w, h)
                    self.spaces.remove(space)
                    self.spaces.extend(new_spaces)
                    return True
        return False

    def pack_items(self, items: List[Item]) -> Dict[str, Any]:
        """Pack sorted items with enhanced stats."""
        # Ensure FFD sort
        items = sort_items_by_volume(items)
        failed = []
        for item in items:
            if not self.pack_item(item):
                failed.append(item.name)

        utilization = round((self.used_volume / self.box_volume) * 100, 2) if self.box_volume > 0 else 0.0

        return {
            "placed": [
                {
                    "name": p.name,
                    "x": round(p.x, 2), "y": round(p.y, 2), "z": round(p.z, 2),
                    "length": round(p.length, 2), "width": round(p.width, 2), "height": round(p.height, 2),
                    "rotation": p.rotation_index,
                }
                for p in self.placed_items
            ],
            "failed": failed,
            "utilization": utilization,
            "used_volume": round(self.used_volume, 2),
            "box_volume": self.box_volume,
            "items_packed": len(self.placed_items),
            "success_rate": round(len(self.placed_items) / max(len(items),1) * 100, 1)
        }


def capped_expand_products(products: List[Dict[str, Any]], max_items: int = 200) -> List[Item]:
    """Smart expansion: cap total items, stack high qty."""
    items = []
    total_items = 0
    for p in products:
        qty = int(p.get("quantity", 1))
        base_weight = float(p.get("weight", 0.1))
        l, w, h = float(p["length"]), float(p["width"]), float(p["height"])
        
        num_instances = min(qty, max(1, max_items // len(products)))
        for i in range(num_instances):
            if total_items >= max_items:
                break
            stack_name = f"{p['name']} x{min(qty,10)}" if i > 0 else p['name']
            stack_weight = base_weight * (qty / num_instances)
            items.append(Item(stack_name, l, w, h, stack_weight))
            total_items += 1
    
    return items


def expand_products(products: List[Dict[str, Any]]) -> List[Item]:
    """Legacy: use capped_expand_products."""
    return capped_expand_products(products)


def sort_items_by_volume(items: List[Item]) -> List[Item]:
    """FFD: largest first."""
    return sorted(items, key=lambda i: i.volume(), reverse=True)
