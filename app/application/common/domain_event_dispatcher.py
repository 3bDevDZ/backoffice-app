"""Domain event dispatcher for synchronous event handling."""
from typing import Type, Dict, List, TypeVar, Callable
from ...domain.events.domain_event import IDomainEvent

T = TypeVar('T', bound=IDomainEvent)


class DomainEventDispatcher:
    """
    Dispatcher for domain events (similar to MediatR for .NET).
    Handles synchronous dispatch of domain events within the same transaction.
    """
    
    def __init__(self):
        self._handlers: Dict[Type[IDomainEvent], List[Callable]] = {}
    
    def register_handler(self, event_type: Type[T], handler: Callable[[T], None]) -> None:
        """
        Register a handler for a specific domain event type.
        
        Args:
            event_type: The domain event type
            handler: The handler function that takes the event and returns None
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
    
    def dispatch(self, event: IDomainEvent) -> None:
        """
        Dispatch a domain event to all registered handlers.
        Handlers are called synchronously in the order they were registered.
        
        Args:
            event: The domain event to dispatch
        """
        event_type = type(event)
        handlers = self._handlers.get(event_type, [])
        
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                # Log error but continue with other handlers
                # In production, you might want to use proper logging
                print(f"Error in domain event handler {handler.__name__} for {event_type.__name__}: {e}")
                import traceback
                traceback.print_exc()
                raise  # Re-raise to fail the transaction
    
    def dispatch_all(self, events: List[IDomainEvent]) -> None:
        """
        Dispatch multiple domain events.
        
        Args:
            events: List of domain events to dispatch
        """
        for event in events:
            self.dispatch(event)


# Global domain event dispatcher instance
domain_event_dispatcher = DomainEventDispatcher()

