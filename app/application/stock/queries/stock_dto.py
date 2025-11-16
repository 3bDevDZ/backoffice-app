"""DTOs for stock queries."""
from dataclasses import dataclass
from typing import Optional, List
from decimal import Decimal
from datetime import datetime


@dataclass
class LocationDTO:
    """DTO for Location."""
    id: int
    code: str
    name: str
    type: str  # 'warehouse', 'zone', 'aisle', 'shelf', 'level', 'virtual'
    parent_id: Optional[int] = None
    parent_name: Optional[str] = None
    capacity: Optional[Decimal] = None
    is_active: bool = True
    children: List['LocationDTO'] = None
    created_at: Optional[datetime] = None


@dataclass
class StockItemDTO:
    """DTO for StockItem."""
    id: int
    product_id: int
    location_id: int
    physical_quantity: Decimal = Decimal('0')
    reserved_quantity: Decimal = Decimal('0')
    available_quantity: Decimal = Decimal('0')
    product_code: Optional[str] = None
    product_name: Optional[str] = None
    variant_id: Optional[int] = None
    variant_code: Optional[str] = None  # Variant code
    variant_name: Optional[str] = None  # Variant name
    location_code: Optional[str] = None
    location_name: Optional[str] = None
    min_stock: Optional[Decimal] = None
    max_stock: Optional[Decimal] = None
    reorder_point: Optional[Decimal] = None
    reorder_quantity: Optional[Decimal] = None
    valuation_method: str = 'standard'
    last_movement_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    # Alert flags
    is_below_minimum: bool = False
    is_out_of_stock: bool = False
    is_overstock: bool = False


@dataclass
class StockMovementDTO:
    """DTO for StockMovement."""
    id: int
    stock_item_id: int
    product_id: int
    quantity: Decimal
    type: str  # 'entry', 'exit', 'transfer', 'adjustment'
    user_id: int
    created_at: datetime
    product_code: Optional[str] = None
    product_name: Optional[str] = None
    variant_id: Optional[int] = None
    variant_code: Optional[str] = None  # Variant code
    variant_name: Optional[str] = None  # Variant name
    location_from_id: Optional[int] = None
    location_from_code: Optional[str] = None
    location_from_name: Optional[str] = None
    location_to_id: Optional[int] = None
    location_to_code: Optional[str] = None
    location_to_name: Optional[str] = None
    reason: Optional[str] = None
    user_name: Optional[str] = None
    related_document_type: Optional[str] = None
    related_document_id: Optional[int] = None
    related_document_number: Optional[str] = None  # Order number, purchase order number, etc.


@dataclass
class StockAlertDTO:
    """DTO for stock alerts."""
    stock_item_id: int
    product_id: int
    product_code: str
    product_name: str
    location_id: int
    location_code: str
    location_name: str
    alert_type: str  # 'low_stock', 'out_of_stock', 'overstock'
    current_quantity: Decimal
    message: str
    threshold: Optional[Decimal] = None  # min_stock or max_stock depending on alert type

