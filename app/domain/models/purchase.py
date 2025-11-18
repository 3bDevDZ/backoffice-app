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
    # User Story 9: Relationships to receipts and invoices
    receipts = relationship("PurchaseReceipt", foreign_keys="PurchaseReceipt.purchase_order_id", back_populates="purchase_order")
    supplier_invoices = relationship("SupplierInvoice", foreign_keys="SupplierInvoice.matched_purchase_order_id", back_populates="matched_po")
    converted_from_request = relationship("PurchaseRequest", foreign_keys="PurchaseRequest.converted_to_po_id", back_populates="converted_to_po")

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
            number=number.strip() if number and isinstance(number, str) else PurchaseOrder._generate_number(),
            supplier_id=supplier_id,
            order_date=order_date,
            expected_delivery_date=expected_delivery_date,
            notes=notes.strip() if notes and isinstance(notes, str) else (notes if notes else None),
            internal_notes=internal_notes.strip() if internal_notes and isinstance(internal_notes, str) else (internal_notes if internal_notes else None),
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


# ============================================================================
# User Story 9: Complete Purchase Cycle Management
# ============================================================================

class PurchaseRequestStatus(enum.Enum):
    """Purchase request status enumeration."""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    CONVERTED = "converted"  # Converted to purchase order


@dataclass
class PurchaseRequestCreatedDomainEvent(DomainEvent):
    """Domain event raised when a purchase request is created."""
    purchase_request_id: int = 0
    purchase_request_number: str = ""


@dataclass
class PurchaseRequestApprovedDomainEvent(DomainEvent):
    """Domain event raised when a purchase request is approved."""
    purchase_request_id: int = 0
    purchase_request_number: str = ""
    approved_by: int = 0


@dataclass
class PurchaseRequestConvertedDomainEvent(DomainEvent):
    """Domain event raised when a purchase request is converted to purchase order."""
    purchase_request_id: int = 0
    purchase_request_number: str = ""
    purchase_order_id: int = 0
    purchase_order_number: str = ""


