"""Stock management domain models."""
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional, List
from datetime import datetime
import enum

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
    site_id = Column(Integer, ForeignKey('sites.id'), nullable=True)  # User Story 10: Multi-location support
    capacity = Column(Numeric(12, 2), nullable=True)  # Optional capacity limit
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relationships
    parent = relationship("Location", remote_side=[id], backref="children")
    site = relationship("Site", back_populates="locations")
    stock_items = relationship("StockItem", back_populates="location", cascade="all, delete-orphan")

    @staticmethod
    def create(
        code: str,
        name: str,
        type: str,
        parent_id: Optional[int] = None,
        site_id: Optional[int] = None,
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
            site_id: Optional site ID (User Story 10: Multi-location support)
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
        location.site_id = site_id
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
    site_id = Column(Integer, ForeignKey('sites.id'), nullable=True)  # User Story 10: Multi-location support (denormalized for performance)
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
    site = relationship("Site", back_populates="stock_items")
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
        site_id: Optional[int] = None,
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
            site_id: Optional site ID (User Story 10: Multi-location support)
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
        stock_item.site_id = site_id
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


# ============================================================================
# User Story 10: Multi-Location Stock Management Models
# ============================================================================

class Site(Base, AggregateRoot):
    """Site model for multi-location warehouse management."""
    __tablename__ = "sites"

    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    address = Column(Text, nullable=True)
    manager_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # Site manager
    status = Column(String(20), nullable=False, default='active')  # 'active', 'inactive', 'archived'
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    manager = relationship("User", foreign_keys=[manager_id], backref="managed_sites")
    locations = relationship("Location", back_populates="site", cascade="all, delete-orphan")
    stock_items = relationship("StockItem", back_populates="site")
    transfers_from = relationship("StockTransfer", foreign_keys="StockTransfer.source_site_id", back_populates="source_site")
    transfers_to = relationship("StockTransfer", foreign_keys="StockTransfer.destination_site_id", back_populates="destination_site")

    @staticmethod
    def create(
        code: str,
        name: str,
        address: Optional[str] = None,
        manager_id: Optional[int] = None,
        status: str = 'active'
    ) -> "Site":
        """
        Factory method to create a new Site.
        
        Args:
            code: Unique site code
            name: Site name
            address: Optional site address
            manager_id: Optional site manager user ID
            status: Site status ('active', 'inactive', 'archived')
            
        Returns:
            Site instance
            
        Raises:
            ValueError: If validation fails
        """
        valid_statuses = ['active', 'inactive', 'archived']
        if status not in valid_statuses:
            raise ValueError(f"Site status must be one of: {', '.join(valid_statuses)}")
        
        if not code or not code.strip():
            raise ValueError("Site code is required.")
        
        if not name or not name.strip():
            raise ValueError("Site name is required.")
        
        site = Site()
        site.code = code.strip()
        site.name = name.strip()
        site.address = address.strip() if address else None
        site.manager_id = manager_id
        site.status = status
        
        return site

    def deactivate(self) -> None:
        """Deactivate the site."""
        if self.status == 'archived':
            raise ValueError("Cannot deactivate an archived site.")
        self.status = 'inactive'
        self.updated_at = datetime.utcnow()

    def activate(self) -> None:
        """Activate the site."""
        if self.status == 'archived':
            raise ValueError("Cannot activate an archived site.")
        self.status = 'active'
        self.updated_at = datetime.utcnow()

    def archive(self) -> None:
        """Archive the site."""
        self.status = 'archived'
        self.updated_at = datetime.utcnow()


class StockTransferStatus(enum.Enum):
    """Stock transfer status enumeration."""
    CREATED = "created"
    IN_TRANSIT = "in_transit"
    RECEIVED = "received"
    CANCELLED = "cancelled"


@dataclass
class StockTransferCreatedDomainEvent(DomainEvent):
    """Domain event raised when a stock transfer is created."""
    transfer_id: int = 0
    source_site_id: int = 0
    destination_site_id: int = 0


@dataclass
class StockTransferReceivedDomainEvent(DomainEvent):
    """Domain event raised when a stock transfer is received."""
    transfer_id: int = 0
    destination_site_id: int = 0


class StockTransferLine(Base):
    """StockTransferLine model for transfer line items."""
    __tablename__ = "stock_transfer_lines"

    id = Column(Integer, primary_key=True)
    transfer_id = Column(Integer, ForeignKey('stock_transfers.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    variant_id = Column(Integer, ForeignKey('product_variants.id'), nullable=True)
    quantity = Column(Numeric(12, 3), nullable=False)
    quantity_received = Column(Numeric(12, 3), nullable=False, default=Decimal('0'))
    sequence = Column(Integer, nullable=False, default=0)
    notes = Column(Text, nullable=True)

    # Relationships
    transfer = relationship("StockTransfer", back_populates="lines")
    product = relationship("Product", backref="transfer_lines")

    @staticmethod
    def create(
        transfer_id: int,
        product_id: int,
        quantity: Decimal,
        variant_id: Optional[int] = None,
        sequence: int = 0,
        notes: Optional[str] = None
    ) -> "StockTransferLine":
        """
        Factory method to create a new StockTransferLine.
        
        Args:
            transfer_id: StockTransfer ID
            product_id: Product ID
            quantity: Quantity to transfer
            variant_id: Optional product variant ID
            sequence: Line sequence number
            notes: Optional notes
            
        Returns:
            StockTransferLine instance
            
        Raises:
            ValueError: If validation fails
        """
        if quantity <= 0:
            raise ValueError("Transfer quantity must be positive.")
        
        line = StockTransferLine()
        line.transfer_id = transfer_id
        line.product_id = product_id
        line.variant_id = variant_id
        line.quantity = quantity
        line.quantity_received = Decimal('0')
        line.sequence = sequence
        line.notes = notes
        
        return line


class StockTransfer(Base, AggregateRoot):
    """StockTransfer aggregate root for inter-site stock transfers."""
    __tablename__ = "stock_transfers"

    id = Column(Integer, primary_key=True)
    number = Column(String(50), unique=True, nullable=False, index=True)
    source_site_id = Column(Integer, ForeignKey('sites.id'), nullable=False)
    destination_site_id = Column(Integer, ForeignKey('sites.id'), nullable=False)
    status = Column(String(20), nullable=False, default='created')  # 'created', 'in_transit', 'received', 'cancelled'
    requested_date = Column(DateTime, nullable=True)
    shipped_date = Column(DateTime, nullable=True)
    received_date = Column(DateTime, nullable=True)
    shipped_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    received_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    notes = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    source_site = relationship("Site", foreign_keys=[source_site_id], back_populates="transfers_from")
    destination_site = relationship("Site", foreign_keys=[destination_site_id], back_populates="transfers_to")
    lines = relationship("StockTransferLine", back_populates="transfer", cascade="all, delete-orphan", order_by="StockTransferLine.sequence")
    shipper = relationship("User", foreign_keys=[shipped_by], backref="shipped_transfers")
    receiver = relationship("User", foreign_keys=[received_by], backref="received_transfers")
    creator = relationship("User", foreign_keys=[created_by], backref="created_transfers")

    @staticmethod
    def create(
        number: str,
        source_site_id: int,
        destination_site_id: int,
        created_by: int,
        requested_date: Optional[datetime] = None,
        notes: Optional[str] = None
    ) -> "StockTransfer":
        """
        Factory method to create a new StockTransfer.
        
        Args:
            number: Unique transfer number
            source_site_id: Source site ID
            destination_site_id: Destination site ID
            created_by: User ID who created the transfer
            requested_date: Optional requested date
            notes: Optional notes
            
        Returns:
            StockTransfer instance
            
        Raises:
            ValueError: If validation fails
        """
        if not number or not number.strip():
            raise ValueError("Transfer number is required.")
        
        if source_site_id == destination_site_id:
            raise ValueError("Source and destination sites must be different.")
        
        transfer = StockTransfer()
        transfer.number = number.strip()
        transfer.source_site_id = source_site_id
        transfer.destination_site_id = destination_site_id
        transfer.status = 'created'
        transfer.requested_date = requested_date
        transfer.notes = notes
        transfer.created_by = created_by
        
        return transfer

    def ship(self, shipped_by: int, shipped_date: Optional[datetime] = None) -> None:
        """
        Mark transfer as shipped.
        
        Args:
            shipped_by: User ID who shipped the transfer
            shipped_date: Optional shipping date (defaults to now)
            
        Raises:
            ValueError: If transfer cannot be shipped
        """
        if self.status != 'created':
            raise ValueError(f"Cannot ship transfer with status '{self.status}'. Only 'created' transfers can be shipped.")
        
        if not self.lines:
            raise ValueError("Cannot ship transfer without lines.")
        
        self.status = 'in_transit'
        self.shipped_by = shipped_by
        self.shipped_date = shipped_date or datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def receive(self, received_by: int, received_date: Optional[datetime] = None) -> None:
        """
        Mark transfer as received.
        
        Args:
            received_by: User ID who received the transfer
            received_date: Optional receiving date (defaults to now)
            
        Raises:
            ValueError: If transfer cannot be received
        """
        if self.status != 'in_transit':
            raise ValueError(f"Cannot receive transfer with status '{self.status}'. Only 'in_transit' transfers can be received.")
        
        self.status = 'received'
        self.received_by = received_by
        self.received_date = received_date or datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def cancel(self) -> None:
        """
        Cancel the transfer.
        
        Raises:
            ValueError: If transfer cannot be cancelled
        """
        if self.status == 'received':
            raise ValueError("Cannot cancel a received transfer.")
        
        if self.status == 'cancelled':
            raise ValueError("Transfer is already cancelled.")
        
        self.status = 'cancelled'
        self.updated_at = datetime.utcnow()

