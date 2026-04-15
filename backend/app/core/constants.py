from typing import List, Dict, Any

# ─── Carrier Definitions ───────────────────────────────────────────────────────
CARRIERS: List[Dict[str, Any]] = [
    {
        "name": "BlueDart",
        "rate_per_kg": 85.0,       # INR per kg
        "min_charge": 120.0,
        "base_days": 2,
        "reliability": 4.5,
        "color": "#1e88e5",
    },
    {
        "name": "Delhivery",
        "rate_per_kg": 62.0,
        "min_charge": 80.0,
        "base_days": 3,
        "reliability": 4.1,
        "color": "#e53935",
    },
    {
        "name": "FedEx",
        "rate_per_kg": 120.0,
        "min_charge": 200.0,
        "base_days": 1,
        "reliability": 4.8,
        "color": "#6a1b9a",
    },
    {
        "name": "DHL",
        "rate_per_kg": 110.0,
        "min_charge": 180.0,
        "base_days": 2,
        "reliability": 4.7,
        "color": "#f9a825",
    },
]

# ─── Default Box Catalog ───────────────────────────────────────────────────────
BOX_CATALOG: List[Dict[str, Any]] = [
    {"name": "XS Box",    "length": 15, "width": 10, "height": 8,  "max_weight": 1,  "base_cost": 15.0},
    {"name": "Small Box", "length": 25, "width": 20, "height": 15, "max_weight": 3,  "base_cost": 25.0},
    {"name": "Medium Box","length": 35, "width": 30, "height": 20, "max_weight": 8,  "base_cost": 40.0},
    {"name": "Large Box", "length": 50, "width": 40, "height": 30, "max_weight": 20, "base_cost": 60.0},
    {"name": "XL Box",    "length": 60, "width": 50, "height": 40, "max_weight": 35, "base_cost": 85.0},
    {"name": "XXL Box",   "length": 80, "width": 60, "height": 50, "max_weight": 50, "base_cost": 120.0},
]

# ─── Genetic Algorithm Hyperparameters ────────────────────────────────────────
GA_POPULATION_SIZE = 30
GA_GENERATIONS = 50
GA_MUTATION_RATE = 0.15
GA_TOURNAMENT_K = 3

# ─── Tracking Statuses ────────────────────────────────────────────────────────
TRACKING_STATUSES = ["In Transit", "Delivered", "Delayed", "Processing"]
STATUS_WEIGHTS   = [0.50,         0.25,        0.15,       0.10]
