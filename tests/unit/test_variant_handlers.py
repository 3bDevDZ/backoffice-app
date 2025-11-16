"""Unit tests for product variant command and query handlers."""
import pytest
from decimal import Decimal
from app.application.products.variants.commands.commands import (
    CreateVariantCommand,
    UpdateVariantCommand,
    ArchiveVariantCommand,
    ActivateVariantCommand,
    DeleteVariantCommand
)
from app.application.products.variants.commands.handlers import (
    CreateVariantHandler,
    UpdateVariantHandler,
    ArchiveVariantHandler,
    ActivateVariantHandler,
    DeleteVariantHandler
)
from app.application.products.variants.queries.queries import (
    GetVariantByIdQuery,
    GetVariantsByProductQuery,
    ListVariantsQuery
)
from app.application.products.variants.queries.handlers import (
    GetVariantByIdHandler,
    GetVariantsByProductHandler,
    ListVariantsHandler
)
from app.domain.models.product import Product, ProductVariant
from app.domain.models.category import Category


class TestCreateVariantHandler:
    """Unit tests for CreateVariantHandler."""
    
    def test_create_variant_success(self, db_session, sample_product):
        """Test successful variant creation."""
        handler = CreateVariantHandler()
        command = CreateVariantCommand(
            product_id=sample_product.id,
            code="VAR-001",
            name="Red - Large",
            attributes='{"color": "red", "size": "L"}',
            price=Decimal("110.00"),
            cost=Decimal("55.00"),
            barcode="1234567890123"
        )
        
        variant = handler.handle(command)
        
        # Re-query variant from session
        variant_in_session = db_session.query(ProductVariant).filter(
            ProductVariant.code == "VAR-001"
        ).first()
        
        assert variant_in_session is not None
        assert variant_in_session.code == "VAR-001"
        assert variant_in_session.name == "Red - Large"
        assert variant_in_session.product_id == sample_product.id
        assert variant_in_session.attributes == '{"color": "red", "size": "L"}'
        assert variant_in_session.price == Decimal("110.00")
        assert variant_in_session.cost == Decimal("55.00")
        assert variant_in_session.barcode == "1234567890123"
        assert variant_in_session.status == "active"
    
    def test_create_variant_without_price_uses_product_price(self, db_session, sample_product):
        """Test that variant without price override uses product price."""
        handler = CreateVariantHandler()
        command = CreateVariantCommand(
            product_id=sample_product.id,
            code="VAR-002",
            name="Blue - Medium",
            price=None  # No price override
        )
        
        variant = handler.handle(command)
        
        variant_in_session = db_session.query(ProductVariant).filter(
            ProductVariant.code == "VAR-002"
        ).first()
        
        assert variant_in_session.price is None  # No override, uses product price
    
    def test_create_variant_duplicate_code_fails(self, db_session, sample_product):
        """Test that creating variant with duplicate code fails."""
        # Create first variant
        handler = CreateVariantHandler()
        command1 = CreateVariantCommand(
            product_id=sample_product.id,
            code="VAR-DUP",
            name="First Variant"
        )
        handler.handle(command1)
        
        # Try to create second variant with same code
        command2 = CreateVariantCommand(
            product_id=sample_product.id,
            code="VAR-DUP",
            name="Second Variant"
        )
        
        with pytest.raises(ValueError, match="already exists"):
            handler.handle(command2)
    
    def test_create_variant_duplicate_barcode_fails(self, db_session, sample_product):
        """Test that creating variant with duplicate barcode fails."""
        handler = CreateVariantHandler()
        command1 = CreateVariantCommand(
            product_id=sample_product.id,
            code="VAR-003",
            name="First Variant",
            barcode="1234567890"
        )
        handler.handle(command1)
        
        command2 = CreateVariantCommand(
            product_id=sample_product.id,
            code="VAR-004",
            name="Second Variant",
            barcode="1234567890"  # Same barcode
        )
        
        with pytest.raises(ValueError, match="barcode.*already exists"):
            handler.handle(command2)
    
    def test_create_variant_invalid_product_fails(self, db_session):
        """Test that creating variant for non-existent product fails."""
        handler = CreateVariantHandler()
        command = CreateVariantCommand(
            product_id=99999,  # Non-existent product
            code="VAR-005",
            name="Invalid Product Variant"
        )
        
        with pytest.raises(ValueError, match="Product with ID.*not found"):
            handler.handle(command)


