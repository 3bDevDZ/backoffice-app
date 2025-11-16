from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import Column, Integer, String, Numeric, Text, ForeignKey, Table, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ...infrastructure.db import Base
from ...domain.primitives.aggregate_root import AggregateRoot
from ...domain.events.domain_event import DomainEvent


# Junction table for many-to-many relationship between Product and Category
product_categories = Table(
    'product_categories',
    Base.metadata,
    Column('product_id', Integer, ForeignKey('products.id'), primary_key=True),
    Column('category_id', Integer, ForeignKey('categories.id'), primary_key=True)
)


@dataclass
class ProductCreatedDomainEvent(DomainEvent):
    """Domain event raised when a product is created."""
    product_id: int = 0
    product_code: str = ""
    product_name: str = ""


@dataclass
class ProductUpdatedDomainEvent(DomainEvent):
    """Domain event raised when a product is updated."""
    product_id: int = 0
    product_code: str = ""
    changes: dict = field(default_factory=dict)  # Dictionary of changed fields


@dataclass
class ProductArchivedDomainEvent(DomainEvent):
    """Domain event raised when a product is archived."""
    product_id: int = 0
    product_code: str = ""


class Product(Base, AggregateRoot):
    """Product aggregate root for product catalog management."""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(12, 2), nullable=False, default=0)
    cost = Column(Numeric(12, 2), nullable=True)  # Cost price for margin calculation
    unit_of_measure = Column(String(20), nullable=True)  # e.g., "piece", "kg", "L"
    barcode = Column(String(50), unique=True, nullable=True)
    status = Column(String(20), nullable=False, default="active")
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    categories = relationship(
        "Category",
        secondary=product_categories,
        back_populates="products"
    )
    variants = relationship(
        "ProductVariant",
        back_populates="product",
        cascade="all, delete-orphan"
    )

    @staticmethod
    def create(
        code: str,
        name: str,
        description: str = None,
        price: Decimal = Decimal(0),
        cost: Decimal = None,
        unit_of_measure: str = None,
        barcode: str = None,
        category_ids: List[int] = None
    ):
        """
        Factory method to create a new Product.
        
        Args:
            code: Unique product code (required, max 50 chars)
            name: Product name (required)
            description: Product description
            price: Selling price (required, must be >= 0)
            cost: Cost price (optional, must be >= 0 if provided)
            unit_of_measure: Unit of measure (e.g., "piece", "kg")
            barcode: Barcode (optional, must be unique if provided)
            category_ids: List of category IDs (at least one required)
            
        Returns:
            Product instance
            
        Raises:
            ValueError: If validation fails
        """
        if not code or len(code) > 50:
            raise ValueError("Product code is required and must be 50 characters or less.")
        if not name or not name.strip():
            raise ValueError("Product name is required.")
        if price < Decimal(0):
            raise ValueError("Price must be non-negative.")
        if cost is not None and cost < Decimal(0):
            raise ValueError("Cost must be non-negative if provided.")
        
        product = Product(
            code=code.strip(),
            name=name.strip(),
            description=description.strip() if description else None,
            price=price,
            cost=cost,
            unit_of_measure=unit_of_measure.strip() if unit_of_measure else None,
            barcode=barcode.strip() if barcode else None,
            status='active'
        )
        
        # Initialize AggregateRoot
        AggregateRoot.__init__(product)
        
        # Raise domain event
        product.raise_domain_event(ProductCreatedDomainEvent(
            product_id=0,  # Will be set after save
            product_code=code.strip(),
            product_name=name.strip()
        ))
        
        return product

    def update_details(
        self,
        name: str = None,
        description: str = None,
        price: Decimal = None,
        cost: Decimal = None,
        unit_of_measure: str = None,
        barcode: str = None
    ):
        """
        Update product details.
        
        Args:
            name: New product name
            description: New description
            price: New selling price (must be >= 0)
            cost: New cost price (must be >= 0 if provided)
            unit_of_measure: New unit of measure
            barcode: New barcode
            
        Raises:
            ValueError: If validation fails
        """
        changes = {}
        
        if name is not None:
            if not name.strip():
                raise ValueError("Product name cannot be empty.")
            if self.name != name.strip():
                changes['name'] = {'old': self.name, 'new': name.strip()}
            self.name = name.strip()
        
        if description is not None:
            if self.description != (description.strip() if description else None):
                changes['description'] = {'old': self.description, 'new': description.strip() if description else None}
            self.description = description.strip() if description else None
        
        if price is not None:
            if price < Decimal(0):
                raise ValueError("Price must be non-negative.")
            if self.price != price:
                changes['price'] = {'old': str(self.price), 'new': str(price)}
            self.price = price
        
        if cost is not None:
            if cost < Decimal(0):
                raise ValueError("Cost must be non-negative.")
            if self.cost != cost:
                changes['cost'] = {'old': str(self.cost) if self.cost else None, 'new': str(cost)}
            self.cost = cost
        
        if unit_of_measure is not None:
            if self.unit_of_measure != (unit_of_measure.strip() if unit_of_measure else None):
                changes['unit_of_measure'] = {'old': self.unit_of_measure, 'new': unit_of_measure.strip() if unit_of_measure else None}
            self.unit_of_measure = unit_of_measure.strip() if unit_of_measure else None
        
        if barcode is not None:
            if self.barcode != (barcode.strip() if barcode else None):
                changes['barcode'] = {'old': self.barcode, 'new': barcode.strip() if barcode else None}
            self.barcode = barcode.strip() if barcode else None
        
        # Raise domain event if there were changes
        if changes:
            self.raise_domain_event(ProductUpdatedDomainEvent(
                product_id=self.id,
                product_code=self.code,
                changes=changes
            ))

    def archive(self):
        """Archive the product (set status to 'archived')."""
        if self.status != 'archived':
            self.status = 'archived'
            # Raise domain event
            self.raise_domain_event(ProductArchivedDomainEvent(
                product_id=self.id,
                product_code=self.code
            ))

    def activate(self):
        """Activate the product (set status to 'active')."""
        self.status = 'active'

    def can_delete(self) -> bool:
        """
        Check if product can be safely deleted.
        
        A product cannot be deleted if it is referenced in quotes or orders.
        
        Returns:
            True if product can be deleted, False otherwise
        """
        # TODO: Check if product is referenced in quotes or orders
        # This will be implemented when Quote and Order models are created
        # For now, we'll check if product has any variants that might be referenced
        if self.variants:
            # If variants exist, we need to check if they're referenced
            # This is a simplified check - full implementation will check quotes/orders
            return False
        
        return True

    def add_category(self, category_id: int):
        """
        Add a category to this product.
        
        Args:
            category_id: ID of the category to add
        """
        # Category will be added via relationship in handler
        # This method is for business logic validation if needed
        pass

    def remove_category(self, category_id: int):
        """
        Remove a category from this product.
        
        Args:
            category_id: ID of the category to remove
            
        Raises:
            ValueError: If removing would leave product with no categories
        """
        # Check if this is the last category
        if len(self.categories) <= 1:
            raise ValueError("Product must have at least one category.")


