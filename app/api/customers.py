"""Customer API endpoints."""
from flask import Blueprint, request, send_file, Response
from flask_babel import get_locale, gettext as _
from app.application.common.mediator import mediator
from app.application.customers.commands.commands import (
    CreateCustomerCommand, UpdateCustomerCommand, ArchiveCustomerCommand,
    ActivateCustomerCommand, DeactivateCustomerCommand,
    CreateAddressCommand, UpdateAddressCommand, DeleteAddressCommand,
    CreateContactCommand, UpdateContactCommand, DeleteContactCommand
)
from app.application.customers.queries.queries import (
    GetCustomerByIdQuery, ListCustomersQuery, SearchCustomersQuery, GetCustomerHistoryQuery
)
from app.api.schemas.customer_schema import (
    CustomerCreateSchema, CustomerUpdateSchema, CustomerSchema,
    AddressCreateSchema, AddressUpdateSchema, AddressSchema,
    ContactCreateSchema, ContactUpdateSchema, ContactSchema
)
from app.security.rbac import require_roles
from app.utils.response import success_response, error_response, paginated_response
from app.services.import_export import ImportExportService
import io

customers_bp = Blueprint("customers", __name__)

# Customer Endpoints
@customers_bp.get("")
@require_roles("admin", "commercial", "direction")
def list_customers():
    """List customers with pagination, search, and filters. Supports locale parameter (?locale=fr|ar)."""
    try:
        page = int(request.args.get("page", 1))
        per_page = min(int(request.args.get("page_size", 20)), 100)
        search = request.args.get("search")
        type_filter = request.args.get("type")  # 'B2B' or 'B2C'
        status = request.args.get("status")
        category = request.args.get("category")
        
        query = ListCustomersQuery(
            page=page,
            per_page=per_page,
            search=search,
            type=type_filter,
            status=status,
            category=category
        )
        customers = mediator.dispatch(query)
        
        # Convert DTOs to dicts for serialization
        customers_data = []
        for c in customers:
            customer_dict = {
                'id': c.id,
                'code': c.code,
                'type': c.type,
                'name': c.name,
                'email': c.email,
                'phone': c.phone,
                'mobile': c.mobile,
                'category': c.category,
                'status': c.status,
                'notes': c.notes,
                'company_name': c.company_name,
                'siret': c.siret,
                'vat_number': c.vat_number,
                'rcs': c.rcs,
                'legal_form': c.legal_form,
                'first_name': c.first_name,
                'last_name': c.last_name,
                'birth_date': str(c.birth_date) if c.birth_date else None
            }
            customers_data.append(customer_dict)
        
        # TODO: Get total count for pagination
        total = len(customers_data)  # Simplified - should query total count
        return paginated_response(
            items=customers_data,
            total=total,
            page=page,
            page_size=per_page
        )
    except Exception as e:
        return error_response(_(str(e)), status_code=400)


@customers_bp.get("/<int:customer_id>")
@require_roles("admin", "commercial", "direction")
def get_customer(customer_id: int):
    """Get customer by ID. Supports locale parameter (?locale=fr|ar)."""
    try:
        customer_dto = mediator.dispatch(GetCustomerByIdQuery(id=customer_id))
        
        # Convert DTO to dict
        customer_dict = {
            'id': customer_dto.id,
            'code': customer_dto.code,
            'type': customer_dto.type,
            'name': customer_dto.name,
            'email': customer_dto.email,
            'phone': customer_dto.phone,
            'mobile': customer_dto.mobile,
            'category': customer_dto.category,
            'status': customer_dto.status,
            'notes': customer_dto.notes,
            'company_name': customer_dto.company_name,
            'siret': customer_dto.siret,
            'vat_number': customer_dto.vat_number,
            'rcs': customer_dto.rcs,
            'legal_form': customer_dto.legal_form,
            'first_name': customer_dto.first_name,
            'last_name': customer_dto.last_name,
            'birth_date': str(customer_dto.birth_date) if customer_dto.birth_date else None,
            'addresses': [
                {
                    'id': a.id,
                    'customer_id': a.customer_id,
                    'type': a.type,
                    'is_default_billing': a.is_default_billing,
                    'is_default_delivery': a.is_default_delivery,
                    'street': a.street,
                    'city': a.city,
                    'postal_code': a.postal_code,
                    'country': a.country,
                    'state': a.state
                }
                for a in (customer_dto.addresses or [])
            ],
            'contacts': [
                {
                    'id': c.id,
                    'customer_id': c.customer_id,
                    'first_name': c.first_name,
                    'last_name': c.last_name,
                    'function': c.function,
                    'email': c.email,
                    'phone': c.phone,
                    'mobile': c.mobile,
                    'is_primary': c.is_primary,
                    'receives_quotes': c.receives_quotes,
                    'receives_invoices': c.receives_invoices,
                    'receives_orders': c.receives_orders
                }
                for c in (customer_dto.contacts or [])
            ],
            'commercial_conditions': {
                'id': customer_dto.commercial_conditions.id,
                'customer_id': customer_dto.commercial_conditions.customer_id,
                'payment_terms_days': float(customer_dto.commercial_conditions.payment_terms_days),
                'default_discount_percent': float(customer_dto.commercial_conditions.default_discount_percent),
                'credit_limit': float(customer_dto.commercial_conditions.credit_limit),
                'block_on_credit_exceeded': customer_dto.commercial_conditions.block_on_credit_exceeded
            } if customer_dto.commercial_conditions else None
        }
        
        return success_response(customer_dict)
    except ValueError as e:
        return error_response(_('Customer not found'), status_code=404)
    except Exception as e:
        return error_response(_(str(e)), status_code=400)


