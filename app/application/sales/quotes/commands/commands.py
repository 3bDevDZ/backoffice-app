"""Quote command DTOs for CQRS."""
from dataclasses import dataclass, field
from decimal import Decimal
from datetime import date
from typing import List, Optional
from app.application.common.cqrs import Command


@dataclass
class QuoteLineInput:
    """Input DTO for quote line creation."""
    product_id: int
    quantity: Decimal
    unit_price: Decimal
    variant_id: int = None
    discount_percent: Decimal = Decimal(0)
    tax_rate: Decimal = Decimal(20.0)


@dataclass
class CreateQuoteCommand(Command):
    """Command to create a new quote."""
    customer_id: int
    created_by: int
    number: str = None
    valid_until: date = None
    discount_percent: Decimal = Decimal(0)
    notes: str = None
    internal_notes: str = None
    lines: List[QuoteLineInput] = field(default_factory=list)


@dataclass
class UpdateQuoteCommand(Command):
    """Command to update an existing quote."""
    id: int
    valid_until: date = None
    discount_percent: Decimal = None
    notes: str = None
    internal_notes: str = None


@dataclass
class AddQuoteLineCommand(Command):
    """Command to add a line to a quote."""
    quote_id: int
    product_id: int
    quantity: Decimal
    unit_price: Decimal
    variant_id: int = None
    discount_percent: Decimal = Decimal(0)
    tax_rate: Decimal = Decimal(20.0)


@dataclass
class UpdateQuoteLineCommand(Command):
    """Command to update a quote line."""
    quote_id: int
    line_id: int
    quantity: Decimal = None
    unit_price: Decimal = None
    discount_percent: Decimal = None
    tax_rate: Decimal = None


@dataclass
class RemoveQuoteLineCommand(Command):
    """Command to remove a line from a quote."""
    quote_id: int
    line_id: int


@dataclass
class SendQuoteCommand(Command):
    """Command to send a quote to customer."""
    id: int
    sent_by: int


@dataclass
class AcceptQuoteCommand(Command):
    """Command to accept a quote."""
    id: int


@dataclass
class RejectQuoteCommand(Command):
    """Command to reject a quote."""
    id: int


@dataclass
class CancelQuoteCommand(Command):
    """Command to cancel a quote."""
    id: int


@dataclass
class DeleteQuoteCommand(Command):
    """Command to delete a draft quote."""
    id: int


@dataclass
class ConvertQuoteToOrderCommand(Command):
    """Command to convert an accepted quote to an order."""
    id: int
    created_by: int

