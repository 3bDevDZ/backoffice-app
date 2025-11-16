"""Outbox pattern infrastructure for integration events."""
from .outbox_event import OutboxEvent
from .outbox_service import OutboxService

__all__ = ['OutboxEvent', 'OutboxService']