@customers_bp.post("")
@require_roles("admin", "commercial")
def create_customer():
    """Create a new customer. Supports locale parameter (?locale=fr|ar)."""
    try:
        data = CustomerCreateSchema().load(request.get_json() or {})
        data.pop('locale', None)  # Remove locale if present
        
        command = CreateCustomerCommand(**data)
        customer = mediator.dispatch(command)
        
        # Get full customer DTO for response
        customer_dto = mediator.dispatch(GetCustomerByIdQuery(id=customer.id))
        
        # Convert DTO to dict
        customer_dict = {
            'id': customer_dto.id,
            'code': customer_dto.code,
            'type': customer_dto.type,
            'name': customer_dto.name,
            'email': customer_dto.email,
            'phone': customer_dto.phone,
            'mobile': customer_dto.mobile,
            'category': customer_dto.category,
            'status': customer_dto.status,
            'notes': customer_dto.notes,
            'company_name': customer_dto.company_name,
            'siret': customer_dto.siret,
            'vat_number': customer_dto.vat_number,
            'rcs': customer_dto.rcs,
            'legal_form': customer_dto.legal_form,
            'first_name': customer_dto.first_name,
            'last_name': customer_dto.last_name,
            'birth_date': str(customer_dto.birth_date) if customer_dto.birth_date else None,
            'addresses': [],
            'contacts': [],
            'commercial_conditions': None
        }
        
        return success_response(customer_dict, message=_('Customer created successfully'), status_code=201)
    except ValueError as e:
        return error_response(_(str(e)), status_code=400)
    except Exception as e:
        return error_response(_('Failed to create customer: {}').format(str(e)), status_code=500)


