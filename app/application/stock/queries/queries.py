"""Queries for stock management."""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from decimal import Decimal

from app.application.common.cqrs import Query


@dataclass
class GetStockLevelsQuery(Query):
    """Query to get stock levels for products."""
    product_id: Optional[int] = None
    location_id: Optional[int] = None
    variant_id: Optional[int] = None
    page: int = 1
    per_page: int = 50
    search: Optional[str] = None  # Search by product code or name
    min_quantity: Optional[Decimal] = None  # Filter by minimum quantity
    include_zero: bool = False  # Include items with zero stock


@dataclass
class GetStockAlertsQuery(Query):
    """Query to get stock alerts (low stock, out of stock, etc.)."""
    location_id: Optional[int] = None
    alert_type: Optional[str] = None  # 'low_stock', 'out_of_stock', 'overstock'
    page: int = 1
    per_page: int = 50


@dataclass
class GetStockMovementsQuery(Query):
    """Query to get stock movements history."""
    stock_item_id: Optional[int] = None
    product_id: Optional[int] = None
    variant_id: Optional[int] = None  # Filter by variant ID
    location_id: Optional[int] = None
    movement_type: Optional[str] = None  # 'entry', 'exit', 'transfer', 'adjustment'
    related_document_type: Optional[str] = None  # 'purchase_order', 'order', 'inventory'
    related_document_id: Optional[int] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    page: int = 1
    per_page: int = 50


@dataclass
class GetLocationHierarchyQuery(Query):
    """Query to get location hierarchy."""
    parent_id: Optional[int] = None  # If None, returns root locations
    location_type: Optional[str] = None  # Filter by type
    include_inactive: bool = False


@dataclass
class GetStockItemByIdQuery(Query):
    """Query to get a specific stock item by ID."""
    id: int


@dataclass
class GetLocationByIdQuery(Query):
    """Query to get a specific location by ID."""
    id: int


@dataclass
class GlobalStockQuery(Query):
    """Query to get consolidated stock view across all sites."""
    product_id: Optional[int] = None
    variant_id: Optional[int] = None
    site_id: Optional[int] = None  # If provided, shows stock for specific site only
    include_zero: bool = False
    page: int = 1
    per_page: int = 50
    search: Optional[str] = None  # Search by product code or name

