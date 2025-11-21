"""Command handlers for stock management."""
from app.application.common.cqrs import CommandHandler
from app.domain.models.stock import Location, StockItem, StockMovement
from app.domain.models.product import Product
from app.infrastructure.db import get_session
from decimal import Decimal
from typing import Optional
from .commands import (
    CreateLocationCommand,
    UpdateLocationCommand,
    CreateStockItemCommand,
    UpdateStockItemCommand,
    CreateStockMovementCommand,
    ReserveStockCommand,
    ReleaseStockCommand,
    AdjustStockCommand
)


# Location Handlers
class CreateLocationHandler(CommandHandler):
    def handle(self, command: CreateLocationCommand) -> Location:
        with get_session() as session:
            # Check if code already exists
            existing = session.query(Location).filter(Location.code == command.code).first()
            if existing:
                raise ValueError(f"Location with code '{command.code}' already exists")
            
            # Validate parent if provided
            if command.parent_id:
                parent = session.get(Location, command.parent_id)
                if not parent:
                    raise ValueError("Parent location not found")
            
            # Validate site if provided (None is allowed for simple mode)
            if command.site_id:
                from app.domain.models.stock import Site
                site = session.get(Site, command.site_id)
                if not site:
                    raise ValueError("Site not found")
            
            # Create location using domain factory method
            location = Location.create(
                code=command.code,
                name=command.name,
                type=command.type,
                parent_id=command.parent_id,
                site_id=command.site_id,
                capacity=command.capacity,
                is_active=command.is_active
            )
            
            session.add(location)
            session.flush()  # Flush to get ID
            
            # Access all attributes while still in session
            # This ensures they're loaded before commit
            _ = location.id, location.code, location.name, location.type, location.site_id
            
            session.commit()
            
            # Return location - it will be detached when session closes
            # Attributes accessed above are already loaded, so they're safe to use
            return location


class UpdateLocationHandler(CommandHandler):
    def handle(self, command: UpdateLocationCommand) -> Location:
        with get_session() as session:
            location = session.get(Location, command.id)
            if not location:
                raise ValueError("Location not found")
            
            # Update fields if provided
            if command.code is not None:
                # Check if new code already exists (excluding current location)
                existing = session.query(Location).filter(
                    Location.code == command.code,
                    Location.id != command.id
                ).first()
                if existing:
                    raise ValueError(f"Location with code '{command.code}' already exists")
                location.code = command.code
            
            if command.name is not None:
                location.name = command.name
            
            if command.type is not None:
                location.type = command.type
            
            # Handle site_id update: use sentinel to distinguish "not provided" from "explicitly None"
            from app.application.stock.commands.commands import _MISSING
            if command.site_id is not _MISSING:
                # site_id was explicitly provided in the command (can be None)
                if command.site_id is not None:
                    # Validate site if provided
                    from app.domain.models.stock import Site
                    site = session.get(Site, command.site_id)
                    if not site:
                        raise ValueError("Site not found")
                # Set site_id (can be None for simple mode)
                location.site_id = command.site_id
            
            if command.parent_id is not None:
                # Validate parent if provided
                if command.parent_id:
                    parent = session.get(Location, command.parent_id)
                    if not parent:
                        raise ValueError("Parent location not found")
                    if command.parent_id == command.id:
                        raise ValueError("Location cannot be its own parent")
                location.parent_id = command.parent_id
            
            if command.capacity is not None:
                location.capacity = command.capacity
            
            if command.is_active is not None:
                location.is_active = command.is_active
            
            session.commit()
            session.refresh(location)  # Refresh to ensure all attributes are loaded
            # Expunge to detach from session so it can be used after context closes
            session.expunge(location)
            return location


# StockItem Handlers
class CreateStockItemHandler(CommandHandler):
    def handle(self, command: CreateStockItemCommand) -> StockItem:
        with get_session() as session:
            # Validate product exists
            product = session.get(Product, command.product_id)
            if not product:
                raise ValueError("Product not found")
            
            # Validate location exists
            location = session.get(Location, command.location_id)
            if not location:
                raise ValueError("Location not found")
            
            # Check if stock item already exists for this product+location combination
            existing = session.query(StockItem).filter(
                StockItem.product_id == command.product_id,
                StockItem.location_id == command.location_id,
                StockItem.variant_id == command.variant_id
            ).first()
            if existing:
                raise ValueError(f"Stock item already exists for product {command.product_id} at location {command.location_id}")
            
            # Create stock item using domain factory method
            stock_item = StockItem.create(
                product_id=command.product_id,
                location_id=command.location_id,
                physical_quantity=command.physical_quantity,
                variant_id=command.variant_id,
                min_stock=command.min_stock,
                max_stock=command.max_stock,
                reorder_point=command.reorder_point,
                reorder_quantity=command.reorder_quantity,
                valuation_method=command.valuation_method
            )
            
            session.add(stock_item)
            session.flush()  # Flush to get ID
            
            session.commit()
            return stock_item


class UpdateStockItemHandler(CommandHandler):
    def handle(self, command: UpdateStockItemCommand) -> StockItem:
        with get_session() as session:
            stock_item = session.get(StockItem, command.id)
            if not stock_item:
                raise ValueError("Stock item not found")
            
            # Update fields if provided
            if command.min_stock is not None:
                stock_item.min_stock = command.min_stock
            
            if command.max_stock is not None:
                stock_item.max_stock = command.max_stock
            
            if command.reorder_point is not None:
                stock_item.reorder_point = command.reorder_point
            
            if command.reorder_quantity is not None:
                stock_item.reorder_quantity = command.reorder_quantity
            
            if command.valuation_method is not None:
                stock_item.valuation_method = command.valuation_method
            
            session.commit()
            return stock_item