class PurchaseRequestLine(Base):
    """Purchase request line entity."""
    __tablename__ = "purchase_request_lines"

    id = Column(Integer, primary_key=True)
    purchase_request_id = Column(Integer, ForeignKey("purchase_requests.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Numeric(12, 3), nullable=False)  # Requested quantity
    unit_price_estimate = Column(Numeric(12, 2), nullable=True)  # Estimated price (optional)
    notes = Column(Text, nullable=True)
    sequence = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relationships
    purchase_request = relationship("PurchaseRequest", back_populates="lines")
    product = relationship("Product")

    @staticmethod
    def create(
        purchase_request_id: int,
        product_id: int,
        quantity: Decimal,
        unit_price_estimate: Decimal = None,
        sequence: int = 1,
        notes: str = None
    ):
        """Factory method to create a new PurchaseRequestLine."""
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0.")
        if unit_price_estimate is not None and unit_price_estimate < 0:
            raise ValueError("Unit price estimate cannot be negative.")
        
        return PurchaseRequestLine(
            purchase_request_id=purchase_request_id,
            product_id=product_id,
            quantity=quantity,
            unit_price_estimate=unit_price_estimate,
            sequence=sequence,
            notes=notes.strip() if notes else None
        )


class PurchaseRequest(Base, AggregateRoot):
    """Purchase request aggregate root."""
    __tablename__ = "purchase_requests"

    id = Column(Integer, primary_key=True)
    number = Column(String(50), unique=True, nullable=False, index=True)  # Format: PR-YYYY-XXXXX
    
    # Request details
    requested_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    requested_date = Column(Date, nullable=False, server_default=func.current_date())
    required_date = Column(Date, nullable=True)  # When items are needed
    
    # Status workflow
    status = Column(String(20), nullable=False, default='draft', index=True)
    
    # Approval workflow
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)  # Reason if rejected
    
    # Conversion to purchase order
    converted_to_po_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=True)
    converted_at = Column(DateTime, nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    lines = relationship("PurchaseRequestLine", back_populates="purchase_request", cascade="all, delete-orphan", order_by="PurchaseRequestLine.sequence")
    requester = relationship("User", foreign_keys=[requested_by])
    approver = relationship("User", foreign_keys=[approved_by])
    converted_to_po = relationship("PurchaseOrder", foreign_keys=[converted_to_po_id])

    @staticmethod
    def _generate_number() -> str:
        """Generate unique purchase request number in format PR-YYYY-XXXXX."""
        import random
        import string
        from datetime import datetime
        from app.infrastructure.db import get_session
        
        year = datetime.now().year
        max_attempts = 10
        
        for _ in range(max_attempts):
            suffix = ''.join(random.choices(string.digits, k=5))
            number = f"PR-{year}-{suffix}"
            
            with get_session() as session:
                existing = session.query(PurchaseRequest).filter_by(number=number).first()
                if not existing:
                    return number
        
        import time
        timestamp = int(time.time()) % 100000
        return f"PR-{year}-{timestamp:05d}"

    @staticmethod
    def create(
        requested_by: int,
        number: str = None,
        requested_date: date = None,
        required_date: date = None,
        notes: str = None,
        internal_notes: str = None
    ):
        """Factory method to create a new PurchaseRequest."""
        if requested_date is None:
            requested_date = date.today()
        
        request = PurchaseRequest(
            number=number.strip() if number else PurchaseRequest._generate_number(),
            requested_by=requested_by,
            requested_date=requested_date,
            required_date=required_date,
            notes=notes.strip() if notes else None,
            internal_notes=internal_notes.strip() if internal_notes else None,
            status='draft'
        )
        
        request.raise_domain_event(PurchaseRequestCreatedDomainEvent(
            purchase_request_id=request.id,
            purchase_request_number=request.number
        ))
        
        return request

    def submit_for_approval(self):
        """Submit the purchase request for approval."""
        if self.status != 'draft':
            raise ValueError(f"Cannot submit purchase request in status '{self.status}'.")
        
        if not self.lines:
            raise ValueError("Cannot submit purchase request without lines.")
        
        self.status = 'pending_approval'
        self.updated_at = datetime.utcnow()

    def approve(self, approved_by: int):
        """Approve the purchase request."""
        if self.status != 'pending_approval':
            raise ValueError(f"Cannot approve purchase request in status '{self.status}'.")
        
        self.status = 'approved'
        self.approved_by = approved_by
        self.approved_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        self.raise_domain_event(PurchaseRequestApprovedDomainEvent(
            purchase_request_id=self.id,
            purchase_request_number=self.number,
            approved_by=approved_by
        ))

    def reject(self, rejected_by: int, reason: str):
        """Reject the purchase request."""
        if self.status != 'pending_approval':
            raise ValueError(f"Cannot reject purchase request in status '{self.status}'.")
        
        self.status = 'rejected'
        self.approved_by = rejected_by  # Store who rejected
        self.approved_at = datetime.utcnow()
        self.rejection_reason = reason.strip() if reason else None
        self.updated_at = datetime.utcnow()

    def mark_converted(self, purchase_order_id: int):
        """Mark the purchase request as converted to purchase order."""
        if self.status != 'approved':
            raise ValueError(f"Cannot convert purchase request in status '{self.status}'.")
        
        self.status = 'converted'
        self.converted_to_po_id = purchase_order_id
        self.converted_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        # Get purchase order number for event
        from app.infrastructure.db import get_session
        with get_session() as session:
            po = session.get(PurchaseOrder, purchase_order_id)
            po_number = po.number if po else ""
        
        self.raise_domain_event(PurchaseRequestConvertedDomainEvent(
            purchase_request_id=self.id,
            purchase_request_number=self.number,
            purchase_order_id=purchase_order_id,
            purchase_order_number=po_number
        ))

    def add_line(
        self,
        product_id: int,
        quantity: Decimal,
        unit_price_estimate: Decimal = None,
        notes: str = None
    ):
        """Add a line to the purchase request."""
        if self.status != 'draft':
            raise ValueError(f"Cannot add lines to purchase request in status '{self.status}'.")
        
        sequence = len(self.lines) + 1
        line = PurchaseRequestLine.create(
            purchase_request_id=self.id,
            product_id=product_id,
            quantity=quantity,
            unit_price_estimate=unit_price_estimate,
            sequence=sequence,
            notes=notes
        )
        
        self.lines.append(line)
        self.updated_at = datetime.utcnow()
        
        return line


class PurchaseReceiptStatus(enum.Enum):
    """Purchase receipt status enumeration."""
    DRAFT = "draft"
    VALIDATED = "validated"
    CANCELLED = "cancelled"


@dataclass
class PurchaseReceiptCreatedDomainEvent(DomainEvent):
    """Domain event raised when a purchase receipt is created."""
    purchase_receipt_id: int = 0
    purchase_receipt_number: str = ""
    purchase_order_id: int = 0


@dataclass
class PurchaseReceiptValidatedDomainEvent(DomainEvent):
    """Domain event raised when a purchase receipt is validated."""
    purchase_receipt_id: int = 0
    purchase_receipt_number: str = ""
    purchase_order_id: int = 0


class PurchaseReceiptLine(Base):
    """Purchase receipt line entity."""
    __tablename__ = "purchase_receipt_lines"

    id = Column(Integer, primary_key=True)
    purchase_receipt_id = Column(Integer, ForeignKey("purchase_receipts.id"), nullable=False)
    purchase_order_line_id = Column(Integer, ForeignKey("purchase_order_lines.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    # Quantities
    quantity_ordered = Column(Numeric(12, 3), nullable=False)  # From purchase order line
    quantity_received = Column(Numeric(12, 3), nullable=False)  # Actually received
    quantity_discrepancy = Column(Numeric(12, 3), nullable=False, default=Decimal(0))  # difference (can be negative)
    
    # Quality/discrepancy notes
    discrepancy_reason = Column(Text, nullable=True)  # Reason for quantity discrepancy
    quality_notes = Column(Text, nullable=True)  # Quality issues, damages, etc.
    
    # Location where goods were received
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)
    
    sequence = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relationships
    purchase_receipt = relationship("PurchaseReceipt", back_populates="lines")
    purchase_order_line = relationship("PurchaseOrderLine")
    product = relationship("Product")
    location = relationship("Location")

    @staticmethod
    def create(
        purchase_receipt_id: int,
        purchase_order_line_id: int,
        product_id: int,
        quantity_ordered: Decimal,
        quantity_received: Decimal,
        location_id: int = None,
        discrepancy_reason: str = None,
        quality_notes: str = None,
        sequence: int = 1
    ):
        """Factory method to create a new PurchaseReceiptLine."""
        if quantity_received < 0:
            raise ValueError("Quantity received cannot be negative.")
        
        quantity_discrepancy = quantity_received - quantity_ordered
        
        return PurchaseReceiptLine(
            purchase_receipt_id=purchase_receipt_id,
            purchase_order_line_id=purchase_order_line_id,
            product_id=product_id,
            quantity_ordered=quantity_ordered,
            quantity_received=quantity_received,
            quantity_discrepancy=quantity_discrepancy,
            location_id=location_id,
            discrepancy_reason=discrepancy_reason.strip() if discrepancy_reason else None,
            quality_notes=quality_notes.strip() if quality_notes else None,
            sequence=sequence
        )


class PurchaseReceipt(Base, AggregateRoot):
    """Purchase receipt aggregate root for tracking goods received."""
    __tablename__ = "purchase_receipts"

    id = Column(Integer, primary_key=True)
    number = Column(String(50), unique=True, nullable=False, index=True)  # Format: REC-YYYY-XXXXX
    purchase_order_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False)
    
    # Receipt details
    receipt_date = Column(Date, nullable=False, server_default=func.current_date())
    received_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Status
    status = Column(String(20), nullable=False, default='draft', index=True)
    
    # Validation
    validated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    validated_at = Column(DateTime, nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    purchase_order = relationship("PurchaseOrder", foreign_keys=[purchase_order_id])
    lines = relationship("PurchaseReceiptLine", back_populates="purchase_receipt", cascade="all, delete-orphan", order_by="PurchaseReceiptLine.sequence")
    receiver = relationship("User", foreign_keys=[received_by])
    validator = relationship("User", foreign_keys=[validated_by])

    @staticmethod
    def _generate_number() -> str:
        """Generate unique purchase receipt number in format REC-YYYY-XXXXX."""
        import random
        import string
        from datetime import datetime
        from app.infrastructure.db import get_session
        
        year = datetime.now().year
        max_attempts = 10
        
        for _ in range(max_attempts):
            suffix = ''.join(random.choices(string.digits, k=5))
            number = f"REC-{year}-{suffix}"
            
            with get_session() as session:
                existing = session.query(PurchaseReceipt).filter_by(number=number).first()
                if not existing:
                    return number
        
        import time
        timestamp = int(time.time()) % 100000
        return f"REC-{year}-{timestamp:05d}"

    @staticmethod
    def create(
        purchase_order_id: int,
        received_by: int,
        receipt_date: date = None,
        number: str = None,
        notes: str = None,
        internal_notes: str = None
    ):
        """Factory method to create a new PurchaseReceipt."""
        if receipt_date is None:
            receipt_date = date.today()
        
        receipt = PurchaseReceipt(
            number=number.strip() if number else PurchaseReceipt._generate_number(),
            purchase_order_id=purchase_order_id,
            receipt_date=receipt_date,
            received_by=received_by,
            notes=notes.strip() if notes else None,
            internal_notes=internal_notes.strip() if internal_notes else None,
            status='draft'
        )
        
        receipt.raise_domain_event(PurchaseReceiptCreatedDomainEvent(
            purchase_receipt_id=receipt.id,
            purchase_receipt_number=receipt.number,
            purchase_order_id=purchase_order_id
        ))
        
        return receipt

    def validate(self, validated_by: int):
        """Validate the purchase receipt (triggers stock movements)."""
        if self.status != 'draft':
            raise ValueError(f"Cannot validate purchase receipt in status '{self.status}'.")
        
        if not self.lines:
            raise ValueError("Cannot validate purchase receipt without lines.")
        
        self.status = 'validated'
        self.validated_by = validated_by
        self.validated_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        self.raise_domain_event(PurchaseReceiptValidatedDomainEvent(
            purchase_receipt_id=self.id,
            purchase_receipt_number=self.number,
            purchase_order_id=self.purchase_order_id
        ))

    def cancel(self):
        """Cancel the purchase receipt."""
        if self.status == 'validated':
            raise ValueError("Cannot cancel validated purchase receipt.")
        
        self.status = 'cancelled'
        self.updated_at = datetime.utcnow()


class SupplierInvoiceStatus(enum.Enum):
    """Supplier invoice status enumeration."""
    DRAFT = "draft"
    MATCHED = "matched"  # Matched with PO and receipt (3-way match)
    PARTIALLY_MATCHED = "partially_matched"
    UNMATCHED = "unmatched"  # No matching PO/receipt found
    PAID = "paid"
    CANCELLED = "cancelled"


@dataclass
class SupplierInvoiceCreatedDomainEvent(DomainEvent):
    """Domain event raised when a supplier invoice is created."""
    supplier_invoice_id: int = 0
    supplier_invoice_number: str = ""
    supplier_id: int = 0


@dataclass
class SupplierInvoiceMatchedDomainEvent(DomainEvent):
    """Domain event raised when a supplier invoice is matched with PO and receipt."""
    supplier_invoice_id: int = 0
    supplier_invoice_number: str = ""
    purchase_order_id: int = 0
    purchase_receipt_id: int = 0


class SupplierInvoice(Base, AggregateRoot):
    """Supplier invoice aggregate root for processing supplier invoices."""
    __tablename__ = "supplier_invoices"

    id = Column(Integer, primary_key=True)
    number = Column(String(100), nullable=False, index=True)  # Supplier's invoice number
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    
    # Invoice details
    invoice_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=True)
    received_date = Column(Date, nullable=False, server_default=func.current_date())  # When we received it
    
    # Financial information
    subtotal_ht = Column(Numeric(12, 2), nullable=False, default=Decimal(0))
    tax_amount = Column(Numeric(12, 2), nullable=False, default=Decimal(0))
    total_ttc = Column(Numeric(12, 2), nullable=False, default=Decimal(0))
    
    # Payment tracking
    paid_amount = Column(Numeric(12, 2), default=Decimal(0))
    remaining_amount = Column(Numeric(12, 2), nullable=False, default=Decimal(0))
    
    # Status
    status = Column(String(20), nullable=False, default='draft', index=True)
    
    # 3-way matching
    matched_purchase_order_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=True)
    matched_purchase_receipt_id = Column(Integer, ForeignKey("purchase_receipts.id"), nullable=True)
    matching_status = Column(String(20), nullable=True)  # 'matched', 'partially_matched', 'unmatched'
    matching_notes = Column(Text, nullable=True)  # Notes about matching discrepancies
    
    # Notes
    notes = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)
    
    # User tracking
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    matched_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    matched_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    supplier = relationship("Supplier")
    matched_po = relationship("PurchaseOrder", foreign_keys=[matched_purchase_order_id])
    matched_receipt = relationship("PurchaseReceipt", foreign_keys=[matched_purchase_receipt_id])
    creator = relationship("User", foreign_keys=[created_by])
    matcher = relationship("User", foreign_keys=[matched_by])

    @staticmethod
    def create(
        number: str,
        supplier_id: int,
        invoice_date: date,
        subtotal_ht: Decimal,
        tax_amount: Decimal,
        total_ttc: Decimal,
        created_by: int,
        due_date: date = None,
        received_date: date = None,
        notes: str = None,
        internal_notes: str = None
    ):
        """Factory method to create a new SupplierInvoice."""
        if received_date is None:
            received_date = date.today()
        
        if total_ttc != (subtotal_ht + tax_amount):
            raise ValueError("Total TTC must equal subtotal HT + tax amount.")
        
        invoice = SupplierInvoice(
            number=number.strip(),
            supplier_id=supplier_id,
            invoice_date=invoice_date,
            due_date=due_date,
            received_date=received_date,
            subtotal_ht=subtotal_ht,
            tax_amount=tax_amount,
            total_ttc=total_ttc,
            remaining_amount=total_ttc,
            created_by=created_by,
            notes=notes.strip() if notes else None,
            internal_notes=internal_notes.strip() if internal_notes else None,
            status='draft'
        )
        
        invoice.raise_domain_event(SupplierInvoiceCreatedDomainEvent(
            supplier_invoice_id=invoice.id,
            supplier_invoice_number=invoice.number,
            supplier_id=supplier_id
        ))
        
        return invoice

    def match_with_po_and_receipt(
        self,
        purchase_order_id: int,
        purchase_receipt_id: int,
        matched_by: int,
        matching_status: str,
        matching_notes: str = None
    ):
        """Match supplier invoice with purchase order and receipt (3-way matching)."""
        if self.status == 'cancelled':
            raise ValueError("Cannot match cancelled supplier invoice.")
        
        self.matched_purchase_order_id = purchase_order_id
        self.matched_purchase_receipt_id = purchase_receipt_id
        self.matching_status = matching_status
        self.matching_notes = matching_notes.strip() if matching_notes else None
        self.matched_by = matched_by
        self.matched_at = datetime.utcnow()
        
        # Update status based on matching
        if matching_status == 'matched':
            self.status = 'matched'
        elif matching_status == 'partially_matched':
            self.status = 'partially_matched'
        else:
            self.status = 'unmatched'
        
        self.updated_at = datetime.utcnow()
        
        self.raise_domain_event(SupplierInvoiceMatchedDomainEvent(
            supplier_invoice_id=self.id,
            supplier_invoice_number=self.number,
            purchase_order_id=purchase_order_id,
            purchase_receipt_id=purchase_receipt_id
        ))

    def mark_paid(self, amount: Decimal):
        """Record payment for the supplier invoice."""
        if amount <= 0:
            raise ValueError("Payment amount must be greater than 0.")
        
        if amount > self.remaining_amount:
            raise ValueError(f"Payment amount ({amount}) exceeds remaining amount ({self.remaining_amount}).")
        
        self.paid_amount += amount
        self.remaining_amount = self.total_ttc - self.paid_amount
        
        if self.remaining_amount <= Decimal(0):
            self.status = 'paid'
        
        self.updated_at = datetime.utcnow()

    def cancel(self):
        """Cancel the supplier invoice."""
        if self.status == 'paid':
            raise ValueError("Cannot cancel paid supplier invoice.")
        
        self.status = 'cancelled'
        self.updated_at = datetime.utcnow()


# Extend PurchaseOrder with relationships to receipts and invoices
# Note: These relationships are already defined in the PurchaseOrder class above,
# but we need to add the foreign key columns if they don't exist
# Actually, the relationships are one-to-many from PurchaseOrder's perspective,
# so the foreign keys are in PurchaseReceipt and SupplierInvoice, not in PurchaseOrder
# So we just need to add the reverse relationships if needed

