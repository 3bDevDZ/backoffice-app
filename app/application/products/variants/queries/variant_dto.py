"""DTOs for Product Variant responses."""
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
from datetime import datetime


@dataclass
class ProductVariantDTO:
    """DTO for product variant information."""
    id: int
    product_id: int
    product_code: str
    product_name: str
    code: str
    name: str
    attributes: Optional[str] = None
    price: Optional[Decimal] = None
    cost: Optional[Decimal] = None
    barcode: Optional[str] = None
    status: str = "active"
    created_at: Optional[datetime] = None

