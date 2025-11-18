"""Integration tests for purchase receipt handlers using in-memory database."""
import pytest
from decimal import Decimal
from datetime import date

from app.application.purchases.receipts.commands.commands import (
    CreatePurchaseReceiptCommand,
    ValidatePurchaseReceiptCommand,
    PurchaseReceiptLineInput
)
from app.application.purchases.receipts.commands.handlers import (
    CreatePurchaseReceiptHandler,
    ValidatePurchaseReceiptHandler
)
from app.application.purchases.receipts.events.purchase_receipt_validated_handler import (
    PurchaseReceiptValidatedDomainEventHandler
)
from app.domain.models.purchase import (
    PurchaseReceipt,
    PurchaseReceiptLine,
    PurchaseOrder,
    PurchaseOrderLine,
    PurchaseReceiptValidatedDomainEvent
)
from app.domain.models.stock import StockItem, StockMovement, Location
from app.application.common.domain_event_dispatcher import domain_event_dispatcher


@pytest.fixture(autouse=True)
def setup_event_handlers():
    """Ensure domain event handlers are registered for tests."""
    # Register the purchase receipt validated event handler
    domain_event_dispatcher.register_handler(
        PurchaseReceiptValidatedDomainEvent,
        PurchaseReceiptValidatedDomainEventHandler().handle
    )
    yield
    # Cleanup is handled by the dispatcher itself


@pytest.fixture
def sample_location(db_session):
    """Create a sample warehouse location for testing."""
    location = Location.create(
        name="Main Warehouse",
        code="WH-001",
        type="warehouse",
        is_active=True
    )
    db_session.add(location)
    db_session.commit()
    db_session.refresh(location)
    return location


@pytest.fixture
def sample_confirmed_purchase_order(db_session, sample_supplier, sample_user, sample_product):
    """Create a confirmed purchase order with lines for testing."""
    from app.domain.models.purchase import PurchaseOrderLine
    
    # Create purchase order
    order = PurchaseOrder.create(
        supplier_id=sample_supplier.id,
        created_by=sample_user.id,
        order_date=date.today(),
        expected_delivery_date=date(2025, 12, 31)
    )
    db_session.add(order)
    db_session.flush()
    
    # Add lines
    line1 = PurchaseOrderLine.create(
        purchase_order_id=order.id,
        product_id=sample_product.id,
        quantity=Decimal("100"),
        unit_price=Decimal("10.00"),
        sequence=1
    )
    db_session.add(line1)
    order.lines.append(line1)
    order.calculate_totals()
    
    # Confirm the order
    order.confirm(sample_user.id)
    
    db_session.commit()
    db_session.refresh(order)
    db_session.refresh(line1)
    return order


