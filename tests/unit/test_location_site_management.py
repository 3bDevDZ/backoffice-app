"""Unit tests for location management with site_id support (simple vs advanced mode)."""
import pytest
from decimal import Decimal
from app.application.stock.commands.commands import (
    CreateLocationCommand, UpdateLocationCommand
)
from app.application.stock.commands.handlers import (
    CreateLocationHandler, UpdateLocationHandler
)
from app.domain.models.stock import Location, Site


@pytest.fixture
def sample_site(db_session):
    """Create a sample site for testing."""
    site = Site.create(
        code="SITE-001",
        name="Site Principal",
        address="123 Rue Test, Paris",
        status="active"
    )
    db_session.add(site)
    db_session.commit()
    db_session.refresh(site)
    return site


@pytest.fixture
def sample_location_without_site(db_session):
    """Create a sample location without site (simple mode)."""
    location = Location.create(
        code="WH-001",
        name="Warehouse 1",
        type="warehouse",
        site_id=None  # No site in simple mode
    )
    db_session.add(location)
    db_session.commit()
    db_session.refresh(location)
    return location


@pytest.fixture
def sample_location_with_site(db_session, sample_site):
    """Create a sample location with site (advanced mode)."""
    location = Location.create(
        code="WH-002",
        name="Warehouse 2",
        type="warehouse",
        site_id=sample_site.id  # Linked to site
    )
    db_session.add(location)
    db_session.commit()
    db_session.refresh(location)
    return location


class TestCreateLocationWithSite:
    """Test CreateLocationHandler with site_id support."""
    
    def test_create_location_without_site_simple_mode(self, db_session):
        """Test creating location without site_id (simple mode)."""
        handler = CreateLocationHandler()
        command = CreateLocationCommand(
            code="WH-SIMPLE",
            name="Simple Warehouse",
            type="warehouse",
            site_id=None  # No site in simple mode
        )
        
        location = handler.handle(command)
        
        # Re-query from test session
        location_in_test = db_session.query(Location).filter(Location.code == "WH-SIMPLE").first()
        assert location_in_test is not None
        assert location_in_test.code == "WH-SIMPLE"
        assert location_in_test.name == "Simple Warehouse"
        assert location_in_test.site_id is None  # Should be None in simple mode
    
    def test_create_location_with_site_advanced_mode(self, db_session, sample_site):
        """Test creating location with site_id (advanced mode)."""
        handler = CreateLocationHandler()
        command = CreateLocationCommand(
            code="WH-ADVANCED",
            name="Advanced Warehouse",
            type="warehouse",
            site_id=sample_site.id  # Linked to site
        )
        
        location = handler.handle(command)
        
        # Re-query from test session
        location_in_test = db_session.query(Location).filter(Location.code == "WH-ADVANCED").first()
        assert location_in_test is not None
        assert location_in_test.code == "WH-ADVANCED"
        assert location_in_test.name == "Advanced Warehouse"
        assert location_in_test.site_id == sample_site.id
        assert location_in_test.site.id == sample_site.id
    
    def test_create_location_with_invalid_site(self, db_session):
        """Test creating location with invalid site_id raises error."""
        handler = CreateLocationHandler()
        command = CreateLocationCommand(
            code="WH-INVALID",
            name="Invalid Warehouse",
            type="warehouse",
            site_id=99999  # Non-existent site
        )
        
        with pytest.raises(ValueError, match="Site not found"):
            handler.handle(command)
    
    def test_create_location_with_site_and_parent(self, db_session, sample_site):
        """Test creating location with both site and parent."""
        # Create parent location first
        parent = Location.create(
            code="PARENT-WH",
            name="Parent Warehouse",
            type="warehouse",
            site_id=sample_site.id
        )
        db_session.add(parent)
        db_session.commit()
        db_session.refresh(parent)
        
        handler = CreateLocationHandler()
        command = CreateLocationCommand(
            code="ZONE-001",
            name="Zone 1",
            type="zone",
            parent_id=parent.id,
            site_id=sample_site.id
        )
        
        location = handler.handle(command)
        
        # Re-query from test session
        location_in_test = db_session.query(Location).filter(Location.code == "ZONE-001").first()
        assert location_in_test is not None
        assert location_in_test.parent_id == parent.id
        assert location_in_test.site_id == sample_site.id


