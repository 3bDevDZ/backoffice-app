"""Frontend route handlers for customer management pages."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_babel import get_locale, gettext as _
from app.application.common.mediator import mediator
from app.application.customers.queries.queries import ListCustomersQuery, GetCustomerByIdQuery
from app.application.customers.commands.commands import (
    CreateCustomerCommand, UpdateCustomerCommand, ArchiveCustomerCommand,
    ActivateCustomerCommand, DeactivateCustomerCommand
)
from app.application.products.pricing.queries.queries import ListPriceListsQuery
from app.security.session_auth import require_roles_or_redirect, get_current_user

customers_routes = Blueprint('customers_frontend', __name__)


@customers_routes.route('/customers')
@require_roles_or_redirect('admin', 'commercial', 'direction')
def list():
    """Render customers list page."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    # Get query parameters
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 20)), 100)
    search = request.args.get('search')
    type_filter = request.args.get('type')  # 'B2B' or 'B2C'
    status = request.args.get('status')
    category = request.args.get('category')
    
    # Fetch customers via query
    query = ListCustomersQuery(
        page=page,
        per_page=per_page,
        search=search,
        type=type_filter,
        status=status,
        category=category
    )
    customers = mediator.dispatch(query)
    
    return render_template(
        'customers/list.html',
        customers=customers,
        page=page,
        per_page=per_page,
        search=search,
        type=type_filter,
        status=status,
        category=category,
        locale=locale,
        direction=direction
    )


@customers_routes.route('/customers/new')
@require_roles_or_redirect('admin', 'commercial')
def new():
    """Render new customer form page."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    # Fetch active price lists
    price_lists_query = ListPriceListsQuery(page=1, per_page=1000, is_active=True)
    price_lists_result = mediator.dispatch(price_lists_query)
    price_lists = price_lists_result['items']
    
    return render_template(
        'customers/form.html',
        customer=None,
        price_lists=price_lists,
        locale=locale,
        direction=direction
    )


@customers_routes.route('/customers/<int:customer_id>/edit')
@require_roles_or_redirect('admin', 'commercial')
def edit(customer_id: int):
    """Render edit customer form page."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    # Fetch customer
    customer_dto = mediator.dispatch(GetCustomerByIdQuery(id=customer_id))
    
    # Fetch active price lists
    price_lists_query = ListPriceListsQuery(page=1, per_page=1000, is_active=True)
    price_lists_result = mediator.dispatch(price_lists_query)
    price_lists = price_lists_result['items']
    
    return render_template(
        'customers/form.html',
        customer=customer_dto,
        price_lists=price_lists,
        locale=locale,
        direction=direction
    )


