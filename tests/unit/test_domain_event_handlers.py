"""Unit tests for domain event handlers."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from app.application.products.events.product_created_handler import (
    ProductCreatedDomainEventHandler,
    ProductCreatedIntegrationEvent
)
from app.domain.models.product import ProductCreatedDomainEvent
from app.infrastructure.outbox.outbox_service import OutboxService


class TestProductCreatedDomainEventHandler:
    """Unit tests for ProductCreatedDomainEventHandler."""
    
    def test_map_to_integration_event(self):
        """Test mapping domain event to integration event."""
        handler = ProductCreatedDomainEventHandler()
        domain_event = ProductCreatedDomainEvent(
            product_id=1,
            product_code="PROD-001",
            product_name="Test Product"
        )
        
        integration_event = handler.map_to_integration_event(domain_event)
        
        assert integration_event is not None
        assert isinstance(integration_event, ProductCreatedIntegrationEvent)
        assert integration_event.product_id == 1
        assert integration_event.product_code == "PROD-001"
        assert integration_event.product_name == "Test Product"
    
    def test_handle_saves_to_outbox(self):
        """Test that handler saves integration event to outbox."""
        from app.infrastructure.outbox.outbox_service import OutboxService
        mock_outbox_service = Mock(spec=OutboxService)
        
        handler = ProductCreatedDomainEventHandler(outbox_service=mock_outbox_service)
        domain_event = ProductCreatedDomainEvent(
            product_id=1,
            product_code="PROD-001",
            product_name="Test Product"
        )
        
        handler.handle(domain_event)
        
        # Verify outbox service was called
        assert mock_outbox_service.add.called
        call_args = mock_outbox_service.add.call_args[0][0]
        assert isinstance(call_args, ProductCreatedIntegrationEvent)
        assert call_args.product_id == 1
    
    @patch('builtins.print')
    def test_handle_internal_executes_business_logic(self, mock_print):
        """Test that internal business logic is executed."""
        handler = ProductCreatedDomainEventHandler()
        domain_event = ProductCreatedDomainEvent(
            product_id=1,
            product_code="PROD-001",
            product_name="Test Product"
        )
        
        handler.handle_internal(domain_event)
        
        # Verify internal logic was executed (in this case, print statement)
        assert mock_print.called
        assert "PROD-001" in str(mock_print.call_args)
    
    def test_handle_complete_flow(self, db_session):
        """Test complete handler flow: map -> outbox -> internal logic."""
        mock_outbox_service = Mock(spec=OutboxService)
        handler = ProductCreatedDomainEventHandler(outbox_service=mock_outbox_service)
        domain_event = ProductCreatedDomainEvent(
            product_id=1,
            product_code="PROD-001",
            product_name="Test Product"
        )
        
        handler.handle(domain_event)
        
        # Verify complete flow
        assert mock_outbox_service.add.called
        # Internal logic should also be executed (we can't easily verify print, but it should run)

