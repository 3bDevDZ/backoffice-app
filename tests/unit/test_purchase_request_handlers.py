"""Unit tests for purchase request command handlers."""
import pytest
from decimal import Decimal
from datetime import date
from app.application.purchases.requests.commands.commands import (
    CreatePurchaseRequestCommand,
    SubmitPurchaseRequestCommand,
    ApprovePurchaseRequestCommand,
    RejectPurchaseRequestCommand,
    ConvertPurchaseRequestCommand,
    PurchaseRequestLineInput
)
from app.application.purchases.requests.commands.handlers import (
    CreatePurchaseRequestHandler,
    SubmitPurchaseRequestHandler,
    ApprovePurchaseRequestHandler,
    RejectPurchaseRequestHandler,
    ConvertPurchaseRequestHandler
)
from app.application.purchases.requests.commands.commands import (
    SubmitPurchaseRequestCommand
)
from app.domain.models.purchase import PurchaseRequest, PurchaseRequestLine, PurchaseOrder
from app.domain.models.product import Product
from app.domain.models.supplier import Supplier, SupplierConditions


class TestCreatePurchaseRequestHandler:
    """Unit tests for CreatePurchaseRequestHandler."""
    
    def test_create_purchase_request_success(self, db_session, sample_user, sample_product):
        """Test successful purchase request creation."""
        handler = CreatePurchaseRequestHandler()
        command = CreatePurchaseRequestCommand(
            requested_by=sample_user.id,
            requested_date=date.today(),
            required_date=date(2025, 12, 31),
            notes="Test request",
            internal_notes="Internal notes",
            lines=[
                PurchaseRequestLineInput(
                    product_id=sample_product.id,
                    quantity=Decimal("10"),
                    unit_price_estimate=Decimal("50.00"),
                    notes="Line notes"
                )
            ]
        )
        
        request_id = handler.handle(command)
        
        # Re-query request from session
        request_in_session = db_session.query(PurchaseRequest).filter(PurchaseRequest.id == request_id).first()
        
        assert request_in_session is not None
        assert request_in_session.requested_by == sample_user.id
        assert request_in_session.status == "draft"
        assert request_in_session.number.startswith("PR-")
        assert request_in_session.notes == "Test request"
        assert request_in_session.internal_notes == "Internal notes"
        assert len(request_in_session.lines) == 1
        assert request_in_session.lines[0].product_id == sample_product.id
        assert request_in_session.lines[0].quantity == Decimal("10")
        assert request_in_session.lines[0].unit_price_estimate == Decimal("50.00")
    
    def test_create_purchase_request_without_lines(self, db_session, sample_user):
        """Test creating purchase request without lines."""
        handler = CreatePurchaseRequestHandler()
        command = CreatePurchaseRequestCommand(
            requested_by=sample_user.id,
            requested_date=date.today(),
            lines=[]
        )
        
        request_id = handler.handle(command)
        
        request_in_session = db_session.query(PurchaseRequest).filter(PurchaseRequest.id == request_id).first()
        assert request_in_session is not None
        assert len(request_in_session.lines) == 0


class TestSubmitPurchaseRequestHandler:
    """Unit tests for SubmitPurchaseRequestHandler."""
    
    def test_submit_purchase_request_success(self, db_session, sample_user, sample_product):
        """Test successful purchase request submission."""
        # Create a draft request
        request = PurchaseRequest.create(
            requested_by=sample_user.id,
            requested_date=date.today()
        )
        request.add_line(
            product_id=sample_product.id,
            quantity=Decimal("10"),
            unit_price_estimate=Decimal("50.00")
        )
        db_session.add(request)
        db_session.commit()
        db_session.refresh(request)
        
        handler = SubmitPurchaseRequestHandler()
        command = SubmitPurchaseRequestCommand(purchase_request_id=request.id)
        
        handler.handle(command)
        
        # Expire and refresh to see changes
        db_session.expire_all()
        request_in_session = db_session.query(PurchaseRequest).filter(PurchaseRequest.id == request.id).first()
        
        assert request_in_session.status == "pending_approval"
    
    def test_submit_purchase_request_not_draft_fails(self, db_session, sample_user, sample_product):
        """Test that submitting non-draft request fails."""
        # Create and submit a request
        request = PurchaseRequest.create(
            requested_by=sample_user.id,
            requested_date=date.today()
        )
        request.add_line(
            product_id=sample_product.id,
            quantity=Decimal("10")
        )
        db_session.add(request)
        db_session.commit()
        db_session.refresh(request)
        
        # Submit first time
        handler = SubmitPurchaseRequestHandler()
        command = SubmitPurchaseRequestCommand(purchase_request_id=request.id)
        handler.handle(command)
        db_session.commit()
        
        # Try to submit again (should fail)
        with pytest.raises(ValueError, match="status"):
            handler.handle(command)


