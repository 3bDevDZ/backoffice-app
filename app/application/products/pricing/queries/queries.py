"""Queries for Price List management."""
from dataclasses import dataclass
from typing import Optional
from app.application.common.cqrs import Query


@dataclass
class ListPriceListsQuery(Query):
    """Query to list all price lists."""
    page: int = 1
    per_page: int = 10
    search: Optional[str] = None
    is_active: Optional[bool] = None


@dataclass
class GetPriceListByIdQuery(Query):
    """Query to get a price list by ID."""
    id: int


@dataclass
class GetProductsInPriceListQuery(Query):
    """Query to get all products in a price list."""
    price_list_id: int
    page: int = 1
    per_page: int = 10
    search: Optional[str] = None


# ProductVolumePricing Queries
@dataclass
class GetVolumePricingQuery(Query):
    """Query to get all volume pricing tiers for a product."""
    product_id: int


# ProductPromotionalPrice Queries
@dataclass
class GetActivePromotionalPricesQuery(Query):
    """Query to get all active promotional prices (currently valid)."""
    product_id: Optional[int] = None  # If None, returns all active promotions


@dataclass
class GetPromotionalPricesByProductQuery(Query):
    """Query to get all promotional prices for a product (active and past)."""
    product_id: int
    include_expired: bool = True  # Include expired promotions

