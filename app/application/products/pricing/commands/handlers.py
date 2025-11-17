"""Command handlers for Price List management."""
from datetime import datetime
from decimal import Decimal
from app.application.common.cqrs import CommandHandler
from app.domain.models.product import PriceList, ProductPriceList, Product, ProductVolumePricing, ProductPromotionalPrice
from app.infrastructure.db import get_session
from .commands import (
    CreatePriceListCommand,
    UpdatePriceListCommand,
    DeletePriceListCommand,
    AddProductToPriceListCommand,
    UpdateProductPriceInListCommand,
    RemoveProductFromPriceListCommand,
    CreateVolumePricingCommand,
    UpdateVolumePricingCommand,
    DeleteVolumePricingCommand,
    CreatePromotionalPriceCommand,
    UpdatePromotionalPriceCommand,
    DeletePromotionalPriceCommand
)
from sqlalchemy.exc import IntegrityError


# PriceList Handlers
class CreatePriceListHandler(CommandHandler):
    """Handler for creating a price list."""
    
    def handle(self, command: CreatePriceListCommand) -> PriceList:
        """
        Create a new price list.
        
        Args:
            command: CreatePriceListCommand with price list details
            
        Returns:
            PriceList instance
            
        Raises:
            ValueError: If validation fails
        """
        with get_session() as session:
            if not command.name or not command.name.strip():
                raise ValueError("Price list name is required.")
            
            # Check if name already exists
            existing = session.query(PriceList).filter(
                PriceList.name == command.name.strip()
            ).first()
            if existing:
                raise ValueError(f"Price list with name '{command.name}' already exists.")
            
            price_list = PriceList(
                name=command.name.strip(),
                description=command.description.strip() if command.description else None,
                is_active=command.is_active
            )
            
            session.add(price_list)
            try:
                session.commit()
                session.refresh(price_list)
                session.expunge(price_list)
                return price_list
            except IntegrityError:
                session.rollback()
                raise ValueError("A price list with this name already exists.")


class UpdatePriceListHandler(CommandHandler):
    """Handler for updating a price list."""
    
    def handle(self, command: UpdatePriceListCommand) -> PriceList:
        """
        Update an existing price list.
        
        Args:
            command: UpdatePriceListCommand with price list ID and fields to update
            
        Returns:
            PriceList instance
            
        Raises:
            ValueError: If price list not found or validation fails
        """
        with get_session() as session:
            price_list = session.get(PriceList, command.id)
            if not price_list:
                raise ValueError(f"Price list with ID {command.id} not found.")
            
            # Check if new name conflicts with existing price list
            if command.name and command.name.strip() != price_list.name:
                existing = session.query(PriceList).filter(
                    PriceList.name == command.name.strip(),
                    PriceList.id != command.id
                ).first()
                if existing:
                    raise ValueError(f"Price list with name '{command.name}' already exists.")
            
            # Update fields
            if command.name is not None:
                price_list.name = command.name.strip()
            if command.description is not None:
                price_list.description = command.description.strip() if command.description else None
            if command.is_active is not None:
                price_list.is_active = command.is_active
            
            try:
                session.commit()
                session.refresh(price_list)
                session.expunge(price_list)
                return price_list
            except IntegrityError:
                session.rollback()
                raise ValueError("A price list with this name already exists.")


class DeletePriceListHandler(CommandHandler):
    """Handler for deleting a price list."""
    
    def handle(self, command: DeletePriceListCommand) -> None:
        """
        Delete a price list.
        
        Args:
            command: DeletePriceListCommand with price list ID
            
        Raises:
            ValueError: If price list not found or is referenced by customers
        """
        with get_session() as session:
            price_list = session.get(PriceList, command.id)
            if not price_list:
                raise ValueError(f"Price list with ID {command.id} not found.")
            
            # Check if price list is referenced by customers
            from app.domain.models.customer import CommercialConditions
            referenced = session.query(CommercialConditions).filter(
                CommercialConditions.price_list_id == command.id
            ).first()
            if referenced:
                raise ValueError(f"Cannot delete price list '{price_list.name}': it is assigned to at least one customer.")
            
            session.delete(price_list)
            session.commit()