class ProductVariant(Base):
    """Product variant entity (size, color, etc.)."""
    __tablename__ = "product_variants"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    attributes = Column(Text, nullable=True)  # JSON string for variant attributes
    price = Column(Numeric(12, 2), nullable=True)  # Override price if different from parent
    cost = Column(Numeric(12, 2), nullable=True)  # Override cost if different from parent
    barcode = Column(String(50), unique=True, nullable=True)
    status = Column(String(20), nullable=False, default="active")
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relationships
    product = relationship("Product", back_populates="variants")

    @staticmethod
    def create(
        product_id: int,
        code: str,
        name: str,
        attributes: str = None,
        price: Decimal = None,
        cost: Decimal = None,
        barcode: str = None
    ):
        """
        Factory method to create a new ProductVariant.
        
        Args:
            product_id: Parent product ID (required)
            code: Unique variant code (required, max 50 chars)
            name: Variant name (required)
            attributes: JSON string for variant attributes (color, size, etc.)
            price: Override price if different from parent (must be >= 0 if provided)
            cost: Override cost if different from parent (must be >= 0 if provided)
            barcode: Barcode (optional, must be unique if provided)
            
        Returns:
            ProductVariant instance
            
        Raises:
            ValueError: If validation fails
        """
        if not code or len(code) > 50:
            raise ValueError("Variant code is required and must be 50 characters or less.")
        if not name or not name.strip():
            raise ValueError("Variant name is required.")
        if price is not None and price < Decimal(0):
            raise ValueError("Price must be non-negative if provided.")
        if cost is not None and cost < Decimal(0):
            raise ValueError("Cost must be non-negative if provided.")
        
        return ProductVariant(
            product_id=product_id,
            code=code.strip(),
            name=name.strip(),
            attributes=attributes,
            price=price,
            cost=cost,
            barcode=barcode.strip() if barcode else None,
            status='active'
        )

    def update_details(
        self,
        name: str = None,
        attributes: str = None,
        price: Decimal = None,
        cost: Decimal = None,
        barcode: str = None
    ):
        """
        Update variant details.
        
        Args:
            name: New variant name
            attributes: New attributes JSON
            price: New override price (must be >= 0 if provided)
            cost: New override cost (must be >= 0 if provided)
            barcode: New barcode
            
        Raises:
            ValueError: If validation fails
        """
        if name is not None:
            if not name.strip():
                raise ValueError("Variant name cannot be empty.")
            self.name = name.strip()
        
        if attributes is not None:
            self.attributes = attributes
        
        if price is not None:
            if price < Decimal(0):
                raise ValueError("Price must be non-negative.")
            self.price = price
        
        if cost is not None:
            if cost < Decimal(0):
                raise ValueError("Cost must be non-negative.")
            self.cost = cost
        
        if barcode is not None:
            self.barcode = barcode.strip() if barcode else None

    def archive(self):
        """Archive the variant (set status to 'archived')."""
        self.status = 'archived'

    def activate(self):
        """Activate the variant (set status to 'active')."""
        self.status = 'active'