class TestUpdateVariantHandler:
    """Unit tests for UpdateVariantHandler."""
    
    def test_update_variant_success(self, db_session, sample_product):
        """Test successful variant update."""
        # Create variant first
        create_handler = CreateVariantHandler()
        create_command = CreateVariantCommand(
            product_id=sample_product.id,
            code="VAR-UPDATE",
            name="Original Name",
            price=Decimal("100.00")
        )
        variant = create_handler.handle(create_command)
        
        # Update variant (extract ID before session closes)
        variant_id = variant.id
        
        # Update variant
        update_handler = UpdateVariantHandler()
        update_command = UpdateVariantCommand(
            id=variant_id,
            name="Updated Name",
            price=Decimal("120.00"),
            attributes='{"color": "blue"}'
        )
        
        updated_variant = update_handler.handle(update_command)
        
        variant_in_session = db_session.query(ProductVariant).filter(
            ProductVariant.id == variant_id
        ).first()
        
        assert variant_in_session.name == "Updated Name"
        assert variant_in_session.price == Decimal("120.00")
        assert variant_in_session.attributes == '{"color": "blue"}'
        assert variant_in_session.code == "VAR-UPDATE"  # Code unchanged
    
    def test_update_variant_duplicate_barcode_fails(self, db_session, sample_product):
        """Test that updating variant with duplicate barcode fails."""
        # Create two variants
        create_handler = CreateVariantHandler()
        variant1 = create_handler.handle(CreateVariantCommand(
            product_id=sample_product.id,
            code="VAR-006",
            name="Variant 1",
            barcode="BARCODE-001"
        ))
        variant2 = create_handler.handle(CreateVariantCommand(
            product_id=sample_product.id,
            code="VAR-007",
            name="Variant 2",
            barcode="BARCODE-002"
        ))
        
        # Extract IDs before session closes
        variant1_id = variant1.id
        variant2_id = variant2.id
        
        # Try to update variant2 with variant1's barcode
        update_handler = UpdateVariantHandler()
        update_command = UpdateVariantCommand(
            id=variant2_id,
            barcode="BARCODE-001"  # Duplicate
        )
        
        with pytest.raises(ValueError, match="barcode.*already exists"):
            update_handler.handle(update_command)
    
    def test_update_variant_not_found_fails(self, db_session):
        """Test that updating non-existent variant fails."""
        handler = UpdateVariantHandler()
        command = UpdateVariantCommand(
            id=99999,
            name="Non-existent Variant"
        )
        
        with pytest.raises(ValueError, match="Variant with ID.*not found"):
            handler.handle(command)


class TestArchiveVariantHandler:
    """Unit tests for ArchiveVariantHandler."""
    
    def test_archive_variant_success(self, db_session, sample_product):
        """Test successful variant archiving."""
        # Create variant
        create_handler = CreateVariantHandler()
        variant = create_handler.handle(CreateVariantCommand(
            product_id=sample_product.id,
            code="VAR-ARCHIVE",
            name="To Archive"
        ))
        
        # Extract ID before session closes
        variant_id = variant.id
        
        # Archive variant
        archive_handler = ArchiveVariantHandler()
        archived_variant = archive_handler.handle(ArchiveVariantCommand(id=variant_id))
        
        variant_in_session = db_session.query(ProductVariant).filter(
            ProductVariant.id == variant_id
        ).first()
        
        assert variant_in_session.status == "archived"
    
    def test_archive_variant_not_found_fails(self, db_session):
        """Test that archiving non-existent variant fails."""
        handler = ArchiveVariantHandler()
        command = ArchiveVariantCommand(id=99999)
        
        with pytest.raises(ValueError, match="Variant with ID.*not found"):
            handler.handle(command)


class TestActivateVariantHandler:
    """Unit tests for ActivateVariantHandler."""
    
    def test_activate_variant_success(self, db_session, sample_product):
        """Test successful variant activation."""
        # Create and archive variant
        create_handler = CreateVariantHandler()
        variant = create_handler.handle(CreateVariantCommand(
            product_id=sample_product.id,
            code="VAR-ACTIVATE",
            name="To Activate"
        ))
        
        # Extract ID before session closes
        variant_id = variant.id
        
        archive_handler = ArchiveVariantHandler()
        archive_handler.handle(ArchiveVariantCommand(id=variant_id))
        
        # Activate variant
        activate_handler = ActivateVariantHandler()
        activated_variant = activate_handler.handle(ActivateVariantCommand(id=variant_id))
        
        variant_in_session = db_session.query(ProductVariant).filter(
            ProductVariant.id == variant_id
        ).first()
        
        assert variant_in_session.status == "active"
    
    def test_activate_variant_not_found_fails(self, db_session):
        """Test that activating non-existent variant fails."""
        handler = ActivateVariantHandler()
        command = ActivateVariantCommand(id=99999)
        
        with pytest.raises(ValueError, match="Variant with ID.*not found"):
            handler.handle(command)