# ProductPriceList Handlers
class AddProductToPriceListHandler(CommandHandler):
    """Handler for adding a product to a price list."""
    
    def handle(self, command: AddProductToPriceListCommand) -> ProductPriceList:
        """
        Add a product to a price list with a specific price.
        
        Args:
            command: AddProductToPriceListCommand with price_list_id, product_id, and price
            
        Returns:
            ProductPriceList instance
            
        Raises:
            ValueError: If price list or product not found, or product already in list
        """
        with get_session() as session:
            # Verify price list exists
            price_list = session.get(PriceList, command.price_list_id)
            if not price_list:
                raise ValueError(f"Price list with ID {command.price_list_id} not found.")
            
            # Verify product exists
            product = session.get(Product, command.product_id)
            if not product:
                raise ValueError(f"Product with ID {command.product_id} not found.")
            
            # Check if product is already in this price list
            existing = session.query(ProductPriceList).filter(
                ProductPriceList.price_list_id == command.price_list_id,
                ProductPriceList.product_id == command.product_id
            ).first()
            if existing:
                raise ValueError(f"Product '{product.name}' is already in price list '{price_list.name}'. Use UpdateProductPriceInListCommand instead.")
            
            if command.price < 0:
                raise ValueError("Price must be non-negative.")
            
            product_price_list = ProductPriceList(
                price_list_id=command.price_list_id,
                product_id=command.product_id,
                price=command.price
            )
            
            session.add(product_price_list)
            try:
                session.commit()
                session.refresh(product_price_list)
                session.expunge(product_price_list)
                return product_price_list
            except IntegrityError:
                session.rollback()
                raise ValueError("Product is already in this price list.")


class UpdateProductPriceInListHandler(CommandHandler):
    """Handler for updating a product's price in a price list."""
    
    def handle(self, command: UpdateProductPriceInListCommand) -> ProductPriceList:
        """
        Update a product's price in a price list.
        
        Args:
            command: UpdateProductPriceInListCommand with price_list_id, product_id, and new price
            
        Returns:
            ProductPriceList instance
            
        Raises:
            ValueError: If price list or product not found, or product not in list
        """
        with get_session() as session:
            # Verify price list exists
            price_list = session.get(PriceList, command.price_list_id)
            if not price_list:
                raise ValueError(f"Price list with ID {command.price_list_id} not found.")
            
            # Verify product exists
            product = session.get(Product, command.product_id)
            if not product:
                raise ValueError(f"Product with ID {command.product_id} not found.")
            
            # Find existing entry
            product_price_list = session.query(ProductPriceList).filter(
                ProductPriceList.price_list_id == command.price_list_id,
                ProductPriceList.product_id == command.product_id
            ).first()
            
            if not product_price_list:
                raise ValueError(f"Product '{product.name}' is not in price list '{price_list.name}'. Use AddProductToPriceListCommand instead.")
            
            if command.price < 0:
                raise ValueError("Price must be non-negative.")
            
            product_price_list.price = command.price
            
            try:
                session.commit()
                session.refresh(product_price_list)
                session.expunge(product_price_list)
                return product_price_list
            except IntegrityError:
                session.rollback()
                raise ValueError("Error updating product price in price list.")


class RemoveProductFromPriceListHandler(CommandHandler):
    """Handler for removing a product from a price list."""
    
    def handle(self, command: RemoveProductFromPriceListCommand) -> None:
        """
        Remove a product from a price list.
        
        Args:
            command: RemoveProductFromPriceListCommand with price_list_id and product_id
            
        Raises:
            ValueError: If price list or product not found, or product not in list
        """
        with get_session() as session:
            # Verify price list exists
            price_list = session.get(PriceList, command.price_list_id)
            if not price_list:
                raise ValueError(f"Price list with ID {command.price_list_id} not found.")
            
            # Find existing entry
            product_price_list = session.query(ProductPriceList).filter(
                ProductPriceList.price_list_id == command.price_list_id,
                ProductPriceList.product_id == command.product_id
            ).first()
            
            if not product_price_list:
                raise ValueError(f"Product is not in price list '{price_list.name}'.")
            
            session.delete(product_price_list)
            session.commit()


