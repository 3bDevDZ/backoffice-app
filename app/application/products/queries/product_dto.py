from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional
from datetime import datetime


@dataclass
class CategoryDTO:
    id: int
    name: str
    code: Optional[str] = None
    parent_id: Optional[int] = None
    description: Optional[str] = None


@dataclass
class ProductDTO:
    id: int
    code: str
    name: str
    description: Optional[str]
    price: Decimal
    cost: Optional[Decimal]
    unit_of_measure: Optional[str]
    barcode: Optional[str]
    status: str
    category_ids: List[int] = None
    categories: List[CategoryDTO] = None


@dataclass
class ProductPriceHistoryDTO:
    """DTO for product price history entries."""
    id: int
    product_id: int
    old_price: Optional[Decimal]
    new_price: Decimal
    changed_by: Optional[int]
    changed_by_username: Optional[str]
    changed_at: datetime
    reason: Optional[str]


@dataclass
class ProductCostHistoryDTO:
    """DTO for product cost history entries (AVCO method)."""
    id: int
    product_id: int
    old_cost: Optional[Decimal]
    new_cost: Decimal
    old_stock: Optional[Decimal]
    new_stock: Decimal
    purchase_price: Decimal
    quantity_received: Decimal
    changed_by: Optional[int]
    changed_by_username: Optional[str]
    changed_at: datetime
    reason: Optional[str]
    purchase_order_id: Optional[int]
    purchase_order_line_id: Optional[int]