class TestDeleteVariantHandler:
    """Unit tests for DeleteVariantHandler."""
    
    def test_delete_variant_success(self, db_session, sample_product):
        """Test successful variant deletion."""
        # Create variant
        create_handler = CreateVariantHandler()
        variant = create_handler.handle(CreateVariantCommand(
            product_id=sample_product.id,
            code="VAR-DELETE",
            name="To Delete"
        ))
        variant_id = variant.id
        
        # Delete variant
        delete_handler = DeleteVariantHandler()
        delete_handler.handle(DeleteVariantCommand(id=variant_id))
        
        # Verify variant is deleted
        variant_in_session = db_session.query(ProductVariant).filter(
            ProductVariant.id == variant_id
        ).first()
        
        assert variant_in_session is None
    
    def test_delete_variant_not_found_fails(self, db_session):
        """Test that deleting non-existent variant fails."""
        handler = DeleteVariantHandler()
        command = DeleteVariantCommand(id=99999)
        
        with pytest.raises(ValueError, match="Variant with ID.*not found"):
            handler.handle(command)


class TestGetVariantByIdHandler:
    """Unit tests for GetVariantByIdHandler."""
    
    def test_get_variant_by_id_success(self, db_session, sample_product):
        """Test successful variant retrieval by ID."""
        # Create variant
        create_handler = CreateVariantHandler()
        variant = create_handler.handle(CreateVariantCommand(
            product_id=sample_product.id,
            code="VAR-GET",
            name="Test Variant",
            price=Decimal("105.00")
        ))
        
        # Extract ID before session closes
        variant_id = variant.id
        
        # Get variant
        query_handler = GetVariantByIdHandler()
        dto = query_handler.handle(GetVariantByIdQuery(id=variant_id))
        
        assert dto.id == variant_id
        assert dto.code == "VAR-GET"
        assert dto.name == "Test Variant"
        assert dto.product_id == sample_product.id
        assert dto.product_code == sample_product.code
        assert dto.product_name == sample_product.name
        assert dto.price == Decimal("105.00")
    
    def test_get_variant_by_id_not_found_fails(self, db_session):
        """Test that getting non-existent variant fails."""
        handler = GetVariantByIdHandler()
        
        with pytest.raises(ValueError, match="Variant with ID.*not found"):
            handler.handle(GetVariantByIdQuery(id=99999))


class TestGetVariantsByProductHandler:
    """Unit tests for GetVariantsByProductHandler."""
    
    def test_get_variants_by_product_success(self, db_session, sample_product):
        """Test successful retrieval of variants by product."""
        # Create multiple variants
        create_handler = CreateVariantHandler()
        variant1 = create_handler.handle(CreateVariantCommand(
            product_id=sample_product.id,
            code="VAR-001",
            name="Variant 1"
        ))
        variant2 = create_handler.handle(CreateVariantCommand(
            product_id=sample_product.id,
            code="VAR-002",
            name="Variant 2"
        ))
        
        # Get variants
        query_handler = GetVariantsByProductHandler()
        variants = query_handler.handle(GetVariantsByProductQuery(
            product_id=sample_product.id,
            include_archived=False
        ))
        
        assert len(variants) == 2
        assert variants[0].code in ["VAR-001", "VAR-002"]
        assert variants[1].code in ["VAR-001", "VAR-002"]
        assert variants[0].code != variants[1].code
    
    def test_get_variants_by_product_excludes_archived(self, db_session, sample_product):
        """Test that archived variants are excluded by default."""
        create_handler = CreateVariantHandler()
        variant1 = create_handler.handle(CreateVariantCommand(
            product_id=sample_product.id,
            code="VAR-ACTIVE",
            name="Active Variant"
        ))
        variant2 = create_handler.handle(CreateVariantCommand(
            product_id=sample_product.id,
            code="VAR-ARCHIVED",
            name="Archived Variant"
        ))
        
        # Extract IDs before session closes
        variant1_id = variant1.id
        variant2_id = variant2.id
        
        # Archive second variant
        archive_handler = ArchiveVariantHandler()
        archive_handler.handle(ArchiveVariantCommand(id=variant2_id))
        
        # Get variants (exclude archived)
        query_handler = GetVariantsByProductHandler()
        variants = query_handler.handle(GetVariantsByProductQuery(
            product_id=sample_product.id,
            include_archived=False
        ))
        
        assert len(variants) == 1
        assert variants[0].code == "VAR-ACTIVE"
    
    def test_get_variants_by_product_includes_archived(self, db_session, sample_product):
        """Test that archived variants are included when requested."""
        create_handler = CreateVariantHandler()
        variant1 = create_handler.handle(CreateVariantCommand(
            product_id=sample_product.id,
            code="VAR-ACTIVE",
            name="Active Variant"
        ))
        variant2 = create_handler.handle(CreateVariantCommand(
            product_id=sample_product.id,
            code="VAR-ARCHIVED",
            name="Archived Variant"
        ))
        
        # Extract IDs before session closes
        variant1_id = variant1.id
        variant2_id = variant2.id
        
        # Archive second variant
        archive_handler = ArchiveVariantHandler()
        archive_handler.handle(ArchiveVariantCommand(id=variant2_id))
        
        # Get variants (include archived)
        query_handler = GetVariantsByProductHandler()
        variants = query_handler.handle(GetVariantsByProductQuery(
            product_id=sample_product.id,
            include_archived=True
        ))
        
        assert len(variants) == 2


