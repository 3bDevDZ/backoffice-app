"""Unit tests for variant integration in quotes, orders, and stock."""
import pytest
from decimal import Decimal
from app.application.sales.quotes.commands.commands import AddQuoteLineCommand
from app.application.sales.quotes.commands.handlers import AddQuoteLineHandler
from app.application.sales.orders.commands.commands import AddOrderLineCommand
from app.application.sales.orders.commands.handlers import AddOrderLineHandler
from app.application.stock.queries.queries import GetStockLevelsQuery, GetStockMovementsQuery
from app.application.stock.queries.handlers import GetStockLevelsHandler, GetStockMovementsHandler
from app.domain.models.product import Product, ProductVariant
from app.domain.models.quote import Quote
from app.domain.models.order import Order
from app.domain.models.stock import StockItem, StockMovement, Location
from app.domain.models.customer import Customer, CommercialConditions
from app.domain.models.user import User


@pytest.fixture
def sample_variant_with_price(db_session, sample_product):
    """Create a sample product variant with price override."""
    variant = ProductVariant.create(
        product_id=sample_product.id,
        code="VAR-001",
        name="Variant 1",
        attributes='{"color": "red", "size": "large"}',
        price=Decimal("120.00"),  # Override price
        cost=Decimal("60.00")
    )
    db_session.add(variant)
    db_session.commit()
    db_session.refresh(variant)
    return variant


@pytest.fixture
def sample_variant_no_price(db_session, sample_product):
    """Create a sample product variant without price override."""
    variant = ProductVariant.create(
        product_id=sample_product.id,
        code="VAR-002",
        name="Variant 2",
        attributes='{"color": "blue", "size": "medium"}',
        price=None,  # No price override
        cost=None
    )
    db_session.add(variant)
    db_session.commit()
    db_session.refresh(variant)
    return variant


@pytest.fixture
def sample_quote_with_customer(db_session, sample_b2b_customer, sample_user):
    """Create a sample quote with customer."""
    quote = Quote.create(
        customer_id=sample_b2b_customer.id,
        created_by=sample_user.id
    )
    db_session.add(quote)
    db_session.commit()
    db_session.refresh(quote)
    return quote


@pytest.fixture
def sample_order_with_customer(db_session, sample_b2b_customer, sample_user):
    """Create a sample order with customer."""
    order = Order.create(
        customer_id=sample_b2b_customer.id,
        created_by=sample_user.id
    )
    db_session.add(order)
    db_session.commit()
    db_session.refresh(order)
    return order


