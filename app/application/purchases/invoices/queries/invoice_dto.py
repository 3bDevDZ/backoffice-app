"""DTOs for supplier invoice query responses."""
from dataclasses import dataclass
from decimal import Decimal
from datetime import date, datetime
from typing import Optional


@dataclass
class SupplierInvoiceDTO:
    """DTO for supplier invoice information."""
    id: int
    number: str
    supplier_id: int = 0
    supplier_name: Optional[str] = None
    invoice_date: date = None
    due_date: Optional[date] = None
    received_date: date = None
    subtotal_ht: Decimal = Decimal(0)
    tax_amount: Decimal = Decimal(0)
    total_ttc: Decimal = Decimal(0)
    paid_amount: Decimal = Decimal(0)
    remaining_amount: Decimal = Decimal(0)
    status: str = "draft"
    matched_purchase_order_id: Optional[int] = None
    matched_purchase_order_number: Optional[str] = None
    matched_purchase_receipt_id: Optional[int] = None
    matched_purchase_receipt_number: Optional[str] = None
    matching_status: Optional[str] = None
    matching_notes: Optional[str] = None
    matched_by: Optional[int] = None
    matched_by_name: Optional[str] = None
    matched_at: Optional[datetime] = None
    notes: Optional[str] = None
    internal_notes: Optional[str] = None
    created_by: int = 0
    created_by_name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None




