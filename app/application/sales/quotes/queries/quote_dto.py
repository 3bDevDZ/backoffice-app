"""DTOs for quote queries."""
from dataclasses import dataclass
from decimal import Decimal
from datetime import date, datetime
from typing import List, Optional


@dataclass
class QuoteLineDTO:
    id: int
    quote_id: int
    product_id: int
    product_code: Optional[str] = None
    product_name: Optional[str] = None
    variant_id: Optional[int] = None
    quantity: Decimal = Decimal(0)
    unit_price: Decimal = Decimal(0)
    discount_percent: Decimal = Decimal(0)
    discount_amount: Decimal = Decimal(0)
    tax_rate: Decimal = Decimal(20.0)
    line_total_ht: Decimal = Decimal(0)
    line_total_ttc: Decimal = Decimal(0)
    sequence: int = 1


@dataclass
class QuoteVersionDTO:
    id: int
    quote_id: int
    version_number: int
    created_by: int
    created_by_username: Optional[str] = None
    created_at: datetime = None
    data: dict = None  # JSON snapshot


@dataclass
class QuoteDTO:
    id: int
    number: str
    version: int
    customer_id: int
    customer_code: Optional[str] = None
    customer_name: Optional[str] = None
    status: str = 'draft'
    valid_until: date = None
    subtotal: Decimal = Decimal(0)
    tax_amount: Decimal = Decimal(0)
    total: Decimal = Decimal(0)
    discount_percent: Decimal = Decimal(0)
    discount_amount: Decimal = Decimal(0)
    notes: Optional[str] = None
    internal_notes: Optional[str] = None
    sent_at: Optional[datetime] = None
    sent_by: Optional[int] = None
    sent_by_username: Optional[str] = None
    accepted_at: Optional[datetime] = None
    created_by: int = 0
    created_by_username: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    # Relationships
    lines: List[QuoteLineDTO] = None
    versions: List[QuoteVersionDTO] = None

