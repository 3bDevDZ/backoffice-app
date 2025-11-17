"""Payment DTOs for query responses."""
from dataclasses import dataclass
from decimal import Decimal
from datetime import date, datetime
from typing import List, Optional


@dataclass
class PaymentAllocationDTO:
    """DTO for payment allocation."""
    id: int
    invoice_id: int
    invoice_number: Optional[str] = None
    allocated_amount: Decimal = Decimal(0)
    created_at: Optional[datetime] = None


@dataclass
class PaymentDTO:
    """DTO for payment information."""
    id: int
    customer_id: int
    payment_method: str
    amount: Decimal
    payment_date: date
    status: str
    # Optional fields with defaults
    customer_code: Optional[str] = None
    customer_name: Optional[str] = None
    value_date: Optional[date] = None
    reference: Optional[str] = None
    bank_reference: Optional[str] = None
    bank_account: Optional[str] = None
    reconciled: bool = False
    reconciled_at: Optional[datetime] = None
    notes: Optional[str] = None
    internal_notes: Optional[str] = None
    total_allocated: Decimal = Decimal(0)
    unallocated_amount: Decimal = Decimal(0)
    allocations: Optional[List[PaymentAllocationDTO]] = None
    created_at: Optional[datetime] = None
    created_by: Optional[int] = None


@dataclass
class OverdueInvoiceDTO:
    """DTO for overdue invoice information."""
    invoice_id: int
    invoice_number: str
    customer_id: int
    invoice_date: date
    due_date: date
    total: Decimal
    paid_amount: Decimal
    remaining_amount: Decimal
    days_overdue: int
    status: str
    # Optional fields with defaults
    customer_code: Optional[str] = None
    customer_name: Optional[str] = None


@dataclass
class AgingBucketDTO:
    """DTO for aging bucket (0-30, 31-60, 61-90, 90+ days)."""
    bucket_name: str
    total_amount: Decimal
    invoice_count: int


@dataclass
class AgingReportDTO:
    """DTO for aging report."""
    customer_id: Optional[int] = None
    customer_code: Optional[str] = None
    customer_name: Optional[str] = None
    total_outstanding: Decimal = Decimal(0)
    buckets: Optional[List[AgingBucketDTO]] = None
    invoices: Optional[List[OverdueInvoiceDTO]] = None

