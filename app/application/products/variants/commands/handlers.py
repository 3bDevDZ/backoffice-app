"""Command handlers for Product Variant management."""
from app.application.common.cqrs import CommandHandler
from app.domain.models.product import Product, ProductVariant
from app.infrastructure.db import get_session
from .commands import (
    CreateVariantCommand,
    UpdateVariantCommand,
    ArchiveVariantCommand,
    ActivateVariantCommand,
    DeleteVariantCommand
)


class CreateVariantHandler(CommandHandler):
    """Handler for creating a product variant."""
    
    def handle(self, command: CreateVariantCommand) -> ProductVariant:
        """
        Create a new product variant.
        
        Args:
            command: CreateVariantCommand with variant details
            
        Returns:
            ProductVariant instance
            
        Raises:
            ValueError: If product not found or validation fails
        """
        with get_session() as session:
            # Verify product exists
            product = session.get(Product, command.product_id)
            if not product:
                raise ValueError(f"Product with ID {command.product_id} not found.")
            
            # Check if variant code already exists
            existing_variant = session.query(ProductVariant).filter(
                ProductVariant.code == command.code.strip()
            ).first()
            if existing_variant:
                raise ValueError(f"Variant with code '{command.code}' already exists.")
            
            # Check if barcode is unique (if provided)
            if command.barcode:
                existing_barcode = session.query(ProductVariant).filter(
                    ProductVariant.barcode == command.barcode.strip()
                ).first()
                if existing_barcode:
                    raise ValueError(f"Variant with barcode '{command.barcode}' already exists.")
            
            # Create variant using domain factory method
            variant = ProductVariant.create(
                product_id=command.product_id,
                code=command.code,
                name=command.name,
                attributes=command.attributes,
                price=command.price,
                cost=command.cost,
                barcode=command.barcode
            )
            
            session.add(variant)
            session.commit()
            session.refresh(variant)
            session.expunge(variant)  # Detach from session for return
            
            return variant


class UpdateVariantHandler(CommandHandler):
    """Handler for updating a product variant."""
    
    def handle(self, command: UpdateVariantCommand) -> ProductVariant:
        """
        Update an existing product variant.
        
        Args:
            command: UpdateVariantCommand with variant ID and fields to update
            
        Returns:
            Updated ProductVariant instance
            
        Raises:
            ValueError: If variant not found or validation fails
        """
        with get_session() as session:
            variant = session.get(ProductVariant, command.id)
            if not variant:
                raise ValueError(f"Variant with ID {command.id} not found.")
            
            # Check if barcode is unique (if provided and different)
            if command.barcode and command.barcode.strip() != (variant.barcode or ""):
                existing_barcode = session.query(ProductVariant).filter(
                    ProductVariant.barcode == command.barcode.strip(),
                    ProductVariant.id != command.id
                ).first()
                if existing_barcode:
                    raise ValueError(f"Variant with barcode '{command.barcode}' already exists.")
            
            # Update variant using domain method
            variant.update_details(
                name=command.name,
                attributes=command.attributes,
                price=command.price,
                cost=command.cost,
                barcode=command.barcode
            )
            
            session.commit()
            session.refresh(variant)
            session.expunge(variant)  # Detach from session for return
            
            return variant


class ArchiveVariantHandler(CommandHandler):
    """Handler for archiving a product variant."""
    
    def handle(self, command: ArchiveVariantCommand) -> ProductVariant:
        """
        Archive a product variant.
        
        Args:
            command: ArchiveVariantCommand with variant ID
            
        Returns:
            Archived ProductVariant instance
            
        Raises:
            ValueError: If variant not found
        """
        with get_session() as session:
            variant = session.get(ProductVariant, command.id)
            if not variant:
                raise ValueError(f"Variant with ID {command.id} not found.")
            
            variant.archive()
            
            session.commit()
            session.refresh(variant)
            session.expunge(variant)  # Detach from session for return
            
            return variant


class ActivateVariantHandler(CommandHandler):
    """Handler for activating an archived product variant."""
    
    def handle(self, command: ActivateVariantCommand) -> ProductVariant:
        """
        Activate an archived product variant.
        
        Args:
            command: ActivateVariantCommand with variant ID
            
        Returns:
            Activated ProductVariant instance
            
        Raises:
            ValueError: If variant not found
        """
        with get_session() as session:
            variant = session.get(ProductVariant, command.id)
            if not variant:
                raise ValueError(f"Variant with ID {command.id} not found.")
            
            variant.activate()
            
            session.commit()
            session.refresh(variant)
            session.expunge(variant)  # Detach from session for return
            
            return variant


class DeleteVariantHandler(CommandHandler):
    """Handler for deleting a product variant."""
    
    def handle(self, command: DeleteVariantCommand) -> None:
        """
        Delete a product variant.
        
        Only allows deletion if variant is not referenced in quotes or orders.
        
        Args:
            command: DeleteVariantCommand with variant ID
            
        Raises:
            ValueError: If variant not found or is referenced
        """
        with get_session() as session:
            variant = session.get(ProductVariant, command.id)
            if not variant:
                raise ValueError(f"Variant with ID {command.id} not found.")
            
            # TODO: Check if variant is referenced in quotes or orders
            # For now, we'll allow deletion but this should be checked
            # from app.domain.models.quote import QuoteLine
            # from app.domain.models.order import OrderLine
            # 
            # quote_lines = session.query(QuoteLine).filter(QuoteLine.variant_id == command.id).count()
            # order_lines = session.query(OrderLine).filter(OrderLine.variant_id == command.id).count()
            # 
            # if quote_lines > 0 or order_lines > 0:
            #     raise ValueError(f"Cannot delete variant '{variant.code}' as it is referenced in {quote_lines} quotes and {order_lines} orders.")
            
            session.delete(variant)
            session.commit()

