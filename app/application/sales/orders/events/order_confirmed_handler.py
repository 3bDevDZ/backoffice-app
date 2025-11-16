"""Domain event handler for order confirmed events."""
from typing import Optional
from sqlalchemy.orm import joinedload
from app.application.common.domain_event_handler import DomainEventHandler
from app.domain.models.order import OrderConfirmedDomainEvent, Order, OrderLine, StockReservation
from app.domain.events.integration_event import IntegrationEvent, IIntegrationEvent
from app.infrastructure.db import get_session
from app.services.stock_service import StockService
from decimal import Decimal
from datetime import datetime
from dataclasses import dataclass


@dataclass
class OrderConfirmedIntegrationEvent(IntegrationEvent):
    """Integration event for order confirmed (external communication)."""
    order_id: int = 0
    order_number: str = ""
    customer_id: int = 0


class OrderConfirmedDomainEventHandler(DomainEventHandler):
    """Handler for OrderConfirmedDomainEvent - reserves stock automatically."""
    
    def map_to_integration_event(
        self,
        domain_event: OrderConfirmedDomainEvent
    ) -> Optional[IIntegrationEvent]:
        """
        Map domain event to integration event for external systems.
        
        Args:
            domain_event: The domain event
            
        Returns:
            Integration event or None
        """
        # For MVP, we might want to notify external systems when an order is confirmed
        # For now, return None (no external communication needed)
        return None
    
    def handle_internal(self, event: OrderConfirmedDomainEvent) -> None:
        """
        Handle order confirmed event by reserving stock.
        
        When an order is confirmed, this handler:
        1. Retrieves the order and its lines
        2. Uses StockService to reserve stock (which handles business rules and validation)
        3. Creates StockReservation entities for tracking
        
        The StockService is used because:
        - It encapsulates complex stock reservation logic
        - It validates stock business rules (RG-STOCK-001 to RG-STOCK-007)
        - It handles multi-location reservation strategies
        - It uses StockItem.reserve() method (domain method) instead of direct manipulation
        """
        with get_session() as session:
            # Get the order with lines
            order = session.query(Order).options(
                joinedload(Order.lines),
                joinedload(Order.stock_reservations)
            ).filter(Order.id == event.order_id).first()
            
            if not order:
                return  # Order not found, skip
            
            # Check if stock is already reserved (prevent duplicate reservations)
            existing_reservations = session.query(StockReservation).filter(
                StockReservation.order_id == order.id,
                StockReservation.status == "reserved"
            ).count()
            
            if existing_reservations > 0:
                return  # Stock already reserved, skip
            
            # Use StockService to handle stock reservation logic
            stock_service = StockService(session)
            
            # Process each order line individually
            for line in order.lines:
                # Prepare line data for the service
                order_line_data = [{
                    'product_id': line.product_id,
                    'quantity': line.quantity,
                    'variant_id': line.variant_id,
                    'preferred_location_id': None  # Could be set based on order delivery preferences
                }]
                
                # Reserve stock for this line using the service
                # The service handles business rules, validation, and multi-location logic
                reservation_results = stock_service.reserve_stock_for_order(
                    order_id=order.id,
                    order_lines=order_line_data
                )
                
                # Create StockReservation entities through the aggregate root
                # This maintains DDD principles: entities are created via aggregate root
                for result in reservation_results:
                    if result.success and result.quantity_reserved > 0:
                        # Use Order.add_stock_reservation() to create through aggregate root
                        order.add_stock_reservation(
                            order_line_id=line.id,
                            stock_item_id=result.stock_item_id,
                            quantity=result.quantity_reserved
                        )
            
            session.commit()

