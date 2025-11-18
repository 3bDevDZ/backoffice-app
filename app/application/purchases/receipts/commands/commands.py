"""Commands for purchase receipt management."""
from dataclasses import dataclass
from decimal import Decimal
from datetime import date
from typing import List, Optional
from app.application.common.cqrs import Command


@dataclass
class CreatePurchaseReceiptCommand(Command):
    """Command to create a new purchase receipt."""
    purchase_order_id: int
    received_by: int
    receipt_date: Optional[date] = None
    notes: Optional[str] = None
    internal_notes: Optional[str] = None
    lines: Optional[List['PurchaseReceiptLineInput']] = None


@dataclass
class PurchaseReceiptLineInput:
    """Input for a purchase receipt line."""
    purchase_order_line_id: int
    product_id: int
    quantity_ordered: Decimal
    quantity_received: Decimal
    location_id: Optional[int] = None
    discrepancy_reason: Optional[str] = None
    quality_notes: Optional[str] = None


@dataclass
class ValidatePurchaseReceiptCommand(Command):
    """Command to validate a purchase receipt (triggers stock movements)."""
    purchase_receipt_id: int
    validated_by: int




