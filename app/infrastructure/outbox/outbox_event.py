"""OutboxEvent entity for storing integration events."""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from ...infrastructure.db import Base


class OutboxEvent(Base):
    """
    OutboxEvent entity for storing integration events.
    Events are saved here in the same transaction as the domain change,
    then published asynchronously by a Celery worker to RabbitMQ.
    """
    __tablename__ = "outbox_events"

    id = Column(Integer, primary_key=True)
    event_type = Column(String(255), nullable=False)  # Full class name of integration event
    event_data = Column(Text, nullable=False)  # JSON serialized event
    tenant_id = Column(String(50), nullable=True)  # For multi-tenant support
    occurred_on = Column(DateTime, nullable=False, server_default=func.now())
    is_processed = Column(Boolean, nullable=False, default=False)
    processed_on = Column(DateTime, nullable=True)
    retry_count = Column(Integer, nullable=False, default=0)
    error_message = Column(Text, nullable=True)  # Error if processing failed

