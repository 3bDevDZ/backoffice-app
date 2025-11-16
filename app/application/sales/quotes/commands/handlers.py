"""Command handlers for quote management."""
from decimal import Decimal
from app.application.common.cqrs import CommandHandler
from app.domain.models.quote import Quote, QuoteLine, QuoteVersion, QuoteStatus
from app.infrastructure.db import get_session
from app.services.pricing_service import PricingService
from .commands import (
    CreateQuoteCommand, UpdateQuoteCommand, AddQuoteLineCommand,
    UpdateQuoteLineCommand, RemoveQuoteLineCommand,
    SendQuoteCommand, AcceptQuoteCommand, RejectQuoteCommand,
    CancelQuoteCommand, DeleteQuoteCommand, ConvertQuoteToOrderCommand
)


class CreateQuoteHandler(CommandHandler):
    def handle(self, command: CreateQuoteCommand) -> Quote:
        with get_session() as session:
            # Use Pricing Service to get customer discount if not provided
            discount_percent = command.discount_percent
            if discount_percent == 0:
                pricing_service = PricingService(session)
                try:
                    suggested_discount = pricing_service.calculate_document_discount(
                        customer_id=command.customer_id,
                        current_discount_percent=discount_percent
                    )
                    if suggested_discount > 0:
                        discount_percent = suggested_discount
                except:
                    pass  # Use provided discount_percent if pricing service fails
            
            quote = Quote.create(
                customer_id=command.customer_id,
                created_by=command.created_by,
                number=command.number,
                valid_until=command.valid_until,
                discount_percent=discount_percent,
                notes=command.notes,
                internal_notes=command.internal_notes
            )
            
            session.add(quote)
            session.flush()  # Flush to get ID for domain event
            
            # Update domain event with quote ID
            events = quote.get_domain_events()
            for event in events:
                if hasattr(event, 'quote_id'):
                    event.quote_id = quote.id
            
            # Add lines if provided
            pricing_service = PricingService(session)
            for line_input in command.lines:
                # Use Pricing Service to get customer price if unit_price not provided
                unit_price = line_input.unit_price
                line_discount = line_input.discount_percent
                
                if unit_price == 0 or unit_price is None:
                    try:
                        price_result = pricing_service.get_price_for_customer(
                            product_id=line_input.product_id,
                            customer_id=command.customer_id,
                            quantity=line_input.quantity
                        )
                        # IMPORTANT: If the price comes from a customer_discount, the discount is already
                        # included in final_price. We should use the BASE price as unit_price and apply
                        # the discount_percent separately. Otherwise, use final_price as unit_price.
                        if price_result.source == 'customer_discount' and price_result.applied_discount_percent > 0:
                            # Use base price and apply discount separately
                            unit_price = price_result.base_price
                            # Only apply discount if not already set
                            if line_discount == 0:
                                line_discount = price_result.applied_discount_percent
                        else:
                            # For price_list, promotional_price, volume_pricing, or base price:
                            # Use final_price as unit_price, no discount
                            unit_price = price_result.final_price
                            # Don't apply discount for non-customer-discount sources
                            if line_discount == 0:
                                line_discount = Decimal(0)
                    except ValueError:
                        # If pricing service fails, use product base price
                        from app.domain.models.product import Product
                        product = session.get(Product, line_input.product_id)
                        if product:
                            unit_price = product.price
                
                line = quote.add_line(
                    product_id=line_input.product_id,
                    quantity=line_input.quantity,
                    unit_price=unit_price,
                    variant_id=line_input.variant_id,
                    discount_percent=line_discount,
                    tax_rate=line_input.tax_rate
                )
                session.add(line)
            
            # Validate pricing rules
            try:
                pricing_service.validate_price_rules(quote)
            except ValueError as e:
                # Log warning but don't fail quote creation
                import logging
                logging.warning(f"Pricing validation warning for quote {quote.id}: {e}")
            
            # Access quote.id before commit to ensure it's available
            quote_id = quote.id
            
            session.commit()
            
            # Refresh quote to ensure all attributes are loaded before session closes
            session.refresh(quote)
            
            # Return quote_id instead of quote object to avoid detached instance issues
            # The route can reload the quote if needed
            return quote_id


