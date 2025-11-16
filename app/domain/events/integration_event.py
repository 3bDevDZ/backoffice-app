"""Integration Event base classes and interfaces."""
from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


class IIntegrationEvent(ABC):
    """Interface for all integration events."""
    occurred_on: datetime
    tenant_id: Optional[str] = None


@dataclass
class IntegrationEvent(IIntegrationEvent):
    """
    Base class for all integration events.
    Integration events are for external communication (e-commerce, other projects).
    They are saved to OutboxEvents table and published asynchronously via Celery to RabbitMQ.
    """
    occurred_on: datetime = field(default_factory=datetime.utcnow)
    tenant_id: Optional[str] = None

