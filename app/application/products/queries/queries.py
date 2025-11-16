from dataclasses import dataclass
from typing import Optional
from app.application.common.cqrs import Query


# Product Queries
@dataclass
class GetProductByIdQuery(Query):
    id: int


@dataclass
class ListProductsQuery(Query):
    page: int = 1
    per_page: int = 10
    search: Optional[str] = None
    category_id: Optional[int] = None
    status: Optional[str] = None


@dataclass
class SearchProductsQuery(Query):
    search_term: str
    limit: int = 20


# Category Queries
@dataclass
class GetCategoryByIdQuery(Query):
    id: int


@dataclass
class ListCategoriesQuery(Query):
    parent_id: Optional[int] = None


# Price History Queries
@dataclass
class GetPriceHistoryQuery(Query):
    product_id: int
    limit: Optional[int] = 100  # Limit number of history entries


# Cost History Queries
@dataclass
class GetCostHistoryQuery(Query):
    product_id: int
    limit: Optional[int] = 100  # Limit number of history entries