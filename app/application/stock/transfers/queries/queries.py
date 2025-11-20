"""Queries for stock transfer management."""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

from app.application.common.cqrs import Query


@dataclass
class ListStockTransfersQuery(Query):
    """Query to list stock transfers."""
    page: int = 1
    per_page: int = 20
    source_site_id: Optional[int] = None
    destination_site_id: Optional[int] = None
    status: Optional[str] = None  # 'created', 'in_transit', 'received', 'cancelled'
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


@dataclass
class GetStockTransferByIdQuery(Query):
    """Query to get a specific stock transfer by ID."""
    id: int