class TestVariantValidationInQuotes:
    """Test variant validation in AddQuoteLineHandler."""
    
    def test_add_quote_line_with_valid_variant(self, db_session, sample_quote_with_customer, 
                                               sample_product, sample_variant_with_price):
        """Test adding a quote line with a valid variant."""
        handler = AddQuoteLineHandler()
        
        command = AddQuoteLineCommand(
            quote_id=sample_quote_with_customer.id,
            product_id=sample_product.id,
            variant_id=sample_variant_with_price.id,
            quantity=Decimal("2.00"),
            unit_price=Decimal("0"),  # Will be calculated
            discount_percent=Decimal("0")
        )
        
        # Handler returns QuoteLine, but it's detached from session
        # Query the line from test session instead
        handler.handle(command)
        
        # Retrieve line from test session (handler uses its own session)
        from app.domain.models.quote import QuoteLine
        line = db_session.query(QuoteLine).filter(
            QuoteLine.quote_id == sample_quote_with_customer.id,
            QuoteLine.product_id == sample_product.id,
            QuoteLine.variant_id == sample_variant_with_price.id
        ).first()
        
        assert line is not None
        assert line.product_id == sample_product.id
        assert line.variant_id == sample_variant_with_price.id
        assert line.quantity == Decimal("2.00")
        # Should use variant price (120.00) as base price
        assert line.unit_price == Decimal("120.00")
    
    def test_add_quote_line_with_invalid_variant_not_found(self, db_session, 
                                                           sample_quote_with_customer, 
                                                           sample_product):
        """Test adding a quote line with a non-existent variant."""
        handler = AddQuoteLineHandler()
        
        command = AddQuoteLineCommand(
            quote_id=sample_quote_with_customer.id,
            product_id=sample_product.id,
            variant_id=99999,  # Non-existent variant
            quantity=Decimal("1.00"),
            unit_price=Decimal("100.00"),
            discount_percent=Decimal("0")
        )
        
        with pytest.raises(ValueError, match="Variant with ID 99999 not found"):
            handler.handle(command)
    
    def test_add_quote_line_with_variant_wrong_product(self, db_session, 
                                                       sample_quote_with_customer, 
                                                       sample_product, sample_category):
        """Test adding a quote line with a variant that belongs to a different product."""
        # Create another product
        other_product = Product.create(
            code="PROD-OTHER",
            name="Other Product",
            price=Decimal("200.00"),
            cost=Decimal("100.00"),
            category_ids=[sample_category.id]
        )
        db_session.add(other_product)
        db_session.commit()
        db_session.refresh(other_product)
        
        # Create variant for the first product
        variant = ProductVariant.create(
            product_id=sample_product.id,
            code="VAR-WRONG",
            name="Wrong Variant",
            price=Decimal("150.00")
        )
        db_session.add(variant)
        db_session.commit()
        db_session.refresh(variant)
        
        handler = AddQuoteLineHandler()
        
        command = AddQuoteLineCommand(
            quote_id=sample_quote_with_customer.id,
            product_id=other_product.id,  # Different product
            variant_id=variant.id,  # Variant belongs to sample_product
            quantity=Decimal("1.00"),
            unit_price=Decimal("200.00"),
            discount_percent=Decimal("0")
        )
        
        with pytest.raises(ValueError, match="does not belong to product"):
            handler.handle(command)
    
    def test_add_quote_line_with_variant_price_override(self, db_session, 
                                                       sample_quote_with_customer, 
                                                       sample_product, sample_variant_with_price):
        """Test that variant price override is used when variant has price."""
        handler = AddQuoteLineHandler()
        
        command = AddQuoteLineCommand(
            quote_id=sample_quote_with_customer.id,
            product_id=sample_product.id,
            variant_id=sample_variant_with_price.id,
            quantity=Decimal("1.00"),
            unit_price=Decimal("0"),  # Will be calculated
            discount_percent=Decimal("0")
        )
        
        # Handler returns QuoteLine, but it's detached from session
        # Query the line from test session instead
        handler.handle(command)
        
        # Retrieve line from test session (handler uses its own session)
        from app.domain.models.quote import QuoteLine
        line = db_session.query(QuoteLine).filter(
            QuoteLine.quote_id == sample_quote_with_customer.id,
            QuoteLine.product_id == sample_product.id,
            QuoteLine.variant_id == sample_variant_with_price.id
        ).first()
        
        assert line is not None
        # Variant has price override of 120.00, should use that
        assert line.unit_price == Decimal("120.00")
        assert line.variant_id == sample_variant_with_price.id
    
    def test_add_quote_line_with_variant_no_price_override(self, db_session, 
                                                          sample_quote_with_customer, 
                                                          sample_product, sample_variant_no_price):
        """Test that product price is used when variant has no price override."""
        handler = AddQuoteLineHandler()
        
        # Set product price
        sample_product.price = Decimal("100.00")
        db_session.commit()
        
        command = AddQuoteLineCommand(
            quote_id=sample_quote_with_customer.id,
            product_id=sample_product.id,
            variant_id=sample_variant_no_price.id,
            quantity=Decimal("1.00"),
            unit_price=Decimal("0"),  # Will be calculated
            discount_percent=Decimal("0")
        )
        
        # Handler returns QuoteLine, but it's detached from session
        # Query the line from test session instead
        handler.handle(command)
        
        # Retrieve line from test session (handler uses its own session)
        from app.domain.models.quote import QuoteLine
        line = db_session.query(QuoteLine).filter(
            QuoteLine.quote_id == sample_quote_with_customer.id,
            QuoteLine.product_id == sample_product.id,
            QuoteLine.variant_id == sample_variant_no_price.id
        ).first()
        
        assert line is not None
        # Variant has no price override, should use product price (100.00)
        # or pricing service result
        assert line.variant_id == sample_variant_no_price.id
        # Price should come from pricing service (product price or customer pricing)
        assert line.unit_price > Decimal("0")


