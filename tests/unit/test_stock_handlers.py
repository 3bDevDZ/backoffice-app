"""Unit tests for stock command handlers."""
import pytest
from decimal import Decimal
from app.application.stock.commands.commands import (
    CreateLocationCommand, UpdateLocationCommand,
    CreateStockItemCommand, CreateStockMovementCommand,
    ReserveStockCommand, ReleaseStockCommand, AdjustStockCommand
)
from app.application.stock.commands.handlers import (
    CreateLocationHandler, UpdateLocationHandler,
    CreateStockItemHandler, CreateStockMovementHandler,
    ReserveStockHandler, ReleaseStockHandler, AdjustStockHandler
)
from app.domain.models.stock import Location, StockItem, StockMovement
from app.domain.models.product import Product


@pytest.fixture
def sample_location(db_session):
    """Create a sample location for testing."""
    location = Location.create(
        code="WH-001",
        name="Warehouse 1",
        type="warehouse"
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
    from app.domain.models.user import User
    user = User(username="testuser", role="admin")
    user.set_password("testpass")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


class TestCreateLocationHandler:
    """Test CreateLocationHandler."""
    
    def test_create_location_success(self, db_session):
        """Test successful location creation."""
        handler = CreateLocationHandler()
        command = CreateLocationCommand(
            code="WH-002",
            name="Warehouse 2",
            type="warehouse"
        )
        
        location = handler.handle(command)
        
        # Re-query from test session since handler uses its own session
        location_in_test = db_session.query(Location).filter(Location.code == "WH-002").first()
        assert location_in_test is not None
        assert location_in_test.code == "WH-002"
        assert location_in_test.name == "Warehouse 2"
        assert location_in_test.type == "warehouse"
        assert location_in_test.is_active is True
    
    def test_create_location_with_parent(self, db_session, sample_location):
        """Test creating location with parent."""
        handler = CreateLocationHandler()
        command = CreateLocationCommand(
            code="ZONE-001",
            name="Zone 1",
            type="zone",
            parent_id=sample_location.id
        )
        
        location = handler.handle(command)
        
        # Re-query from test session
        location_in_test = db_session.query(Location).filter(Location.code == "ZONE-001").first()
        assert location_in_test is not None
        assert location_in_test.parent_id == sample_location.id


class TestCreateStockItemHandler:
    """Test CreateStockItemHandler."""
    
    def test_create_stock_item_success(self, db_session, sample_product, sample_location):
        """Test successful stock item creation."""
        handler = CreateStockItemHandler()
        command = CreateStockItemCommand(
            product_id=sample_product.id,
            location_id=sample_location.id,
            physical_quantity=Decimal("100.00"),
            min_stock=Decimal("10.00")
        )
        
        stock_item = handler.handle(command)
        
        # Re-query from test session
        stock_item_in_test = db_session.query(StockItem).filter(
            StockItem.product_id == sample_product.id,
            StockItem.location_id == sample_location.id
        ).first()
        assert stock_item_in_test is not None
        assert stock_item_in_test.product_id == sample_product.id
        assert stock_item_in_test.location_id == sample_location.id
        assert stock_item_in_test.physical_quantity == Decimal("100.00")
        assert stock_item_in_test.min_stock == Decimal("10.00")


class TestCreateStockMovementHandler:
    """Test CreateStockMovementHandler."""
    
    def test_create_entry_movement(self, db_session, sample_product, sample_location, sample_user):
        """Test creating an entry movement."""
        # Create stock item first
        stock_item = StockItem.create(
            product_id=sample_product.id,
            location_id=sample_location.id,
            physical_quantity=Decimal("50.00")
        )
        db_session.add(stock_item)
        db_session.commit()
        db_session.refresh(stock_item)
        
        handler = CreateStockMovementHandler()
        command = CreateStockMovementCommand(
            stock_item_id=stock_item.id,
            product_id=sample_product.id,
            quantity=Decimal("30.00"),
            movement_type="entry",
            user_id=sample_user.id,
            location_to_id=sample_location.id,
            reason="Test entry"
        )
        
        movement = handler.handle(command)
        
        # Re-query from test session
        movement_in_test = db_session.query(StockMovement).filter(
            StockMovement.stock_item_id == stock_item.id
        ).order_by(StockMovement.id.desc()).first()
        assert movement_in_test is not None
        assert movement_in_test.type == "entry"
        assert movement_in_test.quantity == Decimal("30.00")
        assert movement_in_test.location_to_id == sample_location.id
        
        # Verify stock item was updated
        db_session.refresh(stock_item)
        assert stock_item.physical_quantity == Decimal("80.00")  # 50 + 30


class TestReserveStockHandler:
    """Test ReserveStockHandler."""
    
    def test_reserve_stock_success(self, db_session, sample_product, sample_location):
        """Test successful stock reservation."""
        stock_item = StockItem.create(
            product_id=sample_product.id,
            location_id=sample_location.id,
            physical_quantity=Decimal("100.00")
        )
        db_session.add(stock_item)
        db_session.commit()
        db_session.refresh(stock_item)
        
        handler = ReserveStockHandler()
        command = ReserveStockCommand(
            product_id=sample_product.id,
            location_id=sample_location.id,
            quantity=Decimal("30.00")
        )
        
        result = handler.handle(command)
        
        # Expire all to force reload from database
        db_session.expire_all()
        
        # Re-query from test session
        stock_item_in_test = db_session.query(StockItem).filter(
            StockItem.product_id == sample_product.id,
            StockItem.location_id == sample_location.id
        ).first()
        assert stock_item_in_test.reserved_quantity == Decimal("30.00")
        assert stock_item_in_test.available_quantity == Decimal("70.00")
    
    def test_reserve_stock_insufficient(self, db_session, sample_product, sample_location):
        """Test reservation fails when insufficient stock."""
        stock_item = StockItem.create(
            product_id=sample_product.id,
            location_id=sample_location.id,
            physical_quantity=Decimal("100.00")
        )
        db_session.add(stock_item)
        db_session.commit()
        
        handler = ReserveStockHandler()
        command = ReserveStockCommand(
            product_id=sample_product.id,
            location_id=sample_location.id,
            quantity=Decimal("150.00")  # More than available
        )
        
        with pytest.raises(ValueError, match="(?i)insufficient"):
            handler.handle(command)


class TestReleaseStockHandler:
    """Test ReleaseStockHandler."""
    
    def test_release_stock_success(self, db_session, sample_product, sample_location):
        """Test successful stock release."""
        stock_item = StockItem.create(
            product_id=sample_product.id,
            location_id=sample_location.id,
            physical_quantity=Decimal("100.00")
        )
        stock_item.reserved_quantity = Decimal("30.00")
        db_session.add(stock_item)
        db_session.commit()
        db_session.refresh(stock_item)
        
        handler = ReleaseStockHandler()
        command = ReleaseStockCommand(
            product_id=sample_product.id,
            location_id=sample_location.id,
            quantity=Decimal("20.00")
        )
        
        result = handler.handle(command)
        
        # Expire all to force reload from database
        db_session.expire_all()
        
        # Re-query from test session
        stock_item_in_test = db_session.query(StockItem).filter(
            StockItem.product_id == sample_product.id,
            StockItem.location_id == sample_location.id
        ).first()
        assert stock_item_in_test.reserved_quantity == Decimal("10.00")  # 30 - 20
        assert stock_item_in_test.available_quantity == Decimal("90.00")  # 100 - 10


class TestAdjustStockHandler:
    """Test AdjustStockHandler."""
    
    def test_adjust_stock_increase(self, db_session, sample_product, sample_location, sample_user):
        """Test increasing stock via adjustment."""
        stock_item = StockItem.create(
            product_id=sample_product.id,
            location_id=sample_location.id,
            physical_quantity=Decimal("100.00")
        )
        db_session.add(stock_item)
        db_session.commit()
        db_session.refresh(stock_item)
        
        handler = AdjustStockHandler()
        command = AdjustStockCommand(
            product_id=sample_product.id,
            location_id=sample_location.id,
            quantity=Decimal("20.00"),
            reason="Inventory adjustment",
            user_id=sample_user.id
        )
        
        result = handler.handle(command)
        
        # Expire all to force reload from database
        db_session.expire_all()
        
        # Re-query from test session
        stock_item_in_test = db_session.query(StockItem).filter(
            StockItem.product_id == sample_product.id,
            StockItem.location_id == sample_location.id
        ).first()
        assert stock_item_in_test.physical_quantity == Decimal("120.00")  # 100 + 20
    
    def test_adjust_stock_decrease(self, db_session, sample_product, sample_location, sample_user):
        """Test decreasing stock via adjustment."""
        stock_item = StockItem.create(
            product_id=sample_product.id,
            location_id=sample_location.id,
            physical_quantity=Decimal("100.00")
        )
        stock_item.reserved_quantity = Decimal("10.00")
        db_session.add(stock_item)
        db_session.commit()
        db_session.refresh(stock_item)
        
        handler = AdjustStockHandler()
        command = AdjustStockCommand(
            product_id=sample_product.id,
            location_id=sample_location.id,
            quantity=Decimal("-20.00"),  # Negative for decrease
            reason="Inventory adjustment",
            user_id=sample_user.id
        )
        
        result = handler.handle(command)
        
        # Expire all to force reload from database
        db_session.expire_all()
        
        # Re-query from test session
        stock_item_in_test = db_session.query(StockItem).filter(
            StockItem.product_id == sample_product.id,
            StockItem.location_id == sample_location.id
        ).first()
        assert stock_item_in_test.physical_quantity == Decimal("80.00")  # 100 - 20