# ProductVolumePricing Handlers
class CreateVolumePricingHandler(CommandHandler):
    """Handler for creating a volume pricing tier."""
    
    def handle(self, command: CreateVolumePricingCommand) -> ProductVolumePricing:
        """
        Create a new volume pricing tier for a product.
        
        Args:
            command: CreateVolumePricingCommand with product_id, min_quantity, max_quantity, price
            
        Returns:
            ProductVolumePricing instance
            
        Raises:
            ValueError: If product not found or validation fails
        """
        with get_session() as session:
            # Verify product exists
            product = session.get(Product, command.product_id)
            if not product:
                raise ValueError(f"Product with ID {command.product_id} not found.")
            
            if command.min_quantity < 0:
                raise ValueError("Minimum quantity must be non-negative.")
            if command.max_quantity is not None and command.max_quantity < command.min_quantity:
                raise ValueError("Maximum quantity must be greater than or equal to minimum quantity.")
            if command.price < 0:
                raise ValueError("Price must be non-negative.")
            
            # Check for overlapping quantity ranges
            existing_tiers = session.query(ProductVolumePricing).filter(
                ProductVolumePricing.product_id == command.product_id
            ).all()
            
            for tier in existing_tiers:
                # Check if ranges overlap
                tier_max = tier.max_quantity if tier.max_quantity is not None else float('inf')
                command_max = float(command.max_quantity) if command.max_quantity is not None else float('inf')
                
                if not (command_max < tier.min_quantity or command.min_quantity > tier_max):
                    raise ValueError(f"Quantity range overlaps with existing tier (min: {tier.min_quantity}, max: {tier.max_quantity})")
            
            volume_pricing = ProductVolumePricing(
                product_id=command.product_id,
                min_quantity=command.min_quantity,
                max_quantity=command.max_quantity,
                price=command.price
            )
            
            session.add(volume_pricing)
            try:
                session.commit()
                session.refresh(volume_pricing)
                session.expunge(volume_pricing)
                return volume_pricing
            except IntegrityError:
                session.rollback()
                raise ValueError("Error creating volume pricing tier.")


class UpdateVolumePricingHandler(CommandHandler):
    """Handler for updating a volume pricing tier."""
    
    def handle(self, command: UpdateVolumePricingCommand) -> ProductVolumePricing:
        """
        Update an existing volume pricing tier.
        
        Args:
            command: UpdateVolumePricingCommand with tier ID and fields to update
            
        Returns:
            ProductVolumePricing instance
            
        Raises:
            ValueError: If tier not found or validation fails
        """
        with get_session() as session:
            volume_pricing = session.get(ProductVolumePricing, command.id)
            if not volume_pricing:
                raise ValueError(f"Volume pricing tier with ID {command.id} not found.")
            
            # Update fields
            if command.min_quantity is not None:
                if command.min_quantity < 0:
                    raise ValueError("Minimum quantity must be non-negative.")
                volume_pricing.min_quantity = command.min_quantity
            
            if command.max_quantity is not None:
                if command.max_quantity < volume_pricing.min_quantity:
                    raise ValueError("Maximum quantity must be greater than or equal to minimum quantity.")
                volume_pricing.max_quantity = command.max_quantity
            
            if command.price is not None:
                if command.price < 0:
                    raise ValueError("Price must be non-negative.")
                volume_pricing.price = command.price
            
            # Check for overlapping quantity ranges (excluding current tier)
            existing_tiers = session.query(ProductVolumePricing).filter(
                ProductVolumePricing.product_id == volume_pricing.product_id,
                ProductVolumePricing.id != command.id
            ).all()
            
            for tier in existing_tiers:
                tier_max = tier.max_quantity if tier.max_quantity is not None else float('inf')
                updated_max = float(volume_pricing.max_quantity) if volume_pricing.max_quantity is not None else float('inf')
                
                if not (updated_max < tier.min_quantity or volume_pricing.min_quantity > tier_max):
                    raise ValueError(f"Quantity range overlaps with existing tier (min: {tier.min_quantity}, max: {tier.max_quantity})")
            
            try:
                session.commit()
                session.refresh(volume_pricing)
                session.expunge(volume_pricing)
                return volume_pricing
            except IntegrityError:
                session.rollback()
                raise ValueError("Error updating volume pricing tier.")


