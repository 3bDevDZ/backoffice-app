"""Command handlers for purchase management."""
from app.application.common.cqrs import CommandHandler
from app.domain.models.supplier import (
    Supplier, SupplierAddress, SupplierContact, SupplierConditions
)
from app.domain.models.purchase import PurchaseOrder, PurchaseOrderLine
from app.infrastructure.db import get_session
from .commands import (
    CreateSupplierCommand, UpdateSupplierCommand, ArchiveSupplierCommand,
    ActivateSupplierCommand, DeactivateSupplierCommand,
    CreateSupplierAddressCommand, UpdateSupplierAddressCommand, DeleteSupplierAddressCommand,
    CreateSupplierContactCommand, UpdateSupplierContactCommand, DeleteSupplierContactCommand,
    CreatePurchaseOrderCommand, UpdatePurchaseOrderCommand, ConfirmPurchaseOrderCommand,
    CancelPurchaseOrderCommand, AddPurchaseOrderLineCommand, UpdatePurchaseOrderLineCommand,
    RemovePurchaseOrderLineCommand, ReceivePurchaseOrderLineCommand
)


# Supplier Handlers
class CreateSupplierHandler(CommandHandler):
    def handle(self, command: CreateSupplierCommand) -> Supplier:
        with get_session() as session:
            supplier = Supplier.create(
                name=command.name,
                email=command.email,
                code=command.code,
                phone=command.phone,
                mobile=command.mobile,
                category=command.category,
                notes=command.notes,
                company_name=command.company_name,
                siret=command.siret,
                vat_number=command.vat_number,
                rcs=command.rcs,
                legal_form=command.legal_form,
                payment_terms_days=command.payment_terms_days,
                default_discount_percent=command.default_discount_percent,
                minimum_order_amount=command.minimum_order_amount,
                delivery_lead_time_days=command.delivery_lead_time_days
            )
            
            session.add(supplier)
            session.flush()  # Flush to get ID for domain event
            
            # Update domain event with supplier ID
            events = supplier.get_domain_events()
            for event in events:
                if hasattr(event, 'supplier_id'):
                    event.supplier_id = supplier.id
            
            # Create supplier conditions
            conditions = SupplierConditions(
                supplier_id=supplier.id,
                payment_terms_days=command.payment_terms_days,
                default_discount_percent=command.default_discount_percent,
                minimum_order_amount=command.minimum_order_amount,
                delivery_lead_time_days=command.delivery_lead_time_days
            )
            session.add(conditions)
            
            session.commit()
            return supplier


class UpdateSupplierHandler(CommandHandler):
    def handle(self, command: UpdateSupplierCommand) -> Supplier:
        with get_session() as session:
            supplier = session.get(Supplier, command.id)
            if not supplier:
                raise ValueError("Supplier not found")
            
            supplier.update_details(
                name=command.name,
                email=command.email,
                phone=command.phone,
                mobile=command.mobile,
                category=command.category,
                notes=command.notes,
                company_name=command.company_name,
                siret=command.siret,
                vat_number=command.vat_number,
                rcs=command.rcs,
                legal_form=command.legal_form
            )
            
            session.commit()
            return supplier


class ArchiveSupplierHandler(CommandHandler):
    def handle(self, command: ArchiveSupplierCommand) -> Supplier:
        with get_session() as session:
            supplier = session.get(Supplier, command.id)
            if not supplier:
                raise ValueError("Supplier not found")
            
            supplier.archive()
            session.commit()
            return supplier


class ActivateSupplierHandler(CommandHandler):
    def handle(self, command: ActivateSupplierCommand) -> Supplier:
        with get_session() as session:
            supplier = session.get(Supplier, command.id)
            if not supplier:
                raise ValueError("Supplier not found")
            
            supplier.activate()
            session.commit()
            return supplier


