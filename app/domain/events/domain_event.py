"""Domain Event base classes and interfaces."""
from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional


class IDomainEvent(ABC):
    """Interface for all domain events."""
    occurred_on: datetime


@dataclass
class DomainEvent(IDomainEvent):
    """
    Base class for all domain events.
    Domain events are raised by aggregates to communicate state changes internally.
    They are processed synchronously within the same transaction.
    """
    occurred_on: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Ensure occurred_on is set if not provided."""
        if self.occurred_on is None:
            self.occurred_on = datetime.utcnow()