class TestCreatePurchaseReceiptHandler:
    """Integration tests for CreatePurchaseReceiptHandler."""
    
    def test_create_purchase_receipt_success(
        self,
        db_session,
        sample_confirmed_purchase_order,
        sample_user,
        sample_location
    ):
        """Test successful purchase receipt creation."""
        handler = CreatePurchaseReceiptHandler()
        
        po_line = sample_confirmed_purchase_order.lines[0]
        
        command = CreatePurchaseReceiptCommand(
            purchase_order_id=sample_confirmed_purchase_order.id,
            received_by=sample_user.id,
            receipt_date=date.today(),
            lines=[
                PurchaseReceiptLineInput(
                    purchase_order_line_id=po_line.id,
                    product_id=po_line.product_id,
                    quantity_ordered=po_line.quantity,
                    quantity_received=Decimal("50"),  # Partial receipt
                    location_id=sample_location.id
                )
            ]
        )
        
        receipt_id = handler.handle(command)
        
        # Verify receipt was created
        receipt = db_session.get(PurchaseReceipt, receipt_id)
        assert receipt is not None
        assert receipt.purchase_order_id == sample_confirmed_purchase_order.id
        assert receipt.status == "draft"
        assert receipt.received_by == sample_user.id
        assert len(receipt.lines) == 1
        
        # Verify receipt line
        receipt_line = receipt.lines[0]
        assert receipt_line.quantity_ordered == Decimal("100")
        assert receipt_line.quantity_received == Decimal("50")
        assert receipt_line.quantity_discrepancy == Decimal("-50")  # Received less than ordered
        assert receipt_line.location_id == sample_location.id
    
    def test_create_purchase_receipt_with_full_quantity(
        self,
        db_session,
        sample_confirmed_purchase_order,
        sample_user,
        sample_location
    ):
        """Test creating receipt with full ordered quantity."""
        handler = CreatePurchaseReceiptHandler()
        
        po_line = sample_confirmed_purchase_order.lines[0]
        
        command = CreatePurchaseReceiptCommand(
            purchase_order_id=sample_confirmed_purchase_order.id,
            received_by=sample_user.id,
            receipt_date=date.today(),
            lines=[
                PurchaseReceiptLineInput(
                    purchase_order_line_id=po_line.id,
                    product_id=po_line.product_id,
                    quantity_ordered=po_line.quantity,
                    quantity_received=po_line.quantity,  # Full receipt
                    location_id=sample_location.id
                )
            ]
        )
        
        receipt_id = handler.handle(command)
        
        receipt = db_session.get(PurchaseReceipt, receipt_id)
        receipt_line = receipt.lines[0]
        
        assert receipt_line.quantity_received == Decimal("100")
        assert receipt_line.quantity_discrepancy == Decimal("0")
    
    def test_create_purchase_receipt_fails_for_draft_order(
        self,
        db_session,
        sample_purchase_order,
        sample_user,
        sample_location,
        sample_product
    ):
        """Test that receipt creation fails for draft purchase order."""
        handler = CreatePurchaseReceiptHandler()
        
        # Add a line to the draft order
        from app.domain.models.purchase import PurchaseOrderLine
        po_line = PurchaseOrderLine.create(
            purchase_order_id=sample_purchase_order.id,
            product_id=sample_product.id,
            quantity=Decimal("50"),
            unit_price=Decimal("10.00"),
            sequence=1
        )
        db_session.add(po_line)
        sample_purchase_order.lines.append(po_line)
        db_session.commit()
        db_session.refresh(po_line)
        
        command = CreatePurchaseReceiptCommand(
            purchase_order_id=sample_purchase_order.id,
            received_by=sample_user.id,
            lines=[
                PurchaseReceiptLineInput(
                    purchase_order_line_id=po_line.id,
                    product_id=po_line.product_id,
                    quantity_ordered=po_line.quantity,
                    quantity_received=Decimal("50"),
                    location_id=sample_location.id
                )
            ]
        )
        
        with pytest.raises(ValueError, match="status"):
            handler.handle(command)


