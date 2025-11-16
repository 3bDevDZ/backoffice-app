"""Invoice command DTOs for CQRS."""
from dataclasses import dataclass, field
from decimal import Decimal
from datetime import date
from typing import List, Optional
from app.application.common.cqrs import Command


@dataclass
class InvoiceLineInput:
    """Input DTO for invoice line creation."""
    product_id: int
    quantity: Decimal
    unit_price: Decimal
    order_line_id: Optional[int] = None
    variant_id: Optional[int] = None
    description: Optional[str] = None
    discount_percent: Decimal = Decimal(0)
    tax_rate: Decimal = Decimal(20.0)


@dataclass
class CreateInvoiceCommand(Command):
    """Command to create a new invoice from an order."""
    order_id: int
    customer_id: int
    invoice_date: date
    due_date: date
    created_by: int
    number: Optional[str] = None
    notes: Optional[str] = None
    internal_notes: Optional[str] = None
    discount_percent: Decimal = Decimal(0)
    lines: List[InvoiceLineInput] = field(default_factory=list)


@dataclass
class ValidateInvoiceCommand(Command):
    """Command to validate an invoice (make it official)."""
    id: int
    validated_by: int


@dataclass
class SendInvoiceCommand(Command):
    """Command to send an invoice to customer."""
    id: int
    sent_by: int


@dataclass
class CreateCreditNoteCommand(Command):
    """Command to create a credit note for an invoice."""
    invoice_id: int
    customer_id: int
    reason: str
    total_amount: Decimal
    tax_amount: Decimal = Decimal(0)
    created_by: int = None
    number: Optional[str] = None