@customers_bp.put("/<int:customer_id>")
@require_roles("admin", "commercial")
def update_customer(customer_id: int):
    """Update a customer. Supports locale parameter (?locale=fr|ar)."""
    try:
        data = CustomerUpdateSchema().load(request.get_json() or {})
        data.pop('locale', None)  # Remove locale if present
        
        command = UpdateCustomerCommand(id=customer_id, **data)
        customer = mediator.dispatch(command)
        
        # Get full customer DTO for response
        customer_dto = mediator.dispatch(GetCustomerByIdQuery(id=customer_id))
        
        # Convert DTO to dict (same as in get_customer)
        customer_dict = {
            'id': customer_dto.id,
            'code': customer_dto.code,
            'type': customer_dto.type,
            'name': customer_dto.name,
            'email': customer_dto.email,
            'phone': customer_dto.phone,
            'mobile': customer_dto.mobile,
            'category': customer_dto.category,
            'status': customer_dto.status,
            'notes': customer_dto.notes,
            'company_name': customer_dto.company_name,
            'siret': customer_dto.siret,
            'vat_number': customer_dto.vat_number,
            'rcs': customer_dto.rcs,
            'legal_form': customer_dto.legal_form,
            'first_name': customer_dto.first_name,
            'last_name': customer_dto.last_name,
            'birth_date': str(customer_dto.birth_date) if customer_dto.birth_date else None,
            'addresses': [
                {
                    'id': a.id,
                    'customer_id': a.customer_id,
                    'type': a.type,
                    'is_default_billing': a.is_default_billing,
                    'is_default_delivery': a.is_default_delivery,
                    'street': a.street,
                    'city': a.city,
                    'postal_code': a.postal_code,
                    'country': a.country,
                    'state': a.state
                }
                for a in (customer_dto.addresses or [])
            ],
            'contacts': [
                {
                    'id': c.id,
                    'customer_id': c.customer_id,
                    'first_name': c.first_name,
                    'last_name': c.last_name,
                    'function': c.function,
                    'email': c.email,
                    'phone': c.phone,
                    'mobile': c.mobile,
                    'is_primary': c.is_primary,
                    'receives_quotes': c.receives_quotes,
                    'receives_invoices': c.receives_invoices,
                    'receives_orders': c.receives_orders
                }
                for c in (customer_dto.contacts or [])
            ],
            'commercial_conditions': {
                'id': customer_dto.commercial_conditions.id,
                'customer_id': customer_dto.commercial_conditions.customer_id,
                'payment_terms_days': customer_dto.commercial_conditions.payment_terms_days,
                'default_discount_percent': float(customer_dto.commercial_conditions.default_discount_percent),
                'credit_limit': float(customer_dto.commercial_conditions.credit_limit),
                'block_on_credit_exceeded': customer_dto.commercial_conditions.block_on_credit_exceeded
            } if customer_dto.commercial_conditions else None
        }
        
        return success_response(customer_dict, message=_('Customer updated successfully'))
    except ValueError as e:
        return error_response(_('Customer not found'), status_code=404)
    except Exception as e:
        return error_response(_(str(e)), status_code=400)


@customers_bp.delete("/<int:customer_id>")
@require_roles("admin")
def delete_customer(customer_id: int):
    """Delete a customer. Supports locale parameter (?locale=fr|ar)."""
    try:
        # TODO: Implement DeleteCustomerCommand
        return error_response(_('Delete not yet implemented'), status_code=501)
    except ValueError as e:
        return error_response(_('Customer not found'), status_code=404)
    except Exception as e:
        return error_response(_(str(e)), status_code=400)


@customers_bp.post("/<int:customer_id>/archive")
@require_roles("admin")
def archive_customer(customer_id: int):
    """Archive a customer. Supports locale parameter (?locale=fr|ar)."""
    try:
        command = ArchiveCustomerCommand(id=customer_id)
        customer = mediator.dispatch(command)
        
        # Get full customer DTO for response
        customer_dto = mediator.dispatch(GetCustomerByIdQuery(id=customer_id))
        customer_dict = {
            'id': customer_dto.id,
            'code': customer_dto.code,
            'type': customer_dto.type,
            'name': customer_dto.name,
            'email': customer_dto.email,
            'status': customer_dto.status
        }
        return success_response(customer_dict, message=_('Customer archived successfully'))
    except ValueError as e:
        return error_response(_('Customer not found'), status_code=404)
    except Exception as e:
        return error_response(_(str(e)), status_code=400)


@customers_bp.post("/<int:customer_id>/activate")
@require_roles("admin", "commercial")
def activate_customer(customer_id: int):
    """Activate a customer. Supports locale parameter (?locale=fr|ar)."""
    try:
        command = ActivateCustomerCommand(id=customer_id)
        customer = mediator.dispatch(command)
        
        # Get full customer DTO for response
        customer_dto = mediator.dispatch(GetCustomerByIdQuery(id=customer_id))
        customer_dict = {
            'id': customer_dto.id,
            'code': customer_dto.code,
            'type': customer_dto.type,
            'name': customer_dto.name,
            'email': customer_dto.email,
            'status': customer_dto.status
        }
        return success_response(customer_dict, message=_('Customer activated successfully'))
    except ValueError as e:
        return error_response(_('Customer not found'), status_code=404)
    except Exception as e:
        return error_response(_(str(e)), status_code=400)