class TestValidatePurchaseReceiptHandler:
    """Integration tests for ValidatePurchaseReceiptHandler."""
    
    def test_validate_purchase_receipt_updates_stock_and_order(
        self,
        db_session,
        sample_confirmed_purchase_order,
        sample_user,
        sample_location,
        sample_product
    ):
        """Test that validating receipt updates stock and purchase order."""
        # Create receipt first
        create_handler = CreatePurchaseReceiptHandler()
        po_line = sample_confirmed_purchase_order.lines[0]
        
        create_command = CreatePurchaseReceiptCommand(
            purchase_order_id=sample_confirmed_purchase_order.id,
            received_by=sample_user.id,
            receipt_date=date.today(),
            lines=[
                PurchaseReceiptLineInput(
                    purchase_order_line_id=po_line.id,
                    product_id=po_line.product_id,
                    quantity_ordered=po_line.quantity,
                    quantity_received=Decimal("50"),
                    location_id=sample_location.id
                )
            ]
        )
        
        receipt_id = create_handler.handle(create_command)
        
        # Verify initial state
        po_line_before = db_session.get(PurchaseOrderLine, po_line.id)
        assert po_line_before.quantity_received == Decimal("0")
        
        # Check no stock item exists yet
        stock_item = db_session.query(StockItem).filter(
            StockItem.product_id == sample_product.id,
            StockItem.location_id == sample_location.id
        ).first()
        assert stock_item is None
        
        # Validate receipt
        validate_handler = ValidatePurchaseReceiptHandler()
        validate_command = ValidatePurchaseReceiptCommand(
            purchase_receipt_id=receipt_id,
            validated_by=sample_user.id
        )
        
        validate_handler.handle(validate_command)
        
        # Refresh to see changes
        db_session.expire_all()
        
        # Verify receipt is validated
        receipt = db_session.get(PurchaseReceipt, receipt_id)
        assert receipt.status == "validated"
        assert receipt.validated_by == sample_user.id
        assert receipt.validated_at is not None
        
        # Verify purchase order line was updated
        po_line_after = db_session.get(PurchaseOrderLine, po_line.id)
        assert po_line_after.quantity_received == Decimal("50")
        
        # Verify purchase order status
        po_after = db_session.get(PurchaseOrder, sample_confirmed_purchase_order.id)
        assert po_after.status == "partially_received"  # Not fully received yet
        
        # Verify stock item was created
        stock_item = db_session.query(StockItem).filter(
            StockItem.product_id == sample_product.id,
            StockItem.location_id == sample_location.id
        ).first()
        assert stock_item is not None
        assert stock_item.physical_quantity == Decimal("50")
        
        # Verify stock movement was created
        movements = db_session.query(StockMovement).filter(
            StockMovement.stock_item_id == stock_item.id
        ).all()
        assert len(movements) == 1
        assert movements[0].quantity == Decimal("50")
        assert movements[0].type == "entry"
        assert movements[0].related_document_type == "purchase_receipt"
        assert movements[0].related_document_id == receipt_id
    
    def test_validate_purchase_receipt_full_quantity_updates_order_status(
        self,
        db_session,
        sample_confirmed_purchase_order,
        sample_user,
        sample_location
    ):
        """Test that validating full receipt marks order as received."""
        # Create receipt with full quantity
        create_handler = CreatePurchaseReceiptHandler()
        po_line = sample_confirmed_purchase_order.lines[0]
        
        create_command = CreatePurchaseReceiptCommand(
            purchase_order_id=sample_confirmed_purchase_order.id,
            received_by=sample_user.id,
            receipt_date=date.today(),
            lines=[
                PurchaseReceiptLineInput(
                    purchase_order_line_id=po_line.id,
                    product_id=po_line.product_id,
                    quantity_ordered=po_line.quantity,
                    quantity_received=po_line.quantity,  # Full quantity
                    location_id=sample_location.id
                )
            ]
        )
        
        receipt_id = create_handler.handle(create_command)
        
        # Validate receipt
        validate_handler = ValidatePurchaseReceiptHandler()
        validate_command = ValidatePurchaseReceiptCommand(
            purchase_receipt_id=receipt_id,
            validated_by=sample_user.id
        )
        
        validate_handler.handle(validate_command)
        
        # Refresh to see changes
        db_session.expire_all()
        
        # Verify purchase order is fully received
        po_after = db_session.get(PurchaseOrder, sample_confirmed_purchase_order.id)
        assert po_after.status == "received"
        
        # Verify line is fully received
        po_line_after = db_session.get(PurchaseOrderLine, po_line.id)
        assert po_line_after.quantity_received == po_line_after.quantity
    
    def test_validate_purchase_receipt_fails_for_validated_receipt(
        self,
        db_session,
        sample_confirmed_purchase_order,
        sample_user,
        sample_location
    ):
        """Test that validating an already validated receipt fails."""
        # Create and validate receipt
        create_handler = CreatePurchaseReceiptHandler()
        po_line = sample_confirmed_purchase_order.lines[0]
        
        create_command = CreatePurchaseReceiptCommand(
            purchase_order_id=sample_confirmed_purchase_order.id,
            received_by=sample_user.id,
            receipt_date=date.today(),
            lines=[
                PurchaseReceiptLineInput(
                    purchase_order_line_id=po_line.id,
                    product_id=po_line.product_id,
                    quantity_ordered=po_line.quantity,
                    quantity_received=Decimal("50"),
                    location_id=sample_location.id
                )
            ]
        )
        
        receipt_id = create_handler.handle(create_command)
        
        validate_handler = ValidatePurchaseReceiptHandler()
        validate_command = ValidatePurchaseReceiptCommand(
            purchase_receipt_id=receipt_id,
            validated_by=sample_user.id
        )
        
        # First validation should succeed
        validate_handler.handle(validate_command)
        
        # Second validation should fail
        with pytest.raises(ValueError, match="status"):
            validate_handler.handle(validate_command)
    
    def test_validate_purchase_receipt_fails_without_lines(
        self,
        db_session,
        sample_confirmed_purchase_order,
        sample_user
    ):
        """Test that validating receipt without lines fails."""
        # Create receipt without lines
        receipt = PurchaseReceipt.create(
            purchase_order_id=sample_confirmed_purchase_order.id,
            received_by=sample_user.id
        )
        db_session.add(receipt)
        db_session.commit()
        db_session.refresh(receipt)
        
        validate_handler = ValidatePurchaseReceiptHandler()
        validate_command = ValidatePurchaseReceiptCommand(
            purchase_receipt_id=receipt.id,
            validated_by=sample_user.id
        )
        
        with pytest.raises(ValueError, match="without lines"):
            validate_handler.handle(validate_command)


