"""Command handlers for stock transfer management."""
from decimal import Decimal
from typing import Dict, Optional
from datetime import datetime

from app.application.common.cqrs import CommandHandler
from app.domain.models.stock import StockTransfer
from app.infrastructure.db import get_session
from app.services.stock_transfer_service import StockTransferService
from .commands import (
    CreateStockTransferCommand,
    ShipStockTransferCommand,
    ReceiveStockTransferCommand,
    CancelStockTransferCommand
)


class CreateStockTransferHandler(CommandHandler):
    """Handler for creating a new stock transfer."""
    
    def handle(self, command: CreateStockTransferCommand) -> int:
        """
        Create a new stock transfer.
        
        Args:
            command: CreateStockTransferCommand with transfer details
            
        Returns:
            Transfer ID (int)
        """
        with get_session() as session:
            transfer_service = StockTransferService(session)
            
            # Convert line inputs to dict format
            lines = None
            if command.lines:
                lines = [
                    {
                        'product_id': line.product_id,
                        'variant_id': line.variant_id,
                        'quantity': line.quantity,
                        'notes': line.notes
                    }
                    for line in command.lines
                ]
            
            transfer = transfer_service.create_transfer(
                number=command.number,
                source_site_id=command.source_site_id,
                destination_site_id=command.destination_site_id,
                created_by=command.created_by,
                requested_date=command.requested_date,
                notes=command.notes,
                lines=lines
            )
            
            transfer_id = transfer.id
            session.commit()
            
            return transfer_id


class ShipStockTransferHandler(CommandHandler):
    """Handler for shipping a stock transfer."""
    
    def handle(self, command: ShipStockTransferCommand) -> int:
        """
        Ship a stock transfer (creates exit movements).
        
        Args:
            command: ShipStockTransferCommand with transfer details
            
        Returns:
            Transfer ID (int)
        """
        with get_session() as session:
            transfer_service = StockTransferService(session)
            
            transfer = transfer_service.ship_transfer(
                transfer_id=command.transfer_id,
                shipped_by=command.shipped_by,
                shipped_date=command.shipped_date
            )
            
            transfer_id = transfer.id
            session.commit()
            
            return transfer_id


class ReceiveStockTransferHandler(CommandHandler):
    """Handler for receiving a stock transfer."""
    
    def handle(self, command: ReceiveStockTransferCommand) -> int:
        """
        Receive a stock transfer (creates entry movements).
        
        Args:
            command: ReceiveStockTransferCommand with transfer details
            
        Returns:
            Transfer ID (int)
        """
        with get_session() as session:
            transfer_service = StockTransferService(session)
            
            transfer = transfer_service.receive_transfer(
                transfer_id=command.transfer_id,
                received_by=command.received_by,
                received_date=command.received_date,
                received_quantities=command.received_quantities
            )
            
            transfer_id = transfer.id
            session.commit()
            
            return transfer_id


class CancelStockTransferHandler(CommandHandler):
    """Handler for cancelling a stock transfer."""
    
    def handle(self, command: CancelStockTransferCommand) -> int:
        """
        Cancel a stock transfer.
        
        Args:
            command: CancelStockTransferCommand with transfer ID
            
        Returns:
            Transfer ID (int)
        """
        with get_session() as session:
            transfer = session.get(StockTransfer, command.transfer_id)
            if not transfer:
                raise ValueError(f"Transfer with ID {command.transfer_id} not found.")
            
            transfer.cancel()
            
            transfer_id = transfer.id
            session.commit()
            
            return transfer_id


