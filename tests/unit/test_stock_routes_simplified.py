"""Unit tests for simplified stock routes (base_url/[sub_module])."""
import pytest
from flask import Flask
from app import create_app
from app.domain.models.user import User
from app.domain.models.stock import Location, Site
from app.domain.models.settings import AppSettings
from app.infrastructure.db import get_session


@pytest.fixture
def app():
    """Create Flask app for testing."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    return app


@pytest.fixture
def client(app, db_session):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def authenticated_user(app, db_session):
    """Create and login a test user."""
    user = User(username="testuser", role="admin")
    user.set_password("testpass")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    # Login via test client
    with app.test_client() as client:
        client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass'
        })
        yield user


@pytest.fixture
def sample_site(db_session):
    """Create a sample site for testing."""
    site = Site.create(
        code="SITE-001",
        name="Test Site",
        status="active"
    )
    db_session.add(site)
    db_session.commit()
    db_session.refresh(site)
    return site


@pytest.fixture
def app_settings_simple(db_session):
    """Create app settings with simple stock management mode."""
    settings = AppSettings.get_or_create(db_session)
    settings.stock_management_mode = 'simple'
    db_session.commit()
    return settings


@pytest.fixture
def app_settings_advanced(db_session):
    """Create app settings with advanced stock management mode."""
    settings = AppSettings.get_or_create(db_session)
    settings.stock_management_mode = 'advanced'
    db_session.commit()
    return settings


class TestSimplifiedStockRoutes:
    """Test simplified stock routes (base_url/[sub_module])."""
    
    def test_locations_route_simple_mode(self, client, authenticated_user, app_settings_simple):
        """Test /locations route in simple mode (no site selection)."""
        response = client.get('/locations')
        assert response.status_code == 200
        # In simple mode, site selection should not be visible
        assert b'site_id' not in response.data or b'None (No Site)' not in response.data
    
    def test_locations_route_advanced_mode(self, client, authenticated_user, app_settings_advanced, sample_site):
        """Test /locations route in advanced mode (with site selection)."""
        response = client.get('/locations')
        assert response.status_code == 200
        # In advanced mode, site selection should be visible
        assert b'Site' in response.data or b'site_id' in response.data
    
    def test_create_location_simple_mode(self, client, authenticated_user, app_settings_simple):
        """Test creating location in simple mode (no site_id)."""
        response = client.post('/locations', json={
            'code': 'TEST-WH',
            'name': 'Test Warehouse',
            'type': 'warehouse',
            'is_active': True
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        
        # Verify location was created without site_id
        with get_session() as session:
            location = session.query(Location).filter(Location.code == 'TEST-WH').first()
            assert location is not None
            assert location.site_id is None
    
    def test_create_location_advanced_mode_with_site(self, client, authenticated_user, app_settings_advanced, sample_site):
        """Test creating location in advanced mode with site_id."""
        response = client.post('/locations', json={
            'code': 'TEST-WH-ADV',
            'name': 'Test Warehouse Advanced',
            'type': 'warehouse',
            'site_id': sample_site.id,
            'is_active': True
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        
        # Verify location was created with site_id
        with get_session() as session:
            location = session.query(Location).filter(Location.code == 'TEST-WH-ADV').first()
            assert location is not None
            assert location.site_id == sample_site.id
    
    def test_create_location_advanced_mode_without_site(self, client, authenticated_user, app_settings_advanced):
        """Test creating location in advanced mode without site_id (optional)."""
        response = client.post('/locations', json={
            'code': 'TEST-WH-ADV-NO-SITE',
            'name': 'Test Warehouse Advanced No Site',
            'type': 'warehouse',
            'is_active': True
            # site_id not provided, should be None
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        
        # Verify location was created without site_id (None is allowed)
        with get_session() as session:
            location = session.query(Location).filter(Location.code == 'TEST-WH-ADV-NO-SITE').first()
            assert location is not None
            assert location.site_id is None
    
    def test_update_location_add_site(self, client, authenticated_user, app_settings_advanced, sample_site):
        """Test updating location to add site_id."""
        # Create location without site
        location = Location.create(
            code="UPDATE-WH",
            name="Update Warehouse",
            type="warehouse",
            site_id=None
        )
        with get_session() as session:
            session.add(location)
            session.commit()
            session.refresh(location)
            location_id = location.id
        
        # Update to add site
        response = client.put(f'/locations/{location_id}', json={
            'site_id': sample_site.id
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        
        # Verify location was updated with site_id
        with get_session() as session:
            location = session.query(Location).filter(Location.id == location_id).first()
            assert location.site_id == sample_site.id
    
    def test_sites_route(self, client, authenticated_user):
        """Test /sites route (simplified from /stock/sites)."""
        response = client.get('/sites')
        assert response.status_code == 200
    
    def test_transfers_route(self, client, authenticated_user):
        """Test /transfers route (simplified from /stock/transfers)."""
        response = client.get('/transfers')
        assert response.status_code == 200
    
    def test_alerts_route(self, client, authenticated_user):
        """Test /alerts route (simplified from /stock/alerts)."""
        response = client.get('/alerts')
        assert response.status_code == 200
    
    def test_movements_route(self, client, authenticated_user):
        """Test /movements route (simplified from /stock/movements)."""
        response = client.get('/movements')
        assert response.status_code == 200
    
    def test_stock_index_route(self, client, authenticated_user):
        """Test /stock route (main stock page, unchanged)."""
        response = client.get('/stock')
        assert response.status_code == 200

