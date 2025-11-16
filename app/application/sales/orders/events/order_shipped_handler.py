"""Domain event handler for order shipped events (stock exit movements)."""
from typing import Optional
from sqlalchemy.orm import joinedload
from app.application.common.domain_event_handler import DomainEventHandler
from app.domain.models.order import OrderShippedDomainEvent, Order, StockReservation
from app.domain.models.stock import StockMovement, StockItem
from app.domain.events.integration_event import IntegrationEvent, IIntegrationEvent
from app.infrastructure.db import get_session
from decimal import Decimal
from dataclasses import dataclass


@dataclass
class OrderShippedIntegrationEvent(IntegrationEvent):
    """Integration event for order shipped (external communication)."""
    order_id: int = 0
    order_number: str = ""
    customer_id: int = 0


class OrderShippedDomainEventHandler(DomainEventHandler):
    """Handler for OrderShippedDomainEvent - creates stock exit movements."""
    
    def map_to_integration_event(
        self,
        domain_event: OrderShippedDomainEvent
    ) -> Optional[IIntegrationEvent]:
        """
        Map domain event to integration event for external systems.
        
        Args:
            domain_event: The domain event
            
        Returns:
            Integration event or None
        """
        # For MVP, we might want to notify external systems when an order is shipped
        # For now, return None (no external communication needed)
        return None
    
    def handle_internal(self, event: OrderShippedDomainEvent) -> None:
        """
        Handle order shipped event by creating stock exit movements.
        
        When an order is shipped, this handler:
        1. Retrieves the order with stock reservations
        2. For each stock reservation:
           - Creates a stock exit movement (negative quantity)
           - Reduces physical_quantity of the StockItem
           - Marks the reservation as fulfilled
        3. Updates stock item quantities
        
        This physically removes stock from the warehouse when the order leaves.
        """
        with get_session() as session:
            # Get the order with stock reservations
            order = session.query(Order).options(
                joinedload(Order.stock_reservations).joinedload(StockReservation.stock_item)
            ).filter(Order.id == event.order_id).first()
            
            if not order:
                return  # Order not found, skip
            
            # Get all active reservations for this order
            reservations = session.query(StockReservation).filter(
                StockReservation.order_id == order.id,
                StockReservation.status == "reserved"
            ).all()
            
            if not reservations:
                # No reservations to process (should not happen, but handle gracefully)
                return
            
            # Process each reservation to create exit movements
            for reservation in reservations:
                stock_item = reservation.stock_item
                if not stock_item:
                    continue  # Skip if stock item not found
                
                # Create stock exit movement (negative quantity)
                exit_movement = StockMovement.create(
                    stock_item_id=stock_item.id,
                    product_id=reservation.order_line.product_id,
                    quantity=-reservation.quantity,  # Negative for exit
                    movement_type='exit',
                    user_id=event.shipped_by,
                    location_from_id=stock_item.location_id,
                    variant_id=reservation.order_line.variant_id,
                    reason=f'Expédition commande {order.number}',
                    related_document_type='order',
                    related_document_id=order.id
                )
                
                session.add(exit_movement)
                session.flush()  # Get movement.id
                
                # Reduce physical quantity (stock physically leaves warehouse)
                stock_item.physical_quantity -= reservation.quantity
                stock_item.reserved_quantity -= reservation.quantity  # Release reservation
                stock_item.last_movement_at = exit_movement.created_at
                
                # Mark reservation as fulfilled
                reservation.status = "fulfilled"
            
            session.commit()

