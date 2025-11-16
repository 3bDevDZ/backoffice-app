"""DTOs for Price List management."""
from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional
from datetime import datetime


@dataclass
class PriceListDTO:
    """DTO for price list."""
    id: int
    name: str
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    product_count: int = 0  # Number of products in this price list


@dataclass
class ProductPriceListDTO:
    """DTO for product price in a price list."""
    id: int
    price_list_id: int
    price_list_name: str
    product_id: int
    product_code: str
    product_name: str
    price: Decimal
    base_price: Decimal  # Product's base price for comparison
    created_at: datetime
    updated_at: datetime


@dataclass
class ProductVolumePricingDTO:
    """DTO for ProductVolumePricing (volume pricing tier)."""
    id: int
    product_id: int
    min_quantity: Decimal
    max_quantity: Optional[Decimal]  # None = unlimited
    price: Decimal
    created_at: datetime
    updated_at: datetime


@dataclass
class ProductPromotionalPriceDTO:
    """DTO for ProductPromotionalPrice (promotional price)."""
    id: int
    product_id: int
    price: Decimal
    start_date: datetime
    end_date: datetime
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int]

