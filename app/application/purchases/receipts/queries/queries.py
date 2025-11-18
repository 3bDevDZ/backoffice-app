"""Queries for purchase receipt management."""
from dataclasses import dataclass
from datetime import date
from typing import Optional
from app.application.common.cqrs import Query


@dataclass
class ListPurchaseReceiptsQuery(Query):
    """Query to list purchase receipts."""
    page: int = 1
    per_page: int = 50
    purchase_order_id: Optional[int] = None
    status: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None


@dataclass
class GetPurchaseReceiptByIdQuery(Query):
    """Query to get a purchase receipt by ID."""
    id: int




