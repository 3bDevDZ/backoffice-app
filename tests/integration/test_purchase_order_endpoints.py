"""Integration tests for purchase order endpoints."""
import pytest
import json
from datetime import date
from decimal import Decimal
from app import create_app
from app.infrastructure.db import get_session, Base
from app.domain.models.supplier import Supplier, SupplierConditions
from app.domain.models.user import User
from app.domain.models.product import Product
from app.domain.models.category import Category


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        from app.infrastructure.db import engine
        Base.metadata.create_all(bind=engine)
        yield app
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def db_session(app):
    """Create database session."""
    with app.app_context():
        with get_session() as session:
            yield session
            session.rollback()


@pytest.fixture
def test_user(app, db_session):
    """Create a test user and login."""
    user = User(username='testuser', role='admin')
    user.set_password('testpass')
    user.locale = 'fr'
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def authenticated_client(client, test_user):
    """Create authenticated test client."""
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id
        sess['username'] = test_user.username
        sess['role'] = test_user.role
        sess['locale'] = test_user.locale
    return client


@pytest.fixture
def test_supplier(app, db_session):
    """Create a test supplier."""
    supplier = Supplier.create(
        name='Test Supplier',
        email='supplier@example.com',
        code='SUP001'
    )
    db_session.add(supplier)
    db_session.flush()
    
    conditions = SupplierConditions(
        supplier_id=supplier.id,
        payment_terms_days=30,
        default_discount_percent=Decimal('5.00')
    )
    db_session.add(conditions)
    db_session.commit()
    db_session.refresh(supplier)
    return supplier


@pytest.fixture
def test_product(app, db_session):
    """Create a test product."""
    category = Category(name='Test Category', code='CAT001')
    db_session.add(category)
    db_session.flush()
    
    product = Product.create(
        name='Test Product',
        code='PROD001',
        price=Decimal('100.00'),
        cost=Decimal('50.00')
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product


def test_create_purchase_order_endpoint(authenticated_client, test_supplier):
    """Test creating a purchase order via POST endpoint."""
    data = {
        'supplier_id': test_supplier.id,
        'order_date': date.today().strftime('%Y-%m-%d'),
        'expected_delivery_date': date(2025, 12, 31).strftime('%Y-%m-%d'),
        'notes': 'Test order notes',
        'internal_notes': 'Internal test notes',
        'lines': []
    }
    
    response = authenticated_client.post(
        '/purchase-orders',
        data=json.dumps(data),
        content_type='application/json'
    )
    
    if response.status_code != 201:
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.data.decode('utf-8')}")
    
    assert response.status_code == 201, f"Expected 201, got {response.status_code}. Response: {response.data.decode('utf-8')}"
    result = json.loads(response.data)
    assert result['status'] == 'success'
    assert 'data' in result
    assert 'id' in result['data']
    assert result['data']['id'] > 0


def test_create_purchase_order_with_lines(authenticated_client, test_supplier, test_product):
    """Test creating a purchase order with lines."""
    data = {
        'supplier_id': test_supplier.id,
        'order_date': date.today().strftime('%Y-%m-%d'),
        'expected_delivery_date': date(2025, 12, 31).strftime('%Y-%m-%d'),
        'notes': 'Test order with lines',
        'lines': [
            {
                'product_id': test_product.id,
                'quantity': 10.0,
                'unit_price': 50.0,
                'discount_percent': 5.0,
                'tax_rate': 20.0
            },
            {
                'product_id': test_product.id,
                'quantity': 5.0,
                'unit_price': 30.0,
                'discount_percent': 0.0,
                'tax_rate': 20.0
            }
        ]
    }
    
    response = authenticated_client.post(
        '/purchase-orders',
        data=json.dumps(data),
        content_type='application/json'
    )
    
    if response.status_code != 201:
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.data.decode('utf-8')}")
    
    assert response.status_code == 201, f"Expected 201, got {response.status_code}. Response: {response.data.decode('utf-8')}"
    result = json.loads(response.data)
    assert result['status'] == 'success'
    assert 'data' in result
    assert 'id' in result['data']
    
    # Verify order was created with lines
    order_id = result['data']['id']
    from app.application.common.mediator import mediator
    from app.application.purchases.queries.queries import GetPurchaseOrderByIdQuery
    
    with authenticated_client.application.app_context():
        order_dto = mediator.dispatch(GetPurchaseOrderByIdQuery(id=order_id))
        assert order_dto is not None
        assert len(order_dto.lines) == 2
        assert order_dto.lines[0].quantity == Decimal('10.0')
        assert order_dto.lines[1].quantity == Decimal('5.0')


