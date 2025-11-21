"""Commands for stock transfer management."""
from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional, Dict
from datetime import datetime

from app.application.common.cqrs import Command


@dataclass
class StockTransferLineInput:
    """Input for a stock transfer line."""
    product_id: int
    variant_id: Optional[int] = None
    quantity: Decimal = Decimal('0')
    notes: Optional[str] = None


@dataclass
class CreateStockTransferCommand(Command):
    """Command to create a new stock transfer."""
    number: str
    source_site_id: int
    destination_site_id: int
    created_by: int
    requested_date: Optional[datetime] = None
    notes: Optional[str] = None
    lines: Optional[List[StockTransferLineInput]] = None


@dataclass
class ShipStockTransferCommand(Command):
    """Command to ship a stock transfer."""
    transfer_id: int
    shipped_by: int
    shipped_date: Optional[datetime] = None


@dataclass
class ReceiveStockTransferCommand(Command):
    """Command to receive a stock transfer."""
    transfer_id: int
    received_by: int
    received_date: Optional[datetime] = None
    received_quantities: Optional[Dict[int, Decimal]] = None  # Map line_id to received quantity


@dataclass
class CancelStockTransferCommand(Command):
    """Command to cancel a stock transfer."""
    transfer_id: int


