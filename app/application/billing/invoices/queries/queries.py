"""Invoice query DTOs for CQRS."""
from dataclasses import dataclass
from datetime import date
from typing import Optional
from app.application.common.cqrs import Query


@dataclass
class ListInvoicesQuery(Query):
    """Query to list invoices with optional filters."""
    page: int = 1
    per_page: int = 50
    status: Optional[str] = None
    customer_id: Optional[int] = None
    order_id: Optional[int] = None
    search: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None


@dataclass
class GetInvoiceByIdQuery(Query):
    """Query to get an invoice by ID."""
    id: int


@dataclass
class GetInvoiceHistoryQuery(Query):
    """Query to get invoice history (status changes, payments, etc.)."""
    invoice_id: int

