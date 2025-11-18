"""Queries for supplier invoice management."""
from dataclasses import dataclass
from datetime import date
from typing import Optional
from app.application.common.cqrs import Query


@dataclass
class ListSupplierInvoicesQuery(Query):
    """Query to list supplier invoices."""
    page: int = 1
    per_page: int = 50
    supplier_id: Optional[int] = None
    status: Optional[str] = None
    matching_status: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None


@dataclass
class GetSupplierInvoiceByIdQuery(Query):
    """Query to get a supplier invoice by ID."""
    id: int




