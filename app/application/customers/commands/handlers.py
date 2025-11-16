"""Command handlers for customer management."""
from app.application.common.cqrs import CommandHandler
from app.domain.models.customer import (
    Customer, Address, Contact, CommercialConditions
)
from app.infrastructure.db import get_session
from .commands import (
    CreateCustomerCommand, UpdateCustomerCommand, ArchiveCustomerCommand,
    ActivateCustomerCommand, DeactivateCustomerCommand,
    CreateAddressCommand, UpdateAddressCommand, DeleteAddressCommand,
    CreateContactCommand, UpdateContactCommand, DeleteContactCommand
)


class CreateCustomerHandler(CommandHandler):
    def handle(self, command: CreateCustomerCommand) -> Customer:
        with get_session() as session:
            # Create customer using domain factory method
            customer = Customer.create(
                type=command.type,
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
                first_name=command.first_name,
                last_name=command.last_name,
                birth_date=command.birth_date
            )
            
            session.add(customer)
            session.flush()  # Flush to get ID for domain event
            
            # Update domain event with customer ID
            events = customer.get_domain_events()
            for event in events:
                if hasattr(event, 'customer_id'):
                    event.customer_id = customer.id
            
            # Create commercial conditions
            commercial_conditions = CommercialConditions(
                customer_id=customer.id,
                payment_terms_days=command.payment_terms_days,
                default_discount_percent=command.default_discount_percent,
                credit_limit=command.credit_limit,
                block_on_credit_exceeded=command.block_on_credit_exceeded
            )
            session.add(commercial_conditions)
            
            session.commit()
            return customer


class UpdateCustomerHandler(CommandHandler):
    def handle(self, command: UpdateCustomerCommand) -> Customer:
        with get_session() as session:
            customer = session.get(Customer, command.id)
            if not customer:
                raise ValueError("Customer not found")
            
            # Use domain method for business logic
            customer.update_details(
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
                legal_form=command.legal_form,
                first_name=command.first_name,
                last_name=command.last_name,
                birth_date=command.birth_date
            )
            
            # Update commercial conditions if provided
            if (command.payment_terms_days is not None or 
                command.default_discount_percent is not None or 
                command.credit_limit is not None or 
                command.block_on_credit_exceeded is not None):
                
                # Get or create commercial conditions
                if not customer.commercial_conditions:
                    from app.domain.models.customer import CommercialConditions
                    commercial_conditions = CommercialConditions(customer_id=customer.id)
                    session.add(commercial_conditions)
                    session.flush()  # Flush to get the ID
                else:
                    commercial_conditions = customer.commercial_conditions
                
                # Update fields if provided
                if command.payment_terms_days is not None:
                    commercial_conditions.payment_terms_days = command.payment_terms_days
                if command.default_discount_percent is not None:
                    commercial_conditions.default_discount_percent = command.default_discount_percent
                if command.credit_limit is not None:
                    commercial_conditions.credit_limit = command.credit_limit
                if command.block_on_credit_exceeded is not None:
                    commercial_conditions.block_on_credit_exceeded = command.block_on_credit_exceeded
            
            session.commit()
            return customer


class ArchiveCustomerHandler(CommandHandler):
    def handle(self, command: ArchiveCustomerCommand) -> Customer:
        with get_session() as session:
            customer = session.get(Customer, command.id)
            if not customer:
                raise ValueError("Customer not found")
            
            # Use domain method for business logic
            customer.archive()
            session.commit()
            return customer


class ActivateCustomerHandler(CommandHandler):
    def handle(self, command: ActivateCustomerCommand) -> Customer:
        with get_session() as session:
            customer = session.get(Customer, command.id)
            if not customer:
                raise ValueError("Customer not found")
            
            customer.activate()
            session.commit()
            return customer


class DeactivateCustomerHandler(CommandHandler):
    def handle(self, command: DeactivateCustomerCommand) -> Customer:
        with get_session() as session:
            customer = session.get(Customer, command.id)
            if not customer:
                raise ValueError("Customer not found")
            
            customer.status = 'inactive'
            session.commit()
            return customer


