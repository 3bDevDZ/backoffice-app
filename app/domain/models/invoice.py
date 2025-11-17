"""Invoice domain models for billing and invoicing."""
from dataclasses import dataclass
from decimal import Decimal
from datetime import date, datetime
from typing import List, Optional
from sqlalchemy import Column, Integer, String, Text, Numeric, ForeignKey, Date, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from ...infrastructure.db import Base
from ...domain.primitives.aggregate_root import AggregateRoot
from ...domain.events.domain_event import DomainEvent


class InvoiceStatus(enum.Enum):
    """Invoice status enumeration."""
    DRAFT = "draft"
    VALIDATED = "validated"
    SENT = "sent"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELED = "canceled"


@dataclass
class InvoiceCreatedDomainEvent(DomainEvent):
    """Domain event raised when an invoice is created."""
    invoice_id: int = 0
    invoice_number: str = ""
    customer_id: int = 0
    order_id: Optional[int] = None


@dataclass
class InvoiceValidatedDomainEvent(DomainEvent):
    """Domain event raised when an invoice is validated."""
    invoice_id: int = 0
    invoice_number: str = ""
    validated_by: int = 0


@dataclass
class InvoiceSentDomainEvent(DomainEvent):
    """Domain event raised when an invoice is sent to customer."""
    invoice_id: int = 0
    invoice_number: str = ""
    customer_id: int = 0
    sent_by: int = 0


@dataclass
class InvoicePaidDomainEvent(DomainEvent):
    """Domain event raised when an invoice is fully paid."""
    invoice_id: int = 0
    invoice_number: str = ""
    customer_id: int = 0
    paid_amount: Decimal = Decimal(0)


@dataclass
class CreditNoteCreatedDomainEvent(DomainEvent):
    """Domain event raised when a credit note is created."""
    credit_note_id: int = 0
    credit_note_number: str = ""
    invoice_id: int = 0
    invoice_number: str = ""
    customer_id: int = 0


class InvoiceLine(Base):
    """Invoice line entity."""
    __tablename__ = "invoice_lines"

    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    order_line_id = Column(Integer, ForeignKey("order_lines.id"), nullable=True)  # Link to original order line
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    variant_id = Column(Integer, ForeignKey("product_variants.id"), nullable=True)
    
    # Line details
    description = Column(String(500), nullable=True)  # Product description or custom description
    quantity = Column(Numeric(12, 3), nullable=False)
    unit_price = Column(Numeric(12, 2), nullable=False)
    discount_percent = Column(Numeric(5, 2), default=Decimal(0))
    discount_amount = Column(Numeric(12, 2), default=Decimal(0))
    tax_rate = Column(Numeric(5, 2), default=Decimal(20.0))
    
    # Calculated totals
    line_total_ht = Column(Numeric(12, 2), nullable=False, default=Decimal(0))
    line_total_ttc = Column(Numeric(12, 2), nullable=False, default=Decimal(0))
    
    sequence = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relationships
    invoice = relationship("Invoice", back_populates="lines")
    order_line = relationship("OrderLine", foreign_keys=[order_line_id])
    product = relationship("Product")
    variant = relationship("ProductVariant", foreign_keys=[variant_id])

    def calculate_totals(self):
        """Calculate line totals."""
        # Calculate line total HT
        subtotal = self.quantity * self.unit_price
        discount_amount = subtotal * (self.discount_percent / Decimal(100))
        self.discount_amount = discount_amount
        self.line_total_ht = subtotal - discount_amount
        
        # Calculate line total TTC
        self.line_total_ttc = self.line_total_ht * (Decimal(1) + self.tax_rate / Decimal(100))


