"""Payment domain models for payment and collection management."""
from dataclasses import dataclass
from decimal import Decimal
from datetime import date, datetime
from typing import List, Optional
from sqlalchemy import Column, Integer, String, Text, Numeric, ForeignKey, Date, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from ...infrastructure.db import Base
from ...domain.primitives.aggregate_root import AggregateRoot
from ...domain.events.domain_event import DomainEvent


class PaymentMethod(enum.Enum):
    """Payment method enumeration."""
    CASH = "cash"
    CHECK = "check"
    BANK_TRANSFER = "bank_transfer"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PAYPAL = "paypal"
    OTHER = "other"


class PaymentStatus(enum.Enum):
    """Payment status enumeration."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    RECONCILED = "reconciled"
    CANCELLED = "cancelled"


@dataclass
class PaymentCreatedDomainEvent(DomainEvent):
    """Domain event raised when a payment is created."""
    payment_id: int = 0
    customer_id: int = 0
    amount: Decimal = Decimal(0)
    payment_method: str = ""


@dataclass
class PaymentAllocatedDomainEvent(DomainEvent):
    """Domain event raised when a payment is allocated to invoices."""
    payment_id: int = 0
    invoice_id: int = 0
    allocated_amount: Decimal = Decimal(0)


@dataclass
class PaymentReconciledDomainEvent(DomainEvent):
    """Domain event raised when a payment is reconciled with bank statement."""
    payment_id: int = 0
    bank_reference: str = ""


class PaymentAllocation(Base):
    """Payment allocation linking payments to invoices (many-to-many with amounts)."""
    __tablename__ = "payment_allocations"

    id = Column(Integer, primary_key=True)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=False)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    allocated_amount = Column(Numeric(12, 2), nullable=False)  # Amount allocated to this invoice
    
    # Audit fields
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    payment = relationship("Payment", back_populates="allocations")
    invoice = relationship("Invoice", foreign_keys=[invoice_id], back_populates="payment_allocations")

    @staticmethod
    def create(
        payment_id: int,
        invoice_id: int,
        allocated_amount: Decimal,
        created_by: Optional[int] = None
    ):
        """
        Factory method to create a new PaymentAllocation.
        
        Args:
            payment_id: Payment ID
            invoice_id: Invoice ID
            allocated_amount: Amount allocated to this invoice
            created_by: User ID who created the allocation
            
        Returns:
            PaymentAllocation instance
            
        Raises:
            ValueError: If validation fails
        """
        if allocated_amount <= 0:
            raise ValueError("Allocated amount must be greater than zero.")
        
        allocation = PaymentAllocation()
        allocation.payment_id = payment_id
        allocation.invoice_id = invoice_id
        allocation.allocated_amount = allocated_amount
        allocation.created_by = created_by
        
        return allocation


class PaymentReminder(Base):
    """Payment reminder for tracking reminder history."""
    __tablename__ = "payment_reminders"

    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    reminder_type = Column(String(20), nullable=False)  # 'first', 'second', 'third', 'final'
    reminder_date = Column(Date, nullable=False)
    sent_at = Column(DateTime, nullable=True)
    sent_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    email_sent = Column(Boolean, default=False)
    letter_sent = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    
    # Audit fields
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    
    # Relationships
    invoice = relationship("Invoice", foreign_keys=[invoice_id], back_populates="reminders")

    @staticmethod
    def create(
        invoice_id: int,
        reminder_type: str,
        reminder_date: date,
        sent_by: Optional[int] = None,
        notes: Optional[str] = None
    ):
        """
        Factory method to create a new PaymentReminder.
        
        Args:
            invoice_id: Invoice ID
            reminder_type: Type of reminder ('first', 'second', 'third', 'final')
            reminder_date: Date of reminder
            sent_by: User ID who sent the reminder
            notes: Additional notes
            
        Returns:
            PaymentReminder instance
            
        Raises:
            ValueError: If validation fails
        """
        valid_types = ['first', 'second', 'third', 'final']
        if reminder_type not in valid_types:
            raise ValueError(f"Reminder type must be one of: {', '.join(valid_types)}")
        
        reminder = PaymentReminder()
        reminder.invoice_id = invoice_id
        reminder.reminder_type = reminder_type
        reminder.reminder_date = reminder_date
        reminder.sent_by = sent_by
        reminder.notes = notes
        
        return reminder

    def mark_sent(self, sent_by: Optional[int] = None, email: bool = False, letter: bool = False):
        """
        Mark reminder as sent.
        
        Args:
            sent_by: User ID who sent the reminder
            email: Whether email was sent
            letter: Whether letter was sent
        """
        self.sent_at = datetime.now()
        if sent_by:
            self.sent_by = sent_by
        if email:
            self.email_sent = True
        if letter:
            self.letter_sent = True


class Payment(Base, AggregateRoot):
    """Payment aggregate root for payment management."""
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    
    # Payment information
    payment_method = Column(SQLEnum(PaymentMethod), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    payment_date = Column(Date, nullable=False)  # Date payment was received
    value_date = Column(Date, nullable=True)  # Date payment is effective (for bank transfers)
    
    # Status
    status = Column(SQLEnum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING)
    
    # Bank reconciliation
    bank_reference = Column(String(100), nullable=True)  # Bank statement reference
    bank_account = Column(String(100), nullable=True)  # Bank account number
    reconciled = Column(Boolean, default=False)
    reconciled_at = Column(DateTime, nullable=True)
    reconciled_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Additional information
    reference = Column(String(100), nullable=True)  # Payment reference (check number, transfer reference, etc.)
    notes = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)
    
    # Audit fields
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    allocations = relationship("PaymentAllocation", back_populates="payment", cascade="all, delete-orphan")
    customer = relationship("Customer", foreign_keys=[customer_id])

    @staticmethod
    def create(
        customer_id: int,
        payment_method: PaymentMethod,
        amount: Decimal,
        payment_date: date,
        value_date: Optional[date] = None,
        reference: Optional[str] = None,
        notes: Optional[str] = None,
        internal_notes: Optional[str] = None,
        created_by: Optional[int] = None
    ):
        """
        Factory method to create a new Payment.
        
        Args:
            customer_id: Customer ID
            payment_method: Payment method
            amount: Payment amount
            payment_date: Date payment was received
            value_date: Date payment is effective (for bank transfers)
            reference: Payment reference (check number, transfer reference, etc.)
            notes: Customer-visible notes
            internal_notes: Internal notes
            created_by: User ID who created the payment
            
        Returns:
            Payment instance
            
        Raises:
            ValueError: If validation fails
        """
        if amount <= 0:
            raise ValueError("Payment amount must be greater than zero.")
        
        if value_date and value_date < payment_date:
            raise ValueError("Value date cannot be before payment date.")
        
        payment = Payment()
        payment.customer_id = customer_id
        payment.payment_method = payment_method
        payment.amount = amount
        payment.payment_date = payment_date
        payment.value_date = value_date or payment_date
        payment.reference = reference
        payment.notes = notes
        payment.internal_notes = internal_notes
        payment.created_by = created_by
        payment.status = PaymentStatus.PENDING
        
        # Raise domain event
        payment.raise_domain_event(PaymentCreatedDomainEvent(
            payment_id=0,  # Will be set after flush
            customer_id=customer_id,
            amount=amount,
            payment_method=payment_method.value
        ))
        
        return payment

    def allocate_to_invoice(self, invoice_id: int, amount: Decimal, created_by: Optional[int] = None):
        """
        Allocate payment amount to an invoice.
        
        Args:
            invoice_id: Invoice ID
            amount: Amount to allocate
            created_by: User ID who created the allocation
            
        Raises:
            ValueError: If allocation exceeds available amount or validation fails
        """
        if amount <= 0:
            raise ValueError("Allocation amount must be greater than zero.")
        
        # Calculate total allocated amount
        total_allocated = sum(alloc.allocated_amount for alloc in self.allocations)
        available_amount = self.amount - total_allocated
        
        if amount > available_amount:
            raise ValueError(
                f"Cannot allocate {amount} to invoice {invoice_id}. "
                f"Available amount: {available_amount}"
            )
        
        # Create allocation
        allocation = PaymentAllocation.create(
            payment_id=self.id,
            invoice_id=invoice_id,
            allocated_amount=amount,
            created_by=created_by
        )
        
        self.allocations.append(allocation)
        
        # Raise domain event
        self.raise_domain_event(PaymentAllocatedDomainEvent(
            payment_id=self.id,
            invoice_id=invoice_id,
            allocated_amount=amount
        ))

    def get_total_allocated(self) -> Decimal:
        """Get total amount allocated to invoices."""
        return sum(alloc.allocated_amount for alloc in self.allocations)

    def get_unallocated_amount(self) -> Decimal:
        """Get unallocated amount."""
        return self.amount - self.get_total_allocated()

    def confirm(self):
        """Confirm the payment."""
        if self.status != PaymentStatus.PENDING:
            raise ValueError(f"Cannot confirm payment in status '{self.status.value}'. Payment must be 'pending'.")
        
        self.status = PaymentStatus.CONFIRMED

    def reconcile(self, bank_reference: str, bank_account: Optional[str] = None, reconciled_by: Optional[int] = None):
        """
        Reconcile payment with bank statement.
        
        Args:
            bank_reference: Bank statement reference
            bank_account: Bank account number
            reconciled_by: User ID who reconciled the payment
        """
        if self.reconciled:
            raise ValueError("Payment is already reconciled.")
        
        self.reconciled = True
        self.reconciled_at = datetime.now()
        self.reconciled_by = reconciled_by
        self.bank_reference = bank_reference
        if bank_account:
            self.bank_account = bank_account
        self.status = PaymentStatus.RECONCILED
        
        # Raise domain event
        self.raise_domain_event(PaymentReconciledDomainEvent(
            payment_id=self.id,
            bank_reference=bank_reference
        ))

    def cancel(self):
        """Cancel the payment."""
        if self.status == PaymentStatus.RECONCILED:
            raise ValueError("Cannot cancel a reconciled payment.")
        
        if self.get_total_allocated() > 0:
            raise ValueError("Cannot cancel payment with allocations. Remove allocations first.")
        
        self.status = PaymentStatus.CANCELLED

