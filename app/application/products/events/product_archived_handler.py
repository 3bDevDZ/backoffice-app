"""Domain event handler for ProductArchivedDomainEvent."""
from dataclasses import dataclass
from typing import Optional
from app.application.common.domain_event_handler import DomainEventHandler
from app.domain.events.integration_event import IntegrationEvent, IIntegrationEvent
from app.domain.models.product import ProductArchivedDomainEvent


@dataclass
class ProductArchivedIntegrationEvent(IntegrationEvent):
    """Integration event for product archival (external communication)."""
    product_id: int = 0
    product_code: str = ""


class ProductArchivedDomainEventHandler(DomainEventHandler):
    """Handler for ProductArchivedDomainEvent."""
    
    def map_to_integration_event(
        self, 
        domain_event: ProductArchivedDomainEvent
    ) -> Optional[IIntegrationEvent]:
        """Map to integration event for external systems."""
        return ProductArchivedIntegrationEvent(
            product_id=domain_event.product_id,
            product_code=domain_event.product_code
        )
    
    def handle_internal(self, domain_event: ProductArchivedDomainEvent) -> None:
        """Execute internal business logic for product archival."""
        # Internal business logic examples:
        # - Remove from search index
        # - Invalidate cache
        # - Update statistics
        print(f"Product archived: {domain_event.product_code}")

