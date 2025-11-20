"""Queries for site management."""
from dataclasses import dataclass
from typing import Optional

from app.application.common.cqrs import Query


@dataclass
class ListSitesQuery(Query):
    """Query to list sites."""
    page: int = 1
    per_page: int = 20
    status: Optional[str] = None  # 'active', 'inactive', 'archived'
    search: Optional[str] = None  # Search by code or name


@dataclass
class GetSiteByIdQuery(Query):
    """Query to get a specific site by ID."""
    id: int


@dataclass
class GetSiteStockQuery(Query):
    """Query to get stock for a specific site."""
    site_id: int
    product_id: Optional[int] = None
    variant_id: Optional[int] = None
    page: int = 1
    per_page: int = 50


