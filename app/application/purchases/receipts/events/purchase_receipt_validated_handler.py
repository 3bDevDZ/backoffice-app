"""Domain event handler for purchase receipt validated events."""
from typing import Optional
from decimal import Decimal

from app.application.common.domain_event_handler import DomainEventHandler
from app.domain.models.purchase import PurchaseReceiptValidatedDomainEvent, PurchaseReceipt
from app.domain.models.stock import StockItem, StockMovement, Location
from app.domain.events.integration_event import IntegrationEvent, IIntegrationEvent
from app.infrastructure.db import get_session
from dataclasses import dataclass


@dataclass
class PurchaseReceiptValidatedIntegrationEvent(IntegrationEvent):
    """Integration event for purchase receipt validated (external communication)."""
    purchase_receipt_id: int = 0
    purchase_receipt_number: str = ""
    purchase_order_id: int = 0


class PurchaseReceiptValidatedDomainEventHandler(DomainEventHandler):
    """Handler for PurchaseReceiptValidatedDomainEvent - updates stock from receipt lines."""
    
    def map_to_integration_event(
        self,
        domain_event: PurchaseReceiptValidatedDomainEvent
    ) -> Optional[IIntegrationEvent]:
        """
        Map domain event to integration event for external systems.
        
        Args:
            domain_event: The domain event
            
        Returns:
            Integration event or None
        """
        # For MVP, we might want to notify external systems when stock is received
        # For now, return None (no external communication needed)
        return None
    
    def handle_internal(self, event: PurchaseReceiptValidatedDomainEvent) -> None:
        """
        Handle purchase receipt validated event by creating stock movements for each receipt line.
        
        This handler ONLY handles stock domain updates:
        1. Loads the receipt with its lines
        2. For each receipt line, creates/updates stock items
        3. Creates stock movements
        4. Updates stock quantities
        
        PurchaseOrder updates are handled separately in ValidatePurchaseReceiptHandler
        to respect DDD boundaries between domains.
        
        Args:
            event: The domain event containing receipt validation information
        """
        with get_session() as session:
            # Load receipt with lines
            receipt = session.get(PurchaseReceipt, event.purchase_receipt_id)
            if not receipt:
                # Receipt not found - this shouldn't happen, but handle gracefully
                return
            
            # Load lines (they should be loaded by relationship, but ensure they are)
            if not receipt.lines:
                # No lines to process
                return
            
            # Process each receipt line - ONLY stock domain updates
            for receipt_line in receipt.lines:
                # Get or create stock item
                location_id = receipt_line.location_id
                site_id = None
                location = None
                
                if not location_id:
                    # Use default location (first warehouse location)
                    location = session.query(Location).filter(
                        Location.type == 'warehouse',
                        Location.is_active == True
                    ).first()
                    
                    if not location:
                        # Log warning but continue with other lines
                        # In production, you'd want to log this properly
                        continue
                    
                    location_id = location.id
                else:
                    # Load location to determine site_id
                    location = session.get(Location, location_id)
                
                # Get site_id from location (access within session context)
                if location:
                    # Access site_id while location is still in session
                    site_id = location.site_id if location.site_id else None
                    
                    if not site_id:
                        # If location has no site, try to get default site
                        from app.domain.models.stock import Site
                        default_site = session.query(Site).filter(
                            Site.status == 'active'
                        ).first()
                        if default_site:
                            site_id = default_site.id
                
                # Get or create stock item
                stock_item = session.query(StockItem).filter(
                    StockItem.product_id == receipt_line.product_id,
                    StockItem.location_id == location_id,
                    StockItem.variant_id == None  # For now, no variants
                ).first()
                
                if not stock_item:
                    # Create stock item
                    stock_item = StockItem.create(
                        product_id=receipt_line.product_id,
                        location_id=location_id,
                        physical_quantity=Decimal(0),
                        variant_id=None,
                        site_id=site_id  # Set site_id if available
                    )
                    session.add(stock_item)
                    session.flush()  # Get stock_item.id
                elif site_id and not stock_item.site_id:
                    # Update existing stock item with site_id if not set
                    stock_item.site_id = site_id
                
                # Create stock movement
                # Use validated_by from receipt, or fallback to received_by if not set
                user_id = receipt.validated_by if receipt.validated_by else receipt.received_by
                movement = StockMovement.create(
                    stock_item_id=stock_item.id,
                    product_id=receipt_line.product_id,
                    quantity=receipt_line.quantity_received,  # Positive for entry
                    movement_type='entry',
                    user_id=user_id,
                    location_to_id=location_id,
                    variant_id=None,
                    reason=f"Purchase receipt {receipt.number}",
                    related_document_type='purchase_receipt',
                    related_document_id=receipt.id
                )
                session.add(movement)
                
                # Update stock item quantity using adjust method
                stock_item.adjust(
                    receipt_line.quantity_received,
                    reason=f"Purchase receipt {receipt.number} validation"
                )
            
            session.commit()