class DeactivateSupplierHandler(CommandHandler):
    def handle(self, command: DeactivateSupplierCommand) -> Supplier:
        with get_session() as session:
            supplier = session.get(Supplier, command.id)
            if not supplier:
                raise ValueError("Supplier not found")
            
            supplier.deactivate()
            session.commit()
            return supplier


# Supplier Address Handlers
class CreateSupplierAddressHandler(CommandHandler):
    def handle(self, command: CreateSupplierAddressCommand) -> SupplierAddress:
        with get_session() as session:
            # Check if setting as default, unset other defaults
            if command.is_default_billing:
                session.query(SupplierAddress).filter_by(
                    supplier_id=command.supplier_id,
                    is_default_billing=True
                ).update({'is_default_billing': False})
            
            if command.is_default_delivery:
                session.query(SupplierAddress).filter_by(
                    supplier_id=command.supplier_id,
                    is_default_delivery=True
                ).update({'is_default_delivery': False})
            
            address = SupplierAddress.create(
                supplier_id=command.supplier_id,
                type=command.type,
                street=command.street,
                city=command.city,
                postal_code=command.postal_code,
                country=command.country,
                state=command.state,
                is_default_billing=command.is_default_billing,
                is_default_delivery=command.is_default_delivery
            )
            
            session.add(address)
            session.commit()
            return address


class UpdateSupplierAddressHandler(CommandHandler):
    def handle(self, command: UpdateSupplierAddressCommand) -> SupplierAddress:
        with get_session() as session:
            address = session.get(SupplierAddress, command.id)
            if not address:
                raise ValueError("Supplier address not found")
            
            # Handle default flags
            if command.is_default_billing is not None:
                if command.is_default_billing:
                    session.query(SupplierAddress).filter_by(
                        supplier_id=address.supplier_id,
                        is_default_billing=True
                    ).update({'is_default_billing': False})
                address.is_default_billing = command.is_default_billing
            
            if command.is_default_delivery is not None:
                if command.is_default_delivery:
                    session.query(SupplierAddress).filter_by(
                        supplier_id=address.supplier_id,
                        is_default_delivery=True
                    ).update({'is_default_delivery': False})
                address.is_default_delivery = command.is_default_delivery
            
            if command.type is not None:
                address.type = command.type
            if command.street is not None:
                address.street = command.street
            if command.city is not None:
                address.city = command.city
            if command.postal_code is not None:
                address.postal_code = command.postal_code
            if command.country is not None:
                address.country = command.country
            if command.state is not None:
                address.state = command.state
            
            session.commit()
            return address


class DeleteSupplierAddressHandler(CommandHandler):
    def handle(self, command: DeleteSupplierAddressCommand) -> None:
        with get_session() as session:
            address = session.get(SupplierAddress, command.id)
            if not address:
                raise ValueError("Supplier address not found")
            
            session.delete(address)
            session.commit()


# Supplier Contact Handlers
class CreateSupplierContactHandler(CommandHandler):
    def handle(self, command: CreateSupplierContactCommand) -> SupplierContact:
        with get_session() as session:
            # If setting as primary, unset other primary contacts
            if command.is_primary:
                session.query(SupplierContact).filter_by(
                    supplier_id=command.supplier_id,
                    is_primary=True
                ).update({'is_primary': False})
            
            contact = SupplierContact.create(
                supplier_id=command.supplier_id,
                first_name=command.first_name,
                last_name=command.last_name,
                function=command.function,
                email=command.email,
                phone=command.phone,
                mobile=command.mobile,
                is_primary=command.is_primary,
                receives_orders=command.receives_orders,
                receives_invoices=command.receives_invoices
            )
            
            session.add(contact)
            session.commit()
            return contact


