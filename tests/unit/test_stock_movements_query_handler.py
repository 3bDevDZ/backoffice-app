"""Unit tests for GetStockMovementsHandler with order number retrieval."""
import pytest
from decimal import Decimal
from datetime import datetime
from app.application.stock.queries.queries import GetStockMovementsQuery
from app.application.stock.queries.handlers import GetStockMovementsHandler
from app.domain.models.stock import StockItem, StockMovement, Location
from app.domain.models.order import Order, OrderStatus
from app.domain.models.purchase import PurchaseOrder


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
def sample_order(db_session, sample_b2b_customer, sample_user):
    """Create a sample order for testing."""
    order = Order.create(
        customer_id=sample_b2b_customer.id,
        created_by=sample_user.id
    )
    order.status = OrderStatus.CONFIRMED.value
    db_session.add(order)
    db_session.commit()
    db_session.refresh(order)
    return order


@pytest.fixture
def sample_purchase_order_with_number(db_session, sample_supplier, sample_user):
    """Create a sample purchase order with number for testing."""
    from datetime import date
    po = PurchaseOrder.create(
        supplier_id=sample_supplier.id,
        created_by=sample_user.id,
        expected_delivery_date=date(2025, 12, 1)
    )
    db_session.add(po)
    db_session.commit()
    db_session.refresh(po)
    return po


