"""Queries for purchase management."""
from dataclasses import dataclass
from typing import Optional
from app.application.common.cqrs import Query


@dataclass
class GetSupplierByIdQuery(Query):
    id: int


@dataclass
class ListSuppliersQuery(Query):
    page: int = 1
    per_page: int = 20
    search: Optional[str] = None
    status: Optional[str] = None  # 'active', 'inactive', 'archived', 'blocked'
    category: Optional[str] = None


@dataclass
class SearchSuppliersQuery(Query):
    search_term: str
    limit: int = 20


@dataclass
class GetPurchaseOrderByIdQuery(Query):
    id: int


@dataclass
class ListPurchaseOrdersQuery(Query):
    page: int = 1
    per_page: int = 20
    supplier_id: Optional[int] = None
    status: Optional[str] = None  # 'draft', 'sent', 'confirmed', 'partially_received', 'received', 'cancelled'
    search: Optional[str] = None

