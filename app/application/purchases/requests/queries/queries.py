"""Queries for purchase request management."""
from dataclasses import dataclass
from datetime import date
from typing import Optional
from app.application.common.cqrs import Query


@dataclass
class ListPurchaseRequestsQuery(Query):
    """Query to list purchase requests."""
    page: int = 1
    per_page: int = 50
    status: Optional[str] = None
    requested_by: Optional[int] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None


@dataclass
class GetPurchaseRequestByIdQuery(Query):
    """Query to get a purchase request by ID."""
    id: int




