"""Quote domain models for sales quote management."""
from dataclasses import dataclass, field
from decimal import Decimal
from datetime import date, datetime, timedelta
from typing import List, Optional
from sqlalchemy import Column, Integer, String, Text, Numeric, ForeignKey, Date, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
import json

from ...infrastructure.db import Base
from ...domain.primitives.aggregate_root import AggregateRoot
from ...domain.events.domain_event import DomainEvent


class QuoteStatus(enum.Enum):
    """Quote status enumeration."""
    DRAFT = "draft"
    SENT = "sent"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CANCELED = "canceled"


@dataclass
class QuoteCreatedDomainEvent(DomainEvent):
    """Domain event raised when a quote is created."""
    quote_id: int = 0
    quote_number: str = ""
    customer_id: int = 0


@dataclass
class QuoteSentDomainEvent(DomainEvent):
    """Domain event raised when a quote is sent to customer."""
    quote_id: int = 0
    quote_number: str = ""
    customer_id: int = 0
    sent_by: int = 0


@dataclass
class QuoteAcceptedDomainEvent(DomainEvent):
    """Domain event raised when a quote is accepted by customer."""
    quote_id: int = 0
    quote_number: str = ""
    customer_id: int = 0


@dataclass
class QuoteRejectedDomainEvent(DomainEvent):
    """Domain event raised when a quote is rejected by customer."""
    quote_id: int = 0
    quote_number: str = ""
    customer_id: int = 0


@dataclass
class QuoteExpiredDomainEvent(DomainEvent):
    """Domain event raised when a quote expires."""
    quote_id: int = 0
    quote_number: str = ""
    customer_id: int = 0


