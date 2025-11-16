"""Purchase domain models for purchase order management."""
from dataclasses import dataclass, field
from decimal import Decimal
from datetime import date, datetime
from typing import List, Optional
from sqlalchemy import Column, Integer, String, Text, Boolean, Numeric, ForeignKey, Date, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from ...infrastructure.db import Base
from ...domain.primitives.aggregate_root import AggregateRoot
from ...domain.events.domain_event import DomainEvent


class PurchaseOrderStatus(enum.Enum):
    """Purchase order status enumeration."""
    DRAFT = "draft"
    SENT = "sent"
    CONFIRMED = "confirmed"
    PARTIALLY_RECEIVED = "partially_received"
    RECEIVED = "received"
    CANCELLED = "cancelled"


@dataclass
class PurchaseOrderCreatedDomainEvent(DomainEvent):
    """Domain event raised when a purchase order is created."""
    purchase_order_id: int = 0
    purchase_order_number: str = ""
    supplier_id: int = 0


@dataclass
class PurchaseOrderConfirmedDomainEvent(DomainEvent):
    """Domain event raised when a purchase order is confirmed."""
    purchase_order_id: int = 0
    purchase_order_number: str = ""


@dataclass
class PurchaseOrderLineReceivedDomainEvent(DomainEvent):
    """Domain event raised when a purchase order line is received (partial or full)."""
    purchase_order_id: int = 0
    purchase_order_number: str = ""
    line_id: int = 0
    product_id: int = 0
    quantity_received: Decimal = Decimal(0)
    location_id: int = None


@dataclass
class PurchaseOrderReceivedDomainEvent(DomainEvent):
    """Domain event raised when a purchase order is fully received."""
    purchase_order_id: int = 0
    purchase_order_number: str = ""


