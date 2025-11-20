"""DTOs for site query responses."""
from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime
from typing import Optional


@dataclass
class SiteDTO:
    """DTO for site information."""
    id: int
    code: str
    name: str
    address: Optional[str] = None
    manager_id: Optional[int] = None
    manager_name: Optional[str] = None
    status: str = 'active'
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class SiteStockItemDTO:
    """DTO for stock item at a site."""
    id: int
    product_id: int
    location_id: int
    product_code: Optional[str] = None
    product_name: Optional[str] = None
    variant_id: Optional[int] = None
    location_code: Optional[str] = None
    location_name: Optional[str] = None
    physical_quantity: Decimal = Decimal('0')
    reserved_quantity: Decimal = Decimal('0')
    available_quantity: Decimal = Decimal('0')


