"""Order query DTOs for CQRS."""
from dataclasses import dataclass
from typing import Optional
from datetime import date
from app.application.common.cqrs import Query


@dataclass
class ListOrdersQuery(Query):
    """Query to list orders with optional filtering."""
    status: Optional[str] = None  # Filter by status
    customer_id: Optional[int] = None  # Filter by customer
    page: int = 1
    per_page: int = 20
    search: Optional[str] = None  # Search in order number or customer name
    date_from: Optional[date] = None  # Filter by creation date from
    date_to: Optional[date] = None  # Filter by creation date to


@dataclass
class GetOrderByIdQuery(Query):
    """Query to get an order by ID."""
    order_id: int
    include_lines: bool = True
    include_reservations: bool = False


@dataclass
class GetOrderHistoryQuery(Query):
    """Query to get order status history."""
    order_id: int
    page: int = 1
    per_page: int = 20

