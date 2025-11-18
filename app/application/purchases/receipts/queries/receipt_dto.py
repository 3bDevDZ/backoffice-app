"""DTOs for purchase receipt query responses."""
from dataclasses import dataclass
from decimal import Decimal
from datetime import date, datetime
from typing import List, Optional


@dataclass
class PurchaseReceiptLineDTO:
    """DTO for purchase receipt line."""
    id: int
    purchase_order_line_id: int
    product_id: int
    product_code: Optional[str] = None
    product_name: Optional[str] = None
    quantity_ordered: Decimal = Decimal(0)
    quantity_received: Decimal = Decimal(0)
    quantity_discrepancy: Decimal = Decimal(0)
    discrepancy_reason: Optional[str] = None
    quality_notes: Optional[str] = None
    location_id: Optional[int] = None
    location_code: Optional[str] = None
    sequence: int = 0


@dataclass
class PurchaseReceiptDTO:
    """DTO for purchase receipt information."""
    id: int
    number: str
    purchase_order_id: int
    purchase_order_number: Optional[str] = None
    receipt_date: date = None
    received_by: int = 0
    received_by_name: Optional[str] = None
    status: str = "draft"
    validated_by: Optional[int] = None
    validated_by_name: Optional[str] = None
    validated_at: Optional[datetime] = None
    notes: Optional[str] = None
    internal_notes: Optional[str] = None
    lines: Optional[List[PurchaseReceiptLineDTO]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None