class QuoteLine(Base):
    """Quote line entity."""
    __tablename__ = "quote_lines"

    id = Column(Integer, primary_key=True)
    quote_id = Column(Integer, ForeignKey("quotes.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    variant_id = Column(Integer, ForeignKey("product_variants.id"), nullable=True)
    quantity = Column(Numeric(12, 3), nullable=False)
    unit_price = Column(Numeric(12, 2), nullable=False)
    discount_percent = Column(Numeric(5, 2), default=Decimal(0))
    discount_amount = Column(Numeric(12, 2), default=Decimal(0))
    tax_rate = Column(Numeric(5, 2), default=Decimal(20.0))
    line_total_ht = Column(Numeric(12, 2), nullable=False, default=Decimal(0))
    line_total_ttc = Column(Numeric(12, 2), nullable=False, default=Decimal(0))
    sequence = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relationships
    quote = relationship("Quote", back_populates="lines")
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

    @staticmethod
    def create(
        quote_id: int,
        product_id: int,
        quantity: Decimal,
        unit_price: Decimal,
        variant_id: int = None,
        discount_percent: Decimal = Decimal(0),
        tax_rate: Decimal = Decimal(20.0),
        sequence: int = 1
    ):
        """Factory method to create a new QuoteLine."""
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0.")
        if unit_price < 0:
            raise ValueError("Unit price cannot be negative.")
        if discount_percent < 0 or discount_percent > 100:
            raise ValueError("Discount percent must be between 0 and 100.")
        
        line = QuoteLine(
            quote_id=quote_id,
            product_id=product_id,
            variant_id=variant_id,
            quantity=quantity,
            unit_price=unit_price,
            discount_percent=discount_percent,
            tax_rate=tax_rate,
            sequence=sequence
        )
        
        line.calculate_totals()
        return line


class QuoteVersion(Base):
    """Quote version entity for version history."""
    __tablename__ = "quote_versions"

    id = Column(Integer, primary_key=True)
    quote_id = Column(Integer, ForeignKey("quotes.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    data = Column(JSON, nullable=False)  # Snapshot of quote and lines data
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relationships
    quote = relationship("Quote", back_populates="versions")
    creator = relationship("User", foreign_keys=[created_by])

    @staticmethod
    def create(quote: "Quote", created_by: int):
        """Factory method to create a new QuoteVersion from a quote."""
        # Create snapshot of quote and lines data
        quote_data = {
            "id": quote.id,
            "number": quote.number,
            "version": quote.version,
            "customer_id": quote.customer_id,
            "status": quote.status,
            "valid_until": quote.valid_until.isoformat() if quote.valid_until else None,
            "subtotal": str(quote.subtotal),
            "tax_amount": str(quote.tax_amount),
            "total": str(quote.total),
            "discount_percent": str(quote.discount_percent),
            "discount_amount": str(quote.discount_amount),
            "notes": quote.notes,
            "internal_notes": quote.internal_notes,
            "lines": [
                {
                    "id": line.id,
                    "product_id": line.product_id,
                    "variant_id": line.variant_id,
                    "quantity": str(line.quantity),
                    "unit_price": str(line.unit_price),
                    "discount_percent": str(line.discount_percent),
                    "discount_amount": str(line.discount_amount),
                    "tax_rate": str(line.tax_rate),
                    "line_total_ht": str(line.line_total_ht),
                    "line_total_ttc": str(line.line_total_ttc),
                    "sequence": line.sequence
                }
                for line in quote.lines
            ]
        }
        
        version = QuoteVersion(
            quote_id=quote.id,
            version_number=quote.version,
            data=quote_data,
            created_by=created_by
        )
        
        return version


class Quote(Base, AggregateRoot):
    """Quote aggregate root for sales quote management."""
    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True)
    number = Column(String(50), unique=True, nullable=False)  # Format: DEV-YYYY-XXXXX
    version = Column(Integer, nullable=False, default=1)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    
    # Status
    status = Column(String(20), nullable=False, default='draft')  # draft, sent, accepted, rejected, expired, canceled
    
    # Dates
    valid_until = Column(Date, nullable=False)  # Expiration date (default: created_at + 30 days)
    
    # Totals
    subtotal = Column(Numeric(12, 2), nullable=False, default=Decimal(0))  # Subtotal HT
    tax_amount = Column(Numeric(12, 2), nullable=False, default=Decimal(0))  # Total TVA
    total = Column(Numeric(12, 2), nullable=False, default=Decimal(0))  # Total TTC
    
    # Discounts
    discount_percent = Column(Numeric(5, 2), default=Decimal(0))  # Document-level discount %
    discount_amount = Column(Numeric(12, 2), default=Decimal(0))  # Document-level discount amount
    
    # Notes
    notes = Column(Text, nullable=True)  # Customer-facing notes
    internal_notes = Column(Text, nullable=True)  # Internal notes
    
    # Tracking
    sent_at = Column(DateTime, nullable=True)
    sent_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    accepted_at = Column(DateTime, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    customer = relationship("Customer")
    lines = relationship("QuoteLine", back_populates="quote", cascade="all, delete-orphan", order_by="QuoteLine.sequence")
    versions = relationship("QuoteVersion", back_populates="quote", order_by="QuoteVersion.version_number.desc()")
    creator = relationship("User", foreign_keys=[created_by])
    sender = relationship("User", foreign_keys=[sent_by])

    @staticmethod
    def _generate_number() -> str:
        """Generate unique quote number in format DEV-YYYY-XXXXX."""
        import random
        import string
        from datetime import datetime
        from app.infrastructure.db import get_session
        
        year = datetime.now().year
        max_attempts = 10
        
        for _ in range(max_attempts):
            suffix = ''.join(random.choices(string.digits, k=5))
            number = f"DEV-{year}-{suffix}"
            
            # Check if number exists
            with get_session() as session:
                existing = session.query(Quote).filter_by(number=number).first()
                if not existing:
                    return number
        
        # Fallback: use timestamp-based number
        import time
        timestamp = int(time.time()) % 100000
        return f"DEV-{year}-{timestamp:05d}"

    @staticmethod
    def create(
        customer_id: int,
        created_by: int,
        number: str = None,
        valid_until: date = None,
        discount_percent: Decimal = Decimal(0),
        notes: str = None,
        internal_notes: str = None
    ):
        """
        Factory method to create a new Quote.
        
        Args:
            customer_id: Customer ID
            created_by: User ID who created the quote
            number: Optional quote number (auto-generated if not provided)
            valid_until: Expiration date (defaults to created_at + 30 days)
            discount_percent: Document-level discount percentage
            notes: Customer-facing notes
            internal_notes: Internal notes
            
        Returns:
            Quote instance
        """
        if discount_percent < 0 or discount_percent > 100:
            raise ValueError("Discount percent must be between 0 and 100.")
        
        if valid_until is None:
            valid_until = date.today() + timedelta(days=30)
        elif valid_until <= date.today():
            raise ValueError("Valid until date must be after today.")
        
        quote = Quote(
            number=number.strip() if number else Quote._generate_number(),
            customer_id=customer_id,
            created_by=created_by,
            valid_until=valid_until,
            discount_percent=discount_percent,
            notes=notes.strip() if notes else None,
            internal_notes=internal_notes.strip() if internal_notes else None,
            status='draft',
            version=1
        )
        
        # Raise domain event
        quote.raise_domain_event(QuoteCreatedDomainEvent(
            quote_id=quote.id,
            quote_number=quote.number,
            customer_id=customer_id
        ))
        
        return quote

    def calculate_totals(self):
        """Recalculate quote totals from lines."""
        if not self.lines:
            self.subtotal = Decimal(0)
            self.tax_amount = Decimal(0)
            self.total = Decimal(0)
            return
        
        # Calculate subtotal from lines (HT)
        lines_subtotal = sum(line.line_total_ht for line in self.lines)
        
        # Apply document-level discount
        self.discount_amount = lines_subtotal * (self.discount_percent / Decimal(100))
        self.subtotal = lines_subtotal - self.discount_amount
        
        # Calculate tax amount
        self.tax_amount = sum(line.line_total_ttc - line.line_total_ht for line in self.lines)
        
        # Calculate total TTC
        self.total = self.subtotal + self.tax_amount
        
        self.updated_at = datetime.utcnow()

    def add_line(
        self,
        product_id: int,
        quantity: Decimal,
        unit_price: Decimal,
        variant_id: int = None,
        discount_percent: Decimal = Decimal(0),
        tax_rate: Decimal = Decimal(20.0)
    ):
        """Add a line to the quote."""
        if self.status != 'draft':
            raise ValueError(f"Cannot add line to quote '{self.number}' in status '{self.status}'. Quote must be in 'draft' status.")
        
        # Get next sequence number
        max_sequence = max([line.sequence for line in self.lines], default=0)
        sequence = max_sequence + 1
        
        line = QuoteLine.create(
            quote_id=self.id,
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price,
            variant_id=variant_id,
            discount_percent=discount_percent,
            tax_rate=tax_rate,
            sequence=sequence
        )
        
        self.lines.append(line)
        self.calculate_totals()
        return line

    def send(self, user_id: int):
        """Send the quote to customer."""
        if self.status != 'draft':
            raise ValueError(f"Cannot send quote '{self.number}' in status '{self.status}'. Quote must be in 'draft' status.")
        
        if not self.lines:
            raise ValueError(f"Cannot send quote '{self.number}' without lines. At least one line is required.")
        
        self.status = 'sent'
        self.sent_at = datetime.utcnow()
        self.sent_by = user_id
        self.updated_at = datetime.utcnow()
        
        # Raise domain event
        self.raise_domain_event(QuoteSentDomainEvent(
            quote_id=self.id,
            quote_number=self.number,
            customer_id=self.customer_id,
            sent_by=user_id
        ))

    def accept(self):
        """Accept the quote."""
        if self.status != 'sent':
            raise ValueError(f"Cannot accept quote '{self.number}' in status '{self.status}'. Quote must be in 'sent' status.")
        
        if self.valid_until < date.today():
            raise ValueError(f"Cannot accept quote '{self.number}' because it has expired (valid until: {self.valid_until}).")
        
        self.status = 'accepted'
        self.accepted_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        # Raise domain event
        self.raise_domain_event(QuoteAcceptedDomainEvent(
            quote_id=self.id,
            quote_number=self.number,
            customer_id=self.customer_id
        ))

    def reject(self):
        """Reject the quote."""
        if self.status not in ['sent', 'accepted']:
            raise ValueError(f"Cannot reject quote '{self.number}' in status '{self.status}'. Quote must be in 'sent' or 'accepted' status.")
        
        self.status = 'rejected'
        self.updated_at = datetime.utcnow()
        
        # Raise domain event
        self.raise_domain_event(QuoteRejectedDomainEvent(
            quote_id=self.id,
            quote_number=self.number,
            customer_id=self.customer_id
        ))

    def expire(self):
        """Expire the quote (automatic)."""
        if self.status in ['expired', 'accepted', 'rejected', 'canceled']:
            return  # Already in final state
        
        self.status = 'expired'
        self.updated_at = datetime.utcnow()
        
        # Raise domain event
        self.raise_domain_event(QuoteExpiredDomainEvent(
            quote_id=self.id,
            quote_number=self.number,
            customer_id=self.customer_id
        ))

    def cancel(self):
        """Cancel the quote."""
        if self.status in ['accepted', 'canceled']:
            raise ValueError(f"Cannot cancel quote '{self.number}' in status '{self.status}'.")
        
        self.status = 'canceled'
        self.updated_at = datetime.utcnow()

    def create_version(self, created_by: int):
        """Create a new version of the quote (when editing a sent quote)."""
        if self.status not in ['sent', 'accepted', 'rejected', 'expired']:
            raise ValueError(f"Cannot create version for quote '{self.number}' in status '{self.status}'. Quote must have been sent.")
        
        # Create version snapshot of current state
        version = QuoteVersion.create(self, created_by)
        
        # Increment version number
        self.version += 1
        self.status = 'draft'  # Reset to draft for editing
        self.updated_at = datetime.utcnow()
        
        return version

    def can_convert_to_order(self) -> bool:
        """Check if quote can be converted to order."""
        return self.status == 'accepted'

