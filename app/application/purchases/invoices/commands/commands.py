"""Commands for supplier invoice management."""
from dataclasses import dataclass
from decimal import Decimal
from datetime import date
from typing import Optional
from app.application.common.cqrs import Command


@dataclass
class CreateSupplierInvoiceCommand(Command):
    """Command to create a new supplier invoice."""
    number: str
    supplier_id: int
    invoice_date: date
    subtotal_ht: Decimal
    tax_amount: Decimal
    total_ttc: Decimal
    created_by: int
    due_date: Optional[date] = None
    received_date: Optional[date] = None
    notes: Optional[str] = None
    internal_notes: Optional[str] = None


@dataclass
class MatchSupplierInvoiceCommand(Command):
    """Command to match a supplier invoice with purchase order and receipt (3-way matching)."""
    supplier_invoice_id: int
    purchase_order_id: int
    purchase_receipt_id: Optional[int] = None
    matched_by: int = None




