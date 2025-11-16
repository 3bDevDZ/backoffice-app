"""Domain event handler for purchase order line received events (partial or full)."""
from typing import Optional
from app.application.common.domain_event_handler import DomainEventHandler
from app.domain.models.purchase import PurchaseOrderLineReceivedDomainEvent
from app.domain.models.stock import StockItem, StockMovement
from app.domain.events.integration_event import IntegrationEvent, IIntegrationEvent
from app.infrastructure.db import get_session
from decimal import Decimal
from dataclasses import dataclass


@dataclass
class PurchaseOrderLineReceivedIntegrationEvent(IntegrationEvent):
    """Integration event for purchase order line received (external communication)."""
    purchase_order_id: int = 0
    purchase_order_number: str = ""
    line_id: int = 0
    product_id: int = 0
    quantity_received: Decimal = Decimal(0)


class PurchaseOrderLineReceivedDomainEventHandler(DomainEventHandler):
    """Handler for PurchaseOrderLineReceivedDomainEvent - updates stock immediately for partial or full receipts."""
    
    def map_to_integration_event(
        self,
        domain_event: PurchaseOrderLineReceivedDomainEvent
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
    
    def handle_internal(self, event: PurchaseOrderLineReceivedDomainEvent) -> None:
        """
        Handle purchase order line received event by creating stock entry movements immediately.
        
        This handler is called for both partial and full receipts, ensuring stock is updated
        as soon as goods are received, not just when the entire order is complete.
        
        Args:
            event: The domain event containing line receipt information
        """
        with get_session() as session:
            from app.domain.models.stock import Location
            
            # Get location (use provided location_id or default warehouse)
            location_id = event.location_id
            if not location_id:
                # Get default location (first active warehouse location)
                default_location = session.query(Location).filter(
                    Location.type == 'warehouse',
                    Location.is_active == True
                ).first()
                
                if not default_location:
                    # If no warehouse exists, skip stock update (log warning in production)
                    # In production, you'd want to log this and handle it appropriately
                    return
                
                location_id = default_location.id
            
            # Get or create stock item for this product at the specified location
            stock_item = session.query(StockItem).filter(
                StockItem.product_id == event.product_id,
                StockItem.location_id == location_id,
                StockItem.variant_id == None  # For now, no variants
            ).first()
            
            if not stock_item:
                # Create stock item if it doesn't exist
                stock_item = StockItem.create(
                    product_id=event.product_id,
                    location_id=location_id,
                    physical_quantity=Decimal('0'),
                    variant_id=None
                )
                session.add(stock_item)
                session.flush()  # Get stock_item.id
            
            # Get order to get user_id
            from app.domain.models.purchase import PurchaseOrder
            order = session.get(PurchaseOrder, event.purchase_order_id)
            user_id = order.created_by if order else None
            
            # Create stock movement entry for the incremental quantity received
            movement = StockMovement.create(
                stock_item_id=stock_item.id,
                product_id=event.product_id,
                quantity=event.quantity_received,  # Positive quantity for entry
                movement_type='entry',
                user_id=user_id,
                location_to_id=location_id,
                variant_id=None,
                reason=f'Réception commande d\'achat {event.purchase_order_number} (Ligne {event.line_id})',
                related_document_type='purchase_order',
                related_document_id=event.purchase_order_id
            )
            
            session.add(movement)
            session.flush()  # Get movement.id
            
            # Update stock item quantity (entry increases physical quantity)
            old_stock_quantity = stock_item.physical_quantity
            stock_item.physical_quantity += event.quantity_received
            stock_item.last_movement_at = movement.created_at
            
            # Calculate and update product cost using AVCO method
            # AVCO: new_cost = (old_cost * old_stock + purchase_price * quantity_received) / new_stock
            from app.domain.models.product import Product, ProductCostHistory
            from app.domain.models.purchase import PurchaseOrderLine
            
            product = session.get(Product, event.product_id)
            purchase_order_line = session.get(PurchaseOrderLine, event.line_id)
            
            if product and purchase_order_line:
                # Refresh product to get latest cost (important for multiple receipts)
                session.refresh(product)
                
                purchase_price = purchase_order_line.unit_price
                quantity_received = event.quantity_received
                new_stock_quantity = stock_item.physical_quantity
                
                # Get old cost (use current product cost, or 0 if None)
                old_cost = product.cost if product.cost is not None else Decimal('0')
                had_initial_cost = product.cost is not None
                
                # Calculate new cost using AVCO method
                if new_stock_quantity > 0:
                    # AVCO formula: new_cost = (old_cost * old_stock + purchase_price * quantity_received) / new_stock
                    new_cost = (old_cost * old_stock_quantity + purchase_price * quantity_received) / new_stock_quantity
                    
                    # Round to 2 decimal places for cost
                    new_cost = round(new_cost, 2)
                    
                    # Only update if cost actually changed (avoid unnecessary history entries)
                    if old_cost != new_cost or not had_initial_cost:
                        # Update product cost
                        product.cost = new_cost
                        
                        # Create cost history entry
                        cost_history = ProductCostHistory(
                            product_id=product.id,
                            old_cost=old_cost if had_initial_cost else None,  # NULL for first cost
                            new_cost=new_cost,
                            old_stock=old_stock_quantity,
                            new_stock=new_stock_quantity,
                            purchase_price=purchase_price,
                            quantity_received=quantity_received,
                            changed_by=user_id,
                            reason=f'Réception commande d\'achat {event.purchase_order_number} (AVCO)',
                            purchase_order_id=event.purchase_order_id,
                            purchase_order_line_id=event.line_id
                        )
                        session.add(cost_history)
                else:
                    # Edge case: new_stock = 0 (shouldn't happen, but handle it)
                    # If stock is 0, use purchase price as new cost
                    if product.cost != purchase_price or not had_initial_cost:
                        product.cost = purchase_price
                        cost_history = ProductCostHistory(
                            product_id=product.id,
                            old_cost=old_cost if had_initial_cost else None,
                            new_cost=purchase_price,
                            old_stock=old_stock_quantity,
                            new_stock=Decimal('0'),
                            purchase_price=purchase_price,
                            quantity_received=quantity_received,
                            changed_by=user_id,
                            reason=f'Réception commande d\'achat {event.purchase_order_number} (AVCO - stock initial)',
                            purchase_order_id=event.purchase_order_id,
                            purchase_order_line_id=event.line_id
                        )
                        session.add(cost_history)
            
            session.commit()