@customers_routes.route('/customers', methods=['POST'])
@require_roles_or_redirect('admin', 'commercial')
def create():
    """Handle customer creation form submission."""
    try:
        # Get current user from session
        current_user = get_current_user()
        if not current_user:
            return jsonify({'status': 'error', 'message': _('Authentication required')}), 401
        
        # Get form data
        data = request.get_json() if request.is_json else request.form.to_dict()
        
        # Extract customer data
        from decimal import Decimal
        from datetime import datetime
        customer_data = {
            'type': data.get('type'),
            'name': data.get('name'),
            'email': data.get('email'),
            'code': data.get('code') or None,
            'phone': data.get('phone') or None,
            'mobile': data.get('mobile') or None,
            'category': data.get('category') or None,
            'notes': data.get('notes') or None,
            'payment_terms_days': int(data.get('payment_terms_days', 30)),
            'price_list_id': int(data.get('price_list_id')) if data.get('price_list_id') else None,
            'default_discount_percent': Decimal(str(data.get('default_discount_percent', 0))),
            'credit_limit': Decimal(str(data.get('credit_limit', 0))) if data.get('credit_limit') else Decimal('0'),
            'block_on_credit_exceeded': data.get('block_on_credit_exceeded', False)
        }
        
        # B2B fields
        if customer_data['type'] == 'B2B':
            customer_data['company_name'] = data.get('company_name') or None
            customer_data['siret'] = data.get('siret') or None
            customer_data['vat_number'] = data.get('vat_number') or None
            customer_data['rcs'] = data.get('rcs') or None
            customer_data['legal_form'] = data.get('legal_form') or None
        # B2C fields
        elif customer_data['type'] == 'B2C':
            customer_data['first_name'] = data.get('first_name') or None
            customer_data['last_name'] = data.get('last_name') or None
            if data.get('birth_date'):
                customer_data['birth_date'] = datetime.strptime(data.get('birth_date'), '%Y-%m-%d').date()
        
        # Create customer
        command = CreateCustomerCommand(**customer_data)
        customer = mediator.dispatch(command)
        
        flash(_('Customer created successfully'), 'success')
        
        if request.is_json:
            return jsonify({
                'status': 'success',
                'message': _('Customer created successfully'),
                'data': {'id': customer.id}
            }), 201
        else:
            return redirect(url_for('customers_frontend.list'))
            
    except ValueError as e:
        error_msg = str(e)
        if request.is_json:
            return jsonify({'status': 'error', 'message': error_msg}), 400
        flash(error_msg, 'error')
        return redirect(url_for('customers_frontend.new'))
    except Exception as e:
        error_msg = _('Failed to create customer: {}').format(str(e))
        if request.is_json:
            return jsonify({'status': 'error', 'message': error_msg}), 500
        flash(error_msg, 'error')
        return redirect(url_for('customers_frontend.new'))


@customers_routes.route('/customers/<int:customer_id>', methods=['PUT', 'POST'])
@require_roles_or_redirect('admin', 'commercial')
def update_customer(customer_id: int):
    """Handle customer update form submission."""
    try:
        # Get current user from session
        current_user = get_current_user()
        if not current_user:
            return jsonify({'status': 'error', 'message': _('Authentication required')}), 401
        
        # Get form data
        data = request.get_json() if request.is_json else request.form.to_dict()
        
        # Extract customer data
        from decimal import Decimal
        from datetime import datetime
        update_data = {}
        if 'name' in data:
            update_data['name'] = data.get('name')
        if 'email' in data:
            update_data['email'] = data.get('email')
        if 'phone' in data:
            update_data['phone'] = data.get('phone') or None
        if 'mobile' in data:
            update_data['mobile'] = data.get('mobile') or None
        if 'category' in data:
            update_data['category'] = data.get('category') or None
        if 'notes' in data:
            update_data['notes'] = data.get('notes') or None
        if 'payment_terms_days' in data:
            update_data['payment_terms_days'] = int(data.get('payment_terms_days'))
        if 'price_list_id' in data:
            update_data['price_list_id'] = int(data.get('price_list_id')) if data.get('price_list_id') else None
        if 'default_discount_percent' in data:
            update_data['default_discount_percent'] = Decimal(str(data.get('default_discount_percent')))
        if 'credit_limit' in data:
            update_data['credit_limit'] = Decimal(str(data.get('credit_limit'))) if data.get('credit_limit') else Decimal('0')
        if 'block_on_credit_exceeded' in data:
            update_data['block_on_credit_exceeded'] = data.get('block_on_credit_exceeded', False)
        
        # B2B fields
        if 'company_name' in data:
            update_data['company_name'] = data.get('company_name') or None
        if 'siret' in data:
            update_data['siret'] = data.get('siret') or None
        if 'vat_number' in data:
            update_data['vat_number'] = data.get('vat_number') or None
        if 'rcs' in data:
            update_data['rcs'] = data.get('rcs') or None
        if 'legal_form' in data:
            update_data['legal_form'] = data.get('legal_form') or None
        # B2C fields
        if 'first_name' in data:
            update_data['first_name'] = data.get('first_name') or None
        if 'last_name' in data:
            update_data['last_name'] = data.get('last_name') or None
        if 'birth_date' in data and data.get('birth_date'):
            update_data['birth_date'] = datetime.strptime(data.get('birth_date'), '%Y-%m-%d').date()
        
        # Update customer
        from app.application.customers.commands.commands import UpdateCustomerCommand
        command = UpdateCustomerCommand(id=customer_id, **update_data)
        mediator.dispatch(command)
        
        flash(_('Customer updated successfully'), 'success')
        
        if request.is_json:
            return jsonify({
                'status': 'success',
                'message': _('Customer updated successfully')
            })
        else:
            return redirect(url_for('customers_frontend.list'))
            
    except ValueError as e:
        error_msg = str(e)
        if request.is_json:
            return jsonify({'status': 'error', 'message': error_msg}), 400
        flash(error_msg, 'error')
        return redirect(url_for('customers_frontend.edit', customer_id=customer_id))
    except Exception as e:
        error_msg = _('Failed to update customer: {}').format(str(e))
        if request.is_json:
            return jsonify({'status': 'error', 'message': error_msg}), 500
        flash(error_msg, 'error')
        return redirect(url_for('customers_frontend.edit', customer_id=customer_id))