class UpdateSupplierContactHandler(CommandHandler):
    def handle(self, command: UpdateSupplierContactCommand) -> SupplierContact:
        with get_session() as session:
            contact = session.get(SupplierContact, command.id)
            if not contact:
                raise ValueError("Supplier contact not found")
            
            # Handle primary flag
            if command.is_primary is not None:
                if command.is_primary:
                    session.query(SupplierContact).filter_by(
                        supplier_id=contact.supplier_id,
                        is_primary=True
                    ).update({'is_primary': False})
                contact.is_primary = command.is_primary
            
            if command.first_name is not None:
                contact.first_name = command.first_name
            if command.last_name is not None:
                contact.last_name = command.last_name
            if command.function is not None:
                contact.function = command.function
            if command.email is not None:
                contact.email = command.email
            if command.phone is not None:
                contact.phone = command.phone
            if command.mobile is not None:
                contact.mobile = command.mobile
            if command.receives_orders is not None:
                contact.receives_orders = command.receives_orders
            if command.receives_invoices is not None:
                contact.receives_invoices = command.receives_invoices
            
            session.commit()
            return contact


class DeleteSupplierContactHandler(CommandHandler):
    def handle(self, command: DeleteSupplierContactCommand) -> None:
        with get_session() as session:
            contact = session.get(SupplierContact, command.id)
            if not contact:
                raise ValueError("Supplier contact not found")
            
            session.delete(contact)
            session.commit()


# Purchase Order Handlers
class CreatePurchaseOrderHandler(CommandHandler):
    def handle(self, command: CreatePurchaseOrderCommand) -> PurchaseOrder:
        with get_session() as session:
            order = PurchaseOrder.create(
                supplier_id=command.supplier_id,
                created_by=command.created_by,
                number=command.number,
                order_date=command.order_date,
                expected_delivery_date=command.expected_delivery_date,
                notes=command.notes,
                internal_notes=command.internal_notes
            )
            
            session.add(order)
            session.flush()  # Flush to get ID for domain event
            
            # Get ID before commit (needed for domain event and return value)
            order_id = order.id
            
            # Update domain event with order ID
            events = order.get_domain_events()
            for event in events:
                if hasattr(event, 'purchase_order_id'):
                    event.purchase_order_id = order_id
            
            session.commit()
            
            # Return a simple object with just the ID to avoid session issues
            # The route can query the full order if needed
            from types import SimpleNamespace
            result = SimpleNamespace()
            result.id = order_id
            result.number = order.number
            result.status = order.status
            result.supplier_id = order.supplier_id
            result.created_by = order.created_by
            result.order_date = order.order_date
            result.expected_delivery_date = order.expected_delivery_date
            
            return result


class UpdatePurchaseOrderHandler(CommandHandler):
    def handle(self, command: UpdatePurchaseOrderCommand) -> PurchaseOrder:
        with get_session() as session:
            order = session.get(PurchaseOrder, command.id)
            if not order:
                raise ValueError("Purchase order not found")
            
            if order.status != 'draft':
                raise ValueError(f"Cannot update purchase order in status '{order.status}'.")
            
            if command.expected_delivery_date is not None:
                order.expected_delivery_date = command.expected_delivery_date
            if command.notes is not None:
                order.notes = command.notes
            if command.internal_notes is not None:
                order.internal_notes = command.internal_notes
            
            session.commit()
            return order


class ConfirmPurchaseOrderHandler(CommandHandler):
    def handle(self, command: ConfirmPurchaseOrderCommand) -> PurchaseOrder:
        with get_session() as session:
            order = session.get(PurchaseOrder, command.id)
            if not order:
                raise ValueError("Purchase order not found")
            
            order.confirm(command.confirmed_by)
            session.commit()
            return order


class CancelPurchaseOrderHandler(CommandHandler):
    def handle(self, command: CancelPurchaseOrderCommand) -> PurchaseOrder:
        with get_session() as session:
            order = session.get(PurchaseOrder, command.id)
            if not order:
                raise ValueError("Purchase order not found")
            
            order.cancel()
            session.commit()
            return order


