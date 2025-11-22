"""Integration tests for reports routes."""
import pytest
from flask import Flask
from app import create_app
from app.domain.models.user import User
from app.domain.models.customer import Customer, CommercialConditions
from app.domain.models.product import Product
from app.domain.models.category import Category
from app.domain.models.order import Order, OrderLine
from app.domain.models.supplier import Supplier
from app.domain.models.purchase import PurchaseOrder, PurchaseOrderLine
from app.domain.models.stock import StockItem, Location
from app.domain.models.settings import AppSettings, CompanySettings
from app.infrastructure.db import get_session
from decimal import Decimal
from datetime import date, datetime, timedelta


@pytest.fixture
def app(db_session):
    """Create Flask app for testing."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"
    
    from app.infrastructure.db import SessionLocal, Base
    with SessionLocal() as session:
        Base.metadata.create_all(session.bind)
        session.commit()
    
    return app


@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user = User(username="testuser", role="admin")
    user.set_password("testpass")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def authenticated_client(app, db_session, test_user):
    """Create an authenticated test client."""
    client = app.test_client()
    
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id
        sess['username'] = test_user.username
        sess['role'] = test_user.role
        sess.permanent = True
    
    return client


@pytest.fixture
def app_settings(db_session):
    """Create app settings for testing."""
    settings = db_session.query(AppSettings).first()
    if not settings:
        settings = AppSettings(
            default_language='fr',
            stock_management_mode='simple'
        )
        db_session.add(settings)
        db_session.commit()
    return settings


@pytest.fixture
def sample_category(db_session):
    """Create a sample category."""
    category = Category.create(
        name="Test Category",
        code="TEST-CAT",
        description="Test category"
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


@pytest.fixture
def sample_product(db_session, sample_category):
    """Create a sample product."""
    product = Product.create(
        code="TEST-PROD-001",
        name="Test Product",
        description="Test product",
        price=Decimal("100.00"),
        cost=Decimal("50.00"),
        category_ids=[sample_category.id]
    )
    product.categories = [sample_category]
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product


@pytest.fixture
def sample_customer(db_session):
    """Create a sample customer."""
    customer = Customer.create(
        type='B2B',
        name="Test Customer",
        email="test@example.com",
        code="CUST-001",
        company_name="Test Company"
    )
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)
    
    # Create commercial conditions
    conditions = CommercialConditions(
        customer_id=customer.id,
        payment_terms_days=30,
        credit_limit=Decimal("10000.00")
    )
    db_session.add(conditions)
    db_session.commit()
    
    return customer


@pytest.fixture
def sample_supplier(db_session):
    """Create a sample supplier."""
    supplier = Supplier.create(
        name="Test Supplier",
        email="supplier@example.com",
        code="SUP-001"
    )
    db_session.add(supplier)
    db_session.commit()
    db_session.refresh(supplier)
    return supplier


@pytest.fixture
def sample_location(db_session):
    """Create a sample location."""
    location = Location(
        code="LOC-001",
        name="Test Location",
        type="warehouse"
    )
    db_session.add(location)
    db_session.commit()
    db_session.refresh(location)
    return location


@pytest.fixture
def sample_order(db_session, sample_customer, sample_product, test_user):
    """Create a sample order with lines."""
    # Set order date to recent date for reports
    order_date = datetime.now() - timedelta(days=5)
    
    order = Order.create(
        customer_id=sample_customer.id,
        created_by=test_user.id,
        number="ORD-001"
    )
    order.created_at = order_date  # Set created_at for date filtering
    db_session.add(order)
    db_session.flush()
    
    # Create order line
    line = OrderLine(
        order_id=order.id,
        product_id=sample_product.id,
        quantity=Decimal("10"),
        unit_price=Decimal("100.00"),
        discount_percent=Decimal("0"),
        tax_rate=Decimal("20.0"),
        sequence=1
    )
    line.calculate_totals()
    db_session.add(line)
    
    order.status = 'confirmed'
    order.calculate_totals()
    db_session.commit()
    db_session.refresh(order)
    return order


@pytest.fixture
def sample_purchase_order(db_session, sample_supplier, sample_product, test_user):
    """Create a sample purchase order."""
    # Set order date to recent date for reports
    order_date = datetime.now() - timedelta(days=5)
    
    po = PurchaseOrder.create(
        supplier_id=sample_supplier.id,
        created_by=test_user.id,
        number="PO-001"
    )
    po.created_at = order_date  # Set created_at for date filtering
    db_session.add(po)
    db_session.flush()
    
    # Create purchase order line
    line = PurchaseOrderLine(
        purchase_order_id=po.id,
        product_id=sample_product.id,
        quantity=Decimal("20"),
        unit_price=Decimal("50.00"),
        discount_percent=Decimal("0"),
        tax_rate=Decimal("20.0"),
        sequence=1
    )
    line.calculate_totals()
    db_session.add(line)
    
    po.status = 'confirmed'
    po.calculate_totals()
    db_session.commit()
    db_session.refresh(po)
    return po


class TestReportsRoutes:
    """Integration tests for reports routes."""
    
    def test_sales_report_data(self, authenticated_client, sample_order):
        """Test /reports/data/sales route."""
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        response = authenticated_client.get(
            f'/reports/data/sales?start_date={start_date.isoformat()}&end_date={end_date.isoformat()}'
        )
        
        if response.status_code != 200:
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.get_data(as_text=True)}")
            data = response.get_json()
            if data:
                print(f"Error: {data.get('error', 'Unknown error')}")
                if 'traceback' in data:
                    print(f"Traceback: {data['traceback']}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.get_data(as_text=True)}"
        data = response.get_json()
        assert data['success'] is True
        assert 'data' in data
        assert 'title' in data['data']
        assert 'report_type' in data['data']
        assert data['data']['report_type'] == 'sales'
    
    def test_margins_report_data(self, authenticated_client, sample_order):
        """Test /reports/data/margins route."""
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        response = authenticated_client.get(
            f'/reports/data/margins?start_date={start_date.isoformat()}&end_date={end_date.isoformat()}'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'data' in data
        assert 'title' in data['data']
        assert 'report_type' in data['data']
        assert data['data']['report_type'] == 'margins'
    
    def test_stock_report_data(self, authenticated_client, sample_product, sample_location, db_session):
        """Test /reports/data/stock route."""
        # Create stock item
        stock_item = StockItem(
            product_id=sample_product.id,
            location_id=sample_location.id,
            physical_quantity=Decimal("100"),
            reserved_quantity=Decimal("0")
        )
        db_session.add(stock_item)
        db_session.commit()
        
        response = authenticated_client.get('/reports/data/stock')
        
        if response.status_code != 200:
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.get_data(as_text=True)}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.get_json()
        assert data['success'] is True
        assert 'data' in data
        assert 'title' in data['data']
        assert 'report_type' in data['data']
        assert data['data']['report_type'] == 'stock'
    
    def test_customers_report_data(self, authenticated_client, sample_customer, sample_order):
        """Test /reports/data/customers route."""
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        response = authenticated_client.get(
            f'/reports/data/customers?start_date={start_date.isoformat()}&end_date={end_date.isoformat()}'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'data' in data
        assert 'title' in data['data']
        assert 'report_type' in data['data']
        assert data['data']['report_type'] == 'customers'
    
    def test_purchases_report_data(self, authenticated_client, sample_purchase_order):
        """Test /reports/data/purchases route."""
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        response = authenticated_client.get(
            f'/reports/data/purchases?start_date={start_date.isoformat()}&end_date={end_date.isoformat()}'
        )
        
        if response.status_code != 200:
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.get_data(as_text=True)}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.get_json()
        assert data['success'] is True
        assert 'data' in data
        assert 'title' in data['data']
        assert 'report_type' in data['data']
        assert data['data']['report_type'] == 'purchases'
    
    def test_sales_forecast_data(self, authenticated_client, sample_product, sample_order):
        """Test /reports/data/forecast/sales route."""
        end_date = date.today()
        start_date = end_date - timedelta(days=90)
        
        response = authenticated_client.get(
            f'/reports/data/forecast/sales?start_date={start_date.isoformat()}&end_date={end_date.isoformat()}&forecast_days=30'
        )
        
        if response.status_code != 200:
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.get_data(as_text=True)}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.get_json()
        assert data['success'] is True
        assert 'data' in data
        assert 'forecast_type' in data['data']
    
    def test_stock_forecast_data(self, authenticated_client, sample_product):
        """Test /reports/data/forecast/stock route."""
        response = authenticated_client.get(
            f'/reports/data/forecast/stock?product_id={sample_product.id}&forecast_days=30'
        )
        
        if response.status_code != 200:
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.get_data(as_text=True)}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.get_json()
        assert data['success'] is True
        assert 'data' in data
        assert 'forecast_type' in data['data']
    
    def test_reports_list_page(self, authenticated_client):
        """Test /reports page (list of reports)."""
        response = authenticated_client.get('/reports')
        assert response.status_code == 200
    
    def test_sales_report_page(self, authenticated_client):
        """Test /reports/sales page."""
        response = authenticated_client.get('/reports/sales')
        assert response.status_code == 200
    
    def test_margins_report_page(self, authenticated_client):
        """Test /reports/margins page."""
        response = authenticated_client.get('/reports/margins')
        assert response.status_code == 200
    
    def test_stock_report_page(self, authenticated_client):
        """Test /reports/stock page."""
        response = authenticated_client.get('/reports/stock')
        assert response.status_code == 200
    
    def test_customers_report_page(self, authenticated_client):
        """Test /reports/customers page."""
        response = authenticated_client.get('/reports/customers')
        assert response.status_code == 200
    
    def test_purchases_report_page(self, authenticated_client):
        """Test /reports/purchases page."""
        response = authenticated_client.get('/reports/purchases')
        assert response.status_code == 200
    
    def test_forecast_report_page(self, authenticated_client):
        """Test /reports/forecast page."""
        response = authenticated_client.get('/reports/forecast')
        assert response.status_code == 200
    
    def test_report_builder_page(self, authenticated_client):
        """Test /reports/builder page."""
        response = authenticated_client.get('/reports/builder')
        assert response.status_code == 200
    
    def test_export_report_sales(self, authenticated_client, sample_order):
        """Test /reports/export route for sales report."""
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        response = authenticated_client.post(
            '/reports/export',
            json={
                'report_type': 'sales',
                'format': 'excel',
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            content_type='application/json'
        )
        
        assert response.status_code == 200
        assert response.content_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    
    def test_export_report_margins(self, authenticated_client, sample_order):
        """Test /reports/export route for margins report."""
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        response = authenticated_client.post(
            '/reports/export',
            json={
                'report_type': 'margins',
                'format': 'excel',
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            content_type='application/json'
        )
        
        assert response.status_code == 200
        assert response.content_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    
    def test_reports_require_authentication(self, app, db_session):
        """Test that reports routes require authentication."""
        client = app.test_client()
        
        response = client.get('/reports/data/sales')
        # Should redirect to login
        assert response.status_code in [302, 401]
    
    def test_reports_require_roles(self, app, db_session):
        """Test that reports routes require proper roles."""
        # Create user with insufficient role
        user = User(username="testuser2", role="warehouse")
        user.set_password("testpass")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        client = app.test_client()
        with client.session_transaction() as sess:
            sess['user_id'] = user.id
            sess['username'] = user.username
            sess['role'] = user.role
        
        # Try to access commercial report (should redirect)
        response = client.get('/reports/data/sales')
        assert response.status_code in [302, 403]

