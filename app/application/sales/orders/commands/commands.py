"""Command DTOs for order operations."""
from dataclasses import dataclass
from decimal import Decimal
from datetime import date, datetime
from typing import Optional, List
from app.application.common.cqrs import Command


@dataclass
class CreateOrderCommand(Command):
    """Command to create a new order."""
    customer_id: int
    created_by: int
    quote_id: Optional[int] = None
    delivery_address_id: Optional[int] = None
    delivery_date_requested: Optional[date] = None
    delivery_date_promised: Optional[date] = None
    delivery_instructions: Optional[str] = None
    notes: Optional[str] = None
    discount_percent: Decimal = Decimal('0')


@dataclass
class UpdateOrderCommand(Command):
    """Command to update an existing order."""
    order_id: int
    delivery_address_id: Optional[int] = None
    delivery_date_requested: Optional[date] = None
    delivery_date_promised: Optional[date] = None
    delivery_instructions: Optional[str] = None
    notes: Optional[str] = None
    discount_percent: Optional[Decimal] = None


@dataclass
class ConfirmOrderCommand(Command):
    """Command to confirm an order."""
    order_id: int
    confirmed_by: int


@dataclass
class CancelOrderCommand(Command):
    """Command to cancel an order."""
    order_id: int


@dataclass
class UpdateOrderStatusCommand(Command):
    """Command to update order status."""
    order_id: int
    new_status: str
    updated_by: Optional[int] = None


@dataclass
class AddOrderLineCommand(Command):
    """Command to add a line to an order."""
    order_id: int
    product_id: int
    quantity: Decimal
    unit_price: Decimal
    variant_id: Optional[int] = None
    discount_percent: Decimal = Decimal(0)
    tax_rate: Decimal = Decimal(20.0)


@dataclass
class UpdateOrderLineCommand(Command):
    """Command to update an order line."""
    order_id: int
    line_id: int
    quantity: Optional[Decimal] = None
    unit_price: Optional[Decimal] = None
    discount_percent: Optional[Decimal] = None
    tax_rate: Optional[Decimal] = None


@dataclass
class RemoveOrderLineCommand(Command):
    """Command to remove a line from an order."""
    order_id: int
    line_id: int

