"""Domain event handler for order ready events (delivery note generation)."""
from typing import Optional
from app.application.common.domain_event_handler import DomainEventHandler
from app.domain.models.order import OrderReadyDomainEvent, Order
from app.domain.events.integration_event import IntegrationEvent, IIntegrationEvent
from app.infrastructure.db import get_session
from dataclasses import dataclass


@dataclass
class OrderReadyIntegrationEvent(IntegrationEvent):
    """Integration event for order ready (external communication)."""
    order_id: int = 0
    order_number: str = ""
    customer_id: int = 0


class OrderReadyDomainEventHandler(DomainEventHandler):
    """Handler for OrderReadyDomainEvent - triggers delivery note generation."""
    
    def map_to_integration_event(
        self,
        domain_event: OrderReadyDomainEvent
    ) -> Optional[IIntegrationEvent]:
        """
        Map domain event to integration event for external systems.
        
        Args:
            domain_event: The domain event
            
        Returns:
            Integration event or None
        """
        # For MVP, we might want to notify external systems when an order is ready
        # For now, return None (no external communication needed)
        return None
    
    def handle_internal(self, event: OrderReadyDomainEvent) -> None:
        """
        Handle order ready event by preparing delivery note generation.
        
        When an order is marked as ready, this handler:
        1. Retrieves the order with all necessary data
        2. Prepares data for delivery note generation
        3. Optionally triggers async delivery note PDF generation
        
        Note: The actual PDF generation can be done synchronously here
        or asynchronously via Celery task. For now, we just prepare the data.
        """
        with get_session() as session:
            # Get the order with relationships
            order = session.query(Order).filter(Order.id == event.order_id).first()
            
            if not order:
                return  # Order not found, skip
            
            # The delivery note PDF will be generated on-demand when requested
            # via the API endpoint GET /api/sales/orders/{id}/delivery-note
            # This handler can be extended to:
            # - Pre-generate and store the PDF
            # - Send notification to warehouse staff
            # - Trigger async PDF generation task
            
            # For now, we just log that the order is ready
            # In production, you might want to:
            # - Create a delivery note record
            # - Trigger async PDF generation
            # - Send notification
            
            pass  # Placeholder for future enhancements

