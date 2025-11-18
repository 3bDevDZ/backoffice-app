"""DTOs for purchase request query responses."""
from dataclasses import dataclass
from decimal import Decimal
from datetime import date, datetime
from typing import List, Optional


@dataclass
class PurchaseRequestLineDTO:
    """DTO for purchase request line."""
    id: int
    product_id: int
    product_code: Optional[str] = None
    product_name: Optional[str] = None
    quantity: Decimal = Decimal(0)
    unit_price_estimate: Optional[Decimal] = None
    notes: Optional[str] = None
    sequence: int = 0


@dataclass
class PurchaseRequestDTO:
    """DTO for purchase request information."""
    id: int
    number: str
    requested_by: int = 0
    requested_by_name: Optional[str] = None
    requested_date: date = None
    required_date: Optional[date] = None
    status: str = "draft"
    approved_by: Optional[int] = None
    approved_by_name: Optional[str] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    converted_to_po_id: Optional[int] = None
    converted_to_po_number: Optional[str] = None
    converted_at: Optional[datetime] = None
    notes: Optional[str] = None
    internal_notes: Optional[str] = None
    lines: Optional[List[PurchaseRequestLineDTO]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None




