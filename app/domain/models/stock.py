"""Stock management domain models."""
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional, List
from datetime import datetime

from sqlalchemy import Column, Integer, String, Numeric, Text, ForeignKey, DateTime, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ...infrastructure.db import Base
from ...domain.primitives.aggregate_root import AggregateRoot
from ...domain.events.domain_event import DomainEvent


@dataclass
class StockMovementCreatedDomainEvent(DomainEvent):
    """Domain event raised when a stock movement is created."""
    movement_id: int = 0
    product_id: int = 0
    location_id: int = 0
    quantity: Decimal = Decimal('0')
    movement_type: str = ""


class Location(Base):
    """Location model for hierarchical warehouse structure."""
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    type = Column(String(20), nullable=False)  # 'warehouse', 'zone', 'aisle', 'shelf', 'level', 'virtual'
    parent_id = Column(Integer, ForeignKey('locations.id'), nullable=True)
    capacity = Column(Numeric(12, 2), nullable=True)  # Optional capacity limit
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relationships
    parent = relationship("Location", remote_side=[id], backref="children")
    stock_items = relationship("StockItem", back_populates="location", cascade="all, delete-orphan")

    @staticmethod
    def create(
        code: str,
        name: str,
        type: str,
        parent_id: Optional[int] = None,
        capacity: Optional[Decimal] = None,
        is_active: bool = True
    ) -> "Location":
        """
        Factory method to create a new Location.
        
        Args:
            code: Unique location code
            name: Location name
            type: Location type ('warehouse', 'zone', 'aisle', 'shelf', 'level', 'virtual')
            parent_id: Parent location ID for hierarchy
            capacity: Optional capacity limit
            is_active: Whether location is active
            
        Returns:
            Location instance
            
        Raises:
            ValueError: If validation fails
        """
        valid_types = ['warehouse', 'zone', 'aisle', 'shelf', 'level', 'virtual']
        if type not in valid_types:
            raise ValueError(f"Location type must be one of: {', '.join(valid_types)}")
        
        if not code or not code.strip():
            raise ValueError("Location code is required.")
        
        if not name or not name.strip():
            raise ValueError("Location name is required.")
        
        location = Location()
        location.code = code.strip()
        location.name = name.strip()
        location.type = type
        location.parent_id = parent_id
        location.capacity = capacity
        location.is_active = is_active
        
        return location


