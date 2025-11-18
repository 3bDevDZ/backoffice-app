"""Command handlers for supplier invoice management."""
from decimal import Decimal

from app.application.common.cqrs import CommandHandler
from app.domain.models.purchase import SupplierInvoice
from app.infrastructure.db import get_session
from app.services.three_way_matching_service import ThreeWayMatchingService
from .commands import (
    CreateSupplierInvoiceCommand,
    MatchSupplierInvoiceCommand
)


class CreateSupplierInvoiceHandler(CommandHandler):
    """Handler for creating a new supplier invoice."""
    
    def handle(self, command: CreateSupplierInvoiceCommand) -> int:
        """
        Create a new supplier invoice.
        
        Args:
            command: CreateSupplierInvoiceCommand with invoice details
            
        Returns:
            Supplier invoice ID (int)
        """
        with get_session() as session:
            # Create supplier invoice
            invoice = SupplierInvoice.create(
                number=command.number,
                supplier_id=command.supplier_id,
                invoice_date=command.invoice_date,
                subtotal_ht=command.subtotal_ht,
                tax_amount=command.tax_amount,
                total_ttc=command.total_ttc,
                created_by=command.created_by,
                due_date=command.due_date,
                received_date=command.received_date,
                notes=command.notes,
                internal_notes=command.internal_notes
            )
            
            session.add(invoice)
            invoice_id = invoice.id
            session.commit()
            
            return invoice_id


class MatchSupplierInvoiceHandler(CommandHandler):
    """Handler for matching a supplier invoice with PO and receipt."""
    
    def handle(self, command: MatchSupplierInvoiceCommand) -> dict:
        """
        Match a supplier invoice with purchase order and receipt (3-way matching).
        
        Args:
            command: MatchSupplierInvoiceCommand with invoice ID and matching details
            
        Returns:
            Dictionary with matching results
        """
        with get_session() as session:
            service = ThreeWayMatchingService(session)
            result = service.match_invoice_with_po_and_receipt(
                supplier_invoice_id=command.supplier_invoice_id,
                purchase_order_id=command.purchase_order_id,
                purchase_receipt_id=command.purchase_receipt_id,
                matched_by=command.matched_by
            )
            
            session.commit()
            
            return result