class UpdateQuoteHandler(CommandHandler):
    def handle(self, command: UpdateQuoteCommand) -> Quote:
        with get_session() as session:
            quote = session.get(Quote, command.id)
            if not quote:
                raise ValueError(f"Quote with ID {command.id} not found.")
            
            if command.valid_until is not None:
                quote.valid_until = command.valid_until
            
            if command.discount_percent is not None:
                quote.discount_percent = command.discount_percent
            
            if command.notes is not None:
                quote.notes = command.notes.strip() if command.notes else None
            
            if command.internal_notes is not None:
                quote.internal_notes = command.internal_notes.strip() if command.internal_notes else None
            
            quote.calculate_totals()
            
            # Access quote.id before commit
            quote_id = quote.id
            
            session.commit()
            session.refresh(quote)
            
            # Return quote_id to avoid detached instance issues
            return quote_id


class AddQuoteLineHandler(CommandHandler):
    def handle(self, command: AddQuoteLineCommand) -> QuoteLine:
        with get_session() as session:
            quote = session.get(Quote, command.quote_id)
            if not quote:
                raise ValueError(f"Quote with ID {command.quote_id} not found.")
            
            # Validate variant belongs to product if variant_id is provided
            if command.variant_id:
                from app.domain.models.product import ProductVariant
                variant = session.get(ProductVariant, command.variant_id)
                if not variant:
                    raise ValueError(f"Variant with ID {command.variant_id} not found.")
                if variant.product_id != command.product_id:
                    raise ValueError(f"Variant {command.variant_id} does not belong to product {command.product_id}.")
            
            # Use Pricing Service to get customer price if unit_price not provided
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
                            customer_id=quote.customer_id,
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
            
            # If unit_price is 0 or not provided, get price from Pricing Service
            if unit_price == 0 or unit_price is None:
                pricing_service = PricingService(session)
                try:
                    price_result = pricing_service.get_price_for_customer(
                        product_id=command.product_id,
                        customer_id=quote.customer_id,
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
                    # If pricing service fails, use product base price
                    from app.domain.models.product import Product
                    product = session.get(Product, command.product_id)
                    if product:
                        unit_price = product.price
            
            line = quote.add_line(
                product_id=command.product_id,
                quantity=command.quantity,
                unit_price=unit_price,
                variant_id=command.variant_id,
                discount_percent=discount_percent,
                tax_rate=command.tax_rate
            )
            
            session.add(line)
            quote.calculate_totals()
            line_id = line.id
            session.commit()
            session.refresh(line)
            return line


class UpdateQuoteLineHandler(CommandHandler):
    def handle(self, command: UpdateQuoteLineCommand) -> QuoteLine:
        with get_session() as session:
            quote = session.get(Quote, command.quote_id)
            if not quote:
                raise ValueError(f"Quote with ID {command.quote_id} not found.")
            
            line = session.get(QuoteLine, command.line_id)
            if not line or line.quote_id != command.quote_id:
                raise ValueError(f"Quote line with ID {command.line_id} not found in quote {command.quote_id}.")
            
            if quote.status != 'draft':
                raise ValueError(f"Cannot update line in quote '{quote.number}' in status '{quote.status}'. Quote must be in 'draft' status.")
            
            if command.quantity is not None:
                line.quantity = command.quantity
            
            if command.unit_price is not None:
                line.unit_price = command.unit_price
            
            if command.discount_percent is not None:
                line.discount_percent = command.discount_percent
            
            if command.tax_rate is not None:
                line.tax_rate = command.tax_rate
            
            line.calculate_totals()
            quote.calculate_totals()
            session.commit()
            return line


class RemoveQuoteLineHandler(CommandHandler):
    def handle(self, command: RemoveQuoteLineCommand) -> None:
        with get_session() as session:
            quote = session.get(Quote, command.quote_id)
            if not quote:
                raise ValueError(f"Quote with ID {command.quote_id} not found.")
            
            if quote.status != 'draft':
                raise ValueError(f"Cannot remove line from quote '{quote.number}' in status '{quote.status}'. Quote must be in 'draft' status.")
            
            line = session.get(QuoteLine, command.line_id)
            if not line or line.quote_id != command.quote_id:
                raise ValueError(f"Quote line with ID {command.line_id} not found in quote {command.quote_id}.")
            
            session.delete(line)
            quote.calculate_totals()
            session.commit()


class SendQuoteHandler(CommandHandler):
    def handle(self, command: SendQuoteCommand) -> int:
        with get_session() as session:
            quote = session.get(Quote, command.id)
            if not quote:
                raise ValueError(f"Quote with ID {command.id} not found.")
            
            # Load customer to get email
            from app.domain.models.customer import Customer
            customer = session.get(Customer, quote.customer_id)
            if not customer:
                raise ValueError(f"Customer with ID {quote.customer_id} not found.")
            
            # Send quote
            quote.send(command.sent_by)
            quote_id = quote.id
            recipient_email = customer.email if customer.email else None
            session.commit()
            
            # Trigger email sending via Celery task (async)
            try:
                from app.tasks.email_tasks import send_quote_email_task
                from flask import current_app
                from app.utils.locale import get_user_locale
                
                if not recipient_email:
                    # If no email, log warning but don't fail
                    import logging
                    logging.warning(f"Cannot send quote {quote_id}: customer {quote.customer_id} has no email address")
                else:
                    # Get locale from current context or default to 'fr'
                    locale = 'fr'  # Default
                    try:
                        from flask import has_request_context
                        if has_request_context():
                            locale = get_user_locale()
                    except:
                        pass
                    
                    # Send email asynchronously
                    send_quote_email_task.delay(quote_id, recipient_email, locale)
            except Exception as e:
                # Log error but don't fail the command
                import logging
                logging.error(f"Failed to queue email for quote {quote_id}: {e}")
            
            return quote_id


class AcceptQuoteHandler(CommandHandler):
    def handle(self, command: AcceptQuoteCommand) -> int:
        with get_session() as session:
            quote = session.get(Quote, command.id)
            if not quote:
                raise ValueError(f"Quote with ID {command.id} not found.")
            
            quote.accept()
            quote_id = quote.id
            session.commit()
            return quote_id


class RejectQuoteHandler(CommandHandler):
    def handle(self, command: RejectQuoteCommand) -> int:
        with get_session() as session:
            quote = session.get(Quote, command.id)
            if not quote:
                raise ValueError(f"Quote with ID {command.id} not found.")
            
            quote.reject()
            quote_id = quote.id
            session.commit()
            return quote_id


class CancelQuoteHandler(CommandHandler):
    def handle(self, command: CancelQuoteCommand) -> int:
        with get_session() as session:
            quote = session.get(Quote, command.id)
            if not quote:
                raise ValueError(f"Quote with ID {command.id} not found.")
            
            quote.cancel()
            quote_id = quote.id
            session.commit()
            return quote_id


class DeleteQuoteHandler(CommandHandler):
    def handle(self, command: DeleteQuoteCommand) -> None:
        """Delete a draft quote. Only draft quotes can be deleted."""
        with get_session() as session:
            quote = session.get(Quote, command.id)
            if not quote:
                raise ValueError(f"Quote with ID {command.id} not found.")
            
            if quote.status != QuoteStatus.DRAFT.value:
                raise ValueError(f"Cannot delete quote '{quote.number}' in status '{quote.status}'. Only draft quotes can be deleted.")
            
            # Delete all quote lines first
            for line in quote.lines:
                session.delete(line)
            
            # Delete all quote versions
            for version in quote.versions:
                session.delete(version)
            
            # Delete the quote
            session.delete(quote)
            session.commit()


class ConvertQuoteToOrderHandler(CommandHandler):
    def handle(self, command: ConvertQuoteToOrderCommand) -> dict:
        """
        Convert an accepted quote to an order.
        Returns a dict with 'quote' and 'order' keys.
        Note: Order model will be created in User Story 5, so this is a placeholder.
        """
        with get_session() as session:
            quote = session.get(Quote, command.id)
            if not quote:
                raise ValueError(f"Quote with ID {command.id} not found.")
            
            if not quote.can_convert_to_order():
                raise ValueError(f"Cannot convert quote '{quote.number}' to order. Quote must be in 'accepted' status.")
            
            # TODO: Create Order from Quote (User Story 5)
            # For now, just return the quote
            # This will be implemented when Order model is created
            return {
                'quote': quote,
                'order': None  # Will be created in US5
            }

