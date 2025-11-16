"""Query handlers for customer management."""
from app.application.common.cqrs import QueryHandler
from app.domain.models.customer import Customer, Address, Contact, CommercialConditions
from app.infrastructure.db import get_session
from .queries import (
    GetCustomerByIdQuery,
    ListCustomersQuery,
    SearchCustomersQuery,
    GetCustomerHistoryQuery
)
from .customer_dto import CustomerDTO, AddressDTO, ContactDTO, CommercialConditionsDTO
from typing import List
from sqlalchemy import or_


class GetCustomerByIdHandler(QueryHandler):
    def handle(self, query: GetCustomerByIdQuery) -> CustomerDTO:
        with get_session() as session:
            customer = session.get(Customer, query.id)
            if not customer:
                raise ValueError("Customer not found")
            
            # Load addresses
            address_dtos = [
                AddressDTO(
                    id=addr.id,
                    customer_id=addr.customer_id,
                    type=addr.type,
                    is_default_billing=addr.is_default_billing,
                    is_default_delivery=addr.is_default_delivery,
                    street=addr.street,
                    city=addr.city,
                    postal_code=addr.postal_code,
                    country=addr.country,
                    state=addr.state
                )
                for addr in customer.addresses
            ]
            
            # Load contacts
            contact_dtos = [
                ContactDTO(
                    id=contact.id,
                    customer_id=contact.customer_id,
                    first_name=contact.first_name,
                    last_name=contact.last_name,
                    function=contact.function,
                    email=contact.email,
                    phone=contact.phone,
                    mobile=contact.mobile,
                    is_primary=contact.is_primary,
                    receives_quotes=contact.receives_quotes,
                    receives_invoices=contact.receives_invoices,
                    receives_orders=contact.receives_orders
                )
                for contact in customer.contacts
            ]
            
            # Load commercial conditions
            commercial_conditions_dto = None
            if customer.commercial_conditions:
                cc = customer.commercial_conditions
                commercial_conditions_dto = CommercialConditionsDTO(
                    id=cc.id,
                    customer_id=cc.customer_id,
                    payment_terms_days=cc.payment_terms_days,
                    default_discount_percent=cc.default_discount_percent,
                    credit_limit=cc.credit_limit,
                    block_on_credit_exceeded=cc.block_on_credit_exceeded
                )
            
            return CustomerDTO(
                id=customer.id,
                code=customer.code,
                type=customer.type,
                name=customer.name,
                email=customer.email,
                phone=customer.phone,
                mobile=customer.mobile,
                category=customer.category,
                status=customer.status,
                notes=customer.notes,
                company_name=customer.company_name,
                siret=customer.siret,
                vat_number=customer.vat_number,
                rcs=customer.rcs,
                legal_form=customer.legal_form,
                first_name=customer.first_name,
                last_name=customer.last_name,
                birth_date=customer.birth_date,
                addresses=address_dtos,
                contacts=contact_dtos,
                commercial_conditions=commercial_conditions_dto
            )


class ListCustomersHandler(QueryHandler):
    def handle(self, query: ListCustomersQuery) -> List[CustomerDTO]:
        with get_session() as session:
            # Build query with filters
            q = session.query(Customer)
            
            # Search filter
            if query.search:
                search_term = f"%{query.search}%"
                q = q.filter(
                    or_(
                        Customer.name.ilike(search_term),
                        Customer.code.ilike(search_term),
                        Customer.email.ilike(search_term),
                        Customer.company_name.ilike(search_term) if Customer.company_name else False
                    )
                )
            
            # Type filter
            if query.type:
                q = q.filter(Customer.type == query.type)
            
            # Status filter
            if query.status:
                q = q.filter(Customer.status == query.status)
            
            # Category filter
            if query.category:
                q = q.filter(Customer.category == query.category)
            
            # Pagination
            customers = q.offset((query.page - 1) * query.per_page).limit(query.per_page).all()
            
            return [
                CustomerDTO(
                    id=c.id,
                    code=c.code,
                    type=c.type,
                    name=c.name,
                    email=c.email,
                    phone=c.phone,
                    mobile=c.mobile,
                    category=c.category,
                    status=c.status,
                    notes=c.notes,
                    company_name=c.company_name,
                    siret=c.siret,
                    vat_number=c.vat_number,
                    rcs=c.rcs,
                    legal_form=c.legal_form,
                    first_name=c.first_name,
                    last_name=c.last_name,
                    birth_date=c.birth_date,
                    addresses=[],
                    contacts=[],
                    commercial_conditions=None
                )
                for c in customers
            ]


class SearchCustomersHandler(QueryHandler):
    def handle(self, query: SearchCustomersQuery) -> List[CustomerDTO]:
        with get_session() as session:
            search_term = f"%{query.search_term}%"
            customers = session.query(Customer).filter(
                or_(
                    Customer.name.ilike(search_term),
                    Customer.code.ilike(search_term),
                    Customer.email.ilike(search_term),
                    Customer.company_name.ilike(search_term) if Customer.company_name else False
                )
            ).limit(query.limit).all()
            
            return [
                CustomerDTO(
                    id=c.id,
                    code=c.code,
                    type=c.type,
                    name=c.name,
                    email=c.email,
                    phone=c.phone,
                    mobile=c.mobile,
                    category=c.category,
                    status=c.status,
                    notes=c.notes,
                    company_name=c.company_name,
                    siret=c.siret,
                    vat_number=c.vat_number,
                    rcs=c.rcs,
                    legal_form=c.legal_form,
                    first_name=c.first_name,
                    last_name=c.last_name,
                    birth_date=c.birth_date,
                    addresses=[],
                    contacts=[],
                    commercial_conditions=None
                )
                for c in customers
            ]


class GetCustomerHistoryHandler(QueryHandler):
    def handle(self, query: GetCustomerHistoryQuery) -> dict:
        """Get customer history (quotes, orders, etc.)."""
        # TODO: Implement when Quote and Order models are available
        # For now, return empty history
        return {
            'customer_id': query.customer_id,
            'quotes': [],
            'orders': [],
            'invoices': [],
            'interactions': []
        }
