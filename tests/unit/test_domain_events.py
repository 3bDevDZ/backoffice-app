"""Unit tests for domain events infrastructure."""
import pytest
from datetime import datetime
from app.domain.events.domain_event import DomainEvent, IDomainEvent
from app.domain.primitives.aggregate_root import AggregateRoot
from app.domain.models.product import (
    ProductCreatedDomainEvent,
    ProductUpdatedDomainEvent,
    ProductArchivedDomainEvent
)


class TestDomainEvent:
    """Unit tests for DomainEvent base class."""
    
    def test_domain_event_has_occurred_on(self):
        """Test that domain event has occurred_on timestamp."""
        event = ProductCreatedDomainEvent(
            product_id=1,
            product_code="PROD-001",
            product_name="Test Product"
        )
        
        assert event.occurred_on is not None
        assert isinstance(event.occurred_on, datetime)
    
    def test_domain_event_implements_interface(self):
        """Test that domain event implements IDomainEvent."""
        event = ProductCreatedDomainEvent(
            product_id=1,
            product_code="PROD-001",
            product_name="Test Product"
        )
        
        assert isinstance(event, IDomainEvent)


class TestAggregateRoot:
    """Unit tests for AggregateRoot base class."""
    
    def test_raise_domain_event(self):
        """Test raising a domain event."""
        class TestAggregate(AggregateRoot):
            pass
        
        aggregate = TestAggregate()
        event = ProductCreatedDomainEvent(
            product_id=1,
            product_code="PROD-001",
            product_name="Test Product"
        )
        
        aggregate.raise_domain_event(event)
        
        events = aggregate.get_domain_events()
        assert len(events) == 1
        assert events[0] == event
    
    def test_get_domain_events_returns_copy(self):
        """Test that get_domain_events returns a copy."""
        class TestAggregate(AggregateRoot):
            pass
        
        aggregate = TestAggregate()
        event = ProductCreatedDomainEvent(
            product_id=1,
            product_code="PROD-001",
            product_name="Test Product"
        )
        
        aggregate.raise_domain_event(event)
        events1 = aggregate.get_domain_events()
        events2 = aggregate.get_domain_events()
        
        # Should be different list objects
        assert events1 is not events2
        # But should contain same events
        assert len(events1) == len(events2) == 1
    
    def test_clear_domain_events(self):
        """Test clearing domain events."""
        class TestAggregate(AggregateRoot):
            pass
        
        aggregate = TestAggregate()
        event = ProductCreatedDomainEvent(
            product_id=1,
            product_code="PROD-001",
            product_name="Test Product"
        )
        
        aggregate.raise_domain_event(event)
        assert len(aggregate.get_domain_events()) == 1
        
        aggregate.clear_domain_events()
        assert len(aggregate.get_domain_events()) == 0
    
    def test_multiple_domain_events(self):
        """Test raising multiple domain events."""
        class TestAggregate(AggregateRoot):
            pass
        
        aggregate = TestAggregate()
        event1 = ProductCreatedDomainEvent(
            product_id=1,
            product_code="PROD-001",
            product_name="Test Product 1"
        )
        event2 = ProductUpdatedDomainEvent(
            product_id=1,
            product_code="PROD-001",
            changes={"name": {"old": "Old", "new": "New"}}
        )
        
        aggregate.raise_domain_event(event1)
        aggregate.raise_domain_event(event2)
        
        events = aggregate.get_domain_events()
        assert len(events) == 2
        assert event1 in events
        assert event2 in events

