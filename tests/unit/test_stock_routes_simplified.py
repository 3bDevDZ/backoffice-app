"""Unit tests for simplified stock routes (base_url/[sub_module])."""
import pytest
from flask import Flask
from app import create_app
from app.domain.models.user import User
from app.domain.models.stock import Location, Site
from app.domain.models.settings import AppSettings
from app.infrastructure.db import get_session


@pytest.fixture
def app(db_session):
    """Create Flask app for testing."""
    # The db_session fixture already initializes the database with "sqlite:///:memory:"
    # and creates all tables. We need to ensure create_app() uses the same database.
    # Since db_session runs first, SessionLocal is already set, so create_app() won't reinitialize.
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"
    
    # Ensure all tables exist in the database used by handlers
    # This is important because get_session() creates a new session
    from app.infrastructure.db import SessionLocal, Base
    with SessionLocal() as session:
        Base.metadata.create_all(session.bind)
        session.commit()
    
    return app


@pytest.fixture
def client(app, db_session):
    """Create test client (unauthenticated)."""
    return app.test_client()


@pytest.fixture
def authenticated_client(app, db_session):
    """Create an authenticated test client."""
    user = User(username="testuser", role="admin")
    user.set_password("testpass")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    # Create test client
    client = app.test_client()
    
    # Set session variables directly to simulate authentication
    with client.session_transaction() as sess:
        sess['user_id'] = user.id
        sess['username'] = user.username
        sess['role'] = user.role
        sess.permanent = True
    
    return client


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
    # Get or create app settings (singleton pattern)
    settings = db_session.query(AppSettings).first()
    if not settings:
        settings = AppSettings.create(stock_management_mode='simple')
        db_session.add(settings)
        db_session.flush()
    else:
        settings.stock_management_mode = 'simple'
    db_session.commit()
    db_session.refresh(settings)
    return settings


@pytest.fixture
def app_settings_advanced(db_session):
    """Create app settings with advanced stock management mode."""
    # Get or create app settings (singleton pattern)
    settings = db_session.query(AppSettings).first()
    if not settings:
        settings = AppSettings.create(stock_management_mode='advanced')
        db_session.add(settings)
        db_session.flush()
    else:
        settings.stock_management_mode = 'advanced'
    db_session.commit()
    db_session.refresh(settings)
    return settings


class TestSimplifiedStockRoutes:
    """Test simplified stock routes (base_url/[sub_module])."""
    
    def test_locations_route_simple_mode(self, authenticated_client, app_settings_simple):
        """Test /locations route in simple mode (no site selection)."""
        response = authenticated_client.get('/locations')
        assert response.status_code == 200
        # In simple mode, site selection should not be visible
        assert b'site_id' not in response.data or b'None (No Site)' not in response.data
    
    def test_locations_route_advanced_mode(self, authenticated_client, app_settings_advanced, sample_site):
        """Test /locations route in advanced mode (with site selection)."""
        response = authenticated_client.get('/locations')
        assert response.status_code == 200
        # In advanced mode, site selection should be visible
        assert b'Site' in response.data or b'site_id' in response.data
    
    def test_create_location_simple_mode(self, authenticated_client, app_settings_simple):
        """Test creating location in simple mode (no site_id)."""
        response = authenticated_client.post('/locations', json={
            'code': 'TEST-WH',
            'name': 'Test Warehouse',
            'type': 'warehouse',
            'is_active': True
        })
        
        if response.status_code != 200:
            # Print error details for debugging
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.get_data(as_text=True)}")
            if response.status_code == 500:
                # Try to get JSON error if available
                try:
                    error_data = response.get_json()
                    print(f"Error JSON: {error_data}")
                except:
                    pass
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.get_data(as_text=True)}"
        data = response.get_json()
        assert data['success'] is True
        
        # Verify location was created without site_id
        with get_session() as session:
            location = session.query(Location).filter(Location.code == 'TEST-WH').first()
            assert location is not None
            assert location.site_id is None
    
    def test_create_location_advanced_mode_with_site(self, authenticated_client, app_settings_advanced, sample_site):
        """Test creating location in advanced mode with site_id."""
        response = authenticated_client.post('/locations', json={
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
    
    def test_create_location_advanced_mode_without_site(self, authenticated_client, app_settings_advanced):
        """Test creating location in advanced mode without site_id (optional)."""
        response = authenticated_client.post('/locations', json={
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
    
    def test_update_location_add_site(self, authenticated_client, app_settings_advanced, sample_site):
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
        response = authenticated_client.put(f'/locations/{location_id}', json={
            'site_id': sample_site.id
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        
        # Verify location was updated with site_id
        with get_session() as session:
            location = session.query(Location).filter(Location.id == location_id).first()
            assert location.site_id == sample_site.id
    
    def test_sites_route(self, authenticated_client):
        """Test /sites route (simplified from /stock/sites)."""
        response = authenticated_client.get('/sites')
        assert response.status_code == 200
    
    def test_transfers_route(self, authenticated_client):
        """Test /transfers route (simplified from /stock/transfers)."""
        response = authenticated_client.get('/transfers')
        assert response.status_code == 200
    
    def test_alerts_route(self, authenticated_client):
        """Test /alerts route (simplified from /stock/alerts)."""
        response = authenticated_client.get('/alerts')
        assert response.status_code == 200
    
    def test_movements_route(self, authenticated_client):
        """Test /movements route (simplified from /stock/movements)."""
        response = authenticated_client.get('/movements')
        assert response.status_code == 200
    
    def test_stock_index_route(self, authenticated_client):
        """Test /stock route (main stock page, unchanged)."""
        response = authenticated_client.get('/stock')
        assert response.status_code == 200