# StockMovement Handlers
class CreateStockMovementHandler(CommandHandler):
    def handle(self, command: CreateStockMovementCommand) -> StockMovement:
        with get_session() as session:
            # Validate stock item exists
            stock_item = session.get(StockItem, command.stock_item_id)
            if not stock_item:
                raise ValueError("Stock item not found")
            
            # Validate product exists
            product = session.get(Product, command.product_id)
            if not product:
                raise ValueError("Product not found")
            
            # Validate locations if provided
            if command.location_from_id:
                location_from = session.get(Location, command.location_from_id)
                if not location_from:
                    raise ValueError("Source location not found")
            
            if command.location_to_id:
                location_to = session.get(Location, command.location_to_id)
                if not location_to:
                    raise ValueError("Destination location not found")
            
            # Create movement using domain factory method
            movement = StockMovement.create(
                stock_item_id=command.stock_item_id,
                product_id=command.product_id,
                quantity=command.quantity,
                movement_type=command.movement_type,
                user_id=command.user_id,
                location_from_id=command.location_from_id,
                location_to_id=command.location_to_id,
                variant_id=command.variant_id,
                reason=command.reason,
                related_document_type=command.related_document_type,
                related_document_id=command.related_document_id
            )
            
            session.add(movement)
            session.flush()  # Flush to get ID
            
            # Update stock item based on movement type
            if command.movement_type == 'entry':
                stock_item.physical_quantity += command.quantity
                stock_item.last_movement_at = movement.created_at
            elif command.movement_type == 'exit':
                # Exit quantity is negative, so we add it (which subtracts)
                stock_item.physical_quantity += command.quantity
                stock_item.last_movement_at = movement.created_at
            elif command.movement_type == 'transfer':
                # Transfer: decrease from source location
                # Note: Destination stock item update should be handled separately
                # or in a service that creates two movements (one for source, one for destination)
                stock_item.physical_quantity += command.quantity  # quantity is negative for transfer out
                stock_item.last_movement_at = movement.created_at
                
                # If destination location provided, update destination stock item
                if command.location_to_id:
                    dest_stock_item = session.query(StockItem).filter(
                        StockItem.product_id == command.product_id,
                        StockItem.location_id == command.location_to_id,
                        StockItem.variant_id == command.variant_id
                    ).first()
                    
                    if dest_stock_item:
                        # Increase at destination (quantity is positive for transfer in)
                        dest_stock_item.physical_quantity += abs(command.quantity)
                        dest_stock_item.last_movement_at = movement.created_at
                    else:
                        # Create destination stock item if it doesn't exist
                        dest_stock_item = StockItem.create(
                            product_id=command.product_id,
                            location_id=command.location_to_id,
                            physical_quantity=abs(command.quantity),
                            variant_id=command.variant_id
                        )
                        session.add(dest_stock_item)
            elif command.movement_type == 'adjustment':
                stock_item.adjust(command.quantity, command.reason)
            
            session.commit()
            return movement


class ReserveStockHandler(CommandHandler):
    def handle(self, command: ReserveStockCommand) -> StockItem:
        with get_session() as session:
            # Use row-level locking to prevent race conditions
            stock_item = session.query(StockItem).filter(
                StockItem.product_id == command.product_id,
                StockItem.location_id == command.location_id,
                StockItem.variant_id == command.variant_id
            ).with_for_update().first()
            
            if not stock_item:
                raise ValueError(f"Stock item not found for product {command.product_id} at location {command.location_id}")
            
            # Use domain method for business logic
            stock_item.reserve(command.quantity)
            
            session.commit()
            return stock_item


class ReleaseStockHandler(CommandHandler):
    def handle(self, command: ReleaseStockCommand) -> StockItem:
        with get_session() as session:
            # Use row-level locking to prevent race conditions
            stock_item = session.query(StockItem).filter(
                StockItem.product_id == command.product_id,
                StockItem.location_id == command.location_id,
                StockItem.variant_id == command.variant_id
            ).with_for_update().first()
            
            if not stock_item:
                raise ValueError(f"Stock item not found for product {command.product_id} at location {command.location_id}")
            
            # Use domain method for business logic
            stock_item.release(command.quantity)
            
            session.commit()
            return stock_item


class AdjustStockHandler(CommandHandler):
    def handle(self, command: AdjustStockCommand) -> StockItem:
        with get_session() as session:
            # Use row-level locking to prevent race conditions
            stock_item = session.query(StockItem).filter(
                StockItem.product_id == command.product_id,
                StockItem.location_id == command.location_id,
                StockItem.variant_id == command.variant_id
            ).with_for_update().first()
            
            if not stock_item:
                raise ValueError(f"Stock item not found for product {command.product_id} at location {command.location_id}")
            
            # Use domain method for business logic
            stock_item.adjust(command.quantity, command.reason)
            
            # Create movement record for audit trail
            movement = StockMovement.create(
                stock_item_id=stock_item.id,
                product_id=command.product_id,
                quantity=command.quantity,
                movement_type='adjustment',
                user_id=command.user_id,
                location_to_id=command.location_id,
                variant_id=command.variant_id,
                reason=command.reason
            )
            session.add(movement)
            
            session.commit()
            return stock_item

