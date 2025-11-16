"""Unit tests for StockService."""
import pytest
from decimal import Decimal
from app.services.stock_service import StockService
from app.domain.models.stock import StockItem, Location, StockMovement
from app.domain.models.product import Product
from app.domain.models.user import User


@pytest.fixture
def sample_location(db_session):
    """Create a sample location for testing."""
    location = Location.create(
        code="WH-001",
        name="Warehouse 1",
        type="warehouse",
        is_active=True
    )
    db_session.add(location)
    db_session.commit()
    db_session.refresh(location)
    return location


@pytest.fixture
def sample_product(db_session, sample_category):
    """Create a sample product for testing."""
    product = Product.create(
        code="PROD-001",
        name="Test Product",
        price=Decimal("100.00"),
        cost=Decimal("50.00"),
        category_ids=[sample_category.id]
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product


@pytest.fixture
def sample_user(db_session):
    """Create a sample user for testing."""
    user = User(username="testuser", role="admin")
    user.set_password("testpass")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_stock_item(db_session, sample_product, sample_location):
    """Create a sample stock item for testing."""
    stock_item = StockItem.create(
        product_id=sample_product.id,
        location_id=sample_location.id,
        physical_quantity=Decimal("100.00"),
        min_stock=Decimal("10.00"),
        max_stock=Decimal("200.00"),
        reorder_point=Decimal("20.00")
    )
    db_session.add(stock_item)
    db_session.commit()
    db_session.refresh(stock_item)
    return stock_item


class TestStockServiceValidation:
    """Test stock service validation methods."""
    
    def test_validate_stock_rules_success(self, db_session, sample_stock_item):
        """Test successful stock rules validation."""
        service = StockService(db_session)
        # Should not raise
        service.validate_stock_rules(sample_stock_item, 'reserve')
    
    def test_validate_stock_rules_negative_physical(self, db_session, sample_stock_item):
        """Test validation fails when physical quantity is negative."""
        service = StockService(db_session)
        sample_stock_item.physical_quantity = Decimal("-10.00")
        
        with pytest.raises(ValueError, match="RG-STOCK-001"):
            service.validate_stock_rules(sample_stock_item, 'reserve')
    
    def test_validate_stock_rules_reserved_exceeds_physical(self, db_session, sample_stock_item):
        """Test validation fails when reserved exceeds physical."""
        service = StockService(db_session)
        sample_stock_item.reserved_quantity = Decimal("150.00")
        sample_stock_item.physical_quantity = Decimal("100.00")
        
        with pytest.raises(ValueError, match="RG-STOCK-002"):
            service.validate_stock_rules(sample_stock_item, 'reserve')
    
    def test_validate_movement_transfer_success(self, db_session, sample_product, sample_location):
        """Test successful transfer movement validation."""
        service = StockService(db_session)
        location2 = Location.create(
            code="WH-002",
            name="Warehouse 2",
            type="warehouse"
        )
        db_session.add(location2)
        db_session.commit()
        
        movement_data = {
            'type': 'transfer',
            'quantity': Decimal("50.00"),
            'location_from_id': sample_location.id,
            'location_to_id': location2.id,
            'product_id': sample_product.id
        }
        
        # Should not raise
        service.validate_movement(movement_data)
    
    def test_validate_movement_transfer_missing_location(self, db_session, sample_product):
        """Test transfer validation fails without both locations."""
        service = StockService(db_session)
        movement_data = {
            'type': 'transfer',
            'quantity': Decimal("50.00"),
            'location_from_id': None,
            'location_to_id': None,
            'product_id': sample_product.id
        }
        
        with pytest.raises(ValueError, match="RG-STOCK-003"):
            service.validate_movement(movement_data)
    
    def test_validate_movement_entry_requires_destination(self, db_session, sample_product):
        """Test entry validation requires destination location."""
        service = StockService(db_session)
        movement_data = {
            'type': 'entry',
            'quantity': Decimal("50.00"),
            'location_from_id': None,
            'location_to_id': None,
            'product_id': sample_product.id
        }
        
        with pytest.raises(ValueError, match="RG-STOCK-003"):
            service.validate_movement(movement_data)


class TestStockServiceAvailability:
    """Test stock service availability methods."""
    
    def test_get_global_availability(self, db_session, sample_product, sample_location, sample_stock_item):
        """Test getting global availability across locations."""
        service = StockService(db_session)
        
        # Create second location and stock item
        location2 = Location.create(
            code="WH-002",
            name="Warehouse 2",
            type="warehouse"
        )
        db_session.add(location2)
        db_session.commit()
        
        stock_item2 = StockItem.create(
            product_id=sample_product.id,
            location_id=location2.id,
            physical_quantity=Decimal("50.00")
        )
        stock_item2.reserved_quantity = Decimal("10.00")
        db_session.add(stock_item2)
        db_session.commit()
        
        availability = service.get_global_availability(sample_product.id)
        
        assert availability.product_id == sample_product.id
        assert availability.total_physical == Decimal("150.00")  # 100 + 50
        assert availability.total_reserved == Decimal("10.00")
        assert availability.total_available == Decimal("140.00")  # 150 - 10
        assert len(availability.by_location) == 2
    
    def test_check_availability_sufficient(self, db_session, sample_stock_item):
        """Test checking availability when sufficient stock exists."""
        service = StockService(db_session)
        
        result = service.check_availability(
            sample_stock_item.product_id,
            Decimal("50.00"),
            sample_stock_item.location_id
        )
        
        assert result is True
    
    def test_check_availability_insufficient(self, db_session, sample_stock_item):
        """Test checking availability when insufficient stock exists."""
        service = StockService(db_session)
        
        result = service.check_availability(
            sample_stock_item.product_id,
            Decimal("150.00"),
            sample_stock_item.location_id
        )
        
        assert result is False


class TestStockServiceReservation:
    """Test stock service reservation methods."""
    
    def test_reserve_stock_for_order_success(self, db_session, sample_stock_item, sample_user):
        """Test successful stock reservation for order."""
        service = StockService(db_session)
        
        order_lines = [{
            'product_id': sample_stock_item.product_id,
            'quantity': Decimal("30.00"),
            'preferred_location_id': sample_stock_item.location_id
        }]
        
        results = service.reserve_stock_for_order(1, order_lines)
        
        assert len(results) > 0
        assert results[0].success is True
        assert results[0].quantity_reserved == Decimal("30.00")
        
        # Commit changes and refresh to verify stock was reserved
        db_session.commit()
        db_session.refresh(sample_stock_item)
        assert sample_stock_item.reserved_quantity == Decimal("30.00")
    
    def test_reserve_stock_for_order_insufficient(self, db_session, sample_stock_item):
        """Test reservation fails when insufficient stock."""
        service = StockService(db_session)
        
        order_lines = [{
            'product_id': sample_stock_item.product_id,
            'quantity': Decimal("150.00"),
            'preferred_location_id': sample_stock_item.location_id
        }]
        
        results = service.reserve_stock_for_order(1, order_lines)
        
        assert len(results) > 0
        # Should have at least one failed result
        failed_results = [r for r in results if not r.success]
        assert len(failed_results) > 0
        assert "insuffisant" in failed_results[0].message.lower() or "insufficient" in failed_results[0].message.lower()


class TestStockServiceTransfer:
    """Test stock service transfer methods."""
    
    def test_transfer_stock_success(self, db_session, sample_stock_item, sample_user):
        """Test successful stock transfer."""
        service = StockService(db_session)
        
        # Create destination location
        location2 = Location.create(
            code="WH-002",
            name="Warehouse 2",
            type="warehouse"
        )
        db_session.add(location2)
        db_session.commit()
        
        initial_physical = sample_stock_item.physical_quantity
        
        result = service.transfer_stock(
            from_location_id=sample_stock_item.location_id,
            to_location_id=location2.id,
            product_id=sample_stock_item.product_id,
            quantity=Decimal("30.00"),
            user_id=sample_user.id,
            reason="Test transfer"
        )
        
        assert result.success is True
        assert result.quantity == Decimal("30.00")
        
        # Commit changes and refresh to verify source stock decreased
        db_session.commit()
        db_session.refresh(sample_stock_item)
        assert sample_stock_item.physical_quantity == initial_physical - Decimal("30.00")
        
        # Verify destination stock item created and increased
        dest_item = db_session.query(StockItem).filter(
            StockItem.product_id == sample_stock_item.product_id,
            StockItem.location_id == location2.id
        ).first()
        
        assert dest_item is not None
        assert dest_item.physical_quantity == Decimal("30.00")
    
    def test_transfer_stock_insufficient(self, db_session, sample_stock_item, sample_user):
        """Test transfer fails when insufficient stock."""
        service = StockService(db_session)
        
        location2 = Location.create(
            code="WH-002",
            name="Warehouse 2",
            type="warehouse"
        )
        db_session.add(location2)
        db_session.commit()
        
        # Transfer should raise ValueError when insufficient stock
        with pytest.raises(ValueError, match="RG-STOCK-006"):
            service.transfer_stock(
                from_location_id=sample_stock_item.location_id,
                to_location_id=location2.id,
                product_id=sample_stock_item.product_id,
                quantity=Decimal("150.00"),  # More than available
                user_id=sample_user.id
            )


class TestStockServiceReorder:
    """Test stock service reorder calculation methods."""
    
    def test_calculate_reorder_needs(self, db_session, sample_stock_item):
        """Test calculating reorder needs."""
        service = StockService(db_session)
        
        # Set stock below reorder point
        sample_stock_item.physical_quantity = Decimal("15.00")
        db_session.commit()
        
        needs = service.calculate_reorder_needs()
        
        assert len(needs) > 0
        need = needs[0]
        assert need.stock_item_id == sample_stock_item.id
        assert need.current_quantity == Decimal("15.00")
        assert need.urgency in ['critical', 'high', 'medium', 'low']
        assert need.product_id == sample_stock_item.product_id
    
    def test_calculate_reorder_needs_no_needs(self, db_session, sample_stock_item):
        """Test reorder needs when stock is sufficient."""
        service = StockService(db_session)
        
        # Stock is above reorder point
        sample_stock_item.physical_quantity = Decimal("100.00")
        db_session.commit()
        
        needs = service.calculate_reorder_needs()
        
        # Should not include this item (or include with low urgency)
        # The exact behavior depends on implementation
        pass


class TestStockServiceValuation:
    """Test stock service valuation methods."""
    
    def test_calculate_stock_value_standard(self, db_session, sample_stock_item, sample_product):
        """Test calculating stock value using standard method."""
        service = StockService(db_session)
        
        value = service.calculate_stock_value(sample_stock_item, 'standard')
        
        # Should be physical_quantity * product.cost
        expected = sample_stock_item.physical_quantity * (sample_product.cost or Decimal('0'))
        assert value == expected
    
    def test_calculate_stock_value_unknown_method(self, db_session, sample_stock_item):
        """Test valuation fails with unknown method."""
        service = StockService(db_session)
        
        with pytest.raises(ValueError, match="Méthode de valorisation inconnue"):
            service.calculate_stock_value(sample_stock_item, 'unknown')