class TestPurchaseReceiptValidatedDomainEventHandler:
    """Integration tests for PurchaseReceiptValidatedDomainEventHandler."""
    
    def test_event_handler_updates_stock_only(
        self,
        db_session,
        sample_confirmed_purchase_order,
        sample_user,
        sample_location,
        sample_product
    ):
        """Test that event handler only updates stock domain, not purchase order."""
        # Create receipt
        create_handler = CreatePurchaseReceiptHandler()
        po_line = sample_confirmed_purchase_order.lines[0]
        
        create_command = CreatePurchaseReceiptCommand(
            purchase_order_id=sample_confirmed_purchase_order.id,
            received_by=sample_user.id,
            receipt_date=date.today(),
            lines=[
                PurchaseReceiptLineInput(
                    purchase_order_line_id=po_line.id,
                    product_id=po_line.product_id,
                    quantity_ordered=po_line.quantity,
                    quantity_received=Decimal("50"),
                    location_id=sample_location.id
                )
            ]
        )
        
        receipt_id = create_handler.handle(create_command)
        
        # Get initial PO line state
        po_line_before = db_session.get(PurchaseOrderLine, po_line.id)
        initial_quantity_received = po_line_before.quantity_received
        
        # Manually validate receipt to raise event (but don't commit yet)
        receipt = db_session.get(PurchaseReceipt, receipt_id)
        receipt.validate(sample_user.id)
        
        # Dispatch domain events manually (simulating what happens after commit)
        events = receipt.get_domain_events()
        for event in events:
            if isinstance(event, PurchaseReceiptValidatedDomainEvent):
                # Manually call the event handler
                handler = PurchaseReceiptValidatedDomainEventHandler()
                handler.handle(event)
        
        # Clear events to prevent double dispatch
        receipt.clear_domain_events()
        
        db_session.commit()
        db_session.expire_all()
        
        # Verify stock was updated by event handler
        stock_item = db_session.query(StockItem).filter(
            StockItem.product_id == sample_product.id,
            StockItem.location_id == sample_location.id
        ).first()
        assert stock_item is not None
        assert stock_item.physical_quantity == Decimal("50")
        
        # Verify stock movement was created
        movements = db_session.query(StockMovement).filter(
            StockMovement.stock_item_id == stock_item.id
        ).all()
        assert len(movements) == 1
        
        # Verify purchase order line was NOT updated by event handler
        # (it should be updated by ValidatePurchaseReceiptHandler, not event handler)
        po_line_after = db_session.get(PurchaseOrderLine, po_line.id)
        # The event handler should not update this - it should remain unchanged
        assert po_line_after.quantity_received == initial_quantity_received
    
    def test_event_handler_creates_stock_item_if_not_exists(
        self,
        db_session,
        sample_confirmed_purchase_order,
        sample_user,
        sample_location,
        sample_product
    ):
        """Test that event handler creates stock item if it doesn't exist."""
        # Create receipt
        create_handler = CreatePurchaseReceiptHandler()
        po_line = sample_confirmed_purchase_order.lines[0]
        
        create_command = CreatePurchaseReceiptCommand(
            purchase_order_id=sample_confirmed_purchase_order.id,
            received_by=sample_user.id,
            receipt_date=date.today(),
            lines=[
                PurchaseReceiptLineInput(
                    purchase_order_line_id=po_line.id,
                    product_id=po_line.product_id,
                    quantity_ordered=po_line.quantity,
                    quantity_received=Decimal("30"),
                    location_id=sample_location.id
                )
            ]
        )
        
        receipt_id = create_handler.handle(create_command)
        
        # Verify no stock item exists
        stock_item_before = db_session.query(StockItem).filter(
            StockItem.product_id == sample_product.id,
            StockItem.location_id == sample_location.id
        ).first()
        assert stock_item_before is None
        
        # Validate receipt (triggers event)
        validate_handler = ValidatePurchaseReceiptHandler()
        validate_command = ValidatePurchaseReceiptCommand(
            purchase_receipt_id=receipt_id,
            validated_by=sample_user.id
        )
        
        validate_handler.handle(validate_command)
        
        db_session.expire_all()
        
        # Verify stock item was created
        stock_item_after = db_session.query(StockItem).filter(
            StockItem.product_id == sample_product.id,
            StockItem.location_id == sample_location.id
        ).first()
        assert stock_item_after is not None
        assert stock_item_after.physical_quantity == Decimal("30")
    
    def test_event_handler_uses_default_location_if_not_specified(
        self,
        db_session,
        sample_confirmed_purchase_order,
        sample_user,
        sample_location,
        sample_product
    ):
        """Test that event handler uses default location if not specified in receipt line."""
        # Create receipt without location
        create_handler = CreatePurchaseReceiptHandler()
        po_line = sample_confirmed_purchase_order.lines[0]
        
        create_command = CreatePurchaseReceiptCommand(
            purchase_order_id=sample_confirmed_purchase_order.id,
            received_by=sample_user.id,
            receipt_date=date.today(),
            lines=[
                PurchaseReceiptLineInput(
                    purchase_order_line_id=po_line.id,
                    product_id=po_line.product_id,
                    quantity_ordered=po_line.quantity,
                    quantity_received=Decimal("25"),
                    location_id=None  # No location specified
                )
            ]
        )
        
        receipt_id = create_handler.handle(create_command)
        
        # Validate receipt
        validate_handler = ValidatePurchaseReceiptHandler()
        validate_command = ValidatePurchaseReceiptCommand(
            purchase_receipt_id=receipt_id,
            validated_by=sample_user.id
        )
        
        validate_handler.handle(validate_command)
        
        db_session.expire_all()
        
        # Verify stock item was created at default location
        stock_item = db_session.query(StockItem).filter(
            StockItem.product_id == sample_product.id,
            StockItem.location_id == sample_location.id
        ).first()
        assert stock_item is not None
        assert stock_item.physical_quantity == Decimal("25")

