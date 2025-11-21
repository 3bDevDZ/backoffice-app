"""DTOs for stock transfer query responses."""
from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime
from typing import List, Optional


@dataclass
class StockTransferLineDTO:
    """DTO for stock transfer line."""
    id: int
    product_id: int
    product_code: Optional[str] = None
    product_name: Optional[str] = None
    variant_id: Optional[int] = None
    quantity: Decimal = Decimal('0')
    quantity_received: Decimal = Decimal('0')
    sequence: int = 0
    notes: Optional[str] = None


@dataclass
class StockTransferDTO:
    """DTO for stock transfer information."""
    id: int
    number: str
    source_site_id: int
    destination_site_id: int
    created_by: int
    source_site_code: Optional[str] = None
    source_site_name: Optional[str] = None
    destination_site_code: Optional[str] = None
    destination_site_name: Optional[str] = None
    status: str = 'created'
    requested_date: Optional[datetime] = None
    shipped_date: Optional[datetime] = None
    received_date: Optional[datetime] = None
    shipped_by: Optional[int] = None
    shipped_by_name: Optional[str] = None
    received_by: Optional[int] = None
    received_by_name: Optional[str] = None
    notes: Optional[str] = None
    created_by_name: Optional[str] = None
    lines: Optional[List[StockTransferLineDTO]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