class TestGetStockMovementsHandler:
    """Test GetStockMovementsHandler with order number retrieval."""
    
    def test_get_movements_with_order_number(self, db_session, sample_product, sample_location, 
                                             sample_user, sample_order):
        """Test that movements linked to orders include the order number."""
        # Create stock item
        stock_item = StockItem.create(
            product_id=sample_product.id,
            location_id=sample_location.id,
            physical_quantity=Decimal("100.00")
        )
        db_session.add(stock_item)
        db_session.commit()
        db_session.refresh(stock_item)
        
        # Create exit movement linked to order
        movement = StockMovement.create(
            stock_item_id=stock_item.id,
            product_id=sample_product.id,
            quantity=Decimal("-10.00"),  # Negative for exit
            movement_type="exit",
            user_id=sample_user.id,
            location_from_id=sample_location.id,
            related_document_type="order",
            related_document_id=sample_order.id,
            reason="Order shipment"
        )
        db_session.add(movement)
        db_session.commit()
        db_session.refresh(movement)
        
        # Query movements
        handler = GetStockMovementsHandler()
        query = GetStockMovementsQuery(
            page=1,
            per_page=50
        )
        movements = handler.handle(query)
        
        # Find our movement
        our_movement = next((m for m in movements if m.id == movement.id), None)
        assert our_movement is not None
        assert our_movement.related_document_type == "order"
        assert our_movement.related_document_id == sample_order.id
        assert our_movement.related_document_number == sample_order.number
        assert our_movement.type == "exit"
        assert our_movement.quantity == Decimal("-10.00")
    
    def test_get_movements_with_purchase_order_number(self, db_session, sample_product, 
                                                      sample_location, sample_user, 
                                                      sample_purchase_order_with_number):
        """Test that movements linked to purchase orders include the PO number."""
        # Create stock item
        stock_item = StockItem.create(
            product_id=sample_product.id,
            location_id=sample_location.id,
            physical_quantity=Decimal("50.00")
        )
        db_session.add(stock_item)
        db_session.commit()
        db_session.refresh(stock_item)
        
        # Create entry movement linked to purchase order
        movement = StockMovement.create(
            stock_item_id=stock_item.id,
            product_id=sample_product.id,
            quantity=Decimal("20.00"),  # Positive for entry
            movement_type="entry",
            user_id=sample_user.id,
            location_to_id=sample_location.id,
            related_document_type="purchase_order",
            related_document_id=sample_purchase_order_with_number.id,
            reason="Purchase order receipt"
        )
        db_session.add(movement)
        db_session.commit()
        db_session.refresh(movement)
        
        # Query movements
        handler = GetStockMovementsHandler()
        query = GetStockMovementsQuery(
            page=1,
            per_page=50
        )
        movements = handler.handle(query)
        
        # Find our movement
        our_movement = next((m for m in movements if m.id == movement.id), None)
        assert our_movement is not None
        assert our_movement.related_document_type == "purchase_order"
        assert our_movement.related_document_id == sample_purchase_order_with_number.id
        assert our_movement.related_document_number == sample_purchase_order_with_number.number
        assert our_movement.type == "entry"
        assert our_movement.quantity == Decimal("20.00")
    
    def test_get_movements_without_related_document(self, db_session, sample_product, 
                                                    sample_location, sample_user):
        """Test that movements without related documents work correctly."""
        # Create stock item
        stock_item = StockItem.create(
            product_id=sample_product.id,
            location_id=sample_location.id,
            physical_quantity=Decimal("100.00")
        )
        db_session.add(stock_item)
        db_session.commit()
        db_session.refresh(stock_item)
        
        # Create movement without related document
        movement = StockMovement.create(
            stock_item_id=stock_item.id,
            product_id=sample_product.id,
            quantity=Decimal("5.00"),
            movement_type="adjustment",
            user_id=sample_user.id,
            location_to_id=sample_location.id,
            reason="Manual adjustment"
        )
        db_session.add(movement)
        db_session.commit()
        db_session.refresh(movement)
        
        # Query movements
        handler = GetStockMovementsHandler()
        query = GetStockMovementsQuery(
            page=1,
            per_page=50
        )
        movements = handler.handle(query)
        
        # Find our movement
        our_movement = next((m for m in movements if m.id == movement.id), None)
        assert our_movement is not None
        assert our_movement.related_document_type is None
        assert our_movement.related_document_id is None
        assert our_movement.related_document_number is None
        assert our_movement.type == "adjustment"
    
    def test_get_movements_with_multiple_orders(self, db_session, sample_product, 
                                               sample_location, sample_user, 
                                               sample_b2b_customer):
        """Test that multiple movements with different orders are handled correctly."""
        # Create two orders
        order1 = Order.create(
            customer_id=sample_b2b_customer.id,
            created_by=sample_user.id
        )
        order1.status = OrderStatus.CONFIRMED.value
        db_session.add(order1)
        db_session.commit()
        db_session.refresh(order1)
        
        order2 = Order.create(
            customer_id=sample_b2b_customer.id,
            created_by=sample_user.id
        )
        order2.status = OrderStatus.CONFIRMED.value
        db_session.add(order2)
        db_session.commit()
        db_session.refresh(order2)
        
        # Create stock item
        stock_item = StockItem.create(
            product_id=sample_product.id,
            location_id=sample_location.id,
            physical_quantity=Decimal("200.00")
        )
        db_session.add(stock_item)
        db_session.commit()
        db_session.refresh(stock_item)
        
        # Create movements for each order
        movement1 = StockMovement.create(
            stock_item_id=stock_item.id,
            product_id=sample_product.id,
            quantity=Decimal("-10.00"),
            movement_type="exit",
            user_id=sample_user.id,
            location_from_id=sample_location.id,
            related_document_type="order",
            related_document_id=order1.id,
            reason="Order 1 shipment"
        )
        db_session.add(movement1)
        
        movement2 = StockMovement.create(
            stock_item_id=stock_item.id,
            product_id=sample_product.id,
            quantity=Decimal("-15.00"),
            movement_type="exit",
            user_id=sample_user.id,
            location_from_id=sample_location.id,
            related_document_type="order",
            related_document_id=order2.id,
            reason="Order 2 shipment"
        )
        db_session.add(movement2)
        db_session.commit()
        db_session.refresh(movement1)
        db_session.refresh(movement2)
        
        # Query movements
        handler = GetStockMovementsHandler()
        query = GetStockMovementsQuery(
            page=1,
            per_page=50
        )
        movements = handler.handle(query)
        
        # Find our movements
        m1 = next((m for m in movements if m.id == movement1.id), None)
        m2 = next((m for m in movements if m.id == movement2.id), None)
        
        assert m1 is not None
        assert m1.related_document_number == order1.number
        assert m1.related_document_id == order1.id
        
        assert m2 is not None
        assert m2.related_document_number == order2.number
        assert m2.related_document_id == order2.id
        
        # Verify they have different order numbers
        assert m1.related_document_number != m2.related_document_number
    
    def test_get_movements_filters_by_order(self, db_session, sample_product, 
                                            sample_location, sample_user, 
                                            sample_b2b_customer):
        """Test filtering movements by related document type and ID."""
        # Create two orders
        order1 = Order.create(
            customer_id=sample_b2b_customer.id,
            created_by=sample_user.id
        )
        order1.status = OrderStatus.CONFIRMED.value
        db_session.add(order1)
        db_session.commit()
        db_session.refresh(order1)
        
        order2 = Order.create(
            customer_id=sample_b2b_customer.id,
            created_by=sample_user.id
        )
        order2.status = OrderStatus.CONFIRMED.value
        db_session.add(order2)
        db_session.commit()
        db_session.refresh(order2)
        
        # Create stock item
        stock_item = StockItem.create(
            product_id=sample_product.id,
            location_id=sample_location.id,
            physical_quantity=Decimal("200.00")
        )
        db_session.add(stock_item)
        db_session.commit()
        db_session.refresh(stock_item)
        
        # Create movements for each order
        movement1 = StockMovement.create(
            stock_item_id=stock_item.id,
            product_id=sample_product.id,
            quantity=Decimal("-10.00"),
            movement_type="exit",
            user_id=sample_user.id,
            location_from_id=sample_location.id,
            related_document_type="order",
            related_document_id=order1.id,
            reason="Order 1 shipment"
        )
        db_session.add(movement1)
        
        movement2 = StockMovement.create(
            stock_item_id=stock_item.id,
            product_id=sample_product.id,
            quantity=Decimal("-15.00"),
            movement_type="exit",
            user_id=sample_user.id,
            location_from_id=sample_location.id,
            related_document_type="order",
            related_document_id=order2.id,
            reason="Order 2 shipment"
        )
        db_session.add(movement2)
        db_session.commit()
        
        # Query movements filtered by order1
        handler = GetStockMovementsHandler()
        query = GetStockMovementsQuery(
            page=1,
            per_page=50,
            related_document_type="order",
            related_document_id=order1.id
        )
        movements = handler.handle(query)
        
        # Should only return movement1
        assert len([m for m in movements if m.id == movement1.id]) == 1
        assert len([m for m in movements if m.id == movement2.id]) == 0
        
        # Verify the returned movement has the correct order number
        m1 = next((m for m in movements if m.id == movement1.id), None)
        assert m1 is not None
        assert m1.related_document_number == order1.number

