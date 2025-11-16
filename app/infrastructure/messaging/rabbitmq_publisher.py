"""RabbitMQ publisher for integration events."""
import json
import pika
from typing import Optional
from app.config import Config


class RabbitMQPublisher:
    """
    Publisher for integration events to RabbitMQ.
    Used by Celery worker to publish events from OutboxEvents table.
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize RabbitMQ publisher.
        
        Args:
            config: Optional config object (uses default if None)
        """
        self.config = config or Config()
        self._connection: Optional[pika.BlockingConnection] = None
        self._channel: Optional[pika.channel.Channel] = None
    
    def connect(self) -> None:
        """Establish connection to RabbitMQ."""
        credentials = pika.PlainCredentials(
            self.config.RABBITMQ_USER,
            self.config.RABBITMQ_PASSWORD
        )
        parameters = pika.ConnectionParameters(
            host=self.config.RABBITMQ_HOST,
            port=self.config.RABBITMQ_PORT,
            credentials=credentials,
            heartbeat=600,
            blocked_connection_timeout=300
        )
        self._connection = pika.BlockingConnection(parameters)
        self._channel = self._connection.channel()
        
        # Declare exchange
        self._channel.exchange_declare(
            exchange=self.config.RABBITMQ_EXCHANGE,
            exchange_type='topic',
            durable=True
        )
    
    def close(self) -> None:
        """Close RabbitMQ connection."""
        if self._connection and not self._connection.is_closed:
            self._connection.close()
        self._connection = None
        self._channel = None
    
    def publish(self, routing_key: str, event_data: str, event_type: str) -> None:
        """
        Publish integration event to RabbitMQ.
        
        Args:
            routing_key: Routing key (e.g., "products.created")
            event_data: JSON serialized event data
            event_type: Full class name of the integration event
        """
        if not self._connection or self._connection.is_closed:
            self.connect()
        
        properties = pika.BasicProperties(
            delivery_mode=2,  # Make message persistent
            content_type='application/json',
            type=event_type
        )
        
        self._channel.basic_publish(
            exchange=self.config.RABBITMQ_EXCHANGE,
            routing_key=routing_key,
            body=event_data.encode('utf-8'),
            properties=properties,
            mandatory=True  # Ensure message is routed
        )
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def get_routing_key(event_type: str) -> str:
    """
    Generate routing key from event type.
    Example: "ProductCreatedIntegrationEvent" -> "products.created"
    
    Args:
        event_type: Full class name of integration event
        
    Returns:
        Routing key for RabbitMQ
    """
    # Extract class name (last part after dot)
    class_name = event_type.split('.')[-1]
    
    # Remove "IntegrationEvent" suffix
    if class_name.endswith('IntegrationEvent'):
        class_name = class_name[:-15]  # Remove "IntegrationEvent"
    
    # Convert PascalCase to snake_case and lowercase
    import re
    snake_case = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', class_name)
    snake_case = re.sub('([a-z0-9])([A-Z])', r'\1_\2', snake_case).lower()
    
    # Add module prefix if needed (e.g., "products.created")
    if 'Product' in class_name:
        return f"products.{snake_case}"
    elif 'Order' in class_name:
        return f"orders.{snake_case}"
    elif 'Quote' in class_name:
        return f"quotes.{snake_case}"
    elif 'Category' in class_name:
        return f"categories.{snake_case}"
    elif 'Customer' in class_name:
        return f"customers.{snake_case}"
    else:
        return snake_case

