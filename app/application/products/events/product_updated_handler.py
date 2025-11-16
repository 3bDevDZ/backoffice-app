"""Domain event handler for ProductUpdatedDomainEvent."""
from dataclasses import dataclass, field
from typing import Optional
from app.application.common.domain_event_handler import DomainEventHandler
from app.domain.events.integration_event import IntegrationEvent, IIntegrationEvent
from app.domain.models.product import ProductUpdatedDomainEvent, ProductPriceHistory
from app.infrastructure.db import get_session


@dataclass
class ProductUpdatedIntegrationEvent(IntegrationEvent):
    """Integration event for product updates (external communication)."""
    product_id: int = 0
    product_code: str = ""
    changes: dict = field(default_factory=dict)  # Dictionary of changed fields


class ProductUpdatedDomainEventHandler(DomainEventHandler):
    """Handler for ProductUpdatedDomainEvent."""
    
    def map_to_integration_event(
        self, 
        domain_event: ProductUpdatedDomainEvent
    ) -> Optional[IIntegrationEvent]:
        """Map to integration event for external systems."""
        return ProductUpdatedIntegrationEvent(
            product_id=domain_event.product_id,
            product_code=domain_event.product_code,
            changes=domain_event.changes
        )
    
    def handle_internal(self, domain_event: ProductUpdatedDomainEvent) -> None:
        """
        Execute internal business logic for product update.
        Tracks price changes in ProductPriceHistory.
        """
        # Track price changes in history
        if 'price' in domain_event.changes:
            with get_session() as session:
                price_change = domain_event.changes['price']
                # Changes dict has structure: {'old': ..., 'new': ...}
                old_price_str = price_change.get('old')
                new_price_str = price_change.get('new')
                
                # Convert string prices to Decimal
                from decimal import Decimal
                old_price = Decimal(old_price_str) if old_price_str else None
                new_price = Decimal(new_price_str) if new_price_str else None
                
                # Only create history entry if price actually changed
                if old_price != new_price:
                    # Try to get current user ID from Flask context
                    changed_by = None
                    try:
                        from flask import has_request_context, session, g
                        if has_request_context():
                            # Try session first (more reliable)
                            if 'user_id' in session:
                                changed_by = session['user_id']
                            # Fallback to g.user
                            elif hasattr(g, 'user') and g.user:
                                changed_by = g.user.id
                    except:
                        pass
                    
                    price_history = ProductPriceHistory(
                        product_id=domain_event.product_id,
                        old_price=old_price,
                        new_price=new_price,
                        changed_by=changed_by,
                        reason=domain_event.changes.get('price_reason')  # Optional reason
                    )
                    session.add(price_history)
                    session.commit()
        
        # Other internal business logic:
        # - Update search index
        # - Invalidate cache
        # - Update statistics
        print(f"Product updated: {domain_event.product_code} - Changes: {domain_event.changes}")