def test_create_purchase_order_requires_authentication(client, test_supplier):
    """Test that creating a purchase order requires authentication."""
    data = {
        'supplier_id': test_supplier.id,
        'order_date': date.today().strftime('%Y-%m-%d'),
        'lines': []
    }
    
    response = client.post(
        '/purchase-orders',
        data=json.dumps(data),
        content_type='application/json'
    )
    
    # Should redirect to login
    assert response.status_code in [302, 401]


def test_create_purchase_order_missing_required_fields(authenticated_client, test_supplier):
    """Test that missing required fields return error."""
    data = {
        'order_date': date.today().strftime('%Y-%m-%d'),
        'lines': []
        # Missing supplier_id
    }
    
    response = authenticated_client.post(
        '/purchase-orders',
        data=json.dumps(data),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    result = json.loads(response.data)
    assert result['status'] == 'error'


def test_create_purchase_order_invalid_date_format(authenticated_client, test_supplier):
    """Test that invalid date format returns error."""
    data = {
        'supplier_id': test_supplier.id,
        'order_date': 'invalid-date',
        'lines': []
    }
    
    response = authenticated_client.post(
        '/purchase-orders',
        data=json.dumps(data),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    result = json.loads(response.data)
    assert result['status'] == 'error'


def test_update_purchase_order_endpoint(authenticated_client, test_supplier, test_product):
    """Test updating a purchase order via PUT endpoint."""
    # First create an order
    from app.application.common.mediator import mediator
    from app.application.purchases.commands.commands import CreatePurchaseOrderCommand
    
    with authenticated_client.application.app_context():
        create_command = CreatePurchaseOrderCommand(
            supplier_id=test_supplier.id,
            created_by=1,  # Will be set by route
            order_date=date.today()
        )
        order_result = mediator.dispatch(create_command)
        order_id = order_result.id
    
    # Now update it
    update_data = {
        'notes': 'Updated notes',
        'internal_notes': 'Updated internal notes',
        'expected_delivery_date': date(2026, 1, 15).strftime('%Y-%m-%d')
    }
    
    response = authenticated_client.post(
        f'/purchase-orders/{order_id}',
        data=json.dumps(update_data),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    result = json.loads(response.data)
    assert result['status'] == 'success'
    
    # Verify order was updated
    from app.application.purchases.queries.queries import GetPurchaseOrderByIdQuery
    
    with authenticated_client.application.app_context():
        order_dto = mediator.dispatch(GetPurchaseOrderByIdQuery(id=order_id))
        assert order_dto.notes == 'Updated notes'
        assert order_dto.internal_notes == 'Updated internal notes'


def test_list_purchase_orders_endpoint(authenticated_client, test_supplier):
    """Test listing purchase orders."""
    # Create a few orders first
    from app.application.common.mediator import mediator
    from app.application.purchases.commands.commands import CreatePurchaseOrderCommand
    
    with authenticated_client.application.app_context():
        for i in range(3):
            command = CreatePurchaseOrderCommand(
                supplier_id=test_supplier.id,
                created_by=1,
                order_date=date.today()
            )
            mediator.dispatch(command)
    
    # List orders
    response = authenticated_client.get('/purchase-orders')
    
    assert response.status_code == 200
    # Should render HTML template
    assert b'Purchase Orders' in response.data or b'Commandes' in response.data


def test_get_purchase_order_form(authenticated_client, test_supplier):
    """Test getting the purchase order form."""
    response = authenticated_client.get('/purchase-orders/new')
    
    assert response.status_code == 200
    # Should render form template
    assert b'form' in response.data.lower() or b'Purchase Order' in response.data or b'Commande' in response.data