class TestApprovePurchaseRequestHandler:
    """Unit tests for ApprovePurchaseRequestHandler."""
    
    def test_approve_purchase_request_success(self, db_session, sample_user, sample_product):
        """Test successful purchase request approval."""
        # Create and submit a request
        request = PurchaseRequest.create(
            requested_by=sample_user.id,
            requested_date=date.today()
        )
        request.add_line(
            product_id=sample_product.id,
            quantity=Decimal("10")
        )
        db_session.add(request)
        db_session.commit()
        db_session.refresh(request)
        
        # Submit using handler
        submit_handler = SubmitPurchaseRequestHandler()
        submit_command = SubmitPurchaseRequestCommand(purchase_request_id=request.id)
        submit_handler.handle(submit_command)
        db_session.commit()
        db_session.refresh(request)
        
        handler = ApprovePurchaseRequestHandler()
        command = ApprovePurchaseRequestCommand(
            purchase_request_id=request.id,
            approved_by=sample_user.id
        )
        
        handler.handle(command)
        
        # Expire and refresh to see changes
        db_session.expire_all()
        request_in_session = db_session.query(PurchaseRequest).filter(PurchaseRequest.id == request.id).first()
        
        assert request_in_session.status == "approved"
        assert request_in_session.approved_by == sample_user.id
        assert request_in_session.approved_at is not None
    
    def test_approve_purchase_request_not_pending_fails(self, db_session, sample_user, sample_product):
        """Test that approving non-pending request fails."""
        # Create a draft request
        request = PurchaseRequest.create(
            requested_by=sample_user.id,
            requested_date=date.today()
        )
        request.add_line(
            product_id=sample_product.id,
            quantity=Decimal("10")
        )
        db_session.add(request)
        db_session.commit()
        db_session.refresh(request)
        
        # Try to approve draft (should fail)
        handler = ApprovePurchaseRequestHandler()
        command = ApprovePurchaseRequestCommand(
            purchase_request_id=request.id,
            approved_by=sample_user.id
        )
        
        with pytest.raises(ValueError, match="status"):
            handler.handle(command)


class TestRejectPurchaseRequestHandler:
    """Unit tests for RejectPurchaseRequestHandler."""
    
    def test_reject_purchase_request_success(self, db_session, sample_user, sample_product):
        """Test successful purchase request rejection."""
        # Create and submit a request
        request = PurchaseRequest.create(
            requested_by=sample_user.id,
            requested_date=date.today()
        )
        request.add_line(
            product_id=sample_product.id,
            quantity=Decimal("10")
        )
        db_session.add(request)
        db_session.commit()
        db_session.refresh(request)
        
        # Submit using handler
        submit_handler = SubmitPurchaseRequestHandler()
        submit_command = SubmitPurchaseRequestCommand(purchase_request_id=request.id)
        submit_handler.handle(submit_command)
        db_session.commit()
        db_session.refresh(request)
        
        handler = RejectPurchaseRequestHandler()
        command = RejectPurchaseRequestCommand(
            purchase_request_id=request.id,
            rejected_by=sample_user.id,
            reason="Not needed"
        )
        
        handler.handle(command)
        
        # Expire and refresh to see changes
        db_session.expire_all()
        request_in_session = db_session.query(PurchaseRequest).filter(PurchaseRequest.id == request.id).first()
        
        assert request_in_session.status == "rejected"
        assert request_in_session.rejection_reason == "Not needed"


class TestConvertPurchaseRequestHandler:
    """Unit tests for ConvertPurchaseRequestHandler."""
    
    def test_convert_purchase_request_success(self, db_session, sample_user, sample_product, sample_supplier):
        """Test successful conversion of purchase request to purchase order."""
        # Create and approve a request
        request = PurchaseRequest.create(
            requested_by=sample_user.id,
            requested_date=date.today()
        )
        request.add_line(
            product_id=sample_product.id,
            quantity=Decimal("10"),
            unit_price_estimate=Decimal("50.00")
        )
        db_session.add(request)
        db_session.commit()
        db_session.refresh(request)
        
        # Submit using handler
        submit_handler = SubmitPurchaseRequestHandler()
        submit_command = SubmitPurchaseRequestCommand(purchase_request_id=request.id)
        submit_handler.handle(submit_command)
        db_session.commit()
        db_session.refresh(request)
        
        # Approve using handler
        approve_handler = ApprovePurchaseRequestHandler()
        approve_command = ApprovePurchaseRequestCommand(
            purchase_request_id=request.id,
            approved_by=sample_user.id
        )
        approve_handler.handle(approve_command)
        db_session.commit()
        db_session.refresh(request)
        
        handler = ConvertPurchaseRequestHandler()
        command = ConvertPurchaseRequestCommand(
            purchase_request_id=request.id,
            supplier_id=sample_supplier.id,
            created_by=sample_user.id,
            order_date=date.today(),
            expected_delivery_date=date(2025, 12, 31)
        )
        
        po_id = handler.handle(command)
        
        # Verify purchase order was created
        po = db_session.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
        assert po is not None
        assert po.supplier_id == sample_supplier.id
        assert po.status == "draft"
        assert po.number.startswith("PO-")
        assert len(po.lines) == 1
        assert po.lines[0].product_id == sample_product.id
        assert po.lines[0].quantity == Decimal("10")
        
        # Verify request was marked as converted
        db_session.expire_all()
        request_in_session = db_session.query(PurchaseRequest).filter(PurchaseRequest.id == request.id).first()
        assert request_in_session.status == "converted"
        assert request_in_session.converted_to_po_id == po_id
        assert request_in_session.converted_at is not None
    
    def test_convert_purchase_request_not_approved_fails(self, db_session, sample_user, sample_product, sample_supplier):
        """Test that converting non-approved request fails."""
        # Create a draft request
        request = PurchaseRequest.create(
            requested_by=sample_user.id,
            requested_date=date.today()
        )
        request.add_line(
            product_id=sample_product.id,
            quantity=Decimal("10")
        )
        db_session.add(request)
        db_session.commit()
        db_session.refresh(request)
        
        handler = ConvertPurchaseRequestHandler()
        command = ConvertPurchaseRequestCommand(
            purchase_request_id=request.id,
            supplier_id=sample_supplier.id,
            created_by=sample_user.id
        )
        
        with pytest.raises(ValueError, match="approved"):
            handler.handle(command)

