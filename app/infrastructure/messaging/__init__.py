"""Messaging infrastructure for integration events."""
from .rabbitmq_publisher import RabbitMQPublisher, get_routing_key

__all__ = ['RabbitMQPublisher', 'get_routing_key']