class StockItem(Base, AggregateRoot):
    """StockItem aggregate root for stock level management."""
    __tablename__ = "stock_items"
    __table_args__ = (
        UniqueConstraint('product_id', 'variant_id', 'location_id', name='uq_stock_item_product_location'),
    )

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    variant_id = Column(Integer, ForeignKey('product_variants.id'), nullable=True)  # Product variant ID
    location_id = Column(Integer, ForeignKey('locations.id'), nullable=False)
    physical_quantity = Column(Numeric(12, 3), nullable=False, default=Decimal('0'))
    reserved_quantity = Column(Numeric(12, 3), nullable=False, default=Decimal('0'))
    min_stock = Column(Numeric(12, 3), nullable=True)  # Minimum stock threshold
    max_stock = Column(Numeric(12, 3), nullable=True)  # Maximum stock level
    reorder_point = Column(Numeric(12, 3), nullable=True)  # Point of reorder
    reorder_quantity = Column(Numeric(12, 3), nullable=True)  # Quantity to order
    valuation_method = Column(String(20), default='standard', nullable=False)  # 'standard', 'fifo', 'avco'
    last_movement_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    product = relationship("Product", backref="stock_items")
    location = relationship("Location", back_populates="stock_items")
    movements = relationship("StockMovement", back_populates="stock_item", cascade="all, delete-orphan")

    @property
    def available_quantity(self) -> Decimal:
        """Calculate available quantity (physical - reserved)."""
        return self.physical_quantity - self.reserved_quantity

    @staticmethod
    def create(
        product_id: int,
        location_id: int,
        physical_quantity: Decimal = Decimal('0'),
        variant_id: Optional[int] = None,
        min_stock: Optional[Decimal] = None,
        max_stock: Optional[Decimal] = None,
        reorder_point: Optional[Decimal] = None,
        reorder_quantity: Optional[Decimal] = None,
        valuation_method: str = 'standard'
    ) -> "StockItem":
        """
        Factory method to create a new StockItem.
        
        Args:
            product_id: Product ID
            location_id: Location ID
            physical_quantity: Initial physical quantity
            variant_id: Optional product variant ID
            min_stock: Minimum stock threshold
            max_stock: Maximum stock level
            reorder_point: Reorder point
            reorder_quantity: Reorder quantity
            valuation_method: Valuation method ('standard', 'fifo', 'avco')
            
        Returns:
            StockItem instance
            
        Raises:
            ValueError: If validation fails
        """
        if physical_quantity < 0:
            raise ValueError("Physical quantity cannot be negative.")
        
        valid_valuation_methods = ['standard', 'fifo', 'avco']
        if valuation_method not in valid_valuation_methods:
            raise ValueError(f"Valuation method must be one of: {', '.join(valid_valuation_methods)}")
        
        stock_item = StockItem()
        stock_item.product_id = product_id
        stock_item.variant_id = variant_id
        stock_item.location_id = location_id
        stock_item.physical_quantity = physical_quantity
        stock_item.reserved_quantity = Decimal('0')
        stock_item.min_stock = min_stock
        stock_item.max_stock = max_stock
        stock_item.reorder_point = reorder_point
        stock_item.reorder_quantity = reorder_quantity
        stock_item.valuation_method = valuation_method
        
        return stock_item

    def reserve(self, quantity: Decimal) -> None:
        """
        Reserve stock for orders.
        
        Args:
            quantity: Quantity to reserve
            
        Raises:
            ValueError: If insufficient available stock
        """
        if quantity <= 0:
            raise ValueError("Reservation quantity must be positive.")
        
        if self.available_quantity < quantity:
            raise ValueError(f"Insufficient available stock. Available: {self.available_quantity}, Requested: {quantity}")
        
        self.reserved_quantity += quantity
        self.updated_at = datetime.utcnow()

    def release(self, quantity: Decimal) -> None:
        """
        Release reserved stock.
        
        Args:
            quantity: Quantity to release
            
        Raises:
            ValueError: If insufficient reserved stock
        """
        if quantity <= 0:
            raise ValueError("Release quantity must be positive.")
        
        if self.reserved_quantity < quantity:
            raise ValueError(f"Insufficient reserved stock. Reserved: {self.reserved_quantity}, Requested: {quantity}")
        
        self.reserved_quantity -= quantity
        self.updated_at = datetime.utcnow()

    def adjust(self, quantity: Decimal, reason: Optional[str] = None) -> None:
        """
        Adjust physical stock (for inventory adjustments).
        
        Args:
            quantity: Adjustment quantity (positive for increase, negative for decrease)
            reason: Reason for adjustment
        """
        new_quantity = self.physical_quantity + quantity
        if new_quantity < 0:
            raise ValueError(f"Cannot adjust stock below zero. Current: {self.physical_quantity}, Adjustment: {quantity}")
        
        if new_quantity < self.reserved_quantity:
            raise ValueError(f"Cannot adjust stock below reserved quantity. Reserved: {self.reserved_quantity}, New: {new_quantity}")
        
        self.physical_quantity = new_quantity
        self.last_movement_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def is_below_minimum(self) -> bool:
        """
        Check if stock is below minimum threshold.
        
        Returns:
            True if below minimum, False otherwise
        """
        if self.min_stock is None:
            return False
        return self.physical_quantity < self.min_stock


