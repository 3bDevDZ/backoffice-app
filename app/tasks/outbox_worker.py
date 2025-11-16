"""Celery worker for processing OutboxEvents and publishing to RabbitMQ."""
from datetime import datetime
from celery import Celery
from app.infrastructure.db import get_session
from app.infrastructure.outbox.outbox_event import OutboxEvent
from app.infrastructure.messaging.rabbitmq_publisher import RabbitMQPublisher, get_routing_key
from app.config import Config

# Initialize Celery
celery_app = Celery('commercial_management')
celery_app.config_from_object(Config)


@celery_app.task(bind=True, max_retries=3)
def process_outbox_events(self):
    """
    Process unprocessed outbox events and publish to RabbitMQ.
    This task should be scheduled to run periodically (e.g., every 30 seconds).
    """
    with get_session() as session:
        # Get unprocessed events (limit to 100 per run)
        events = session.query(OutboxEvent).filter(
            OutboxEvent.is_processed == False
        ).order_by(OutboxEvent.occurred_on).limit(100).all()
        
        if not events:
            return  # No events to process
        
        publisher = RabbitMQPublisher()
        try:
            publisher.connect()
            
            for outbox_event in events:
                try:
                    # Get routing key
                    routing_key = get_routing_key(outbox_event.event_type)
                    
                    # Publish to RabbitMQ
                    publisher.publish(
                        routing_key=routing_key,
                        event_data=outbox_event.event_data,
                        event_type=outbox_event.event_type
                    )
                    
                    # Mark as processed
                    outbox_event.is_processed = True
                    outbox_event.processed_on = datetime.utcnow()
                    outbox_event.retry_count = 0
                    outbox_event.error_message = None
                    
                except Exception as e:
                    # Increment retry count
                    outbox_event.retry_count += 1
                    outbox_event.error_message = str(e)
                    
                    # If retry count exceeds threshold, mark as failed
                    if outbox_event.retry_count >= 3:
                        outbox_event.is_processed = True  # Mark as processed to stop retrying
                        # In production, you might want to move to a dead letter queue
                    
                    # Log error (in production, use proper logging)
                    print(f"Error processing outbox event {outbox_event.id}: {e}")
            
            session.commit()
            
        except Exception as e:
            # If connection fails, retry the entire task
            print(f"Error connecting to RabbitMQ: {e}")
            raise self.retry(exc=e)
        finally:
            publisher.close()

