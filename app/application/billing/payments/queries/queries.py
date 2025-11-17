"""Payment query DTOs for CQRS."""
from dataclasses import dataclass
from decimal import Decimal
from datetime import date
from typing import Optional
from app.application.common.cqrs import Query


@dataclass
class ListPaymentsQuery(Query):
    """Query to list payments with filtering."""
    page: int = 1
    per_page: int = 50
    customer_id: Optional[int] = None
    status: Optional[str] = None  # 'pending', 'confirmed', 'reconciled', 'cancelled'
    payment_method: Optional[str] = None
    reconciled: Optional[bool] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    search: Optional[str] = None  # Search in reference, bank_reference


@dataclass
class GetPaymentByIdQuery(Query):
    """Query to get a payment by ID."""
    id: int
    include_allocations: bool = True
    include_invoices: bool = True


@dataclass
class GetOverdueInvoicesQuery(Query):
    """Query to get overdue invoices for a customer or all customers."""
    customer_id: Optional[int] = None
    days_overdue: Optional[int] = None  # Minimum days overdue
    page: int = 1
    per_page: int = 50


@dataclass
class GetAgingReportQuery(Query):
    """Query to get aging report for a customer or all customers."""
    customer_id: Optional[int] = None
    as_of_date: Optional[date] = None  # Default to today
    include_paid: bool = False  # Include paid invoices in report