# Address Handlers
class CreateAddressHandler(CommandHandler):
    def handle(self, command: CreateAddressCommand) -> Address:
        with get_session() as session:
            # Verify customer exists
            customer = session.get(Customer, command.customer_id)
            if not customer:
                raise ValueError("Customer not found")
            
            # If setting as default, unset other defaults
            if command.is_default_billing:
                session.query(Address).filter_by(
                    customer_id=command.customer_id,
                    is_default_billing=True
                ).update({'is_default_billing': False})
            
            if command.is_default_delivery:
                session.query(Address).filter_by(
                    customer_id=command.customer_id,
                    is_default_delivery=True
                ).update({'is_default_delivery': False})
            
            address = Address.create(
                customer_id=command.customer_id,
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


class UpdateAddressHandler(CommandHandler):
    def handle(self, command: UpdateAddressCommand) -> Address:
        with get_session() as session:
            address = session.get(Address, command.id)
            if not address:
                raise ValueError("Address not found")
            
            # If setting as default, unset other defaults
            if command.is_default_billing is True:
                session.query(Address).filter_by(
                    customer_id=address.customer_id,
                    is_default_billing=True
                ).update({'is_default_billing': False})
            
            if command.is_default_delivery is True:
                session.query(Address).filter_by(
                    customer_id=address.customer_id,
                    is_default_delivery=True
                ).update({'is_default_delivery': False})
            
            address.update_details(
                type=command.type,
                street=command.street,
                city=command.city,
                postal_code=command.postal_code,
                country=command.country,
                state=command.state,
                is_default_billing=command.is_default_billing,
                is_default_delivery=command.is_default_delivery
            )
            
            session.commit()
            return address


class DeleteAddressHandler(CommandHandler):
    def handle(self, command: DeleteAddressCommand):
        with get_session() as session:
            address = session.get(Address, command.id)
            if not address:
                raise ValueError("Address not found")
            
            # Check if it's the only billing address
            billing_count = session.query(Address).filter_by(
                customer_id=address.customer_id,
                type='billing'
            ).count()
            
            if address.type in ['billing', 'both'] and billing_count == 1:
                raise ValueError("Cannot delete the only billing address")
            
            session.delete(address)
            session.commit()


# Contact Handlers
class CreateContactHandler(CommandHandler):
    def handle(self, command: CreateContactCommand) -> Contact:
        with get_session() as session:
            # Verify customer exists
            customer = session.get(Customer, command.customer_id)
            if not customer:
                raise ValueError("Customer not found")
            
            # If setting as primary, unset other primary contacts
            if command.is_primary:
                session.query(Contact).filter_by(
                    customer_id=command.customer_id,
                    is_primary=True
                ).update({'is_primary': False})
            
            contact = Contact.create(
                customer_id=command.customer_id,
                first_name=command.first_name,
                last_name=command.last_name,
                function=command.function,
                email=command.email,
                phone=command.phone,
                mobile=command.mobile,
                is_primary=command.is_primary,
                receives_quotes=command.receives_quotes,
                receives_invoices=command.receives_invoices,
                receives_orders=command.receives_orders
            )
            
            session.add(contact)
            session.commit()
            return contact


class UpdateContactHandler(CommandHandler):
    def handle(self, command: UpdateContactCommand) -> Contact:
        with get_session() as session:
            contact = session.get(Contact, command.id)
            if not contact:
                raise ValueError("Contact not found")
            
            # If setting as primary, unset other primary contacts
            if command.is_primary is True:
                session.query(Contact).filter_by(
                    customer_id=contact.customer_id,
                    is_primary=True
                ).update({'is_primary': False})
            
            contact.update_details(
                first_name=command.first_name,
                last_name=command.last_name,
                function=command.function,
                email=command.email,
                phone=command.phone,
                mobile=command.mobile,
                is_primary=command.is_primary,
                receives_quotes=command.receives_quotes,
                receives_invoices=command.receives_invoices,
                receives_orders=command.receives_orders
            )
            
            session.commit()
            return contact


class DeleteContactHandler(CommandHandler):
    def handle(self, command: DeleteContactCommand):
        with get_session() as session:
            contact = session.get(Contact, command.id)
            if not contact:
                raise ValueError("Contact not found")
            
            session.delete(contact)
            session.commit()
