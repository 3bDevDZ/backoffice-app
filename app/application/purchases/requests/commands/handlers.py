"""Command handlers for purchase request management."""
from decimal import Decimal
from datetime import date

from app.application.common.cqrs import CommandHandler
from app.domain.models.purchase import PurchaseRequest, PurchaseRequestLine
from app.infrastructure.db import get_session
from app.services.purchase_request_service import PurchaseRequestService
from .commands import (
    CreatePurchaseRequestCommand,
    SubmitPurchaseRequestCommand,
    ApprovePurchaseRequestCommand,
    RejectPurchaseRequestCommand,
    ConvertPurchaseRequestCommand
)


class CreatePurchaseRequestHandler(CommandHandler):
    """Handler for creating a new purchase request."""
    
    def handle(self, command: CreatePurchaseRequestCommand) -> int:
        """
        Create a new purchase request.
        
        Args:
            command: CreatePurchaseRequestCommand with request details
            
        Returns:
            Purchase request ID (int)
        """
        with get_session() as session:
            # Create purchase request
            request = PurchaseRequest.create(
                requested_by=command.requested_by,
                requested_date=command.requested_date,
                required_date=command.required_date,
                notes=command.notes,
                internal_notes=command.internal_notes
            )
            
            session.add(request)
            session.flush()  # Get request.id
            
            # Add lines if provided
            if command.lines:
                for line_input in command.lines:
                    request.add_line(
                        product_id=line_input.product_id,
                        quantity=line_input.quantity,
                        unit_price_estimate=line_input.unit_price_estimate,
                        notes=line_input.notes
                    )
            
            request_id = request.id
            session.commit()
            
            return request_id


class SubmitPurchaseRequestHandler(CommandHandler):
    """Handler for submitting a purchase request for approval."""
    
    def handle(self, command: SubmitPurchaseRequestCommand) -> None:
        """
        Submit a purchase request for approval.
        
        Args:
            command: SubmitPurchaseRequestCommand with request ID
        """
        with get_session() as session:
            request = session.get(PurchaseRequest, command.purchase_request_id)
            if not request:
                raise ValueError(f"Purchase request with ID {command.purchase_request_id} not found.")
            
            request.submit_for_approval()
            session.commit()


class ApprovePurchaseRequestHandler(CommandHandler):
    """Handler for approving a purchase request."""
    
    def handle(self, command: ApprovePurchaseRequestCommand) -> None:
        """
        Approve a purchase request.
        
        Args:
            command: ApprovePurchaseRequestCommand with request ID and approver
        """
        with get_session() as session:
            request = session.get(PurchaseRequest, command.purchase_request_id)
            if not request:
                raise ValueError(f"Purchase request with ID {command.purchase_request_id} not found.")
            
            request.approve(command.approved_by)
            session.commit()


class RejectPurchaseRequestHandler(CommandHandler):
    """Handler for rejecting a purchase request."""
    
    def handle(self, command: RejectPurchaseRequestCommand) -> None:
        """
        Reject a purchase request.
        
        Args:
            command: RejectPurchaseRequestCommand with request ID, rejector, and reason
        """
        with get_session() as session:
            request = session.get(PurchaseRequest, command.purchase_request_id)
            if not request:
                raise ValueError(f"Purchase request with ID {command.purchase_request_id} not found.")
            
            request.reject(command.rejected_by, command.reason)
            session.commit()


class ConvertPurchaseRequestHandler(CommandHandler):
    """Handler for converting a purchase request to a purchase order."""
    
    def handle(self, command: ConvertPurchaseRequestCommand) -> int:
        """
        Convert an approved purchase request to a purchase order.
        
        Args:
            command: ConvertPurchaseRequestCommand with request ID and PO details
            
        Returns:
            Purchase order ID (int)
        """
        with get_session() as session:
            service = PurchaseRequestService(session)
            po = service.convert_to_purchase_order(
                purchase_request_id=command.purchase_request_id,
                supplier_id=command.supplier_id,
                created_by=command.created_by,
                order_date=command.order_date,
                expected_delivery_date=command.expected_delivery_date
            )
            
            po_id = po.id
            session.commit()
            
            return po_id




