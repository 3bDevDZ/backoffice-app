"""Unit tests for Volume Pricing command handlers."""
import pytest
from decimal import Decimal
from app.application.products.pricing.commands.commands import (
    CreateVolumePricingCommand,
    UpdateVolumePricingCommand,
    DeleteVolumePricingCommand
)
from app.application.products.pricing.commands.handlers import (
    CreateVolumePricingHandler,
    UpdateVolumePricingHandler,
    DeleteVolumePricingHandler
)
from app.application.products.pricing.queries.queries import GetVolumePricingQuery
from app.application.products.pricing.queries.handlers import GetVolumePricingHandler
from app.domain.models.product import Product, ProductVolumePricing


# Use fixtures from conftest.py


class TestCreateVolumePricingHandler:
    """Tests for CreateVolumePricingHandler."""
    
    def test_create_volume_pricing_tier_success(self, db_session, sample_product):
        """Test creating a volume pricing tier successfully."""
        handler = CreateVolumePricingHandler()
        
        command = CreateVolumePricingCommand(
            product_id=sample_product.id,
            min_quantity=Decimal("10.000"),
            price=Decimal("90.00"),
            max_quantity=Decimal("50.000")
        )
        
        result = handler.handle(command)
        
        assert result is not None
        assert result.product_id == sample_product.id
        assert result.min_quantity == Decimal("10.000")
        assert result.max_quantity == Decimal("50.000")
        assert result.price == Decimal("90.00")
        
        # Verify it's persisted
        tier = db_session.get(ProductVolumePricing, result.id)
        assert tier is not None
        assert tier.min_quantity == Decimal("10.000")
    
    def test_create_volume_pricing_tier_unlimited(self, db_session, sample_product):
        """Test creating a volume pricing tier with unlimited max quantity."""
        handler = CreateVolumePricingHandler()
        
        command = CreateVolumePricingCommand(
            product_id=sample_product.id,
            min_quantity=Decimal("100.000"),
            price=Decimal("80.00"),
            max_quantity=None  # Unlimited
        )
        
        result = handler.handle(command)
        
        assert result is not None
        assert result.max_quantity is None
    
    def test_create_volume_pricing_tier_product_not_found(self, db_session):
        """Test creating a volume pricing tier for non-existent product."""
        handler = CreateVolumePricingHandler()
        
        command = CreateVolumePricingCommand(
            product_id=99999,
            min_quantity=Decimal("10.000"),
            price=Decimal("90.00")
        )
        
        with pytest.raises(ValueError, match="Product with ID 99999 not found"):
            handler.handle(command)
    
    def test_create_volume_pricing_tier_negative_min_quantity(self, db_session, sample_product):
        """Test creating a volume pricing tier with negative min quantity."""
        handler = CreateVolumePricingHandler()
        
        command = CreateVolumePricingCommand(
            product_id=sample_product.id,
            min_quantity=Decimal("-10.000"),
            price=Decimal("90.00")
        )
        
        with pytest.raises(ValueError, match="Minimum quantity must be non-negative"):
            handler.handle(command)
    
    def test_create_volume_pricing_tier_max_less_than_min(self, db_session, sample_product):
        """Test creating a volume pricing tier with max < min."""
        handler = CreateVolumePricingHandler()
        
        command = CreateVolumePricingCommand(
            product_id=sample_product.id,
            min_quantity=Decimal("50.000"),
            max_quantity=Decimal("10.000"),  # Less than min
            price=Decimal("90.00")
        )
        
        with pytest.raises(ValueError, match="Maximum quantity must be greater than or equal to minimum quantity"):
            handler.handle(command)
    
    def test_create_volume_pricing_tier_negative_price(self, db_session, sample_product):
        """Test creating a volume pricing tier with negative price."""
        handler = CreateVolumePricingHandler()
        
        command = CreateVolumePricingCommand(
            product_id=sample_product.id,
            min_quantity=Decimal("10.000"),
            price=Decimal("-90.00")
        )
        
        with pytest.raises(ValueError, match="Price must be non-negative"):
            handler.handle(command)
    
    def test_create_volume_pricing_tier_overlapping_ranges(self, db_session, sample_product, sample_volume_pricing):
        """Test creating a volume pricing tier with overlapping quantity ranges."""
        handler = CreateVolumePricingHandler()
        
        # Try to create a tier that overlaps with existing tier (10-50)
        command = CreateVolumePricingCommand(
            product_id=sample_product.id,
            min_quantity=Decimal("30.000"),  # Overlaps with 10-50
            max_quantity=Decimal("70.000"),
            price=Decimal("85.00")
        )
        
        with pytest.raises(ValueError, match="Quantity range overlaps"):
            handler.handle(command)
    
    def test_create_volume_pricing_tier_non_overlapping_ranges(self, db_session, sample_product, sample_volume_pricing):
        """Test creating a volume pricing tier with non-overlapping ranges."""
        handler = CreateVolumePricingHandler()
        
        # Create a tier that doesn't overlap (after 50)
        command = CreateVolumePricingCommand(
            product_id=sample_product.id,
            min_quantity=Decimal("51.000"),  # After existing tier
            max_quantity=Decimal("100.000"),
            price=Decimal("80.00")
        )
        
        result = handler.handle(command)
        assert result is not None
        assert result.min_quantity == Decimal("51.000")


