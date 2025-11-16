"""Integration tests for purchase order creation."""
import pytest
from datetime import date
from app import create_app
from app.infrastructure.db import get_session
from app.domain.models.supplier import Supplier
from app.domain.models.user import User
from app.domain.models.product import Product
from app.domain.models.category import Category
from app.application.common.mediator import mediator
from app.application.purchases.commands.commands import CreatePurchaseOrderCommand, AddPurchaseOrderLineCommand


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    return app


@pytest.fixture
def db_session(app):
    """Create database session."""
    with app.app_context():
        with get_session() as session:
            yield session
            session.rollback()


@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user = User(
        username='testuser',
        email='test@example.com',
        password_hash='hashed_password',
        role='admin',
        locale='fr'
    )
    db_session.add(user)
    db_session.flush()
    return user


@pytest.fixture
def test_supplier(db_session):
    """Create a test supplier."""
    supplier = Supplier.create(
        name='Test Supplier',
        email='supplier@example.com',
        code='SUP001'
    )
    db_session.add(supplier)
    db_session.flush()
    return supplier


@pytest.fixture
def test_product(db_session):
    """Create a test product."""
    category = Category(name='Test Category', code='CAT001')
    db_session.add(category)
    db_session.flush()
    
    product = Product.create(
        name='Test Product',
        code='PROD001',
        price=100.0,
        cost=50.0
    )
    db_session.add(product)
    db_session.flush()
    return product


def test_create_purchase_order_with_lines(db_session, test_user, test_supplier, test_product):
    """Test creating a purchase order with lines."""
    # Create purchase order
    command = CreatePurchaseOrderCommand(
        supplier_id=test_supplier.id,
        created_by=test_user.id,
        order_date=date.today(),
        expected_delivery_date=date(2025, 12, 31),
        notes='Test order'
    )
    
    order = mediator.dispatch(command)
    
    # Try to access order.id - this should work even after session closes
    order_id = order.id
    assert order_id is not None
    assert order_id > 0
    
    # Try to access other attributes
    assert order.number is not None
    assert order.status == 'draft'
    assert order.supplier_id == test_supplier.id
    
    # Now add a line
    line_command = AddPurchaseOrderLineCommand(
        purchase_order_id=order_id,
        product_id=test_product.id,
        quantity=10.0,
        unit_price=50.0,
        discount_percent=5.0,
        tax_rate=20.0
    )
    
    line = mediator.dispatch(line_command)
    assert line is not None
    assert line.purchase_order_id == order_id


def test_create_purchase_order_detached_object(db_session, test_user, test_supplier):
    """Test that purchase order object can be used after session closes."""
    command = CreatePurchaseOrderCommand(
        supplier_id=test_supplier.id,
        created_by=test_user.id,
        order_date=date.today()
    )
    
    order = mediator.dispatch(command)
    
    # Access attributes that should be loaded (not lazy relationships)
    order_id = order.id
    number = order.number
    status = order.status
    supplier_id = order.supplier_id
    order_date = order.order_date
    
    # All these should work without session
    assert order_id is not None
    assert number is not None
    assert status == 'draft'
    assert supplier_id == test_supplier.id
    assert order_date == date.today()
    
    # Try accessing lazy-loaded relationship (this might fail)
    try:
        supplier = order.supplier
        # If we get here, supplier was loaded before session closed
        assert supplier is not None
    except Exception as e:
        # Expected: relationship not loaded
        assert 'not bound to a Session' in str(e) or 'DetachedInstanceError' in str(type(e).__name__)