class DeleteVolumePricingHandler(CommandHandler):
    """Handler for deleting a volume pricing tier."""
    
    def handle(self, command: DeleteVolumePricingCommand) -> None:
        """
        Delete a volume pricing tier.
        
        Args:
            command: DeleteVolumePricingCommand with tier ID
            
        Raises:
            ValueError: If tier not found
        """
        with get_session() as session:
            volume_pricing = session.get(ProductVolumePricing, command.id)
            if not volume_pricing:
                raise ValueError(f"Volume pricing tier with ID {command.id} not found.")
            
            session.delete(volume_pricing)
            session.commit()


# ProductPromotionalPrice Handlers
class CreatePromotionalPriceHandler(CommandHandler):
    """Handler for creating a promotional price."""
    
    def handle(self, command: CreatePromotionalPriceCommand) -> ProductPromotionalPrice:
        from app.application.products.pricing.commands.commands import CreatePromotionalPriceCommand
        
        with get_session() as session:
            product = session.get(Product, command.product_id)
            if not product:
                raise ValueError(f"Product with ID {command.product_id} not found.")
            
            # Parse datetime strings
            try:
                start_date = datetime.fromisoformat(command.start_date.replace('Z', '+00:00'))
                end_date = datetime.fromisoformat(command.end_date.replace('Z', '+00:00'))
            except (ValueError, AttributeError) as e:
                raise ValueError(f"Invalid date format: {e}")
            
            # Validate dates
            if start_date >= end_date:
                raise ValueError("Start date must be before end date.")
            
            if command.price < 0:
                raise ValueError("Price must be non-negative.")
            
            # Check for overlapping promotions (optional - can have multiple active promotions)
            # We'll allow multiple promotions but warn if they overlap
            
            promotional_price = ProductPromotionalPrice(
                product_id=command.product_id,
                price=command.price,
                start_date=start_date,
                end_date=end_date,
                description=command.description,
                is_active=True,
                created_by=command.created_by
            )
            
            session.add(promotional_price)
            try:
                session.commit()
                session.refresh(promotional_price)
                session.expunge(promotional_price)
                return promotional_price
            except IntegrityError:
                session.rollback()
                raise ValueError("Error creating promotional price.")


class UpdatePromotionalPriceHandler(CommandHandler):
    """Handler for updating a promotional price."""
    
    def handle(self, command: UpdatePromotionalPriceCommand) -> ProductPromotionalPrice:
        from app.application.products.pricing.commands.commands import UpdatePromotionalPriceCommand
        
        with get_session() as session:
            promotional_price = session.get(ProductPromotionalPrice, command.id)
            if not promotional_price:
                raise ValueError(f"Promotional price with ID {command.id} not found.")
            
            if command.price is not None:
                if command.price < 0:
                    raise ValueError("Price must be non-negative.")
                promotional_price.price = command.price
            
            if command.start_date is not None:
                try:
                    start_date = datetime.fromisoformat(command.start_date.replace('Z', '+00:00'))
                    promotional_price.start_date = start_date
                except (ValueError, AttributeError) as e:
                    raise ValueError(f"Invalid start date format: {e}")
            
            if command.end_date is not None:
                try:
                    end_date = datetime.fromisoformat(command.end_date.replace('Z', '+00:00'))
                    promotional_price.end_date = end_date
                except (ValueError, AttributeError) as e:
                    raise ValueError(f"Invalid end date format: {e}")
            
            if command.description is not None:
                promotional_price.description = command.description
            
            if command.is_active is not None:
                promotional_price.is_active = command.is_active
            
            # Validate dates after update
            if promotional_price.start_date >= promotional_price.end_date:
                raise ValueError("Start date must be before end date.")
            
            try:
                session.commit()
                session.refresh(promotional_price)
                session.expunge(promotional_price)
                return promotional_price
            except IntegrityError:
                session.rollback()
                raise ValueError("Error updating promotional price.")


class DeletePromotionalPriceHandler(CommandHandler):
    """Handler for deleting a promotional price."""
    
    def handle(self, command: DeletePromotionalPriceCommand) -> None:
        from app.application.products.pricing.commands.commands import DeletePromotionalPriceCommand
        
        with get_session() as session:
            promotional_price = session.get(ProductPromotionalPrice, command.id)
            if not promotional_price:
                raise ValueError(f"Promotional price with ID {command.id} not found.")
            
            session.delete(promotional_price)
            session.commit()