class TestUpdateVolumePricingHandler:
    """Tests for UpdateVolumePricingHandler."""
    
    def test_update_volume_pricing_tier_success(self, db_session, sample_volume_pricing):
        """Test updating a volume pricing tier successfully."""
        handler = UpdateVolumePricingHandler()
        
        command = UpdateVolumePricingCommand(
            id=sample_volume_pricing.id,
            min_quantity=Decimal("15.000"),
            max_quantity=Decimal("60.000"),
            price=Decimal("85.00")
        )
        
        result = handler.handle(command)
        
        assert result is not None
        assert result.min_quantity == Decimal("15.000")
        assert result.max_quantity == Decimal("60.000")
        assert result.price == Decimal("85.00")
    
    def test_update_volume_pricing_tier_partial(self, db_session, sample_volume_pricing):
        """Test updating only price of a volume pricing tier."""
        handler = UpdateVolumePricingHandler()
        
        original_min = sample_volume_pricing.min_quantity
        original_max = sample_volume_pricing.max_quantity
        
        command = UpdateVolumePricingCommand(
            id=sample_volume_pricing.id,
            price=Decimal("88.00")
        )
        
        result = handler.handle(command)
        
        assert result.price == Decimal("88.00")
        assert result.min_quantity == original_min
        assert result.max_quantity == original_max
    
    def test_update_volume_pricing_tier_not_found(self, db_session):
        """Test updating a non-existent volume pricing tier."""
        handler = UpdateVolumePricingHandler()
        
        command = UpdateVolumePricingCommand(
            id=99999,
            price=Decimal("85.00")
        )
        
        with pytest.raises(ValueError, match="Volume pricing tier with ID 99999 not found"):
            handler.handle(command)
    
    def test_update_volume_pricing_tier_negative_min(self, db_session, sample_volume_pricing):
        """Test updating with negative min quantity."""
        handler = UpdateVolumePricingHandler()
        
        command = UpdateVolumePricingCommand(
            id=sample_volume_pricing.id,
            min_quantity=Decimal("-10.000")
        )
        
        with pytest.raises(ValueError, match="Minimum quantity must be non-negative"):
            handler.handle(command)
    
    def test_update_volume_pricing_tier_max_less_than_min(self, db_session, sample_volume_pricing):
        """Test updating with max < min."""
        handler = UpdateVolumePricingHandler()
        
        command = UpdateVolumePricingCommand(
            id=sample_volume_pricing.id,
            min_quantity=Decimal("50.000"),
            max_quantity=Decimal("10.000")  # Less than min
        )
        
        with pytest.raises(ValueError, match="Maximum quantity must be greater than or equal to minimum quantity"):
            handler.handle(command)


class TestDeleteVolumePricingHandler:
    """Tests for DeleteVolumePricingHandler."""
    
    def test_delete_volume_pricing_tier_success(self, db_session, sample_volume_pricing):
        """Test deleting a volume pricing tier successfully."""
        handler = DeleteVolumePricingHandler()
        tier_id = sample_volume_pricing.id
        
        command = DeleteVolumePricingCommand(id=tier_id)
        handler.handle(command)
        
        # Verify it's deleted
        db_session.expire_all()  # Refresh session to see changes
        tier = db_session.get(ProductVolumePricing, tier_id)
        assert tier is None
    
    def test_delete_volume_pricing_tier_not_found(self, db_session):
        """Test deleting a non-existent volume pricing tier."""
        handler = DeleteVolumePricingHandler()
        
        command = DeleteVolumePricingCommand(id=99999)
        
        with pytest.raises(ValueError, match="Volume pricing tier with ID 99999 not found"):
            handler.handle(command)


class TestGetVolumePricingHandler:
    """Tests for GetVolumePricingHandler."""
    
    def test_get_volume_pricing_tiers_success(self, db_session, sample_product):
        """Test getting volume pricing tiers for a product."""
        handler = GetVolumePricingHandler()
        
        # Create multiple tiers
        tier1 = ProductVolumePricing(
            product_id=sample_product.id,
            min_quantity=Decimal("10.000"),
            max_quantity=Decimal("50.000"),
            price=Decimal("90.00")
        )
        tier2 = ProductVolumePricing(
            product_id=sample_product.id,
            min_quantity=Decimal("51.000"),
            max_quantity=None,  # Unlimited
            price=Decimal("80.00")
        )
        db_session.add_all([tier1, tier2])
        db_session.commit()
        
        query = GetVolumePricingQuery(product_id=sample_product.id)
        result = handler.handle(query)
        
        assert len(result) == 2
        # Should be ordered by min_quantity ascending
        assert result[0].min_quantity == Decimal("10.000")
        assert result[1].min_quantity == Decimal("51.000")
        assert result[1].max_quantity is None
    
    def test_get_volume_pricing_tiers_empty(self, db_session, sample_product):
        """Test getting volume pricing tiers when none exist."""
        handler = GetVolumePricingHandler()
        
        query = GetVolumePricingQuery(product_id=sample_product.id)
        result = handler.handle(query)
        
        assert len(result) == 0
        assert result == []
    
    def test_get_volume_pricing_tiers_product_not_found(self, db_session):
        """Test getting volume pricing tiers for non-existent product."""
        handler = GetVolumePricingHandler()
        
        query = GetVolumePricingQuery(product_id=99999)
        
        with pytest.raises(ValueError, match="Product with ID 99999 not found"):
            handler.handle(query)

