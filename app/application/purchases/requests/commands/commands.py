"""Commands for purchase request management."""
from dataclasses import dataclass
from decimal import Decimal
from datetime import date
from typing import List, Optional
from app.application.common.cqrs import Command


@dataclass
class CreatePurchaseRequestCommand(Command):
    """Command to create a new purchase request."""
    requested_by: int
    requested_date: Optional[date] = None
    required_date: Optional[date] = None
    notes: Optional[str] = None
    internal_notes: Optional[str] = None
    lines: Optional[List['PurchaseRequestLineInput']] = None


@dataclass
class PurchaseRequestLineInput:
    """Input for a purchase request line."""
    product_id: int
    quantity: Decimal
    unit_price_estimate: Optional[Decimal] = None
    notes: Optional[str] = None


@dataclass
class SubmitPurchaseRequestCommand(Command):
    """Command to submit a purchase request for approval."""
    purchase_request_id: int


@dataclass
class ApprovePurchaseRequestCommand(Command):
    """Command to approve a purchase request."""
    purchase_request_id: int
    approved_by: int


@dataclass
class RejectPurchaseRequestCommand(Command):
    """Command to reject a purchase request."""
    purchase_request_id: int
    rejected_by: int
    reason: str


@dataclass
class ConvertPurchaseRequestCommand(Command):
    """Command to convert an approved purchase request to a purchase order."""
    purchase_request_id: int
    supplier_id: int
    created_by: int
    order_date: Optional[date] = None
    expected_delivery_date: Optional[date] = None




