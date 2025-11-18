"""Command handlers for purchase receipt management."""
from decimal import Decimal
from datetime import date

from app.application.common.cqrs import CommandHandler
from app.domain.models.purchase import (
    PurchaseReceipt, PurchaseReceiptLine, PurchaseOrder, PurchaseOrderLine
)
from app.domain.models.stock import StockItem, StockMovement
from app.infrastructure.db import get_session
from .commands import (
    CreatePurchaseReceiptCommand,
    ValidatePurchaseReceiptCommand
)


class CreatePurchaseReceiptHandler(CommandHandler):
    """Handler for creating a new purchase receipt."""
    
    def handle(self, command: CreatePurchaseReceiptCommand) -> int:
        """
        Create a new purchase receipt.
        
        Args:
            command: CreatePurchaseReceiptCommand with receipt details
            
        Returns:
            Purchase receipt ID (int)
        """
        with get_session() as session:
            # Verify purchase order exists and is confirmed
            po = session.get(PurchaseOrder, command.purchase_order_id)
            if not po:
                raise ValueError(f"Purchase order with ID {command.purchase_order_id} not found.")
            
            # Allow receipt creation for confirmed, sent, or partially_received orders
            # This follows the workflow: draft -> sent -> confirmed -> partially_received -> received
            if po.status not in ['confirmed', 'sent', 'partially_received']:
                raise ValueError(
                    f"Cannot create receipt for purchase order in status '{po.status}'. "
                    "Order must be confirmed, sent, or partially received."
                )
            
            # Create purchase receipt
            receipt = PurchaseReceipt.create(
                purchase_order_id=command.purchase_order_id,
                received_by=command.received_by,
                receipt_date=command.receipt_date,
                notes=command.notes,
                internal_notes=command.internal_notes
            )
            
            session.add(receipt)
            session.flush()  # Get receipt.id
            
            # Add lines if provided
            if command.lines:
                for line_input in command.lines:
                    # Verify purchase order line exists
                    po_line = session.get(PurchaseOrderLine, line_input.purchase_order_line_id)
                    if not po_line:
                        raise ValueError(
                            f"Purchase order line with ID {line_input.purchase_order_line_id} not found."
                        )
                    
                    if po_line.purchase_order_id != command.purchase_order_id:
                        raise ValueError(
                            f"Purchase order line {line_input.purchase_order_line_id} "
                            f"does not belong to purchase order {command.purchase_order_id}."
                        )
                    
                    receipt_line = PurchaseReceiptLine.create(
                        purchase_receipt_id=receipt.id,
                        purchase_order_line_id=line_input.purchase_order_line_id,
                        product_id=line_input.product_id,
                        quantity_ordered=line_input.quantity_ordered,
                        quantity_received=line_input.quantity_received,
                        location_id=line_input.location_id,
                        discrepancy_reason=line_input.discrepancy_reason,
                        quality_notes=line_input.quality_notes,
                        sequence=len(receipt.lines) + 1
                    )
                    
                    receipt.lines.append(receipt_line)
            
            receipt_id = receipt.id
            session.commit()
            
            return receipt_id


class ValidatePurchaseReceiptHandler(CommandHandler):
    """Handler for validating a purchase receipt (coordinates receipt, stock, and purchase order updates)."""
    
    def handle(self, command: ValidatePurchaseReceiptCommand) -> None:
        """
        Validate a purchase receipt.
        
        This handler coordinates updates across multiple domains:
        1. Validates the receipt (raises PurchaseReceiptValidatedDomainEvent for stock updates)
        2. Updates PurchaseOrder lines with received quantities
        3. Updates PurchaseOrder status if needed
        
        The stock domain is updated via domain event handler (PurchaseReceiptValidatedDomainEventHandler)
        to respect DDD boundaries.
        
        Args:
            command: ValidatePurchaseReceiptCommand with receipt ID and validator
        """
        with get_session() as session:
            # Load receipt with lines
            receipt = session.get(PurchaseReceipt, command.purchase_receipt_id)
            if not receipt:
                raise ValueError(f"Purchase receipt with ID {command.purchase_receipt_id} not found.")
            
            # Validate receipt (this raises PurchaseReceiptValidatedDomainEvent)
            # The domain event handler will process stock movements
            receipt.validate(command.validated_by)
            
            # Ensure receipt is in session for event dispatch
            session.add(receipt)
            session.flush()  # Flush to ensure receipt is in identity_map
            
            # Update PurchaseOrder domain (separate from stock domain)
            # This is done here to coordinate between PurchaseReceipt and PurchaseOrder aggregates
            for receipt_line in receipt.lines:
                po_line = session.get(PurchaseOrderLine, receipt_line.purchase_order_line_id)
                if po_line:
                    # Add the received quantity (may be partial)
                    po_line.quantity_received += receipt_line.quantity_received
                    # Ensure we don't exceed ordered quantity
                    if po_line.quantity_received > po_line.quantity:
                        po_line.quantity_received = po_line.quantity
            
            # Update purchase order status (check if all lines are received)
            po = session.get(PurchaseOrder, receipt.purchase_order_id)
            if po:
                po.mark_received()
            
            # Commit to persist all changes and dispatch domain events
            # The after_commit listener will dispatch domain events
            session.commit()