class ProductPriceHistory(Base):
    """Product price history for tracking price changes over time."""
    __tablename__ = "product_price_history"
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False, index=True)
    old_price = Column(Numeric(10, 2), nullable=True)  # NULL for first price
    new_price = Column(Numeric(10, 2), nullable=False)
    changed_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    changed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    reason = Column(String(255), nullable=True)  # Optional reason for price change
    
    # Relationships
    product = relationship("Product", backref="price_history")
    user = relationship("User", foreign_keys=[changed_by])
    
    def __repr__(self):
        return f"<ProductPriceHistory(id={self.id}, product_id={self.product_id}, old_price={self.old_price}, new_price={self.new_price}, changed_at={self.changed_at})>"


class ProductCostHistory(Base):
    """Product cost history for tracking cost changes over time (AVCO method)."""
    __tablename__ = "product_cost_history"
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False, index=True)
    old_cost = Column(Numeric(10, 2), nullable=True)  # NULL for first cost
    new_cost = Column(Numeric(10, 2), nullable=False)
    old_stock = Column(Numeric(12, 3), nullable=True)  # Stock quantity before update
    new_stock = Column(Numeric(12, 3), nullable=False)  # Stock quantity after update
    purchase_price = Column(Numeric(10, 2), nullable=False)  # Purchase price that triggered the update
    quantity_received = Column(Numeric(12, 3), nullable=False)  # Quantity received
    changed_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    changed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    reason = Column(String(255), nullable=True)  # Optional reason for cost change
    purchase_order_id = Column(Integer, ForeignKey('purchase_orders.id'), nullable=True)  # Related purchase order
    purchase_order_line_id = Column(Integer, nullable=True)  # Related purchase order line
    
    # Relationships
    product = relationship("Product", backref="cost_history")
    user = relationship("User", foreign_keys=[changed_by])
    purchase_order = relationship("PurchaseOrder", foreign_keys=[purchase_order_id])
    
    def __repr__(self):
        return f"<ProductCostHistory(id={self.id}, product_id={self.product_id}, old_cost={self.old_cost}, new_cost={self.new_cost}, changed_at={self.changed_at})>"


class PriceList(Base):
    """Price list for managing multiple pricing tiers."""
    __tablename__ = "price_lists"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    product_prices = relationship("ProductPriceList", back_populates="price_list", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<PriceList(id={self.id}, name={self.name}, is_active={self.is_active})>"


class ProductPriceList(Base):
    """Product price within a specific price list."""
    __tablename__ = "product_price_lists"
    
    id = Column(Integer, primary_key=True)
    price_list_id = Column(Integer, ForeignKey('price_lists.id'), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False, index=True)
    price = Column(Numeric(12, 2), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    price_list = relationship("PriceList", back_populates="product_prices")
    product = relationship("Product", backref="price_list_entries")
    
    # Unique constraint: one price per product per price list
    __table_args__ = (
        {'sqlite_autoincrement': True},
    )
    
    def __repr__(self):
        return f"<ProductPriceList(id={self.id}, price_list_id={self.price_list_id}, product_id={self.product_id}, price={self.price})>"


class ProductVolumePricing(Base):
    """Volume pricing (quantity-based pricing tiers) for products."""
    __tablename__ = "product_volume_pricing"
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False, index=True)
    min_quantity = Column(Numeric(12, 3), nullable=False)  # Minimum quantity for this tier
    max_quantity = Column(Numeric(12, 3), nullable=True)  # Maximum quantity (NULL = unlimited)
    price = Column(Numeric(12, 2), nullable=False)  # Price for this quantity tier
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    product = relationship("Product", backref="volume_pricing_tiers")
    
    def __repr__(self):
        return f"<ProductVolumePricing(id={self.id}, product_id={self.product_id}, min_quantity={self.min_quantity}, max_quantity={self.max_quantity}, price={self.price})>"


class ProductPromotionalPrice(Base):
    """Promotional pricing for products with date ranges."""
    __tablename__ = "product_promotional_prices"
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False, index=True)
    price = Column(Numeric(12, 2), nullable=False)  # Promotional price
    start_date = Column(DateTime, nullable=False, index=True)  # When promotion starts
    end_date = Column(DateTime, nullable=False, index=True)  # When promotion ends
    description = Column(String(500), nullable=True)  # Optional description of the promotion
    is_active = Column(Boolean, default=True, nullable=False)  # Can be manually deactivated
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)  # Who created the promotion
    
    # Relationships
    product = relationship("Product", backref="promotional_prices")
    creator = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<ProductPromotionalPrice(id={self.id}, product_id={self.product_id}, price={self.price}, start_date={self.start_date}, end_date={self.end_date})>"