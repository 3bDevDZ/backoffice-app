"""Queries for Product Variant management."""
from dataclasses import dataclass
from typing import Optional
from app.application.common.cqrs import Query


@dataclass
class GetVariantByIdQuery(Query):
    """Query to get a variant by ID."""
    id: int


@dataclass
class GetVariantsByProductQuery(Query):
    """Query to get all variants for a product."""
    product_id: int
    include_archived: bool = False


@dataclass
class ListVariantsQuery(Query):
    """Query to list variants with optional filters."""
    page: int = 1
    per_page: int = 20
    product_id: Optional[int] = None
    status: Optional[str] = None  # 'active' or 'archived'
    search: Optional[str] = None