@customers_bp.post("/<int:customer_id>/deactivate")
@require_roles("admin", "commercial")
def deactivate_customer(customer_id: int):
    """Deactivate a customer. Supports locale parameter (?locale=fr|ar)."""
    try:
        command = DeactivateCustomerCommand(id=customer_id)
        customer = mediator.dispatch(command)
        
        # Get full customer DTO for response
        customer_dto = mediator.dispatch(GetCustomerByIdQuery(id=customer_id))
        customer_dict = {
            'id': customer_dto.id,
            'code': customer_dto.code,
            'type': customer_dto.type,
            'name': customer_dto.name,
            'email': customer_dto.email,
            'status': customer_dto.status
        }
        return success_response(customer_dict, message=_('Customer deactivated successfully'))
    except ValueError as e:
        return error_response(_('Customer not found'), status_code=404)
    except Exception as e:
        return error_response(_(str(e)), status_code=400)


@customers_bp.get("/search")
@require_roles("admin", "commercial", "direction")
def search_customers():
    """Search customers. Supports locale parameter (?locale=fr|ar)."""
    try:
        search_term = request.args.get("q", "")
        limit = min(int(request.args.get("limit", 20)), 100)
        
        if not search_term:
            return error_response(_('Search term is required'), status_code=400)
        
        query = SearchCustomersQuery(search_term=search_term, limit=limit)
        customers = mediator.dispatch(query)
        
        # Convert DTOs to dicts
        customers_data = []
        for c in customers:
            customers_data.append({
                'id': c.id,
                'code': c.code,
                'type': c.type,
                'name': c.name,
                'email': c.email,
                'status': c.status
            })
        
        return success_response(customers_data)
    except Exception as e:
        return error_response(_(str(e)), status_code=400)


# Address Endpoints
@customers_bp.get("/<int:customer_id>/addresses")
@require_roles("admin", "commercial", "direction")
def list_addresses(customer_id: int):
    """List addresses for a customer. Supports locale parameter (?locale=fr|ar)."""
    try:
        customer_dto = mediator.dispatch(GetCustomerByIdQuery(id=customer_id))
        addresses = [
            {
                'id': a.id,
                'customer_id': a.customer_id,
                'type': a.type,
                'is_default_billing': a.is_default_billing,
                'is_default_delivery': a.is_default_delivery,
                'street': a.street,
                'city': a.city,
                'postal_code': a.postal_code,
                'country': a.country,
                'state': a.state
            }
            for a in (customer_dto.addresses or [])
        ]
        return success_response(addresses)
    except ValueError as e:
        return error_response(_('Customer not found'), status_code=404)
    except Exception as e:
        return error_response(_(str(e)), status_code=400)


@customers_bp.post("/<int:customer_id>/addresses")
@require_roles("admin", "commercial")
def create_address(customer_id: int):
    """Create an address for a customer. Supports locale parameter (?locale=fr|ar)."""
    try:
        data = AddressCreateSchema().load(request.get_json() or {})
        data.pop('locale', None)
        
        command = CreateAddressCommand(customer_id=customer_id, **data)
        address = mediator.dispatch(command)
        
        address_dict = AddressSchema().dump(address)
        return success_response(address_dict, message=_('Address created successfully'), status_code=201)
    except ValueError as e:
        return error_response(_(str(e)), status_code=400)
    except Exception as e:
        return error_response(_('Failed to create address: {}').format(str(e)), status_code=500)


@customers_bp.put("/<int:customer_id>/addresses/<int:address_id>")
@require_roles("admin", "commercial")
def update_address(customer_id: int, address_id: int):
    """Update an address. Supports locale parameter (?locale=fr|ar)."""
    try:
        data = AddressUpdateSchema().load(request.get_json() or {})
        data.pop('locale', None)
        
        command = UpdateAddressCommand(id=address_id, **data)
        address = mediator.dispatch(command)
        
        address_dict = AddressSchema().dump(address)
        return success_response(address_dict, message=_('Address updated successfully'))
    except ValueError as e:
        return error_response(_('Address not found'), status_code=404)
    except Exception as e:
        return error_response(_(str(e)), status_code=400)


@customers_bp.delete("/<int:customer_id>/addresses/<int:address_id>")
@require_roles("admin", "commercial")
def delete_address(customer_id: int, address_id: int):
    """Delete an address. Supports locale parameter (?locale=fr|ar)."""
    try:
        command = DeleteAddressCommand(id=address_id)
        mediator.dispatch(command)
        return success_response(None, message=_('Address deleted successfully'), status_code=204)
    except ValueError as e:
        return error_response(_(str(e)), status_code=404)
    except Exception as e:
        return error_response(_(str(e)), status_code=400)


