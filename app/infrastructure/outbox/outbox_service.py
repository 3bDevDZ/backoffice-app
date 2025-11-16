"""Outbox service for saving integration events."""
import json
from decimal import Decimal
from typing import Optional
from .outbox_event import OutboxEvent
from ...domain.events.integration_event import IIntegrationEvent


class OutboxService:
    """
    Service for saving integration events to OutboxEvents table.
    Events are saved in the same transaction as the domain change.
    
    Note: This service should be called from within a domain event handler
    that is executing within a database transaction context.
    """
    
    def __init__(self, session=None):
        """
        Initialize outbox service.
        
        Args:
            session: Optional SQLAlchemy session. If None, will try to get from context.
        """
        self._session = session
    
    def add(self, integration_event: IIntegrationEvent, session=None) -> None:
        """
        Add an integration event to the outbox.
        Should be called within the same transaction as the domain change.
        
        Args:
            integration_event: The integration event to save
            session: Optional SQLAlchemy session (uses self._session if not provided)
        """
        # Use provided session or instance session
        db_session = session or self._session
        
        if db_session is None:
            # Try to get session from context (for domain event handlers)
            # This is a fallback - ideally session should be passed
            from sqlalchemy.orm import scoped_session
            from ..db import SessionLocal
            db_session = SessionLocal()
        
        outbox_event = OutboxEvent(
            event_type=f"{integration_event.__class__.__module__}.{integration_event.__class__.__name__}",
            event_data=json.dumps(self._serialize_event(integration_event)),
            tenant_id=getattr(integration_event, 'tenant_id', None),
            occurred_on=integration_event.occurred_on,
            is_processed=False
        )
        db_session.add(outbox_event)
        # Don't commit here - let the transaction handle it
    
    def _serialize_event(self, event: IIntegrationEvent) -> dict:
        """
        Serialize integration event to dictionary.
        
        Args:
            event: Integration event to serialize
            
        Returns:
            Dictionary representation of the event
        """
        from datetime import datetime, date
        
        def convert_value(value):
            """Convert value to JSON-serializable format."""
            if isinstance(value, (datetime, date)):
                return value.isoformat()
            elif isinstance(value, Decimal):
                return str(value)
            elif hasattr(value, '__dict__'):
                return {k: convert_value(v) for k, v in value.__dict__.items()}
            elif isinstance(value, dict):
                return {k: convert_value(v) for k, v in value.items()}
            elif isinstance(value, (list, tuple)):
                return [convert_value(item) for item in value]
            else:
                return value
        
        if hasattr(event, '__dataclass_fields__'):
            # Dataclass
            from dataclasses import asdict
            data = asdict(event)
            return convert_value(data)
        elif hasattr(event, '__dict__'):
            data = event.__dict__.copy()
            return convert_value(data)
        else:
            # Fallback to basic serialization
            return {
                'type': event.__class__.__name__,
                'data': str(event)
            }

