"""Order domain models for sales order management."""
from dataclasses import dataclass, field
from decimal import Decimal
from datetime import date, datetime, timedelta
from typing import List, Optional
from sqlalchemy import Column, Integer, String, Text, Numeric, ForeignKey, Date, DateTime, JSON, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
import json

from ...infrastructure.db import Base
from ...domain.primitives.aggregate_root import AggregateRoot
from ...domain.events.domain_event import DomainEvent


class OrderStatus(enum.Enum):
    """Order status enumeration."""
    DRAFT = "draft"
    CONFIRMED = "confirmed"
    IN_PREPARATION = "in_preparation"
    READY = "ready"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    INVOICED = "invoiced"
    CANCELED = "canceled"


@dataclass
class OrderCreatedDomainEvent(DomainEvent):
    """Domain event raised when an order is created."""
    order_id: int = 0
    order_number: str = ""
    customer_id: int = 0
    quote_id: Optional[int] = None


@dataclass
class OrderConfirmedDomainEvent(DomainEvent):
    """Domain event raised when an order is confirmed."""
    order_id: int = 0
    order_number: str = ""
    customer_id: int = 0
    confirmed_by: int = 0


@dataclass
class OrderCanceledDomainEvent(DomainEvent):
    """Domain event raised when an order is canceled."""
    order_id: int = 0
    order_number: str = ""
    customer_id: int = 0


@dataclass
class OrderReadyDomainEvent(DomainEvent):
    """Domain event raised when an order is ready for shipping (delivery note generation)."""
    order_id: int = 0
    order_number: str = ""
    customer_id: int = 0


@dataclass
class OrderShippedDomainEvent(DomainEvent):
    """Domain event raised when an order is shipped (stock exit movements)."""
    order_id: int = 0
    order_number: str = ""
    customer_id: int = 0
    shipped_by: int = 0


class OrderLine(Base):
    """Order line entity."""
    __tablename__ = "order_lines"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    variant_id = Column(Integer, ForeignKey("product_variants.id"), nullable=True)
    quantity = Column(Numeric(12, 3), nullable=False)
    unit_price = Column(Numeric(12, 2), nullable=False)
    discount_percent = Column(Numeric(5, 2), default=Decimal(0))
    discount_amount = Column(Numeric(12, 2), default=Decimal(0))
    tax_rate = Column(Numeric(5, 2), default=Decimal(20.0))
    line_total_ht = Column(Numeric(12, 2), nullable=False, default=Decimal(0))
    line_total_ttc = Column(Numeric(12, 2), nullable=False, default=Decimal(0))
    quantity_delivered = Column(Numeric(12, 3), default=Decimal(0))
    quantity_invoiced = Column(Numeric(12, 3), default=Decimal(0))
    sequence = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relationships
    order = relationship("Order", back_populates="lines")
    product = relationship("Product")
    variant = relationship("ProductVariant", foreign_keys=[variant_id])
    stock_reservations = relationship("StockReservation", back_populates="order_line", cascade="all, delete-orphan")

    def calculate_totals(self):
        """Calculate line totals."""
        # Calculate line total HT
        subtotal = self.quantity * self.unit_price
        discount_amount = subtotal * (self.discount_percent / Decimal(100))
        self.discount_amount = discount_amount
        self.line_total_ht = subtotal - discount_amount
        
        # Calculate line total TTC
        self.line_total_ttc = self.line_total_ht * (Decimal(1) + self.tax_rate / Decimal(100))

    def can_deliver(self, quantity: Decimal) -> bool:
        """Check if quantity can be delivered."""
        return (self.quantity_delivered + quantity) <= self.quantity

    def can_invoice(self, quantity: Decimal) -> bool:
        """Check if quantity can be invoiced."""
        return (self.quantity_invoiced + quantity) <= self.quantity_delivered


class StockReservation(Base):
    """Stock reservation entity for tracking reserved stock per order line."""
    __tablename__ = "stock_reservations"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    order_line_id = Column(Integer, ForeignKey("order_lines.id"), nullable=False)
    stock_item_id = Column(Integer, ForeignKey("stock_items.id"), nullable=False)
    quantity = Column(Numeric(12, 3), nullable=False)
    status = Column(String(20), nullable=False, default="reserved")  # 'reserved', 'fulfilled', 'released'
    reserved_at = Column(DateTime, nullable=False, server_default=func.now())
    released_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relationships
    order = relationship("Order", back_populates="stock_reservations")
    order_line = relationship("OrderLine", back_populates="stock_reservations")
    stock_item = relationship("StockItem")

    __table_args__ = (
        CheckConstraint("quantity > 0", name="check_positive_quantity"),
    )


