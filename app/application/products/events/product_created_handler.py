"""Domain event handler for ProductCreatedDomainEvent."""
from dataclasses import dataclass
from typing import Optional
from app.application.common.domain_event_handler import DomainEventHandler
from app.domain.events.integration_event import IntegrationEvent, IIntegrationEvent
from app.domain.models.product import ProductCreatedDomainEvent


@dataclass
class ProductCreatedIntegrationEvent(IntegrationEvent):
    """Integration event for product creation (external communication)."""
    product_id: int = 0
    product_code: str = ""
    product_name: str = ""


class ProductCreatedDomainEventHandler(DomainEventHandler):
    """
    Handler for ProductCreatedDomainEvent.
    Demonstrates the pattern: map to integration event if needed, then handle internal logic.
    """
    
    def map_to_integration_event(
        self, 
        domain_event: ProductCreatedDomainEvent
    ) -> Optional[IIntegrationEvent]:
        """
        Map domain event to integration event for external systems (e-commerce).
        In this case, we want to notify external systems when a product is created.
        
        Args:
            domain_event: The domain event
            
        Returns:
            Integration event or None
        """
        # For MVP, we'll create integration events for product creation
        # This allows external systems (e-commerce) to sync product catalog
        return ProductCreatedIntegrationEvent(
            product_id=domain_event.product_id,
            product_code=domain_event.product_code,
            product_name=domain_event.product_name
        )
    
    def handle_internal(self, domain_event: ProductCreatedDomainEvent) -> None:
        """
        Execute internal business logic for product creation.
        This runs synchronously within the same transaction.
        
        Args:
            domain_event: The domain event
        """
        # Internal business logic examples:
        # - Update search index
        # - Invalidate cache
        # - Send internal notifications
        # - Update statistics
        
        # For MVP, we'll just log (in production, use proper logging)
        print(f"Product created: {domain_event.product_code} - {domain_event.product_name}")
        
        # TODO: Add internal business logic as needed
        # Example: Update product search index
        # Example: Invalidate product cache
        # Example: Notify internal systems

