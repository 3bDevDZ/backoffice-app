"""DTOs for order queries."""
from dataclasses import dataclass
from decimal import Decimal
from datetime import date, datetime
from typing import List, Optional


@dataclass
class OrderLineDTO:
    """DTO for order line."""
    id: int
    order_id: int
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
    quantity_delivered: Decimal = Decimal(0)
    quantity_invoiced: Decimal = Decimal(0)
    sequence: int = 1


@dataclass
class StockReservationDTO:
    """DTO for stock reservation."""
    id: int
    order_id: int
    order_line_id: int
    stock_item_id: int
    location_id: Optional[int] = None
    location_code: Optional[str] = None
    quantity: Decimal = Decimal(0)
    status: str = "reserved"  # 'reserved', 'fulfilled', 'released'
    reserved_at: Optional[datetime] = None
    released_at: Optional[datetime] = None


@dataclass
class OrderDTO:
    """DTO for order."""
    id: int
    number: str
    customer_id: int
    customer_code: Optional[str] = None
    customer_name: Optional[str] = None
    quote_id: Optional[int] = None
    quote_number: Optional[str] = None
    status: str = 'draft'
    # Delivery information
    delivery_address_id: Optional[int] = None
    delivery_date_requested: Optional[date] = None
    delivery_date_promised: Optional[date] = None
    delivery_date_actual: Optional[date] = None
    delivery_instructions: Optional[str] = None
    # Financial information
    subtotal: Decimal = Decimal(0)
    tax_amount: Decimal = Decimal(0)
    total: Decimal = Decimal(0)
    discount_percent: Decimal = Decimal(0)
    discount_amount: Decimal = Decimal(0)
    # Notes
    notes: Optional[str] = None
    # Audit fields
    confirmed_at: Optional[datetime] = None
    confirmed_by: Optional[int] = None
    confirmed_by_username: Optional[str] = None
    created_by: int = 0
    created_by_username: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    # Relationships
    lines: List[OrderLineDTO] = None
    stock_reservations: List[StockReservationDTO] = None

