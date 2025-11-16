"""Command handlers for order management."""
from decimal import Decimal
from app.application.common.cqrs import CommandHandler
from app.domain.models.order import Order, OrderLine
from app.domain.models.quote import Quote
from app.infrastructure.db import get_session
from app.services.pricing_service import PricingService
from .commands import (
    CreateOrderCommand, UpdateOrderCommand, ConfirmOrderCommand,
    CancelOrderCommand, UpdateOrderStatusCommand,
    AddOrderLineCommand, UpdateOrderLineCommand, RemoveOrderLineCommand
)


class CreateOrderHandler(CommandHandler):
    """Handler for creating a new order."""
    
    def handle(self, command: CreateOrderCommand) -> int:
        """
        Create a new order.
        
        Args:
            command: CreateOrderCommand with order details
            
        Returns:
            Order ID (int) to avoid detached instance issues
        """
        with get_session() as session:
            # If order is created from a quote, validate and copy lines
            if command.quote_id:
                quote = session.get(Quote, command.quote_id)
                if not quote:
                    raise ValueError(f"Quote with ID {command.quote_id} not found.")
                if quote.status != "accepted":
                    raise ValueError(
                        f"Cannot create order from quote '{quote.number}'. "
                        f"Quote must be in 'accepted' status (current: '{quote.status}')."
                    )
            
            # Create order
            order = Order.create(
                customer_id=command.customer_id,
                created_by=command.created_by,
                quote_id=command.quote_id,
                delivery_address_id=command.delivery_address_id,
                delivery_date_requested=command.delivery_date_requested,
                delivery_instructions=command.delivery_instructions,
                discount_percent=command.discount_percent,
                notes=command.notes
            )
            
            session.add(order)
            session.flush()  # Get order.id for domain event
            
            # Update domain event with order ID
            events = order.get_domain_events()
            for event in events:
                if hasattr(event, 'order_id'):
                    event.order_id = order.id
            
            # NOTE: Lines from quote are NOT automatically copied here
            # They will be added from the form data in save_order() route
            # This prevents duplication when creating order from quote via form
            
            # Calculate totals
            order.calculate_totals()
            
            order_id = order.id
            session.commit()
            session.refresh(order)
            
            return order_id


class UpdateOrderHandler(CommandHandler):
    """Handler for updating an existing order."""
    
    def handle(self, command: UpdateOrderCommand) -> int:
        """
        Update an existing order.
        
        Only orders in 'draft' status can be updated.
        
        Args:
            command: UpdateOrderCommand with order updates
            
        Returns:
            Order ID (int)
        """
        with get_session() as session:
            order = session.get(Order, command.order_id)
            if not order:
                raise ValueError(f"Order with ID {command.order_id} not found.")
            
            if order.status != "draft":
                raise ValueError(
                    f"Cannot update order '{order.number}' in status '{order.status}'. "
                    f"Order must be in 'draft' status."
                )
            
            # Update fields if provided
            if command.delivery_address_id is not None:
                order.delivery_address_id = command.delivery_address_id
            
            if command.delivery_date_requested is not None:
                order.delivery_date_requested = command.delivery_date_requested
            
            if command.delivery_date_promised is not None:
                order.delivery_date_promised = command.delivery_date_promised
            
            if command.delivery_instructions is not None:
                order.delivery_instructions = command.delivery_instructions
            
            if command.notes is not None:
                order.notes = command.notes
            
            if command.discount_percent is not None:
                order.discount_percent = command.discount_percent
                # Recalculate totals when discount changes
                order.calculate_totals()
            
            order_id = order.id
            session.commit()
            session.refresh(order)
            
            return order_id


class ConfirmOrderHandler(CommandHandler):
    """Handler for confirming an order."""
    
    def handle(self, command: ConfirmOrderCommand) -> int:
        """
        Confirm an order.
        
        This will:
        - Validate stock availability
        - Validate customer credit limit
        - Change status to 'confirmed'
        - Trigger OrderConfirmedDomainEvent (which reserves stock)
        
        Args:
            command: ConfirmOrderCommand with order_id and confirmed_by
            
        Returns:
            Order ID (int)
            
        Raises:
            ValueError: If order not found, validation fails, or order cannot be confirmed
        """
        with get_session() as session:
            order = session.get(Order, command.order_id)
            if not order:
                raise ValueError(f"Order with ID {command.order_id} not found.")
            
            # Pre-validate before attempting confirmation
            if order.status != "draft":
                raise ValueError(
                    f"Cannot confirm order '{order.number}' in status '{order.status}'. "
                    f"Order must be in 'draft' status."
                )
            
            if not order.lines or len(order.lines) == 0:
                raise ValueError(f"Cannot confirm order '{order.number}' without lines.")
            
            try:
                # Confirm order (validates stock and credit, raises domain event)
                order.confirm(command.confirmed_by)
                
                order_id = order.id
                session.commit()
                session.refresh(order)
                
                return order_id
            except ValueError as e:
                # Rollback on validation error
                session.rollback()
                raise
            except Exception as e:
                # Rollback on any other error
                session.rollback()
                raise ValueError(f"Failed to confirm order '{order.number}': {str(e)}")


