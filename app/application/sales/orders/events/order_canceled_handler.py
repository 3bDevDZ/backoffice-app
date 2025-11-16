"""Domain event handler for order canceled events."""
from typing import Optional
from app.application.common.domain_event_handler import DomainEventHandler
from app.domain.models.order import OrderCanceledDomainEvent, StockReservation
from app.domain.models.stock import StockItem
from app.domain.events.integration_event import IntegrationEvent, IIntegrationEvent
from app.infrastructure.db import get_session
from datetime import datetime
from decimal import Decimal
from dataclasses import dataclass


@dataclass
class OrderCanceledIntegrationEvent(IntegrationEvent):
    """Integration event for order canceled (external communication)."""
    order_id: int = 0
    order_number: str = ""
    customer_id: int = 0


class OrderCanceledDomainEventHandler(DomainEventHandler):
    """Handler for OrderCanceledDomainEvent - releases reserved stock automatically."""
    
    def map_to_integration_event(
        self,
        domain_event: OrderCanceledDomainEvent
    ) -> Optional[IIntegrationEvent]:
        """
        Map domain event to integration event for external systems.
        
        Args:
            domain_event: The domain event
            
        Returns:
            Integration event or None
        """
        # For MVP, we might want to notify external systems when an order is canceled
        # For now, return None (no external communication needed)
        return None
    
    def handle_internal(self, event: OrderCanceledDomainEvent) -> None:
        """
        Handle order canceled event by releasing reserved stock.
        
        When an order is canceled, this handler:
        1. Retrieves the order with its reservations
        2. For each reservation with status "reserved":
           - Uses StockService to release stock (which handles business rules)
           - Uses Order.release_stock_reservation() to update through aggregate root
        """
        from sqlalchemy.orm import joinedload
        from app.services.stock_service import StockService
        from app.domain.models.order import Order
        
        with get_session() as session:
            # Get the order with reservations
            order = session.query(Order).options(
                joinedload(Order.stock_reservations)
            ).filter(Order.id == event.order_id).first()
            
            if not order:
                return  # Order not found, skip
            
            # Get all reserved reservations
            reserved_reservations = [
                r for r in order.stock_reservations 
                if r.status == "reserved"
            ]
            
            if not reserved_reservations:
                return  # No reservations to release
            
            # Use StockService to handle stock release logic
            stock_service = StockService(session)
            
            for reservation in reserved_reservations:
                # Release stock using StockItem.release() (domain method)
                stock_item = session.get(StockItem, reservation.stock_item_id)
                if stock_item:
                    try:
                        stock_item.release(reservation.quantity)
                        stock_service.validate_stock_rules(stock_item, 'release')
                    except ValueError:
                        # If release fails, ensure reserved_quantity doesn't go negative
                        if stock_item.reserved_quantity < reservation.quantity:
                            stock_item.reserved_quantity = Decimal(0)
                        else:
                            stock_item.reserved_quantity -= reservation.quantity
                
                # Update reservation through aggregate root
                order.release_stock_reservation(reservation.id)
            
            session.commit()

