"""Unit tests for product command handlers."""
import pytest
from decimal import Decimal
from app.application.products.commands.commands import (
    CreateProductCommand,
    UpdateProductCommand,
    ArchiveProductCommand,
    DeleteProductCommand
)
from app.application.products.commands.handlers import (
    CreateProductHandler,
    UpdateProductHandler,
    ArchiveProductHandler,
    DeleteProductHandler
)
from app.domain.models.product import Product
from app.domain.models.category import Category


class TestCreateProductHandler:
    """Unit tests for CreateProductHandler."""
    
    def test_create_product_success(self, db_session, sample_category):
        """Test successful product creation."""
        handler = CreateProductHandler()
        command = CreateProductCommand(
            code="PROD-001",
            name="New Product",
            description="Product description",
            price=Decimal("100.00"),
            cost=Decimal("50.00"),
            category_ids=[sample_category.id]
        )
        
        product = handler.handle(command)
        
        # Re-query product from session to access attributes
        # (product was created in handler's session, need to get it in test session)
        product_in_session = db_session.query(Product).filter(Product.code == "PROD-001").first()
        
        assert product_in_session is not None
        assert product_in_session.code == "PROD-001"
        assert product_in_session.name == "New Product"
        assert product_in_session.price == Decimal("100.00")
        assert product_in_session.cost == Decimal("50.00")
        assert len(product_in_session.categories) == 1
        assert product_in_session.categories[0].id == sample_category.id
        assert product_in_session.status == "active"
    
    def test_create_product_without_category_fails(self, db_session):
        """Test that product creation fails without category."""
        # Setup: Add category to session so it's available
        category = Category.create(name="Test Category", code="TEST")
        db_session.add(category)
        db_session.commit()
        
        handler = CreateProductHandler()
        command = CreateProductCommand(
            code="PROD-002",
            name="Product Without Category",
            price=Decimal("100.00"),
            category_ids=[]
        )
        
        with pytest.raises(ValueError, match="Product must have at least one category"):
            handler.handle(command)
    
    def test_create_product_invalid_category_fails(self, db_session):
        """Test that product creation fails with invalid category ID."""
        # Setup: Add a valid category to session
        category = Category.create(name="Test Category", code="TEST")
        db_session.add(category)
        db_session.commit()
        
        handler = CreateProductHandler()
        command = CreateProductCommand(
            code="PROD-003",
            name="Product With Invalid Category",
            price=Decimal("100.00"),
            category_ids=[99999]  # Non-existent category
        )
        
        with pytest.raises(ValueError, match="One or more categories not found"):
            handler.handle(command)
    
    def test_create_product_raises_domain_event(self, db_session, sample_category):
        """Test that product creation raises domain event."""
        handler = CreateProductHandler()
        command = CreateProductCommand(
            code="PROD-004",
            name="Product With Event",
            price=Decimal("100.00"),
            category_ids=[sample_category.id]
        )
        
        product = handler.handle(command)
        
        # Check that domain event was raised
        events = product.get_domain_events()
        assert len(events) > 0
        assert events[0].product_code == "PROD-004"
        assert events[0].product_name == "Product With Event"


class TestUpdateProductHandler:
    """Unit tests for UpdateProductHandler."""
    
    def test_update_product_success(self, db_session, sample_product):
        """Test successful product update."""
        handler = UpdateProductHandler()
        command = UpdateProductCommand(
            id=sample_product.id,
            name="Updated Product Name",
            price=Decimal("150.00")
        )
        
        handler.handle(command)
        
        # Expire and refresh to see changes from handler's session
        db_session.expire_all()
        
        # Re-query product from session to verify changes
        updated_product = db_session.query(Product).filter(Product.id == sample_product.id).first()
        
        assert updated_product.name == "Updated Product Name"
        assert updated_product.price == Decimal("150.00")
        # Original values should remain unchanged
        assert updated_product.code == sample_product.code
    
    def test_update_product_not_found(self, db_session):
        """Test that updating non-existent product fails."""
        # Setup: Add category to session
        category = Category.create(name="Test Category", code="TEST")
        db_session.add(category)
        db_session.commit()
        
        handler = UpdateProductHandler()
        command = UpdateProductCommand(
            id=99999,
            name="Non-existent Product"
        )
        
        with pytest.raises(ValueError, match="Product not found"):
            handler.handle(command)
    
    def test_update_product_raises_domain_event(self, db_session, sample_product):
        """Test that product update raises domain event."""
        handler = UpdateProductHandler()
        original_name = sample_product.name
        command = UpdateProductCommand(
            id=sample_product.id,
            name="New Name"
        )
        
        updated_product = handler.handle(command)
        
        # Check that domain event was raised
        events = updated_product.get_domain_events()
        assert len(events) > 0
        assert events[0].product_id == sample_product.id
        assert 'name' in events[0].changes


class TestArchiveProductHandler:
    """Unit tests for ArchiveProductHandler."""
    
    def test_archive_product_success(self, db_session, sample_product):
        """Test successful product archival."""
        handler = ArchiveProductHandler()
        command = ArchiveProductCommand(id=sample_product.id)
        
        handler.handle(command)
        
        # Expire and refresh to see changes from handler's session
        db_session.expire_all()
        
        # Re-query product from session to verify status
        archived_product = db_session.query(Product).filter(Product.id == sample_product.id).first()
        
        assert archived_product.status == "archived"
    
    def test_archive_product_not_found(self, db_session):
        """Test that archiving non-existent product fails."""
        # Setup: Add category to session
        category = Category.create(name="Test Category", code="TEST")
        db_session.add(category)
        db_session.commit()
        
        handler = ArchiveProductHandler()
        command = ArchiveProductCommand(id=99999)
        
        with pytest.raises(ValueError, match="Product not found"):
            handler.handle(command)
    
    def test_archive_product_raises_domain_event(self, db_session, sample_product):
        """Test that product archival raises domain event."""
        handler = ArchiveProductHandler()
        command = ArchiveProductCommand(id=sample_product.id)
        
        archived_product = handler.handle(command)
        
        # Check that domain event was raised
        events = archived_product.get_domain_events()
        assert len(events) > 0
        assert events[0].product_id == sample_product.id
        assert events[0].product_code == sample_product.code


class TestDeleteProductHandler:
    """Unit tests for DeleteProductHandler."""
    
    def test_delete_product_success(self, db_session, sample_product):
        """Test successful product deletion."""
        handler = DeleteProductHandler()
        product_id = sample_product.id
        command = DeleteProductCommand(id=product_id)
        
        handler.handle(command)
        
        # Expire all to clear session cache and see changes from handler's session
        db_session.expire_all()
        
        # Verify product is deleted
        deleted_product = db_session.query(Product).filter(Product.id == product_id).first()
        assert deleted_product is None
    
    def test_delete_product_not_found(self, db_session):
        """Test that deleting non-existent product fails."""
        # Setup: Add category to session
        category = Category.create(name="Test Category", code="TEST")
        db_session.add(category)
        db_session.commit()
        
        handler = DeleteProductHandler()
        command = DeleteProductCommand(id=99999)
        
        with pytest.raises(ValueError, match="Product not found"):
            handler.handle(command)

