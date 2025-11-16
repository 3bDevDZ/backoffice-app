"""Domain event handler for purchase order received events."""
from typing import Optional
from app.application.common.domain_event_handler import DomainEventHandler
from app.domain.models.purchase import PurchaseOrderReceivedDomainEvent
from app.domain.models.stock import StockItem, StockMovement
from app.domain.events.integration_event import IntegrationEvent, IIntegrationEvent
from app.infrastructure.db import get_session
from decimal import Decimal
from dataclasses import dataclass


@dataclass
class PurchaseOrderReceivedIntegrationEvent(IntegrationEvent):
    """Integration event for purchase order received (external communication)."""
    purchase_order_id: int = 0
    purchase_order_number: str = ""


class PurchaseOrderReceivedDomainEventHandler(DomainEventHandler):
    """Handler for PurchaseOrderReceivedDomainEvent - creates stock entries automatically."""
    
    def map_to_integration_event(
        self,
        domain_event: PurchaseOrderReceivedDomainEvent
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
    
    def handle_internal(self, event: PurchaseOrderReceivedDomainEvent) -> None:
        """
        Handle purchase order received event by creating stock entry movements.
        
        When a purchase order is marked as received, this handler:
        1. Retrieves all lines with quantity_received > 0
        2. Creates StockItem if it doesn't exist for the default location
        3. Creates StockMovement entries for each line
        4. Updates stock quantities automatically
        """
        with get_session() as session:
            from app.domain.models.purchase import PurchaseOrder, PurchaseOrderLine
            
            # Get the purchase order
            order = session.get(PurchaseOrder, event.purchase_order_id)
            if not order:
                return  # Order not found, skip
            
            # Get default location (for now, use first active warehouse location)
            # TODO: In future, use supplier's default delivery location or order's delivery location
            from app.domain.models.stock import Location
            default_location = session.query(Location).filter(
                Location.type == 'warehouse',
                Location.is_active == True
            ).first()
            
            if not default_location:
                # If no warehouse exists, skip stock update (log warning in production)
                # For now, we'll create stock items without location validation
                # In production, you'd want to log this and handle it appropriately
                pass
            
            # Process each line that has been received
            # Note: Since we now handle partial receipts via PurchaseOrderLineReceivedDomainEvent,
            # this handler mainly serves as a backup. It checks for any remaining quantities
            # that might not have been processed yet.
            for line in order.lines:
                if line.quantity_received <= 0:
                    continue  # Skip lines with no received quantity
                
                # Check if stock movements already exist for this purchase order line
                # Since partial receipts are handled individually, we need to check the total
                # quantity already processed vs. quantity_received
                existing_movements = session.query(StockMovement).filter(
                    StockMovement.related_document_type == 'purchase_order',
                    StockMovement.related_document_id == order.id,
                    StockMovement.product_id == line.product_id
                ).all()
                
                # Calculate total quantity already processed
                total_processed = sum(m.quantity for m in existing_movements)
                
                # If all quantity has been processed, skip this line
                if total_processed >= line.quantity_received:
                    continue  # Skip this line, already fully processed
                
                # Calculate remaining quantity to process
                remaining_quantity = line.quantity_received - total_processed
                
                # Get or create stock item for this product at default location
                stock_item = session.query(StockItem).filter(
                    StockItem.product_id == line.product_id,
                    StockItem.location_id == default_location.id if default_location else None,
                    StockItem.variant_id == None  # For now, no variants
                ).first()
                
                if not stock_item:
                    # Create stock item if it doesn't exist
                    if not default_location:
                        # Cannot create stock item without location
                        continue
                    
                    stock_item = StockItem.create(
                        product_id=line.product_id,
                        location_id=default_location.id,
                        physical_quantity=Decimal('0'),
                        variant_id=None
                    )
                    session.add(stock_item)
                    session.flush()  # Get stock_item.id
                
                # Create stock movement entry for remaining quantity
                movement = StockMovement.create(
                    stock_item_id=stock_item.id,
                    product_id=line.product_id,
                    quantity=remaining_quantity,  # Only the remaining quantity
                    movement_type='entry',
                    user_id=order.created_by,  # Use order creator as user
                    location_to_id=default_location.id if default_location else None,
                    variant_id=None,
                    reason=f'Réception complète commande d\'achat {order.number} (reste)',
                    related_document_type='purchase_order',
                    related_document_id=order.id
                )
                
                session.add(movement)
                session.flush()  # Get movement.id
                
                # Update stock item quantity (entry increases physical quantity)
                stock_item.physical_quantity += remaining_quantity
                stock_item.last_movement_at = movement.created_at
            
            session.commit()