class PurchaseOrderLine(Base):
    """Purchase order line entity."""
    __tablename__ = "purchase_order_lines"

    id = Column(Integer, primary_key=True)
    purchase_order_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Numeric(12, 3), nullable=False)  # Ordered quantity
    unit_price = Column(Numeric(12, 2), nullable=False)  # Purchase price per unit
    discount_percent = Column(Numeric(5, 2), default=Decimal(0))  # Line discount %
    tax_rate = Column(Numeric(5, 2), default=Decimal(20.0))  # VAT rate %
    line_total_ht = Column(Numeric(12, 2), nullable=False)  # Total HT (calculated)
    line_total_ttc = Column(Numeric(12, 2), nullable=False)  # Total TTC (calculated)
    quantity_received = Column(Numeric(12, 3), default=Decimal(0))  # Received quantity
    sequence = Column(Integer, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relationships
    purchase_order = relationship("PurchaseOrder", back_populates="lines")
    product = relationship("Product")

    def calculate_totals(self):
        """Calculate line totals."""
        # Calculate line total HT
        subtotal = self.quantity * self.unit_price
        discount_amount = subtotal * (self.discount_percent / Decimal(100))
        self.line_total_ht = subtotal - discount_amount
        
        # Calculate line total TTC
        self.line_total_ttc = self.line_total_ht * (Decimal(1) + self.tax_rate / Decimal(100))

    @staticmethod
    def create(
        purchase_order_id: int,
        product_id: int,
        quantity: Decimal,
        unit_price: Decimal,
        discount_percent: Decimal = Decimal(0),
        tax_rate: Decimal = Decimal(20.0),
        sequence: int = 1,
        notes: str = None
    ):
        """Factory method to create a new PurchaseOrderLine."""
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0.")
        if unit_price < 0:
            raise ValueError("Unit price cannot be negative.")
        if discount_percent < 0 or discount_percent > 100:
            raise ValueError("Discount percent must be between 0 and 100.")
        
        line = PurchaseOrderLine(
            purchase_order_id=purchase_order_id,
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price,
            discount_percent=discount_percent,
            tax_rate=tax_rate,
            sequence=sequence,
            notes=notes.strip() if notes else None
        )
        
        line.calculate_totals()
        return line


class PurchaseOrder(Base, AggregateRoot):
    """Purchase order aggregate root."""
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True)
    number = Column(String(50), unique=True, nullable=False)  # Format: PO-YYYY-XXXXX
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    
    # Dates
    order_date = Column(Date, nullable=False, server_default=func.current_date())
    expected_delivery_date = Column(Date, nullable=True)
    received_date = Column(Date, nullable=True)
    
    # Status
    status = Column(String(20), nullable=False, default='draft')  # draft, sent, confirmed, partially_received, received, cancelled
    
    # Totals
    subtotal_ht = Column(Numeric(12, 2), nullable=False, default=Decimal(0))
    total_tax = Column(Numeric(12, 2), nullable=False, default=Decimal(0))
    total_ttc = Column(Numeric(12, 2), nullable=False, default=Decimal(0))
    
    # Additional information
    notes = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)  # Internal notes not visible to supplier
    
    # User tracking
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    confirmed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    confirmed_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    supplier = relationship("Supplier")
    lines = relationship("PurchaseOrderLine", back_populates="purchase_order", cascade="all, delete-orphan", order_by="PurchaseOrderLine.sequence")
    creator = relationship("User", foreign_keys=[created_by])
    confirmer = relationship("User", foreign_keys=[confirmed_by])

    @staticmethod
    def _generate_number() -> str:
        """Generate unique purchase order number in format PO-YYYY-XXXXX."""
        import random
        import string
        from datetime import datetime
        from app.infrastructure.db import get_session
        
        year = datetime.now().year
        max_attempts = 10
        
        for _ in range(max_attempts):
            suffix = ''.join(random.choices(string.digits, k=5))
            number = f"PO-{year}-{suffix}"
            
            # Check if number exists
            with get_session() as session:
                existing = session.query(PurchaseOrder).filter_by(number=number).first()
                if not existing:
                    return number
        
        # Fallback: use timestamp-based number
        import time
        timestamp = int(time.time()) % 100000
        return f"PO-{year}-{timestamp:05d}"

    @staticmethod
    def create(
        supplier_id: int,
        created_by: int,
        number: str = None,
        order_date: date = None,
        expected_delivery_date: date = None,
        notes: str = None,
        internal_notes: str = None
    ):
        """
        Factory method to create a new PurchaseOrder.
        
        Args:
            supplier_id: Supplier ID
            created_by: User ID who created the order
            number: Optional order number (auto-generated if not provided)
            order_date: Order date (defaults to today)
            expected_delivery_date: Expected delivery date
            notes: Notes visible to supplier
            internal_notes: Internal notes
            
        Returns:
            PurchaseOrder instance
        """
        if order_date is None:
            order_date = date.today()
        
        order = PurchaseOrder(
            number=number.strip() if number else PurchaseOrder._generate_number(),
            supplier_id=supplier_id,
            order_date=order_date,
            expected_delivery_date=expected_delivery_date,
            notes=notes.strip() if notes else None,
            internal_notes=internal_notes.strip() if internal_notes else None,
            created_by=created_by,
            status='draft'
        )
        
        # Raise domain event
        order.raise_domain_event(PurchaseOrderCreatedDomainEvent(
            purchase_order_id=order.id,
            purchase_order_number=order.number,
            supplier_id=supplier_id
        ))
        
        return order

    def calculate_totals(self):
        """Calculate order totals from lines."""
        self.subtotal_ht = sum(line.line_total_ht for line in self.lines)
        self.total_tax = sum(line.line_total_ttc - line.line_total_ht for line in self.lines)
        self.total_ttc = sum(line.line_total_ttc for line in self.lines)
        self.updated_at = datetime.utcnow()

    def confirm(self, user_id: int):
        """Confirm the purchase order."""
        if self.status != 'draft' and self.status != 'sent':
            raise ValueError(f"Cannot confirm purchase order in status '{self.status}'.")
        
        if not self.lines:
            raise ValueError("Cannot confirm purchase order without lines.")
        
        self.status = 'confirmed'
        self.confirmed_by = user_id
        self.confirmed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        # Raise domain event
        self.raise_domain_event(PurchaseOrderConfirmedDomainEvent(
            purchase_order_id=self.id,
            purchase_order_number=self.number
        ))

    def cancel(self):
        """Cancel the purchase order."""
        if self.status in ['received', 'cancelled']:
            raise ValueError(f"Cannot cancel purchase order in status '{self.status}'.")
        
        self.status = 'cancelled'
        self.updated_at = datetime.utcnow()

    def mark_received(self):
        """Mark purchase order as fully received."""
        if self.status == 'cancelled':
            raise ValueError("Cannot mark cancelled purchase order as received.")
        
        # Check if all lines are fully received
        if not self.lines:
            return  # No lines, don't change status
        
        all_received = True
        for line in self.lines:
            if line.quantity_received < line.quantity:
                all_received = False
                self.status = 'partially_received'
                self.updated_at = datetime.utcnow()
                return
        
        # All lines are fully received
        if all_received:
            self.status = 'received'
            self.received_date = date.today()
            self.updated_at = datetime.utcnow()
            
            # Raise domain event
            self.raise_domain_event(PurchaseOrderReceivedDomainEvent(
                purchase_order_id=self.id,
                purchase_order_number=self.number
            ))

    def add_line(
        self,
        product_id: int,
        quantity: Decimal,
        unit_price: Decimal,
        discount_percent: Decimal = Decimal(0),
        tax_rate: Decimal = Decimal(20.0),
        notes: str = None
    ):
        """Add a line to the purchase order."""
        if self.status != 'draft':
            raise ValueError(f"Cannot add lines to purchase order in status '{self.status}'.")
        
        sequence = len(self.lines) + 1
        line = PurchaseOrderLine.create(
            purchase_order_id=self.id,
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price,
            discount_percent=discount_percent,
            tax_rate=tax_rate,
            sequence=sequence,
            notes=notes
        )
        
        self.lines.append(line)
        self.calculate_totals()
        
        return line

    def update_line(
        self,
        line_id: int,
        quantity: Decimal = None,
        unit_price: Decimal = None,
        discount_percent: Decimal = None,
        notes: str = None
    ):
        """Update a purchase order line."""
        if self.status != 'draft':
            raise ValueError(f"Cannot update lines in purchase order with status '{self.status}'.")
        
        line = next((l for l in self.lines if l.id == line_id), None)
        if not line:
            raise ValueError(f"Purchase order line {line_id} not found.")
        
        if quantity is not None:
            line.quantity = quantity
        if unit_price is not None:
            line.unit_price = unit_price
        if discount_percent is not None:
            line.discount_percent = discount_percent
        if notes is not None:
            line.notes = notes.strip() if notes else None
        
        line.calculate_totals()
        self.calculate_totals()
        self.updated_at = datetime.utcnow()

    def remove_line(self, line_id: int):
        """Remove a line from the purchase order."""
        if self.status != 'draft':
            raise ValueError(f"Cannot remove lines from purchase order with status '{self.status}'.")
        
        line = next((l for l in self.lines if l.id == line_id), None)
        if not line:
            raise ValueError(f"Purchase order line {line_id} not found.")
        
        self.lines.remove(line)
        self.calculate_totals()
        self.updated_at = datetime.utcnow()

