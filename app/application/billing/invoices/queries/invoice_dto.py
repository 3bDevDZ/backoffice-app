"""Invoice DTOs for API responses."""
from dataclasses import dataclass
from decimal import Decimal
from datetime import date, datetime
from typing import List, Optional


@dataclass
class InvoiceLineDTO:
    """DTO for invoice line."""
    id: int
    product_id: int
    product_code: Optional[str]
    product_name: Optional[str]
    variant_id: Optional[int]
    variant_code: Optional[str]
    variant_name: Optional[str]
    order_line_id: Optional[int]
    description: Optional[str]
    quantity: Decimal
    unit_price: Decimal
    discount_percent: Decimal
    discount_amount: Decimal
    tax_rate: Decimal
    line_total_ht: Decimal
    line_total_ttc: Decimal
    sequence: int


@dataclass
class CreditNoteDTO:
    """DTO for credit note."""
    id: int
    number: str
    invoice_id: int
    invoice_number: str
    customer_id: int
    customer_code: Optional[str]
    customer_name: Optional[str]
    reason: str
    total_amount: Decimal
    tax_amount: Decimal
    total_ttc: Decimal
    status: str
    created_by: int
    created_by_name: Optional[str]
    validated_by: Optional[int]
    validated_by_name: Optional[str]
    validated_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


@dataclass
class InvoiceDTO:
    """DTO for invoice."""
    id: int
    number: str
    order_id: Optional[int]
    order_number: Optional[str]
    customer_id: int
    customer_code: Optional[str]
    customer_name: Optional[str]
    invoice_date: date
    due_date: date
    status: str
    subtotal: Decimal
    discount_percent: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    total: Decimal
    paid_amount: Decimal
    remaining_amount: Decimal
    vat_number: Optional[str]
    siret: Optional[str]
    legal_mention: Optional[str]
    notes: Optional[str]
    internal_notes: Optional[str]
    sent_at: Optional[datetime]
    sent_by: Optional[int]
    sent_by_name: Optional[str]
    email_sent: bool
    validated_at: Optional[datetime]
    validated_by: Optional[int]
    validated_by_name: Optional[str]
    created_by: int
    created_by_name: Optional[str]
    created_at: datetime
    updated_at: datetime
    lines: List[InvoiceLineDTO]
    credit_notes: List[CreditNoteDTO]

