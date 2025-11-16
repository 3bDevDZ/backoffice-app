"""Product domain event handlers."""
from .product_created_handler import ProductCreatedDomainEventHandler, ProductCreatedIntegrationEvent
from .product_updated_handler import ProductUpdatedDomainEventHandler, ProductUpdatedIntegrationEvent
from .product_archived_handler import ProductArchivedDomainEventHandler, ProductArchivedIntegrationEvent

__all__ = [
    'ProductCreatedDomainEventHandler',
    'ProductCreatedIntegrationEvent',
    'ProductUpdatedDomainEventHandler',
    'ProductUpdatedIntegrationEvent',
    'ProductArchivedDomainEventHandler',
    'ProductArchivedIntegrationEvent',
]

