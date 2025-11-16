"""Queries for customer management."""
from dataclasses import dataclass
from typing import Optional
from app.application.common.cqrs import Query


@dataclass
class GetCustomerByIdQuery(Query):
    id: int


@dataclass
class ListCustomersQuery(Query):
    page: int = 1
    per_page: int = 20
    search: Optional[str] = None
    type: Optional[str] = None  # 'B2B' or 'B2C'
    status: Optional[str] = None  # 'active', 'inactive', 'archived', 'blocked'
    category: Optional[str] = None


@dataclass
class SearchCustomersQuery(Query):
    search_term: str
    limit: int = 20


@dataclass
class GetCustomerHistoryQuery(Query):
    customer_id: int
    limit: int = 50