class StockMovement(Base, AggregateRoot):
    """StockMovement aggregate root for tracking stock movements."""
    __tablename__ = "stock_movements"

    id = Column(Integer, primary_key=True)
    stock_item_id = Column(Integer, ForeignKey('stock_items.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    variant_id = Column(Integer, ForeignKey('product_variants.id'), nullable=True)  # Product variant ID
    location_from_id = Column(Integer, ForeignKey('locations.id'), nullable=True)  # For transfers
    location_to_id = Column(Integer, ForeignKey('locations.id'), nullable=True)  # For entries/transfers
    quantity = Column(Numeric(12, 3), nullable=False)  # Positive for entry, negative for exit
    type = Column(String(20), nullable=False)  # 'entry', 'exit', 'transfer', 'adjustment'
    reason = Column(String(200), nullable=True)  # Why movement occurred
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # Who performed movement
    related_document_type = Column(String(50), nullable=True)  # 'order', 'inventory', 'purchase_order'
    related_document_id = Column(Integer, nullable=True)  # Reference to related document
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relationships
    stock_item = relationship("StockItem", back_populates="movements")
    product = relationship("Product", backref="stock_movements")
    location_from = relationship("Location", foreign_keys=[location_from_id], backref="movements_from")
    location_to = relationship("Location", foreign_keys=[location_to_id], backref="movements_to")
    user = relationship("User", backref="stock_movements")

    @staticmethod
    def create(
        stock_item_id: int,
        product_id: int,
        quantity: Decimal,
        movement_type: str,
        user_id: int,
        location_from_id: Optional[int] = None,
        location_to_id: Optional[int] = None,
        variant_id: Optional[int] = None,
        reason: Optional[str] = None,
        related_document_type: Optional[str] = None,
        related_document_id: Optional[int] = None
    ) -> "StockMovement":
        """
        Factory method to create a new StockMovement.
        
        Args:
            stock_item_id: StockItem ID
            product_id: Product ID
            quantity: Movement quantity (positive for entry, negative for exit)
            movement_type: Movement type ('entry', 'exit', 'transfer', 'adjustment')
            user_id: User ID who performed the movement
            location_from_id: Source location ID (for transfers)
            location_to_id: Destination location ID (for entries/transfers)
            variant_id: Optional product variant ID
            reason: Reason for movement
            related_document_type: Related document type
            related_document_id: Related document ID
            
        Returns:
            StockMovement instance
            
        Raises:
            ValueError: If validation fails
        """
        valid_types = ['entry', 'exit', 'transfer', 'adjustment']
        if movement_type not in valid_types:
            raise ValueError(f"Movement type must be one of: {', '.join(valid_types)}")
        
        # Validate movement type and locations
        if movement_type == 'transfer':
            if not location_from_id or not location_to_id:
                raise ValueError("Transfer requires both source and destination locations.")
            if location_from_id == location_to_id:
                raise ValueError("Source and destination locations must be different.")
        elif movement_type == 'entry':
            if not location_to_id:
                raise ValueError("Entry requires destination location.")
            if quantity <= 0:
                raise ValueError("Entry quantity must be positive.")
        elif movement_type == 'exit':
            if not location_from_id:
                raise ValueError("Exit requires source location.")
            if quantity >= 0:
                raise ValueError("Exit quantity must be negative.")
        elif movement_type == 'adjustment':
            # Adjustment can have either location
            if not location_from_id and not location_to_id:
                raise ValueError("Adjustment requires at least one location.")
        
        # Validate quantity sign matches movement type
        if movement_type in ['entry', 'transfer'] and quantity <= 0:
            raise ValueError(f"{movement_type} quantity must be positive.")
        if movement_type == 'exit' and quantity >= 0:
            raise ValueError("Exit quantity must be negative.")
        
        movement = StockMovement()
        movement.stock_item_id = stock_item_id
        movement.product_id = product_id
        movement.variant_id = variant_id
        movement.location_from_id = location_from_id
        movement.location_to_id = location_to_id
        movement.quantity = quantity
        movement.type = movement_type
        movement.reason = reason
        movement.user_id = user_id
        movement.related_document_type = related_document_type
        movement.related_document_id = related_document_id
        
        return movement