@customers_routes.route('/customers/<int:customer_id>/activate', methods=['POST'])
@require_roles_or_redirect('admin', 'commercial')
def activate_customer(customer_id: int):
    """Activate a customer."""
    try:
        command = ActivateCustomerCommand(id=customer_id)
        mediator.dispatch(command)
        
        if request.is_json:
            return jsonify({'status': 'success', 'message': _('Customer activated successfully')})
        flash(_('Customer activated successfully'), 'success')
        return redirect(url_for('customers_frontend.list'))
    except Exception as e:
        error_msg = str(e)
        if request.is_json:
            return jsonify({'status': 'error', 'message': error_msg}), 400
        flash(error_msg, 'error')
        return redirect(url_for('customers_frontend.list'))


@customers_routes.route('/customers/<int:customer_id>/deactivate', methods=['POST'])
@require_roles_or_redirect('admin', 'commercial')
def deactivate_customer(customer_id: int):
    """Deactivate a customer."""
    try:
        command = DeactivateCustomerCommand(id=customer_id)
        mediator.dispatch(command)
        
        if request.is_json:
            return jsonify({'status': 'success', 'message': _('Customer deactivated successfully')})
        flash(_('Customer deactivated successfully'), 'success')
        return redirect(url_for('customers_frontend.list'))
    except Exception as e:
        error_msg = str(e)
        if request.is_json:
            return jsonify({'status': 'error', 'message': error_msg}), 400
        flash(error_msg, 'error')
        return redirect(url_for('customers_frontend.list'))


@customers_routes.route('/customers/<int:customer_id>/archive', methods=['POST'])
@require_roles_or_redirect('admin', 'commercial')
def archive_customer(customer_id: int):
    """Archive a customer."""
    try:
        command = ArchiveCustomerCommand(id=customer_id)
        mediator.dispatch(command)
        
        if request.is_json:
            return jsonify({'status': 'success', 'message': _('Customer archived successfully')})
        flash(_('Customer archived successfully'), 'success')
        return redirect(url_for('customers_frontend.list'))
    except Exception as e:
        error_msg = str(e)
        if request.is_json:
            return jsonify({'status': 'error', 'message': error_msg}), 400
        flash(error_msg, 'error')
        return redirect(url_for('customers_frontend.list'))


@customers_routes.route('/customers/export')
@require_roles_or_redirect('admin', 'commercial', 'direction')
def export():
    """Handle customer export request - redirects to API endpoint."""
    # Build API URL with query parameters
    search = request.args.get('search')
    type_filter = request.args.get('type')
    status = request.args.get('status')
    category = request.args.get('category')
    format_type = request.args.get('format', 'csv')
    
    # Build query string
    query_parts = [f'format={format_type}']
    if search:
        query_parts.append(f'search={search}')
    if type_filter:
        query_parts.append(f'type={type_filter}')
    if status:
        query_parts.append(f'status={status}')
    if category:
        query_parts.append(f'category={category}')
    
    api_url = f'/api/customers/export?{"&".join(query_parts)}'
    return redirect(api_url)