class CancelOrderHandler(CommandHandler):
    """Handler for canceling an order."""
    
    def handle(self, command: CancelOrderCommand) -> int:
        """
        Cancel an order.
        
        This will:
        - Change status to 'canceled'
        - Trigger OrderCanceledDomainEvent (which releases reserved stock)
        
        Args:
            command: CancelOrderCommand with order_id
            
        Returns:
            Order ID (int)
        """
        with get_session() as session:
            order = session.get(Order, command.order_id)
            if not order:
                raise ValueError(f"Order with ID {command.order_id} not found.")
            
            # Cancel order (raises domain event for stock release)
            order.cancel()
            
            order_id = order.id
            session.commit()
            session.refresh(order)
            
            return order_id


class UpdateOrderStatusHandler(CommandHandler):
    """Handler for updating order status."""
    
    def handle(self, command: UpdateOrderStatusCommand) -> int:
        """
        Update order status using the workflow.
        
        This handler uses the appropriate domain methods for status transitions:
        - mark_ready() for in_preparation -> ready (raises OrderReadyDomainEvent)
        - ship() for ready -> shipped
        - deliver() for shipped -> delivered
        - update_status() for other transitions
        
        Args:
            command: UpdateOrderStatusCommand with order_id and new_status
            
        Returns:
            Order ID (int)
        """
        with get_session() as session:
            order = session.get(Order, command.order_id)
            if not order:
                raise ValueError(f"Order with ID {command.order_id} not found.")
            
            # Use domain methods for specific transitions to trigger events
            if command.new_status == "ready" and order.status == "in_preparation":
                order.mark_ready()  # Raises OrderReadyDomainEvent
            elif command.new_status == "shipped" and order.status == "ready":
                user_id = command.updated_by if command.updated_by else None
                if not user_id:
                    # Fallback: try to get from current user context
                    from app.security.auth import get_current_user
                    current_user = get_current_user()
                    user_id = current_user.id if current_user else None
                if not user_id:
                    raise ValueError("User ID is required to ship an order")
                order.ship(user_id)  # Raises OrderShippedDomainEvent
            elif command.new_status == "delivered":
                # Use update_status for delivered transition (validates workflow and sets delivery_date_actual)
                # The deliver() method is for partial deliveries, not for marking entire order as delivered
                if order.status != "shipped":
                    raise ValueError(f"Cannot mark order as delivered from status '{order.status}'. Order must be 'shipped'.")
                order.update_status("delivered")
            else:
                # Use update_status for other transitions (validates workflow)
                order.update_status(command.new_status)
            
            order_id = order.id
            session.commit()
            session.refresh(order)
            
            return order_id


