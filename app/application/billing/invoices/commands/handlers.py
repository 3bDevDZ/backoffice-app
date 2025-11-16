"""Command handlers for invoice management."""
from decimal import Decimal
from datetime import date, timedelta
from app.application.common.cqrs import CommandHandler
from app.domain.models.invoice import Invoice, InvoiceLine, CreditNote
from app.domain.models.order import Order, OrderStatus
from app.infrastructure.db import get_session
from app.services.invoice_numbering_service import InvoiceNumberingService
from .commands import (
    CreateInvoiceCommand, ValidateInvoiceCommand, SendInvoiceCommand, CreateCreditNoteCommand
)


class CreateInvoiceHandler(CommandHandler):
    """Handler for creating a new invoice from an order."""
    
    def handle(self, command: CreateInvoiceCommand) -> int:
        """
        Create a new invoice from a delivered order.
        
        Args:
            command: CreateInvoiceCommand with invoice details
            
        Returns:
            Invoice ID (int) to avoid detached instance issues
        """
        with get_session() as session:
            # Get the order with lines eagerly loaded
            from sqlalchemy.orm import joinedload
            order = session.query(Order).options(
                joinedload(Order.lines)
            ).filter(Order.id == command.order_id).first()
            
            if not order:
                raise ValueError(f"Order with ID {command.order_id} not found.")
            
            # Validate order status - must be delivered
            if order.status != OrderStatus.DELIVERED.value:
                raise ValueError(
                    f"Cannot create invoice from order '{order.number}' in status '{order.status}'. "
                    f"Order must be in 'delivered' status."
                )
            
            # Check if invoice already exists for this order
            existing_invoice = session.query(Invoice).filter(
                Invoice.order_id == command.order_id,
                Invoice.status != "canceled"
            ).first()
            
            if existing_invoice:
                raise ValueError(
                    f"An invoice already exists for order '{order.number}': {existing_invoice.number}"
                )
            
            # Use InvoiceNumberingService to generate number
            numbering_service = InvoiceNumberingService(session)
            invoice_number = command.number or numbering_service.generate_invoice_number()
            
            # Calculate due date if not provided (default: 30 days from invoice date)
            due_date = command.due_date
            if not due_date:
                due_date = command.invoice_date + timedelta(days=30)
            
            # Create invoice
            invoice = Invoice.create(
                customer_id=command.customer_id,
                order_id=command.order_id,
                invoice_date=command.invoice_date,
                due_date=due_date,
                created_by=command.created_by,
                number=invoice_number,
                notes=command.notes,
                internal_notes=command.internal_notes,
                discount_percent=command.discount_percent
            )
            
            session.add(invoice)
            session.flush()  # Get invoice.id for domain event
            
            # Update domain event with invoice ID
            events = invoice.get_domain_events()
            for event in events:
                if hasattr(event, 'invoice_id'):
                    event.invoice_id = invoice.id
            
            # Add lines from order if not provided in command
            if not command.lines:
                # Copy lines from order
                for order_line in order.lines:
                    # Calculate invoicable quantity (not yet invoiced)
                    # If quantity_delivered is 0 but order is delivered, use quantity as fallback
                    # (for orders marked as delivered before the fix)
                    delivered_qty = order_line.quantity_delivered
                    if delivered_qty == 0 and order.status == OrderStatus.DELIVERED.value:
                        delivered_qty = order_line.quantity
                        # Update quantity_delivered for consistency
                        order_line.quantity_delivered = delivered_qty
                    
                    invoicable_quantity = delivered_qty - order_line.quantity_invoiced
                    
                    if invoicable_quantity > 0:
                        invoice.add_line(
                            product_id=order_line.product_id,
                            quantity=invoicable_quantity,
                            unit_price=order_line.unit_price,
                            order_line_id=order_line.id,
                            variant_id=order_line.variant_id,
                            discount_percent=order_line.discount_percent,
                            tax_rate=order_line.tax_rate
                        )
                        
                        # Update order line invoiced quantity
                        order_line.quantity_invoiced += invoicable_quantity
            else:
                # Use provided lines
                for line_input in command.lines:
                    invoice.add_line(
                        product_id=line_input.product_id,
                        quantity=line_input.quantity,
                        unit_price=line_input.unit_price,
                        order_line_id=line_input.order_line_id,
                        variant_id=line_input.variant_id,
                        description=line_input.description,
                        discount_percent=line_input.discount_percent,
                        tax_rate=line_input.tax_rate
                    )
            
            # Calculate totals
            invoice.calculate_totals()
            
            # Copy customer legal information if available
            if order.customer:
                if hasattr(order.customer, 'vat_number') and order.customer.vat_number:
                    invoice.vat_number = order.customer.vat_number
                if hasattr(order.customer, 'siret') and order.customer.siret:
                    invoice.siret = order.customer.siret
            
            invoice_id = invoice.id
            session.commit()
            
            return invoice_id


