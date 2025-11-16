"""Integration tests for stock API endpoints."""
import pytest
from decimal import Decimal
from app import create_app
from app.domain.models.stock import Location, StockItem
from app.domain.models.product import Product
from app.domain.models.user import User


@pytest.fixture
def client(db_session):
    """Create a test client."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture
def auth_headers(client, db_session):
    """Create authentication headers for API requests."""
    # Create a test user
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash="hash",
        role="admin",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    
    # Login to get token
    response = client.post('/api/auth/login', json={
        'username': 'testuser',
        'password': 'password'  # Adjust based on your auth implementation
    })
    
    if response.status_code == 200:
        token = response.json.get('access_token')
        return {'Authorization': f'Bearer {token}'}
    return {}


class TestStockLevelsEndpoints:
    """Test stock levels API endpoints."""
    
    def test_get_stock_levels(self, client, db_session, sample_product, sample_location):
        """Test getting stock levels."""
        # Create stock item
        stock_item = StockItem.create(
            product_id=sample_product.id,
            location_id=sample_location.id,
            physical_quantity=Decimal("100.00")
        )
        db_session.add(stock_item)
        db_session.commit()
        
        response = client.get('/api/stock/levels')
        
        assert response.status_code == 200
        data = response.json
        assert 'items' in data
        assert len(data['items']) > 0
    
    def test_get_stock_levels_with_filters(self, client, db_session, sample_product, sample_location):
        """Test getting stock levels with filters."""
        stock_item = StockItem.create(
            product_id=sample_product.id,
            location_id=sample_location.id,
            physical_quantity=Decimal("100.00")
        )
        db_session.add(stock_item)
        db_session.commit()
        
        response = client.get(f'/api/stock/levels?location_id={sample_location.id}')
        
        assert response.status_code == 200
        data = response.json
        assert 'items' in data


class TestStockAlertsEndpoints:
    """Test stock alerts API endpoints."""
    
    def test_get_stock_alerts(self, client, db_session, sample_product, sample_location):
        """Test getting stock alerts."""
        # Create stock item with low stock
        stock_item = StockItem.create(
            product_id=sample_product.id,
            location_id=sample_location.id,
            physical_quantity=Decimal("5.00"),
            min_stock=Decimal("10.00")
        )
        db_session.add(stock_item)
        db_session.commit()
        
        response = client.get('/api/stock/alerts')
        
        assert response.status_code == 200
        data = response.json
        assert 'items' in data


class TestStockMovementsEndpoints:
    """Test stock movements API endpoints."""
    
    def test_get_stock_movements(self, client, db_session):
        """Test getting stock movements."""
        response = client.get('/api/stock/movements')
        
        assert response.status_code == 200
        data = response.json
        assert 'items' in data


class TestLocationsEndpoints:
    """Test locations API endpoints."""
    
    def test_get_locations(self, client, db_session, sample_location):
        """Test getting locations."""
        response = client.get('/api/stock/locations')
        
        assert response.status_code == 200
        data = response.json
        assert isinstance(data, list) or 'data' in data
    
    def test_get_location_by_id(self, client, db_session, sample_location):
        """Test getting a specific location."""
        response = client.get(f'/api/stock/locations/{sample_location.id}')
        
        assert response.status_code == 200
        data = response.json
        assert 'id' in data or 'data' in data

