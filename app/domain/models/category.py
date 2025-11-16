"""Category domain model for product classification."""
from dataclasses import dataclass
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ...infrastructure.db import Base
from ...domain.primitives.aggregate_root import AggregateRoot
from ...domain.events.domain_event import DomainEvent


@dataclass
class CategoryCreatedDomainEvent(DomainEvent):
    """Domain event raised when a category is created."""
    category_id: int = 0
    category_name: str = ""
    category_code: str = None


class Category(Base, AggregateRoot):
    """Category aggregate root for hierarchical product classification."""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, nullable=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relationships
    parent = relationship("Category", remote_side=[id], backref="children")
    products = relationship(
        "Product",
        secondary="product_categories",
        back_populates="categories"
    )

    @staticmethod
    def create(name: str, code: str = None, parent_id: int = None, description: str = None):
        """
        Factory method to create a new Category.
        
        Args:
            name: Category name (required)
            code: Optional unique category code
            parent_id: Optional parent category ID for hierarchy
            description: Optional description
            
        Returns:
            Category instance
            
        Raises:
            ValueError: If name is empty or code is invalid
        """
        if not name or not name.strip():
            raise ValueError("Category name is required.")
        
        if code and len(code) > 50:
            raise ValueError("Category code must be 50 characters or less.")
        
        category = Category(
            name=name.strip(),
            code=code.strip() if code else None,
            parent_id=parent_id,
            description=description.strip() if description else None
        )
        
        # Ensure AggregateRoot is initialized (domain events list)
        category._ensure_domain_events()
        
        # Raise domain event
        category.raise_domain_event(CategoryCreatedDomainEvent(
            category_id=0,  # Will be set after save
            category_name=name.strip(),
            category_code=code.strip() if code else None
        ))
        
        return category

    def update_details(self, name: str = None, code: str = None, description: str = None):
        """
        Update category details.
        
        Args:
            name: New category name
            code: New category code
            description: New description
            
        Raises:
            ValueError: If validation fails
        """
        if name is not None:
            if not name.strip():
                raise ValueError("Category name cannot be empty.")
            self.name = name.strip()
        
        if code is not None:
            if len(code) > 50:
                raise ValueError("Category code must be 50 characters or less.")
            self.code = code.strip() if code else None
        
        if description is not None:
            self.description = description.strip() if description else None

    def can_delete(self) -> bool:
        """
        Check if category can be safely deleted.
        
        Returns:
            True if category has no products assigned and no children
        """
        # Check if has products (via relationship)
        if self.products:
            return False
        
        # Check if has children
        if self.children:
            return False
        
        return True

