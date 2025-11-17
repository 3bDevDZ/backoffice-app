"""Payment command DTOs for CQRS."""
from dataclasses import dataclass, field
from decimal import Decimal
from datetime import date
from typing import List, Optional
from app.application.common.cqrs import Command


@dataclass
class PaymentAllocationInput:
    """Input DTO for payment allocation."""
    invoice_id: int
    amount: Decimal


@dataclass
class CreatePaymentCommand(Command):
    """Command to create a new payment."""
    customer_id: int
    payment_method: str  # 'cash', 'check', 'bank_transfer', 'credit_card', 'debit_card', 'paypal', 'other'
    amount: Decimal
    payment_date: date
    value_date: Optional[date] = None
    reference: Optional[str] = None
    notes: Optional[str] = None
    internal_notes: Optional[str] = None
    created_by: Optional[int] = None
    allocations: List[PaymentAllocationInput] = field(default_factory=list)  # Optional initial allocations
    auto_allocation_strategy: Optional[str] = None  # 'fifo' or 'proportional' for automatic allocation


@dataclass
class AllocatePaymentCommand(Command):
    """Command to allocate a payment to one or more invoices."""
    payment_id: int
    allocations: List[PaymentAllocationInput]  # List of invoice_id and amount pairs
    created_by: Optional[int] = None


@dataclass
class ReconcilePaymentCommand(Command):
    """Command to reconcile a payment with bank statement."""
    payment_id: int
    bank_reference: str
    bank_account: Optional[str] = None
    reconciled_by: Optional[int] = None


@dataclass
class ImportBankStatementCommand(Command):
    """Command to import bank statement and auto-reconcile payments."""
    bank_account: str
    statement_date: date
    transactions: List[dict]  # List of transaction dicts with reference, amount, date, etc.
    imported_by: Optional[int] = None


@dataclass
class ConfirmPaymentCommand(Command):
    """Command to confirm a pending payment."""
    payment_id: int
    confirmed_by: Optional[int] = None