class Order(Base, AggregateRoot):
    """Order aggregate root."""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    number = Column(String(50), unique=True, nullable=False, index=True)
    quote_id = Column(Integer, ForeignKey("quotes.id"), nullable=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    status = Column(String(20), nullable=False, default="draft", index=True)
    
    # Delivery information
    delivery_address_id = Column(Integer, ForeignKey("addresses.id"), nullable=True)
    delivery_date_requested = Column(Date, nullable=True)
    delivery_date_promised = Column(Date, nullable=True)
    delivery_date_actual = Column(Date, nullable=True)
    delivery_instructions = Column(Text, nullable=True)
    
    # Financial information
    subtotal = Column(Numeric(12, 2), nullable=False, default=Decimal(0))
    tax_amount = Column(Numeric(12, 2), nullable=False, default=Decimal(0))
    total = Column(Numeric(12, 2), nullable=False, default=Decimal(0))
    discount_percent = Column(Numeric(5, 2), default=Decimal(0))
    discount_amount = Column(Numeric(12, 2), default=Decimal(0))
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Audit fields
    confirmed_at = Column(DateTime, nullable=True)
    confirmed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    quote = relationship("Quote", foreign_keys=[quote_id])
    customer = relationship("Customer")
    delivery_address = relationship("Address", foreign_keys=[delivery_address_id])
    lines = relationship("OrderLine", back_populates="order", cascade="all, delete-orphan", order_by="OrderLine.sequence")
    stock_reservations = relationship("StockReservation", back_populates="order", cascade="all, delete-orphan")
    confirmed_by_user = relationship("User", foreign_keys=[confirmed_by])
    created_by_user = relationship("User", foreign_keys=[created_by])

    @staticmethod
    def _generate_number() -> str:
        """Generate order number in format CMD-YYYY-XXXXX."""
        from datetime import datetime
        from ...infrastructure.db import get_session
        
        year = datetime.now().year
        # Get last order number for this year
        with get_session() as session:
            last_order = session.query(Order).filter(
                Order.number.like(f"CMD-{year}-%")
            ).order_by(Order.id.desc()).first()
            
            if last_order:
                # Extract sequence number
                try:
                    sequence = int(last_order.number.split('-')[-1])
                    sequence += 1
                except (ValueError, IndexError):
                    sequence = 1
            else:
                sequence = 1
            
            return f"CMD-{year}-{sequence:05d}"

    @classmethod
    def create(cls, customer_id: int, created_by: int, quote_id: Optional[int] = None,
               delivery_address_id: Optional[int] = None,
               delivery_date_requested: Optional[date] = None,
               delivery_instructions: Optional[str] = None,
               discount_percent: Decimal = Decimal(0),
               notes: Optional[str] = None,
               number: Optional[str] = None) -> "Order":
        """Create a new order."""
        order = cls()
        order.customer_id = customer_id
        order.created_by = created_by
        order.quote_id = quote_id
        order.delivery_address_id = delivery_address_id
        order.delivery_date_requested = delivery_date_requested
        order.delivery_instructions = delivery_instructions
        order.discount_percent = discount_percent
        order.notes = notes
        order.status = "draft"
        order.number = number or cls._generate_number()
        
        # Validate quote if provided
        if quote_id:
            from app.domain.models.quote import Quote
            from ...infrastructure.db import get_session
            with get_session() as session:
                quote = session.get(Quote, quote_id)
                if not quote:
                    raise ValueError(f"Quote with ID {quote_id} not found")
                if quote.status != "accepted":
                    raise ValueError(f"Cannot create order from quote '{quote.number}'. Quote must be in 'accepted' status.")
        
        # Raise domain event
        order.raise_domain_event(OrderCreatedDomainEvent(
            order_id=order.id,
            order_number=order.number,
            customer_id=order.customer_id,
            quote_id=order.quote_id
        ))
        
        return order

    def add_line(self, product_id: int, quantity: Decimal, unit_price: Decimal,
                 discount_percent: Decimal = Decimal(0), tax_rate: Decimal = Decimal(20.0),
                 variant_id: Optional[int] = None, sequence: Optional[int] = None) -> OrderLine:
        """Add a line to the order."""
        if self.status != "draft":
            raise ValueError(f"Cannot add line to order '{self.number}' in status '{self.status}'. Order must be in 'draft' status.")
        
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0")
        
        if unit_price < 0:
            raise ValueError("Unit price cannot be negative")
        
        # Determine sequence
        if sequence is None:
            sequence = len(self.lines) + 1
        
        line = OrderLine()
        line.order_id = self.id
        line.product_id = product_id
        line.variant_id = variant_id
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
        """Calculate order totals."""
        # Calculate subtotal from lines
        self.subtotal = sum(line.line_total_ht for line in self.lines)
        
        # Apply document discount
        self.discount_amount = self.subtotal * (self.discount_percent / Decimal(100))
        subtotal_after_discount = self.subtotal - self.discount_amount
        
        # Calculate tax
        self.tax_amount = sum(line.line_total_ttc - line.line_total_ht for line in self.lines)
        # Adjust tax proportionally if document discount applied
        if self.discount_percent > 0:
            tax_rate_avg = sum(line.tax_rate for line in self.lines) / len(self.lines) if self.lines else Decimal(0)
            self.tax_amount = subtotal_after_discount * (tax_rate_avg / Decimal(100))
        
        # Calculate total
        self.total = subtotal_after_discount + self.tax_amount

    def validate_stock(self) -> dict:
        """
        Validate stock availability for all lines.
        Returns dict with 'valid': bool, 'issues': List[str]
        """
        from ...infrastructure.db import get_session
        from app.domain.models.stock import StockItem
        
        issues = []
        
        with get_session() as session:
            for line in self.lines:
                # Find stock items for this product
                stock_items = session.query(StockItem).filter(
                    StockItem.product_id == line.product_id,
                    StockItem.variant_id == line.variant_id
                ).all()
                
                total_available = sum(item.available_quantity for item in stock_items)
                
                if total_available < line.quantity:
                    product_code = line.product.code if hasattr(line.product, 'code') else f"Product {line.product_id}"
                    issues.append(
                        f"Insufficient stock for {product_code}: "
                        f"required {line.quantity}, available {total_available}"
                    )
        
        return {
            'valid': len(issues) == 0,
            'issues': issues
        }

    def validate_credit(self) -> dict:
        """
        Validate customer credit limit using CreditService.
        Returns dict with 'valid': bool, 'current_debt': Decimal, 'credit_limit': Decimal, 'message': str
        
        Note: This method delegates to CreditService for credit validation logic.
        The service encapsulates complex credit calculation and validation rules.
        """
        from ...infrastructure.db import get_session
        from app.services.credit_service import CreditService
        
        with get_session() as session:
            credit_service = CreditService(session)
            result = credit_service.validate_credit_for_order(
                customer_id=self.customer_id,
                order_total=self.total,
                order_id=self.id if self.id else None
            )
            
            return {
                'valid': result.valid,
                'current_debt': result.current_debt,
                'credit_limit': result.credit_limit,
                'message': result.message
            }

    def confirm(self, user_id: int):
        """
        Confirm the order: validate stock and credit, change status.
        Stock reservation will be handled by OrderConfirmedDomainEventHandler.
        """
        if self.status != "draft":
            raise ValueError(f"Cannot confirm order '{self.number}' in status '{self.status}'. Order must be in 'draft' status.")
        
        if not self.lines:
            raise ValueError(f"Cannot confirm order '{self.number}' without lines.")
        
        # Validate stock
        stock_validation = self.validate_stock()
        if not stock_validation['valid']:
            # Raise exception if stock is insufficient
            issues_str = "; ".join(stock_validation['issues'])
            raise ValueError(f"Cannot confirm order '{self.number}': {issues_str}")
        
        # Validate credit
        credit_validation = self.validate_credit()
        if not credit_validation['valid']:
            raise ValueError(credit_validation['message'])
        
        # Update status
        self.status = "confirmed"
        self.confirmed_at = datetime.now()
        self.confirmed_by = user_id
        
        # Raise domain event - stock reservation will be handled by event handler
        self.raise_domain_event(OrderConfirmedDomainEvent(
            order_id=self.id,
            order_number=self.number,
            customer_id=self.customer_id,
            confirmed_by=user_id
        ))

    def cancel(self):
        """
        Cancel the order: change status.
        Stock release will be handled by OrderCanceledDomainEventHandler.
        """
        if self.status in ("invoiced", "canceled"):
            raise ValueError(f"Cannot cancel order '{self.number}' in status '{self.status}'.")
        
        # Update status
        self.status = "canceled"
        
        # Raise domain event - stock release will be handled by event handler
        self.raise_domain_event(OrderCanceledDomainEvent(
            order_id=self.id,
            order_number=self.number,
            customer_id=self.customer_id
        ))

    def update_status(self, new_status: str):
        """Update order status with validation."""
        valid_transitions = {
            "draft": ["confirmed", "canceled"],
            "confirmed": ["in_preparation", "canceled"],
            "in_preparation": ["ready", "canceled"],
            "ready": ["shipped", "canceled"],
            "shipped": ["delivered", "canceled"],
            "delivered": ["invoiced"],
            "invoiced": [],
            "canceled": []
        }
        
        if self.status not in valid_transitions:
            raise ValueError(f"Invalid current status: {self.status}")
        
        if new_status not in valid_transitions[self.status]:
            raise ValueError(
                f"Cannot transition from '{self.status}' to '{new_status}'. "
                f"Valid transitions: {valid_transitions[self.status]}"
            )
        
        self.status = new_status
        
        # Special handling for delivered status
        if new_status == "delivered":
            if not self.delivery_date_actual:
                self.delivery_date_actual = date.today()
            # Update quantity_delivered on all lines to match quantity (full delivery)
            for line in self.lines:
                if line.quantity_delivered < line.quantity:
                    line.quantity_delivered = line.quantity

    def ship(self, user_id: int):
        """
        Mark order as shipped.
        Stock exit movements will be handled by OrderShippedDomainEventHandler.
        """
        if self.status != "ready":
            raise ValueError(f"Cannot ship order '{self.number}' in status '{self.status}'. Order must be 'ready'.")
        self.update_status("shipped")
        
        # Raise domain event - stock exit movements will be handled by event handler
        self.raise_domain_event(OrderShippedDomainEvent(
            order_id=self.id,
            order_number=self.number,
            customer_id=self.customer_id,
            shipped_by=user_id
        ))
    
    def mark_ready(self):
        """
        Mark order as ready for shipping.
        Delivery note generation will be handled by OrderReadyDomainEventHandler.
        """
        if self.status != "in_preparation":
            raise ValueError(f"Cannot mark order '{self.number}' as ready in status '{self.status}'. Order must be 'in_preparation'.")
        self.update_status("ready")
        
        # Raise domain event - delivery note generation will be handled by event handler
        self.raise_domain_event(OrderReadyDomainEvent(
            order_id=self.id,
            order_number=self.number,
            customer_id=self.customer_id
        ))
    
    def deliver(self, delivered_quantity: Optional[Decimal] = None, line_id: Optional[int] = None):
        """
        Mark order as delivered.
        If delivered_quantity and line_id are provided, update partial delivery.
        """
        if self.status != "shipped":
            raise ValueError(f"Cannot deliver order '{self.number}' in status '{self.status}'. Order must be 'shipped'.")
        
        # Handle partial delivery if specified
        if delivered_quantity is not None and line_id is not None:
            for line in self.lines:
                if line.id == line_id:
                    if not line.can_deliver(delivered_quantity):
                        raise ValueError(f"Cannot deliver {delivered_quantity} for line {line_id}. Maximum deliverable: {line.quantity - line.quantity_delivered}")
                    line.quantity_delivered += delivered_quantity
                    break
        
        # If all lines are fully delivered, mark order as delivered
        all_delivered = all(
            line.quantity_delivered >= line.quantity 
            for line in self.lines
        )
        
        if all_delivered:
            self.update_status("delivered")
    
    def add_stock_reservation(
        self,
        order_line_id: int,
        stock_item_id: int,
        quantity: Decimal
    ) -> StockReservation:
        """
        Add a stock reservation to this order.
        
        This method should be called by domain event handlers when reserving stock.
        It ensures that StockReservation entities are created through the aggregate root,
        maintaining DDD principles.
        
        Args:
            order_line_id: ID of the order line this reservation is for
            stock_item_id: ID of the stock item being reserved
            quantity: Quantity to reserve
            
        Returns:
            Created StockReservation instance
        """
        # Validate that the order line belongs to this order
        line = next((l for l in self.lines if l.id == order_line_id), None)
        if not line:
            raise ValueError(f"Order line {order_line_id} does not belong to order {self.number}")
        
        # Create reservation through aggregate root
        reservation = StockReservation()
        reservation.order_id = self.id
        reservation.order_line_id = order_line_id
        reservation.stock_item_id = stock_item_id
        reservation.quantity = quantity
        reservation.status = "reserved"
        reservation.reserved_at = datetime.now()
        
        # Add to collection (will be persisted by session)
        self.stock_reservations.append(reservation)
        
        return reservation
    
    def release_stock_reservation(self, reservation_id: int) -> None:
        """
        Release a stock reservation.
        
        This method should be called by domain event handlers when releasing stock.
        
        Args:
            reservation_id: ID of the reservation to release
        """
        reservation = next((r for r in self.stock_reservations if r.id == reservation_id), None)
        if not reservation:
            raise ValueError(f"Reservation {reservation_id} does not belong to order {self.number}")
        
        if reservation.status != "reserved":
            raise ValueError(f"Cannot release reservation {reservation_id} with status '{reservation.status}'")
        
        reservation.status = "released"
        reservation.released_at = datetime.now()