class TestVariantValidationInOrders:
    """Test variant validation in AddOrderLineHandler."""
    
    def test_add_order_line_with_valid_variant(self, db_session, sample_order_with_customer, 
                                              sample_product, sample_variant_with_price):
        """Test adding an order line with a valid variant."""
        handler = AddOrderLineHandler()
        
        command = AddOrderLineCommand(
            order_id=sample_order_with_customer.id,
            product_id=sample_product.id,
            variant_id=sample_variant_with_price.id,
            quantity=Decimal("3.00"),
            unit_price=Decimal("0"),  # Will be calculated
            discount_percent=Decimal("0")
        )
        
        order_id = handler.handle(command)
        
        assert order_id == sample_order_with_customer.id
        
        # Verify line was added
        db_session.refresh(sample_order_with_customer)
        assert len(sample_order_with_customer.lines) == 1
        line = sample_order_with_customer.lines[0]
        assert line.product_id == sample_product.id
        assert line.variant_id == sample_variant_with_price.id
        assert line.quantity == Decimal("3.00")
        # Should use variant price (120.00) as base price
        assert line.unit_price == Decimal("120.00")
    
    def test_add_order_line_with_invalid_variant_not_found(self, db_session, 
                                                          sample_order_with_customer, 
                                                          sample_product):
        """Test adding an order line with a non-existent variant."""
        handler = AddOrderLineHandler()
        
        command = AddOrderLineCommand(
            order_id=sample_order_with_customer.id,
            product_id=sample_product.id,
            variant_id=99999,  # Non-existent variant
            quantity=Decimal("1.00"),
            unit_price=Decimal("100.00"),
            discount_percent=Decimal("0")
        )
        
        with pytest.raises(ValueError, match="Variant with ID 99999 not found"):
            handler.handle(command)
    
    def test_add_order_line_with_variant_wrong_product(self, db_session, 
                                                       sample_order_with_customer, 
                                                       sample_product, sample_category):
        """Test adding an order line with a variant that belongs to a different product."""
        # Create another product
        other_product = Product.create(
            code="PROD-OTHER2",
            name="Other Product 2",
            price=Decimal("200.00"),
            cost=Decimal("100.00"),
            category_ids=[sample_category.id]
        )
        db_session.add(other_product)
        db_session.commit()
        db_session.refresh(other_product)
        
        # Create variant for the first product
        variant = ProductVariant.create(
            product_id=sample_product.id,
            code="VAR-WRONG2",
            name="Wrong Variant 2",
            price=Decimal("150.00")
        )
        db_session.add(variant)
        db_session.commit()
        db_session.refresh(variant)
        
        handler = AddOrderLineHandler()
        
        command = AddOrderLineCommand(
            order_id=sample_order_with_customer.id,
            product_id=other_product.id,  # Different product
            variant_id=variant.id,  # Variant belongs to sample_product
            quantity=Decimal("1.00"),
            unit_price=Decimal("200.00"),
            discount_percent=Decimal("0")
        )
        
        with pytest.raises(ValueError, match="does not belong to product"):
            handler.handle(command)
    
    def test_add_order_line_with_variant_price_override(self, db_session, 
                                                       sample_order_with_customer, 
                                                       sample_product, sample_variant_with_price):
        """Test that variant price override is used when variant has price."""
        handler = AddOrderLineHandler()
        
        command = AddOrderLineCommand(
            order_id=sample_order_with_customer.id,
            product_id=sample_product.id,
            variant_id=sample_variant_with_price.id,
            quantity=Decimal("1.00"),
            unit_price=Decimal("0"),  # Will be calculated
            discount_percent=Decimal("0")
        )
        
        handler.handle(command)
        
        # Verify line was added with variant price
        db_session.refresh(sample_order_with_customer)
        line = sample_order_with_customer.lines[0]
        # Variant has price override of 120.00, should use that
        assert line.unit_price == Decimal("120.00")
        assert line.variant_id == sample_variant_with_price.id