# Contact Endpoints
@customers_bp.get("/<int:customer_id>/contacts")
@require_roles("admin", "commercial", "direction")
def list_contacts(customer_id: int):
    """List contacts for a customer. Supports locale parameter (?locale=fr|ar)."""
    try:
        customer_dto = mediator.dispatch(GetCustomerByIdQuery(id=customer_id))
        contacts = [
            {
                'id': c.id,
                'customer_id': c.customer_id,
                'first_name': c.first_name,
                'last_name': c.last_name,
                'function': c.function,
                'email': c.email,
                'phone': c.phone,
                'mobile': c.mobile,
                'is_primary': c.is_primary,
                'receives_quotes': c.receives_quotes,
                'receives_invoices': c.receives_invoices,
                'receives_orders': c.receives_orders
            }
            for c in (customer_dto.contacts or [])
        ]
        return success_response(contacts)
    except ValueError as e:
        return error_response(_('Customer not found'), status_code=404)
    except Exception as e:
        return error_response(_(str(e)), status_code=400)


@customers_bp.post("/<int:customer_id>/contacts")
@require_roles("admin", "commercial")
def create_contact(customer_id: int):
    """Create a contact for a customer. Supports locale parameter (?locale=fr|ar)."""
    try:
        data = ContactCreateSchema().load(request.get_json() or {})
        data.pop('locale', None)
        
        command = CreateContactCommand(customer_id=customer_id, **data)
        contact = mediator.dispatch(command)
        
        contact_dict = ContactSchema().dump(contact)
        return success_response(contact_dict, message=_('Contact created successfully'), status_code=201)
    except ValueError as e:
        return error_response(_(str(e)), status_code=400)
    except Exception as e:
        return error_response(_('Failed to create contact: {}').format(str(e)), status_code=500)


@customers_bp.put("/<int:customer_id>/contacts/<int:contact_id>")
@require_roles("admin", "commercial")
def update_contact(customer_id: int, contact_id: int):
    """Update a contact. Supports locale parameter (?locale=fr|ar)."""
    try:
        data = ContactUpdateSchema().load(request.get_json() or {})
        data.pop('locale', None)
        
        command = UpdateContactCommand(id=contact_id, **data)
        contact = mediator.dispatch(command)
        
        contact_dict = ContactSchema().dump(contact)
        return success_response(contact_dict, message=_('Contact updated successfully'))
    except ValueError as e:
        return error_response(_('Contact not found'), status_code=404)
    except Exception as e:
        return error_response(_(str(e)), status_code=400)


@customers_bp.delete("/<int:customer_id>/contacts/<int:contact_id>")
@require_roles("admin", "commercial")
def delete_contact(customer_id: int, contact_id: int):
    """Delete a contact. Supports locale parameter (?locale=fr|ar)."""
    try:
        command = DeleteContactCommand(id=contact_id)
        mediator.dispatch(command)
        return success_response(None, message=_('Contact deleted successfully'), status_code=204)
    except ValueError as e:
        return error_response(_(str(e)), status_code=404)
    except Exception as e:
        return error_response(_(str(e)), status_code=400)


# Import/Export Endpoints
@customers_bp.post("/import")
@require_roles("admin", "commercial")
def import_customers():
    """Import customers from CSV or Excel file."""
    try:
        if 'file' not in request.files:
            return error_response(_('No file provided'), status_code=400)
        
        file = request.files['file']
        if file.filename == '':
            return error_response(_('No file selected'), status_code=400)
        
        # TODO: Implement customer import
        return error_response(_('Import not yet implemented'), status_code=501)
        
    except Exception as e:
        return error_response(_('Import failed: {}').format(str(e)), status_code=500)


@customers_bp.get("/export")
@require_roles("admin", "commercial", "direction")
def export_customers():
    """Export customers to CSV or Excel file."""
    try:
        format_type = request.args.get('format', 'csv').lower()
        
        # Get all customers (or filtered)
        search = request.args.get('search')
        type_filter = request.args.get('type')
        status = request.args.get('status')
        category = request.args.get('category')
        
        query = ListCustomersQuery(
            page=1,
            per_page=10000,  # Large limit for export
            search=search,
            type=type_filter,
            status=status,
            category=category
        )
        customers = mediator.dispatch(query)
        
        # TODO: Implement customer export
        return error_response(_('Export not yet implemented'), status_code=501)
            
    except Exception as e:
        return error_response(_('Export failed: {}').format(str(e)), status_code=500)