class ValidateInvoiceHandler(CommandHandler):
    """Handler for validating an invoice."""
    
    def handle(self, command: ValidateInvoiceCommand) -> int:
        """
        Validate an invoice (make it official).
        
        Args:
            command: ValidateInvoiceCommand with invoice ID and user ID
            
        Returns:
            Invoice ID (int)
        """
        with get_session() as session:
            invoice = session.get(Invoice, command.id)
            if not invoice:
                raise ValueError(f"Invoice with ID {command.id} not found.")
            
            invoice.validate(command.validated_by)
            
            invoice_id = invoice.id
            session.commit()
            
            return invoice_id


class SendInvoiceHandler(CommandHandler):
    """Handler for sending an invoice to customer."""
    
    def handle(self, command: SendInvoiceCommand) -> int:
        """
        Send an invoice to customer (via email).
        
        Args:
            command: SendInvoiceCommand with invoice ID and user ID
            
        Returns:
            Invoice ID (int)
        """
        with get_session() as session:
            invoice = session.get(Invoice, command.id)
            if not invoice:
                raise ValueError(f"Invoice with ID {command.id} not found.")
            
            invoice.send(command.sent_by)
            
            invoice_id = invoice.id
            session.commit()
            
            return invoice_id


class CreateCreditNoteHandler(CommandHandler):
    """Handler for creating a credit note."""
    
    def handle(self, command: CreateCreditNoteCommand) -> int:
        """
        Create a credit note for an invoice.
        
        Args:
            command: CreateCreditNoteCommand with credit note details
            
        Returns:
            Credit note ID (int)
        """
        with get_session() as session:
            # Get the invoice
            invoice = session.get(Invoice, command.invoice_id)
            if not invoice:
                raise ValueError(f"Invoice with ID {command.invoice_id} not found.")
            
            # Validate invoice status
            if invoice.status == "canceled":
                raise ValueError(f"Cannot create credit note for canceled invoice '{invoice.number}'.")
            
            # Use InvoiceNumberingService to generate credit note number
            numbering_service = InvoiceNumberingService(session)
            credit_note_number = command.number or numbering_service.generate_credit_note_number()
            
            # Create credit note
            credit_note = CreditNote.create(
                invoice_id=command.invoice_id,
                customer_id=command.customer_id,
                reason=command.reason,
                total_amount=command.total_amount,
                tax_amount=command.tax_amount,
                created_by=command.created_by,
                number=credit_note_number
            )
            
            session.add(credit_note)
            session.flush()  # Get credit_note.id for domain event
            
            # Update domain event with credit note ID and invoice number
            events = credit_note.get_domain_events()
            for event in events:
                if hasattr(event, 'credit_note_id'):
                    event.credit_note_id = credit_note.id
                if hasattr(event, 'invoice_number'):
                    event.invoice_number = invoice.number
            
            credit_note_id = credit_note.id
            session.commit()
            
            return credit_note_id

