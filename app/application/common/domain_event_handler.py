"""Base class for domain event handlers."""
from abc import ABC, abstractmethod
from typing import Optional, TypeVar
from ...domain.events.domain_event import IDomainEvent
from ...domain.events.integration_event import IIntegrationEvent
from ...infrastructure.outbox.outbox_service import OutboxService

T = TypeVar('T', bound=IDomainEvent)


class DomainEventHandler(ABC):
    """
    Base class for all domain event handlers.
    Handles automatic mapping to integration events and outbox saving.
    
    Following the architecture pattern:
    1. Map DomainEvent → IntegrationEvent (if needed)
    2. Save IntegrationEvent to Outbox (in same transaction)
    3. Execute business logic (INTERNAL)
    """
    
    def __init__(self, outbox_service: Optional[OutboxService] = None, session=None):
        """
        Initialize domain event handler.
        
        Args:
            outbox_service: Optional outbox service (will create default if None)
            session: Optional SQLAlchemy session for outbox operations
        """
        self._outbox_service = outbox_service or OutboxService(session=session)
        self._session = session
    
    def handle(self, domain_event: T) -> None:
        """
        Handle a domain event.
        This is the entry point called by the dispatcher.
        
        Args:
            domain_event: The domain event to handle
        """
        # 1. Map to IntegrationEvent if necessary
        integration_event = self.map_to_integration_event(domain_event)
        
        # 2. Save to Outbox if IntegrationEvent exists
        if integration_event is not None:
            # Try to get session from context if not provided
            session = self._session
            if session is None:
                # Try to get from thread-local context
                from sqlalchemy.orm import scoped_session
                from ...infrastructure.db import SessionLocal
                try:
                    session = SessionLocal()
                except:
                    session = None
            
            self._outbox_service.add(integration_event, session=session)
        
        # 3. Execute business logic (INTERNAL)
        self.handle_internal(domain_event)
    
    @abstractmethod
    def map_to_integration_event(self, domain_event: T) -> Optional[IIntegrationEvent]:
        """
        Map a domain event to an integration event if external communication is needed.
        Return None if no integration event is required.
        
        Args:
            domain_event: The domain event
            
        Returns:
            Integration event or None
        """
        pass
    
    @abstractmethod
    def handle_internal(self, domain_event: T) -> None:
        """
        Execute internal business logic for the domain event.
        This runs synchronously within the same transaction.
        
        Args:
            domain_event: The domain event
        """
        pass