class TestListVariantsHandler:
    """Unit tests for ListVariantsHandler."""
    
    def test_list_variants_success(self, db_session, sample_product):
        """Test successful variant listing."""
        # Create variants
        create_handler = CreateVariantHandler()
        create_handler.handle(CreateVariantCommand(
            product_id=sample_product.id,
            code="VAR-LIST-1",
            name="Variant 1"
        ))
        create_handler.handle(CreateVariantCommand(
            product_id=sample_product.id,
            code="VAR-LIST-2",
            name="Variant 2"
        ))
        
        # List variants
        query_handler = ListVariantsHandler()
        result = query_handler.handle(ListVariantsQuery(
            page=1,
            per_page=20,
            product_id=sample_product.id
        ))
        
        assert result['total'] == 2
        assert len(result['items']) == 2
        assert result['page'] == 1
        assert result['per_page'] == 20
    
    def test_list_variants_with_pagination(self, db_session, sample_product):
        """Test variant listing with pagination."""
        # Create multiple variants
        create_handler = CreateVariantHandler()
        for i in range(5):
            create_handler.handle(CreateVariantCommand(
                product_id=sample_product.id,
                code=f"VAR-PAGE-{i}",
                name=f"Variant {i}"
            ))
        
        # List with pagination
        query_handler = ListVariantsHandler()
        result = query_handler.handle(ListVariantsQuery(
            page=1,
            per_page=2,
            product_id=sample_product.id
        ))
        
        assert result['total'] == 5
        assert len(result['items']) == 2
        assert result['page'] == 1
    
    def test_list_variants_with_search(self, db_session, sample_product):
        """Test variant listing with search filter."""
        create_handler = CreateVariantHandler()
        create_handler.handle(CreateVariantCommand(
            product_id=sample_product.id,
            code="VAR-RED",
            name="Red Variant"
        ))
        create_handler.handle(CreateVariantCommand(
            product_id=sample_product.id,
            code="VAR-BLUE",
            name="Blue Variant"
        ))
        
        query_handler = ListVariantsHandler()
        result = query_handler.handle(ListVariantsQuery(
            page=1,
            per_page=20,
            product_id=sample_product.id,
            search="Red"
        ))
        
        assert result['total'] == 1
        assert result['items'][0].code == "VAR-RED"
    
    def test_list_variants_with_status_filter(self, db_session, sample_product):
        """Test variant listing with status filter."""
        create_handler = CreateVariantHandler()
        variant1 = create_handler.handle(CreateVariantCommand(
            product_id=sample_product.id,
            code="VAR-ACTIVE",
            name="Active Variant"
        ))
        variant2 = create_handler.handle(CreateVariantCommand(
            product_id=sample_product.id,
            code="VAR-ARCHIVED",
            name="Archived Variant"
        ))
        
        # Extract IDs before session closes
        variant1_id = variant1.id
        variant2_id = variant2.id
        
        # Archive second variant
        archive_handler = ArchiveVariantHandler()
        archive_handler.handle(ArchiveVariantCommand(id=variant2_id))
        
        # List only active
        query_handler = ListVariantsHandler()
        result = query_handler.handle(ListVariantsQuery(
            page=1,
            per_page=20,
            product_id=sample_product.id,
            status="active"
        ))
        
        assert result['total'] == 1
        assert result['items'][0].code == "VAR-ACTIVE"