class CreditNote(Base, AggregateRoot):
    """Credit note aggregate root for invoice corrections."""
    __tablename__ = "credit_notes"

    id = Column(Integer, primary_key=True)
    number = Column(String(50), unique=True, nullable=False, index=True)  # AV-YYYY-XXXXX format
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    
    # Credit note details
    reason = Column(Text, nullable=False)  # Reason for credit note
    total_amount = Column(Numeric(12, 2), nullable=False)  # Total credit amount (HT)
    tax_amount = Column(Numeric(12, 2), nullable=False, default=Decimal(0))  # Total tax
    total_ttc = Column(Numeric(12, 2), nullable=False)  # Total credit amount (TTC)
    
    # Status
    status = Column(String(20), nullable=False, default="draft")  # draft, validated, applied, canceled
    
    # Audit fields
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    validated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    validated_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    invoice = relationship("Invoice", foreign_keys=[invoice_id])
    customer = relationship("Customer")
    creator = relationship("User", foreign_keys=[created_by])
    validator = relationship("User", foreign_keys=[validated_by])

    @staticmethod
    def _generate_number() -> str:
        """Generate credit note number in format AV-YYYY-XXXXX."""
        from datetime import datetime
        from ...infrastructure.db import get_session
        
        year = datetime.now().year
        # Get last credit note number for this year
        with get_session() as session:
            last_credit_note = session.query(CreditNote).filter(
                CreditNote.number.like(f"AV-{year}-%")
            ).order_by(CreditNote.id.desc()).first()
            
            if last_credit_note:
                # Extract sequence number
                try:
                    sequence = int(last_credit_note.number.split('-')[-1])
                    sequence += 1
                except (ValueError, IndexError):
                    sequence = 1
            else:
                sequence = 1
            
            return f"AV-{year}-{sequence:05d}"

    @staticmethod
    def create(
        invoice_id: int,
        customer_id: int,
        reason: str,
        total_amount: Decimal,
        tax_amount: Decimal = Decimal(0),
        created_by: int = None,
        number: Optional[str] = None
    ):
        """Factory method to create a new CreditNote."""
        if not reason or not reason.strip():
            raise ValueError("Reason is required for credit note.")
        if total_amount <= 0:
            raise ValueError("Credit note amount must be greater than 0.")
        if tax_amount < 0:
            raise ValueError("Tax amount cannot be negative.")
        
        credit_note = CreditNote(
            number=number or CreditNote._generate_number(),
            invoice_id=invoice_id,
            customer_id=customer_id,
            reason=reason.strip(),
            total_amount=total_amount,
            tax_amount=tax_amount,
            total_ttc=total_amount + tax_amount,
            status="draft",
            created_by=created_by
        )
        
        # Initialize AggregateRoot
        AggregateRoot.__init__(credit_note)
        
        # Raise domain event
        credit_note.raise_domain_event(CreditNoteCreatedDomainEvent(
            credit_note_id=0,  # Will be set after save
            credit_note_number=credit_note.number,
            invoice_id=invoice_id,
            invoice_number="",  # Will be set from invoice
            customer_id=customer_id
        ))
        
        return credit_note

    def validate(self, user_id: int):
        """Validate the credit note."""
        if self.status != "draft":
            raise ValueError(f"Cannot validate credit note '{self.number}' in status '{self.status}'. Credit note must be in 'draft' status.")
        
        self.status = "validated"
        self.validated_by = user_id
        self.validated_at = datetime.now()

    def apply(self):
        """Mark credit note as applied to invoice."""
        if self.status != "validated":
            raise ValueError(f"Cannot apply credit note '{self.number}' in status '{self.status}'. Credit note must be validated first.")
        
        self.status = "applied"

    def cancel(self):
        """Cancel the credit note."""
        if self.status in ["applied"]:
            raise ValueError(f"Cannot cancel credit note '{self.number}' in status '{self.status}'.")
        
        self.status = "canceled"


