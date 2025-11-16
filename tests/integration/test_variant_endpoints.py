"""Integration tests for product variant API endpoints."""
import pytest
import json
from decimal import Decimal
from app import create_app
from app.infrastructure.db import get_session, Base
from app.domain.models.user import User
from app.domain.models.product import Product, ProductVariant
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
    """Create a test user."""
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
    # Login to get JWT token
    login_response = client.post('/api/auth/login', json={
        'username': 'testuser',
        'password': 'testpass'
    })
    assert login_response.status_code == 200
    response_data = json.loads(login_response.data)
    # API returns 'access_token' not 'token'
    token = response_data['data']['access_token']
    
    # Set authorization header
    client.environ_base['HTTP_AUTHORIZATION'] = f'Bearer {token}'
    return client


@pytest.fixture
def test_category(app, db_session):
    """Create a test category."""
    category = Category.create(
        name='Test Category',
        code='TEST-CAT'
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


@pytest.fixture
def test_product(app, db_session, test_category):
    """Create a test product."""
    product = Product.create(
        code='TEST-PROD',
        name='Test Product',
        price=Decimal('100.00'),
        cost=Decimal('50.00'),
        category_ids=[test_category.id]
    )
    product.categories = [test_category]
    db_session.add(product)
    db_session.flush()
    
    # Update domain event
    events = product.get_domain_events()
    for event in events:
        if hasattr(event, 'product_id') and event.product_id == 0:
            event.product_id = product.id
    
    db_session.commit()
    db_session.refresh(product)
    return product


@pytest.fixture
def test_variant(app, db_session, test_product):
    """Create a test variant."""
    variant = ProductVariant.create(
        product_id=test_product.id,
        code='TEST-VAR',
        name='Test Variant',
        attributes='{"color": "red", "size": "L"}',
        price=Decimal('110.00')
    )
    db_session.add(variant)
    db_session.commit()
    db_session.refresh(variant)
    return variant


class TestVariantEndpoints:
    """Integration tests for variant API endpoints."""
    
    def test_list_variants_success(self, authenticated_client, test_product, test_variant):
        """Test GET /api/products/{id}/variants endpoint."""
        response = authenticated_client.get(f'/api/products/{test_product.id}/variants')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['data']) == 1
        assert data['data'][0]['code'] == 'TEST-VAR'
        assert data['data'][0]['name'] == 'Test Variant'
    
    def test_list_variants_unauthorized(self, client, test_product):
        """Test that unauthenticated requests are rejected."""
        response = client.get(f'/api/products/{test_product.id}/variants')
        assert response.status_code == 401
    
    def test_create_variant_success(self, authenticated_client, test_product):
        """Test POST /api/products/{id}/variants endpoint."""
        response = authenticated_client.post(
            f'/api/products/{test_product.id}/variants',
            json={
                'code': 'NEW-VAR',
                'name': 'New Variant',
                'attributes': '{"color": "blue"}',
                'price': '120.00',
                'barcode': '9876543210'
            },
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['code'] == 'NEW-VAR'
        assert data['data']['name'] == 'New Variant'
        assert float(data['data']['price']) == 120.00
    
    def test_create_variant_duplicate_code_fails(self, authenticated_client, test_product, test_variant):
        """Test that creating variant with duplicate code fails."""
        response = authenticated_client.post(
            f'/api/products/{test_product.id}/variants',
            json={
                'code': 'TEST-VAR',  # Duplicate
                'name': 'Duplicate Variant'
            },
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        error_msg = data['error'] if isinstance(data['error'], str) else str(data['error'])
        assert 'already exists' in error_msg.lower()
    
    def test_get_variant_success(self, authenticated_client, test_variant):
        """Test GET /api/products/variants/{id} endpoint."""
        response = authenticated_client.get(f'/api/products/variants/{test_variant.id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['id'] == test_variant.id
        assert data['data']['code'] == 'TEST-VAR'
    
    def test_get_variant_not_found(self, authenticated_client):
        """Test GET /api/products/variants/{id} with non-existent ID."""
        response = authenticated_client.get('/api/products/variants/99999')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_update_variant_success(self, authenticated_client, test_variant):
        """Test PUT /api/products/variants/{id} endpoint."""
        response = authenticated_client.put(
            f'/api/products/variants/{test_variant.id}',
            json={
                'name': 'Updated Variant',
                'price': '125.00',
                'attributes': '{"color": "green"}'
            },
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['name'] == 'Updated Variant'
        assert float(data['data']['price']) == 125.00
    
    def test_update_variant_not_found(self, authenticated_client):
        """Test PUT /api/products/variants/{id} with non-existent ID."""
        response = authenticated_client.put(
            '/api/products/variants/99999',
            json={'name': 'Non-existent'},
            content_type='application/json'
        )
        
        assert response.status_code == 404
    
    def test_archive_variant_success(self, authenticated_client, test_variant):
        """Test POST /api/products/variants/{id}/archive endpoint."""
        response = authenticated_client.post(f'/api/products/variants/{test_variant.id}/archive')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['status'] == 'archived'
    
    def test_activate_variant_success(self, authenticated_client, test_variant):
        """Test POST /api/products/variants/{id}/activate endpoint."""
        # First archive the variant
        authenticated_client.post(f'/api/products/variants/{test_variant.id}/archive')
        
        # Then activate it
        response = authenticated_client.post(f'/api/products/variants/{test_variant.id}/activate')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['status'] == 'active'
    
    def test_delete_variant_success(self, authenticated_client, test_product):
        """Test DELETE /api/products/variants/{id} endpoint."""
        # Create a variant to delete
        create_response = authenticated_client.post(
            f'/api/products/{test_product.id}/variants',
            json={
                'code': 'TO-DELETE',
                'name': 'To Delete'
            },
            content_type='application/json'
        )
        variant_id = json.loads(create_response.data)['data']['id']
        
        # Delete the variant
        response = authenticated_client.delete(f'/api/products/variants/{variant_id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        # Verify variant is deleted
        get_response = authenticated_client.get(f'/api/products/variants/{variant_id}')
        assert get_response.status_code == 404
    
    def test_list_variants_with_include_archived(self, authenticated_client, test_product, test_variant):
        """Test listing variants with include_archived parameter."""
        # Archive the variant
        authenticated_client.post(f'/api/products/variants/{test_variant.id}/archive')
        
        # List without archived
        response = authenticated_client.get(
            f'/api/products/{test_product.id}/variants?include_archived=false'
        )
        data = json.loads(response.data)
        assert len(data['data']) == 0
        
        # List with archived
        response = authenticated_client.get(
            f'/api/products/{test_product.id}/variants?include_archived=true'
        )
        data = json.loads(response.data)
        assert len(data['data']) == 1
        assert data['data'][0]['status'] == 'archived'
    
    def test_create_variant_without_price(self, authenticated_client, test_product):
        """Test creating variant without price override."""
        response = authenticated_client.post(
            f'/api/products/{test_product.id}/variants',
            json={
                'code': 'NO-PRICE',
                'name': 'No Price Variant'
                # No price field
            },
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['data']['price'] is None
    
    def test_create_variant_invalid_product(self, authenticated_client):
        """Test creating variant for non-existent product."""
        response = authenticated_client.post(
            '/api/products/99999/variants',
            json={
                'code': 'INVALID',
                'name': 'Invalid Product Variant'
            },
            content_type='application/json'
        )
        
        assert response.status_code == 400

