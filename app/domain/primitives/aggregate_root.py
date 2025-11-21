"""Aggregate Root base class with domain event support."""
from typing import List
from ..events.domain_event import DomainEvent, IDomainEvent


class AggregateRoot:
    """
    Base class for aggregate roots.
    Aggregates can raise domain events that are dispatched after save.
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize aggregate root with domain events list."""
        # Call parent __init__ if it exists (for SQLAlchemy models)
        super().__init__(*args, **kwargs) if hasattr(super(), '__init__') else None
        # Initialize domain events list
        if not hasattr(self, '_domain_events'):
            self._domain_events: List[IDomainEvent] = []
    
    def _ensure_domain_events(self):
        """Ensure _domain_events list exists (lazy initialization for SQLAlchemy-loaded instances)."""
        # Use getattr with default to avoid triggering SQLAlchemy lazy loading
        # if object is detached from session
        if not hasattr(self, '_domain_events'):
            try:
                self._domain_events: List[IDomainEvent] = []
            except (AttributeError, RuntimeError):
                # Object might be detached, create list anyway
                object.__setattr__(self, '_domain_events', [])
    
    def raise_domain_event(self, domain_event: IDomainEvent) -> None:
        """
        Raise a domain event.
        Events are collected and dispatched after the transaction commits.
        
        Args:
            domain_event: The domain event to raise
        """
        self._ensure_domain_events()
        if domain_event not in self._domain_events:
            self._domain_events.append(domain_event)
    
    def get_domain_events(self) -> List[IDomainEvent]:
        """
        Get all raised domain events.
        Used by infrastructure layer to dispatch events.
        
        Returns:
            List of domain events
        """
        self._ensure_domain_events()
        return self._domain_events.copy()
    
    def clear_domain_events(self) -> None:
        """Clear all domain events (called after dispatch)."""
        self._ensure_domain_events()
        self._domain_events.clear()