class Invoice(Base, AggregateRoot):
    """Invoice aggregate root for billing management."""
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True)
    number = Column(String(50), unique=True, nullable=False, index=True)  # FA-YYYY-XXXXX format
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)  # Link to original order
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    
    # Invoice dates
    invoice_date = Column(Date, nullable=False)  # Date of invoice (date de facturation)
    due_date = Column(Date, nullable=False)  # Payment due date (date d'échéance)
    
    # Status
    status = Column(String(20), nullable=False, default="draft", index=True)  # draft, validated, sent, partially_paid, paid, overdue, canceled
    
    # Financial information
    subtotal = Column(Numeric(12, 2), nullable=False, default=Decimal(0))
    discount_percent = Column(Numeric(5, 2), default=Decimal(0))
    discount_amount = Column(Numeric(12, 2), default=Decimal(0))
    tax_amount = Column(Numeric(12, 2), nullable=False, default=Decimal(0))
    total = Column(Numeric(12, 2), nullable=False, default=Decimal(0))
    
    # Payment tracking
    paid_amount = Column(Numeric(12, 2), default=Decimal(0))
    remaining_amount = Column(Numeric(12, 2), nullable=False, default=Decimal(0))
    
    # Legal compliance (Article 289 CGI)
    vat_number = Column(String(50), nullable=True)  # Customer VAT number
    siret = Column(String(14), nullable=True)  # Customer SIRET
    legal_mention = Column(Text, nullable=True)  # Legal mentions required by law
    
    # Notes
    notes = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)
    
    # Email tracking
    sent_at = Column(DateTime, nullable=True)
    sent_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    email_sent = Column(Boolean, default=False)
    
    # Audit fields
    validated_at = Column(DateTime, nullable=True)
    validated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    order = relationship("Order", foreign_keys=[order_id])
    customer = relationship("Customer")
    lines = relationship("InvoiceLine", back_populates="invoice", cascade="all, delete-orphan", order_by="InvoiceLine.sequence")
    credit_notes = relationship("CreditNote", foreign_keys="CreditNote.invoice_id", backref="original_invoice")
    payment_allocations = relationship("PaymentAllocation", back_populates="invoice")
    reminders = relationship("PaymentReminder", back_populates="invoice")
    sent_by_user = relationship("User", foreign_keys=[sent_by])
    validated_by_user = relationship("User", foreign_keys=[validated_by])
    creator = relationship("User", foreign_keys=[created_by])

    @staticmethod
    def _generate_number() -> str:
        """Generate invoice number in format FA-YYYY-XXXXX."""
        from datetime import datetime
        from ...infrastructure.db import get_session
        
        year = datetime.now().year
        # Get last invoice number for this year
        with get_session() as session:
            last_invoice = session.query(Invoice).filter(
                Invoice.number.like(f"FA-{year}-%")
            ).order_by(Invoice.id.desc()).first()
            
            if last_invoice:
                # Extract sequence number
                try:
                    sequence = int(last_invoice.number.split('-')[-1])
                    sequence += 1
                except (ValueError, IndexError):
                    sequence = 1
            else:
                sequence = 1
            
            return f"FA-{year}-{sequence:05d}"

    @staticmethod
    def create(
        customer_id: int,
        order_id: Optional[int],
        invoice_date: date,
        due_date: date,
        created_by: int,
        number: Optional[str] = None,
        notes: Optional[str] = None,
        internal_notes: Optional[str] = None,
        discount_percent: Decimal = Decimal(0)
    ):
        """Factory method to create a new Invoice."""
        if invoice_date > due_date:
            raise ValueError("Invoice date cannot be after due date.")
        if discount_percent < 0 or discount_percent > 100:
            raise ValueError("Discount percent must be between 0 and 100.")
        
        invoice = Invoice(
            number=number or Invoice._generate_number(),
            customer_id=customer_id,
            order_id=order_id,
            invoice_date=invoice_date,
            due_date=due_date,
            status="draft",
            discount_percent=discount_percent,
            notes=notes.strip() if notes else None,
            internal_notes=internal_notes.strip() if internal_notes else None,
            created_by=created_by,
            paid_amount=Decimal(0),
            remaining_amount=Decimal(0)
        )
        
        # Initialize AggregateRoot
        AggregateRoot.__init__(invoice)
        
        # Raise domain event
        invoice.raise_domain_event(InvoiceCreatedDomainEvent(
            invoice_id=0,  # Will be set after save
            invoice_number=invoice.number,
            customer_id=customer_id,
            order_id=order_id
        ))
        
        return invoice

    def add_line(
        self,
        product_id: int,
        quantity: Decimal,
        unit_price: Decimal,
        order_line_id: Optional[int] = None,
        variant_id: Optional[int] = None,
        description: Optional[str] = None,
        discount_percent: Decimal = Decimal(0),
        tax_rate: Decimal = Decimal(20.0),
        sequence: Optional[int] = None
    ) -> InvoiceLine:
        """Add a line to the invoice."""
        if self.status not in ["draft", "validated"]:
            raise ValueError(f"Cannot add line to invoice '{self.number}' in status '{self.status}'. Invoice must be in 'draft' or 'validated' status.")
        
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0.")
        if unit_price < 0:
            raise ValueError("Unit price cannot be negative.")
        if discount_percent < 0 or discount_percent > 100:
            raise ValueError("Discount percent must be between 0 and 100.")
        
        # Determine sequence
        if sequence is None:
            sequence = len(self.lines) + 1
        
        line = InvoiceLine()
        line.invoice_id = self.id
        line.order_line_id = order_line_id
        line.product_id = product_id
        line.variant_id = variant_id
        line.description = description
        line.quantity = quantity
        line.unit_price = unit_price
        line.discount_percent = discount_percent
        line.tax_rate = tax_rate
        line.sequence = sequence
        line.calculate_totals()
        
        self.lines.append(line)
        self.calculate_totals()
        
        return line

    def calculate_totals(self):
        """Calculate invoice totals."""
        # Calculate subtotal from lines
        self.subtotal = sum(line.line_total_ht for line in self.lines)
        
        # Apply document discount
        self.discount_amount = self.subtotal * (self.discount_percent / Decimal(100))
        subtotal_after_discount = self.subtotal - self.discount_amount
        
        # Calculate tax amount
        self.tax_amount = sum(line.line_total_ttc - line.line_total_ht for line in self.lines)
        
        # Calculate total TTC
        self.total = subtotal_after_discount + self.tax_amount
        
        # Update remaining amount
        self.remaining_amount = self.total - self.paid_amount

    def validate(self, user_id: int):
        """Validate the invoice (make it official)."""
        if self.status != "draft":
            raise ValueError(f"Cannot validate invoice '{self.number}' in status '{self.status}'. Invoice must be in 'draft' status.")
        
        if not self.lines:
            raise ValueError(f"Cannot validate invoice '{self.number}' without lines.")
        
        # Ensure totals are calculated
        self.calculate_totals()
        
        # Update status
        self.status = "validated"
        self.validated_at = datetime.now()
        self.validated_by = user_id
        
        # Raise domain event
        self.raise_domain_event(InvoiceValidatedDomainEvent(
            invoice_id=self.id,
            invoice_number=self.number,
            validated_by=user_id
        ))

    def send(self, user_id: int):
        """Send the invoice to customer (via email)."""
        if self.status not in ["validated", "sent"]:
            raise ValueError(f"Cannot send invoice '{self.number}' in status '{self.status}'. Invoice must be validated first.")
        
        # Update status
        if self.status == "validated":
            self.status = "sent"
        
        self.sent_at = datetime.now()
        self.sent_by = user_id
        self.email_sent = True
        
        # Raise domain event
        self.raise_domain_event(InvoiceSentDomainEvent(
            invoice_id=self.id,
            invoice_number=self.number,
            customer_id=self.customer_id,
            sent_by=user_id
        ))

    def mark_paid(self, amount: Decimal):
        """Record payment for the invoice."""
        if self.status in ["draft", "canceled"]:
            raise ValueError(f"Cannot record payment for invoice '{self.number}' in status '{self.status}'.")
        
        if amount <= 0:
            raise ValueError("Payment amount must be greater than 0.")
        
        if amount > self.remaining_amount:
            raise ValueError(f"Payment amount ({amount}) exceeds remaining amount ({self.remaining_amount}).")
        
        # Update payment tracking
        self.paid_amount += amount
        self.remaining_amount = self.total - self.paid_amount
        
        # Update status based on payment
        if self.remaining_amount <= Decimal(0):
            self.status = "paid"
            # Raise domain event
            self.raise_domain_event(InvoicePaidDomainEvent(
                invoice_id=self.id,
                invoice_number=self.number,
                customer_id=self.customer_id,
                paid_amount=self.paid_amount
            ))
        elif self.paid_amount > Decimal(0) and self.status == "sent":
            self.status = "partially_paid"

    def mark_overdue(self):
        """Mark invoice as overdue (called by scheduled task)."""
        if self.status in ["paid", "canceled", "overdue"]:
            return  # Already paid, canceled, or already marked overdue
        
        if datetime.now().date() > self.due_date:
            self.status = "overdue"

    def cancel(self):
        """Cancel the invoice."""
        if self.status in ["paid", "canceled"]:
            raise ValueError(f"Cannot cancel invoice '{self.number}' in status '{self.status}'.")
        
        self.status = "canceled"

