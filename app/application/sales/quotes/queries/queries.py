"""Quote query DTOs for CQRS."""
from dataclasses import dataclass
from typing import Optional, List
from app.application.common.cqrs import Query


@dataclass
class ListQuotesQuery(Query):
    """Query to list quotes with optional filtering."""
    status: Optional[str] = None  # Filter by status
    customer_id: Optional[int] = None  # Filter by customer
    page: int = 1
    per_page: int = 20
    search: Optional[str] = None  # Search in quote number or customer name


@dataclass
class GetQuoteByIdQuery(Query):
    """Query to get a quote by ID."""
    id: int
    include_lines: bool = True
    include_versions: bool = False


@dataclass
class GetQuoteHistoryQuery(Query):
    """Query to get quote version history."""
    quote_id: int
    page: int = 1
    per_page: int = 20

