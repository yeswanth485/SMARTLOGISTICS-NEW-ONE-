"""
SmartLogistics – CSV Service
Parses uploaded CSV files into ProductInput lists.
"""
import csv
import io
import logging
from typing import List, Optional
from app.schemas.product import ProductInput

logger = logging.getLogger(__name__)


async def parse_csv(content: bytes) -> List[ProductInput]:
    """Parse CSV bytes to list of ProductInput with strict validation."""
    text_content = content.decode('utf-8-sig')
    reader = csv.DictReader(io.StringIO(text_content))
    
    if not reader.fieldnames or len(reader.fieldnames) < 3:
        raise ValueError("Invalid CSV headers. Required: name, length, width, height, weight")
    
    products = []
    for row_num, row in enumerate(reader, start=2):  # line 2+
        if not any(row.values()):  # skip empty
            continue
        row_clean = {k.lower().strip(): v.strip() for k, v in row.items() if v.strip()}

        name = row_clean.get("name") or row_clean.get("item") or row_clean.get("product")
        if not name:
            raise ValueError(f"Row {row_num}: Missing product 'name'")

        product_dict = {
            "name": name,
            "length": validate_float(row_clean.get("length") or row_clean.get("l"), "length", row_num),
            "width": validate_float(row_clean.get("width") or row_clean.get("w"), "width", row_num),
            "height": validate_float(row_clean.get("height") or row_clean.get("h"), "height", row_num),
            "weight": validate_float(row_clean.get("weight") or row_clean.get("wt"), "weight", row_num),
            "quantity": validate_int(row_clean.get("quantity") or row_clean.get("qty") or "1", "quantity", row_num, min_val=1),
        }
        products.append(ProductInput(**product_dict))
            
    if not products:
        raise ValueError("No valid data rows found in CSV.")
        
    logger.info(f"Parsed {len(products)} valid products from CSV")
    return products


def validate_float(val: Optional[str], col_name: str, row_num: int) -> float:
    """Strict float parse, must be > 0."""
    if not val:
        raise ValueError(f"Row {row_num}: Missing '{col_name}'")
    try:
        f = float(val)
        if f <= 0:
            raise ValueError(f"Row {row_num}: '{col_name}' must be greater than 0")
        return f
    except ValueError as e:
        if "must be greater than 0" in str(e) or "Missing" in str(e):
            raise
        raise ValueError(f"Row {row_num}: '{col_name}' is not a valid number (got '{val}')")


def validate_int(val: Optional[str], col_name: str, row_num: int, min_val: int = 1) -> int:
    """Strict int parse, must be >= min_val."""
    if not val:
        raise ValueError(f"Row {row_num}: Missing '{col_name}'")
    try:
        i = int(val)
        if i < min_val:
            raise ValueError(f"Row {row_num}: '{col_name}' must be at least {min_val}")
        return i
    except ValueError as e:
        if "must be at least" in str(e) or "Missing" in str(e):
            raise
        raise ValueError(f"Row {row_num}: '{col_name}' is not a valid integer (got '{val}')")