class TestVariantInStockQueries:
    """Test variant filtering and display in stock queries."""
    
    def test_get_stock_levels_with_variant_filter(self, db_session, sample_product, 
                                                  sample_variant_with_price):
        """Test filtering stock levels by variant_id."""
        # Create location
        location = Location.create(
            code="WH-001",
            name="Warehouse 1",
            type="warehouse"
        )
        db_session.add(location)
        db_session.commit()
        db_session.refresh(location)
        
        # Create stock items: one without variant, one with variant
        stock_item_no_variant = StockItem.create(
            product_id=sample_product.id,
            location_id=location.id,
            physical_quantity=Decimal("100.00"),
            variant_id=None
        )
        stock_item_with_variant = StockItem.create(
            product_id=sample_product.id,
            location_id=location.id,
            physical_quantity=Decimal("50.00"),
            variant_id=sample_variant_with_price.id
        )
        db_session.add_all([stock_item_no_variant, stock_item_with_variant])
        db_session.commit()
        
        handler = GetStockLevelsHandler()
        
        # Query without variant filter (should return both)
        query_all = GetStockLevelsQuery(
            product_id=sample_product.id,
            page=1,
            per_page=50
        )
        results_all = handler.handle(query_all)
        assert len(results_all) == 2
        
        # Query with variant filter
        query_variant = GetStockLevelsQuery(
            product_id=sample_product.id,
            variant_id=sample_variant_with_price.id,
            page=1,
            per_page=50
        )
        results_variant = handler.handle(query_variant)
        assert len(results_variant) == 1
        assert results_variant[0].variant_id == sample_variant_with_price.id
        assert results_variant[0].variant_code == "VAR-001"
        assert results_variant[0].variant_name == "Variant 1"
        assert results_variant[0].physical_quantity == Decimal("50.00")
        
        # Query for items without variant
        # Note: When variant_id=None is passed, the handler doesn't filter (includes both)
        # This is the current behavior - variant_id=None means "no filter"
        # To filter for NULL only, we'd need to use a different approach
        query_no_variant = GetStockLevelsQuery(
            product_id=sample_product.id,
            variant_id=None,  # Handler includes both by default (no filter)
            page=1,
            per_page=50
        )
        results_no_variant = handler.handle(query_no_variant)
        # Handler includes both when variant_id is None (no filter)
        assert len(results_no_variant) == 2
        # Find the item without variant
        no_variant_items = [r for r in results_no_variant if r.variant_id is None]
        assert len(no_variant_items) == 1
        assert no_variant_items[0].physical_quantity == Decimal("100.00")
    
    def test_get_stock_levels_variant_info_in_dto(self, db_session, sample_product, 
                                                  sample_variant_with_price):
        """Test that variant information is included in StockItemDTO."""
        # Create location
        location = Location.create(
            code="WH-002",
            name="Warehouse 2",
            type="warehouse"
        )
        db_session.add(location)
        db_session.commit()
        db_session.refresh(location)
        
        stock_item = StockItem.create(
            product_id=sample_product.id,
            location_id=location.id,
            physical_quantity=Decimal("75.00"),
            variant_id=sample_variant_with_price.id
        )
        db_session.add(stock_item)
        db_session.commit()
        
        handler = GetStockLevelsHandler()
        query = GetStockLevelsQuery(
            product_id=sample_product.id,
            variant_id=sample_variant_with_price.id,
            page=1,
            per_page=50
        )
        results = handler.handle(query)
        
        assert len(results) == 1
        dto = results[0]
        assert dto.variant_id == sample_variant_with_price.id
        assert dto.variant_code == "VAR-001"
        assert dto.variant_name == "Variant 1"
        assert dto.product_id == sample_product.id
        assert dto.physical_quantity == Decimal("75.00")
    
    def test_get_stock_movements_with_variant_filter(self, db_session, sample_product, 
                                                     sample_variant_with_price, sample_user):
        """Test filtering stock movements by variant_id."""
        # Create location
        location = Location.create(
            code="WH-003",
            name="Warehouse 3",
            type="warehouse"
        )
        db_session.add(location)
        db_session.commit()
        db_session.refresh(location)
        
        # Create stock item
        stock_item = StockItem.create(
            product_id=sample_product.id,
            location_id=location.id,
            physical_quantity=Decimal("100.00"),
            variant_id=sample_variant_with_price.id
        )
        db_session.add(stock_item)
        db_session.commit()
        db_session.refresh(stock_item)
        
        # Create movements: one with variant, one without
        movement_with_variant = StockMovement.create(
            stock_item_id=stock_item.id,
            product_id=sample_product.id,
            variant_id=sample_variant_with_price.id,
            quantity=Decimal("-10.00"),
            movement_type="exit",
            user_id=sample_user.id,
            location_from_id=location.id,
            reason="Sale"
        )
        movement_no_variant = StockMovement.create(
            stock_item_id=stock_item.id,
            product_id=sample_product.id,
            variant_id=None,
            quantity=Decimal("-5.00"),
            movement_type="exit",
            user_id=sample_user.id,
            location_from_id=location.id,
            reason="Sale"
        )
        db_session.add_all([movement_with_variant, movement_no_variant])
        db_session.commit()
        
        handler = GetStockMovementsHandler()
        
        # Query without variant filter (should return both)
        query_all = GetStockMovementsQuery(
            product_id=sample_product.id,
            page=1,
            per_page=50
        )
        results_all = handler.handle(query_all)
        # Should find both movements
        variant_movements = [m for m in results_all if m.variant_id == sample_variant_with_price.id]
        no_variant_movements = [m for m in results_all if m.variant_id is None]
        assert len(variant_movements) >= 1
        assert len(no_variant_movements) >= 1
        
        # Query with variant filter
        query_variant = GetStockMovementsQuery(
            product_id=sample_product.id,
            variant_id=sample_variant_with_price.id,
            page=1,
            per_page=50
        )
        results_variant = handler.handle(query_variant)
        assert len(results_variant) >= 1
        # All results should have the variant
        for result in results_variant:
            if result.product_id == sample_product.id:
                assert result.variant_id == sample_variant_with_price.id
                assert result.variant_code == "VAR-001"
                assert result.variant_name == "Variant 1"
    
    def test_get_stock_movements_variant_info_in_dto(self, db_session, sample_product, 
                                                     sample_variant_with_price, sample_user):
        """Test that variant information is included in StockMovementDTO."""
        # Create location
        location = Location.create(
            code="WH-004",
            name="Warehouse 4",
            type="warehouse"
        )
        db_session.add(location)
        db_session.commit()
        db_session.refresh(location)
        
        stock_item = StockItem.create(
            product_id=sample_product.id,
            location_id=location.id,
            physical_quantity=Decimal("100.00"),
            variant_id=sample_variant_with_price.id
        )
        db_session.add(stock_item)
        db_session.commit()
        db_session.refresh(stock_item)
        
        movement = StockMovement.create(
            stock_item_id=stock_item.id,
            product_id=sample_product.id,
            variant_id=sample_variant_with_price.id,
            quantity=Decimal("-15.00"),
            movement_type="exit",
            user_id=sample_user.id,
            location_from_id=location.id,
            reason="Sale with variant"
        )
        db_session.add(movement)
        db_session.commit()
        
        handler = GetStockMovementsHandler()
        query = GetStockMovementsQuery(
            product_id=sample_product.id,
            variant_id=sample_variant_with_price.id,
            page=1,
            per_page=50
        )
        results = handler.handle(query)
        
        # Find our movement
        our_movement = next((m for m in results if m.id == movement.id), None)
        assert our_movement is not None
        assert our_movement.variant_id == sample_variant_with_price.id
        assert our_movement.variant_code == "VAR-001"
        assert our_movement.variant_name == "Variant 1"
        assert our_movement.quantity == Decimal("-15.00")
        assert our_movement.type == "exit"

