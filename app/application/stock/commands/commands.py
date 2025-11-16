"""Commands for stock management."""
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
from datetime import datetime

from app.application.common.cqrs import Command


@dataclass
class CreateLocationCommand(Command):
    """Command to create a new location."""
    code: str
    name: str
    type: str  # 'warehouse', 'zone', 'aisle', 'shelf', 'level', 'virtual'
    parent_id: Optional[int] = None
    capacity: Optional[Decimal] = None
    is_active: bool = True


@dataclass
class UpdateLocationCommand(Command):
    """Command to update an existing location."""
    id: int
    code: Optional[str] = None
    name: Optional[str] = None
    type: Optional[str] = None
    parent_id: Optional[int] = None
    capacity: Optional[Decimal] = None
    is_active: Optional[bool] = None


@dataclass
class CreateStockItemCommand(Command):
    """Command to create a new stock item."""
    product_id: int
    location_id: int
    physical_quantity: Decimal = Decimal('0')
    variant_id: Optional[int] = None
    min_stock: Optional[Decimal] = None
    max_stock: Optional[Decimal] = None
    reorder_point: Optional[Decimal] = None
    reorder_quantity: Optional[Decimal] = None
    valuation_method: str = 'standard'


@dataclass
class UpdateStockItemCommand(Command):
    """Command to update an existing stock item."""
    id: int
    min_stock: Optional[Decimal] = None
    max_stock: Optional[Decimal] = None
    reorder_point: Optional[Decimal] = None
    reorder_quantity: Optional[Decimal] = None
    valuation_method: Optional[str] = None


@dataclass
class CreateStockMovementCommand(Command):
    """Command to create a stock movement."""
    stock_item_id: int
    product_id: int
    quantity: Decimal
    movement_type: str  # 'entry', 'exit', 'transfer', 'adjustment'
    user_id: int
    location_from_id: Optional[int] = None
    location_to_id: Optional[int] = None
    variant_id: Optional[int] = None
    reason: Optional[str] = None
    related_document_type: Optional[str] = None
    related_document_id: Optional[int] = None


@dataclass
class ReserveStockCommand(Command):
    """Command to reserve stock for an order."""
    product_id: int
    location_id: int
    quantity: Decimal
    variant_id: Optional[int] = None


@dataclass
class ReleaseStockCommand(Command):
    """Command to release reserved stock."""
    product_id: int
    location_id: int
    quantity: Decimal
    variant_id: Optional[int] = None


@dataclass
class AdjustStockCommand(Command):
    """Command to adjust stock (for inventory adjustments)."""
    product_id: int
    location_id: int
    quantity: Decimal  # Positive for increase, negative for decrease
    reason: str
    user_id: int
    variant_id: Optional[int] = None