class TestUpdateLocationWithSite:
    """Test UpdateLocationHandler with site_id support."""
    
    def test_update_location_add_site(self, db_session, sample_location_without_site, sample_site):
        """Test updating location to add site_id."""
        handler = UpdateLocationHandler()
        command = UpdateLocationCommand(
            id=sample_location_without_site.id,
            site_id=sample_site.id
        )
        
        location = handler.handle(command)
        
        # Re-query from test session
        db_session.expire_all()
        location_in_test = db_session.query(Location).filter(Location.id == sample_location_without_site.id).first()
        assert location_in_test.site_id == sample_site.id
    
    def test_update_location_remove_site(self, db_session, sample_location_with_site):
        """Test updating location to remove site_id (set to None)."""
        handler = UpdateLocationHandler()
        command = UpdateLocationCommand(
            id=sample_location_with_site.id,
            site_id=None  # Remove site link
        )
        
        location = handler.handle(command)
        
        # Re-query from test session
        db_session.expire_all()
        location_in_test = db_session.query(Location).filter(Location.id == sample_location_with_site.id).first()
        assert location_in_test.site_id is None
    
    def test_update_location_change_site(self, db_session, sample_location_with_site):
        """Test updating location to change site_id."""
        # Create a new site
        new_site = Site.create(
            code="SITE-002",
            name="Nouveau Site",
            status="active"
        )
        db_session.add(new_site)
        db_session.commit()
        db_session.refresh(new_site)
        
        handler = UpdateLocationHandler()
        command = UpdateLocationCommand(
            id=sample_location_with_site.id,
            site_id=new_site.id
        )
        
        location = handler.handle(command)
        
        # Re-query from test session
        db_session.expire_all()
        location_in_test = db_session.query(Location).filter(Location.id == sample_location_with_site.id).first()
        assert location_in_test.site_id == new_site.id
        assert location_in_test.site.id == new_site.id
    
    def test_update_location_with_invalid_site(self, db_session, sample_location_without_site):
        """Test updating location with invalid site_id raises error."""
        handler = UpdateLocationHandler()
        command = UpdateLocationCommand(
            id=sample_location_without_site.id,
            site_id=99999  # Non-existent site
        )
        
        with pytest.raises(ValueError, match="Site not found"):
            handler.handle(command)
    
    def test_update_location_keep_site_unchanged(self, db_session, sample_location_with_site, sample_site):
        """Test updating other fields without changing site_id."""
        handler = UpdateLocationHandler()
        command = UpdateLocationCommand(
            id=sample_location_with_site.id,
            name="Updated Warehouse Name"
            # site_id not provided, should remain unchanged
        )
        
        location = handler.handle(command)
        
        # Re-query from test session
        db_session.expire_all()
        location_in_test = db_session.query(Location).filter(Location.id == sample_location_with_site.id).first()
        assert location_in_test.name == "Updated Warehouse Name"
        assert location_in_test.site_id == sample_site.id  # Should remain unchanged


class TestLocationDomainModel:
    """Test Location domain model with site_id."""
    
    def test_location_create_without_site(self):
        """Test Location.create() without site_id."""
        location = Location.create(
            code="TEST-WH",
            name="Test Warehouse",
            type="warehouse",
            site_id=None
        )
        
        assert location.code == "TEST-WH"
        assert location.name == "Test Warehouse"
        assert location.type == "warehouse"
        assert location.site_id is None
    
    def test_location_create_with_site(self):
        """Test Location.create() with site_id."""
        # Note: site_id is just an integer in the factory method
        # The actual Site object relationship is set by SQLAlchemy
        location = Location.create(
            code="TEST-WH-2",
            name="Test Warehouse 2",
            type="warehouse",
            site_id=1  # Assuming site with id=1 exists
        )
        
        assert location.code == "TEST-WH-2"
        assert location.name == "Test Warehouse 2"
        assert location.type == "warehouse"
        assert location.site_id == 1
    
    def test_location_create_with_all_fields(self):
        """Test Location.create() with all fields including site_id."""
        location = Location.create(
            code="TEST-WH-3",
            name="Test Warehouse 3",
            type="warehouse",
            parent_id=None,
            site_id=2,
            capacity=Decimal("1000.00"),
            is_active=True
        )
        
        assert location.code == "TEST-WH-3"
        assert location.name == "Test Warehouse 3"
        assert location.type == "warehouse"
        assert location.parent_id is None
        assert location.site_id == 2
        assert location.capacity == Decimal("1000.00")
        assert location.is_active is True


class TestLocationSiteRelationship:
    """Test the relationship between Location and Site."""
    
    def test_location_site_relationship(self, db_session, sample_site):
        """Test that location.site relationship works correctly."""
        location = Location.create(
            code="REL-WH",
            name="Relationship Test Warehouse",
            type="warehouse",
            site_id=sample_site.id
        )
        db_session.add(location)
        db_session.commit()
        db_session.refresh(location)
        
        # Test relationship
        assert location.site is not None
        assert location.site.id == sample_site.id
        assert location.site.code == "SITE-001"
        assert location.site.name == "Site Principal"
        
        # Test reverse relationship
        assert location in sample_site.locations
    
    def test_site_locations_collection(self, db_session, sample_site):
        """Test that site.locations collection contains all linked locations."""
        # Create multiple locations for the same site
        location1 = Location.create(
            code="WH-A",
            name="Warehouse A",
            type="warehouse",
            site_id=sample_site.id
        )
        location2 = Location.create(
            code="WH-B",
            name="Warehouse B",
            type="warehouse",
            site_id=sample_site.id
        )
        location3 = Location.create(
            code="ZONE-A",
            name="Zone A",
            type="zone",
            site_id=sample_site.id
        )
        
        db_session.add_all([location1, location2, location3])
        db_session.commit()
        
        # Refresh site to get updated relationships
        db_session.refresh(sample_site)
        
        # Verify all locations are in the site's locations collection
        location_codes = {loc.code for loc in sample_site.locations}
        assert "WH-A" in location_codes
        assert "WH-B" in location_codes
        assert "ZONE-A" in location_codes
    
    def test_location_without_site_no_relationship(self, db_session):
        """Test that location without site_id has no site relationship."""
        location = Location.create(
            code="NO-SITE-WH",
            name="No Site Warehouse",
            type="warehouse",
            site_id=None
        )
        db_session.add(location)
        db_session.commit()
        db_session.refresh(location)
        
        # site_id should be None
        assert location.site_id is None
        # site relationship should be None
        assert location.site is None