class AddPurchaseOrderLineHandler(CommandHandler):
    def handle(self, command: AddPurchaseOrderLineCommand) -> PurchaseOrderLine:
        with get_session() as session:
            order = session.get(PurchaseOrder, command.purchase_order_id)
            if not order:
                raise ValueError("Purchase order not found")
            
            line = order.add_line(
                product_id=command.product_id,
                quantity=command.quantity,
                unit_price=command.unit_price,
                discount_percent=command.discount_percent,
                tax_rate=command.tax_rate,
                notes=command.notes
            )
            
            session.add(line)
            session.commit()
            return line


class UpdatePurchaseOrderLineHandler(CommandHandler):
    def handle(self, command: UpdatePurchaseOrderLineCommand) -> PurchaseOrderLine:
        with get_session() as session:
            order = session.get(PurchaseOrder, command.purchase_order_id)
            if not order:
                raise ValueError("Purchase order not found")
            
            order.update_line(
                line_id=command.line_id,
                quantity=command.quantity,
                unit_price=command.unit_price,
                discount_percent=command.discount_percent,
                notes=command.notes
            )
            
            session.commit()
            session.refresh(order)
            line = next((l for l in order.lines if l.id == command.line_id), None)
            return line


class RemovePurchaseOrderLineHandler(CommandHandler):
    def handle(self, command: RemovePurchaseOrderLineCommand) -> None:
        with get_session() as session:
            order = session.get(PurchaseOrder, command.purchase_order_id)
            if not order:
                raise ValueError("Purchase order not found")
            
            order.remove_line(command.line_id)
            session.commit()


class ReceivePurchaseOrderLineHandler(CommandHandler):
    def handle(self, command: ReceivePurchaseOrderLineCommand) -> PurchaseOrderLine:
        with get_session() as session:
            from sqlalchemy.orm import joinedload
            # Load order with lines eagerly to ensure they're available
            order = session.query(PurchaseOrder).options(
                joinedload(PurchaseOrder.lines)
            ).filter(PurchaseOrder.id == command.purchase_order_id).first()
            if not order:
                raise ValueError("Purchase order not found")
            
            # Find the line
            line = next((l for l in order.lines if l.id == command.line_id), None)
            if not line:
                raise ValueError(f"Purchase order line {command.line_id} not found")
            
            # Validate quantity
            if command.quantity_received < 0:
                raise ValueError("Received quantity cannot be negative")
            if command.quantity_received > line.quantity:
                raise ValueError(f"Received quantity ({command.quantity_received}) cannot exceed ordered quantity ({line.quantity})")
            
            # Calculate the incremental quantity received (difference between old and new)
            old_quantity_received = line.quantity_received
            new_quantity_received = command.quantity_received
            incremental_quantity = new_quantity_received - old_quantity_received
            
            # Update received quantity
            line.quantity_received = command.quantity_received
            
            # Flush to ensure changes are in the session before checking status
            session.flush()
            
            # If there's an incremental quantity received, trigger event to update stock immediately
            # This must happen BEFORE mark_received() to avoid double processing
            if incremental_quantity > 0:
                from app.domain.models.purchase import PurchaseOrderLineReceivedDomainEvent
                order.raise_domain_event(PurchaseOrderLineReceivedDomainEvent(
                    purchase_order_id=order.id,
                    purchase_order_number=order.number,
                    line_id=line.id,
                    product_id=line.product_id,
                    quantity_received=incremental_quantity,  # Only the new quantity received
                    location_id=command.location_id
                ))
            
            # Check if order should be marked as received/partially_received
            # This will trigger the domain event if fully received
            # Note: PurchaseOrderReceivedDomainEventHandler will check for existing movements
            # and skip lines that have already been processed by PurchaseOrderLineReceivedDomainEventHandler
            old_status = order.status
            order.mark_received()
            
            session.commit()
            session.refresh(order)  # Refresh order to see status changes
            session.refresh(line)
            return line