class AddOrderLineHandler(CommandHandler):
    """Handler for adding a line to an order."""
    
    def handle(self, command: AddOrderLineCommand) -> int:
        """
        Add a line to an order.
        
        Only orders in 'draft' status can have lines added.
        
        Args:
            command: AddOrderLineCommand with order and line details
            
        Returns:
            Order ID (int)
        """
        with get_session() as session:
            order = session.get(Order, command.order_id)
            if not order:
                raise ValueError(f"Order with ID {command.order_id} not found.")
            
            # Validate variant belongs to product if variant_id is provided
            if command.variant_id:
                from app.domain.models.product import ProductVariant
                variant = session.get(ProductVariant, command.variant_id)
                if not variant:
                    raise ValueError(f"Variant with ID {command.variant_id} not found.")
                if variant.product_id != command.product_id:
                    raise ValueError(f"Variant {command.variant_id} does not belong to product {command.product_id}.")
            
            # Use pricing service to get customer price if unit_price is 0
            unit_price = command.unit_price
            discount_percent = command.discount_percent
            
            # Check if variant has price override
            if command.variant_id:
                from app.domain.models.product import ProductVariant
                variant = session.get(ProductVariant, command.variant_id)
                if variant and variant.price is not None:
                    # Use variant price as base price
                    unit_price = variant.price
                    # Still apply customer pricing rules (discounts, price lists, etc.)
                    pricing_service = PricingService(session)
                    try:
                        price_result = pricing_service.get_price_for_customer(
                            product_id=command.product_id,
                            customer_id=order.customer_id,
                            quantity=command.quantity
                        )
                        # For variants with price override, we use variant price but still apply customer discounts
                        if price_result.source == 'customer_discount' and price_result.applied_discount_percent > 0:
                            # Keep variant price as base, apply discount
                            if discount_percent == 0:
                                discount_percent = price_result.applied_discount_percent
                        # Note: Price lists, promotional prices, and volume pricing don't apply to variant prices
                    except ValueError:
                        pass  # Use variant price as fallback
            
            if unit_price == 0 or unit_price is None:
                pricing_service = PricingService(session)
                try:
                    price_result = pricing_service.get_price_for_customer(
                        product_id=command.product_id,
                        customer_id=order.customer_id,
                        quantity=command.quantity
                    )
                    # IMPORTANT: If the price comes from a customer_discount, the discount is already
                    # included in final_price. We should use the BASE price as unit_price and apply
                    # the discount_percent separately. Otherwise, use final_price as unit_price.
                    if price_result.source == 'customer_discount' and price_result.applied_discount_percent > 0:
                        # Use base price and apply discount separately
                        unit_price = price_result.base_price
                        # Only apply discount if not already set
                        if discount_percent == 0:
                            discount_percent = price_result.applied_discount_percent
                    else:
                        # For price_list, promotional_price, volume_pricing, or base price:
                        # Use final_price as unit_price, no discount
                        unit_price = price_result.final_price
                        # Don't apply discount for non-customer-discount sources
                        if discount_percent == 0:
                            discount_percent = Decimal(0)
                except ValueError:
                    # Fallback to product base price
                    from app.domain.models.product import Product
                    product = session.get(Product, command.product_id)
                    if product:
                        unit_price = product.price
            
            # Add line through aggregate root
            line = order.add_line(
                product_id=command.product_id,
                quantity=command.quantity,
                unit_price=unit_price,
                variant_id=command.variant_id,
                discount_percent=discount_percent,
                tax_rate=command.tax_rate
            )
            
            session.add(line)
            order.calculate_totals()
            
            order_id = order.id
            session.commit()
            session.refresh(order)
            
            return order_id


class UpdateOrderLineHandler(CommandHandler):
    """Handler for updating an order line."""
    
    def handle(self, command: UpdateOrderLineCommand) -> int:
        """
        Update an order line.
        
        Only orders in 'draft' status can have lines updated.
        
        Args:
            command: UpdateOrderLineCommand with order_id, line_id, and updates
            
        Returns:
            Order ID (int)
        """
        with get_session() as session:
            order = session.get(Order, command.order_id)
            if not order:
                raise ValueError(f"Order with ID {command.order_id} not found.")
            
            if order.status != "draft":
                raise ValueError(
                    f"Cannot update line in order '{order.number}' in status '{order.status}'. "
                    f"Order must be in 'draft' status."
                )
            
            # Find the line
            line = next((l for l in order.lines if l.id == command.line_id), None)
            if not line:
                raise ValueError(f"Order line with ID {command.line_id} not found in order {command.order_id}.")
            
            # Update fields if provided
            if command.quantity is not None:
                line.quantity = command.quantity
            
            if command.unit_price is not None:
                line.unit_price = command.unit_price
            
            if command.discount_percent is not None:
                line.discount_percent = command.discount_percent
            
            if command.tax_rate is not None:
                line.tax_rate = command.tax_rate
            
            # Recalculate line totals
            line.calculate_totals()
            
            # Recalculate order totals
            order.calculate_totals()
            
            order_id = order.id
            session.commit()
            session.refresh(order)
            
            return order_id


class RemoveOrderLineHandler(CommandHandler):
    """Handler for removing a line from an order."""
    
    def handle(self, command: RemoveOrderLineCommand) -> int:
        """
        Remove a line from an order.
        
        Only orders in 'draft' status can have lines removed.
        
        Args:
            command: RemoveOrderLineCommand with order_id and line_id
            
        Returns:
            Order ID (int)
        """
        with get_session() as session:
            order = session.get(Order, command.order_id)
            if not order:
                raise ValueError(f"Order with ID {command.order_id} not found.")
            
            if order.status != "draft":
                raise ValueError(
                    f"Cannot remove line from order '{order.number}' in status '{order.status}'. "
                    f"Order must be in 'draft' status."
                )
            
            # Find and remove the line
            line = next((l for l in order.lines if l.id == command.line_id), None)
            if not line:
                raise ValueError(f"Order line with ID {command.line_id} not found in order {command.order_id}.")
            
            session.delete(line)
            order.lines.remove(line)
            
            # Recalculate order totals
            order.calculate_totals()
            
            order_id = order.id
            session.commit()
            session.refresh(order)
            
            return order_id

