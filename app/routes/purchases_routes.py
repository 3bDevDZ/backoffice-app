"""Frontend route handlers for purchase management pages."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_babel import get_locale, gettext as _
from app.application.common.mediator import mediator
from app.application.purchases.queries.queries import (
    ListSuppliersQuery, GetSupplierByIdQuery,
    ListPurchaseOrdersQuery, GetPurchaseOrderByIdQuery
)
from app.security.session_auth import require_roles_or_redirect, get_current_user

purchases_routes = Blueprint('purchases_frontend', __name__)


# Supplier Routes
@purchases_routes.route('/suppliers')
@require_roles_or_redirect('admin', 'commercial', 'direction')
def list_suppliers():
    """Render suppliers list page."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    # Get query parameters
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 20)), 100)
    search = request.args.get('search')
    status = request.args.get('status')
    category = request.args.get('category')
    
    # Fetch suppliers via query
    query = ListSuppliersQuery(
        page=page,
        per_page=per_page,
        search=search,
        status=status,
        category=category
    )
    suppliers = mediator.dispatch(query)
    
    return render_template(
        'purchases/suppliers/list.html',
        suppliers=suppliers,
        page=page,
        per_page=per_page,
        search=search,
        status=status,
        category=category,
        locale=locale,
        direction=direction
    )


@purchases_routes.route('/suppliers/new')
@require_roles_or_redirect('admin', 'commercial')
def new_supplier():
    """Render new supplier form page."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    return render_template(
        'purchases/suppliers/form.html',
        supplier=None,
        locale=locale,
        direction=direction
    )


@purchases_routes.route('/suppliers/<int:supplier_id>/edit')
@require_roles_or_redirect('admin', 'commercial')
def edit_supplier(supplier_id: int):
    """Render edit supplier form page."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    # Fetch supplier
    supplier_dto = mediator.dispatch(GetSupplierByIdQuery(id=supplier_id))
    
    return render_template(
        'purchases/suppliers/form.html',
        supplier=supplier_dto,
        locale=locale,
        direction=direction
    )


@purchases_routes.route('/suppliers', methods=['POST'])
@require_roles_or_redirect('admin', 'commercial')
def create_supplier():
    """Handle supplier creation form submission."""
    try:
        # Get current user from session
        current_user = get_current_user()
        if not current_user:
            return jsonify({'status': 'error', 'message': _('Authentication required')}), 401
        
        # Get form data
        data = request.get_json() if request.is_json else request.form.to_dict()
        
        # Extract supplier data
        from decimal import Decimal
        from app.application.purchases.commands.commands import CreateSupplierCommand, CreateSupplierConditionsCommand
        supplier_data = {
            'name': data.get('name'),
            'email': data.get('email'),
            'phone': data.get('phone') or None,
            'mobile': data.get('mobile') or None,
            'company_name': data.get('company_name') or None,
            'siret': data.get('siret') or None,
            'vat_number': data.get('vat_number') or None,
            'rcs': data.get('rcs') or None,
            'legal_form': data.get('legal_form') or None,
            'category': data.get('category') or None,
            'notes': data.get('notes') or None
        }
        
        # Create supplier
        command = CreateSupplierCommand(**supplier_data)
        supplier = mediator.dispatch(command)
        
        # Create supplier conditions if provided
        if any(key in data for key in ['payment_terms_days', 'default_discount_percent', 'minimum_order_amount', 'delivery_lead_time_days']):
            conditions_data = {
                'supplier_id': supplier.id,
                'payment_terms_days': int(data.get('payment_terms_days', 30)),
                'default_discount_percent': Decimal(str(data.get('default_discount_percent', 0))),
                'minimum_order_amount': Decimal(str(data.get('minimum_order_amount', 0))) if data.get('minimum_order_amount') else None,
                'delivery_lead_time_days': int(data.get('delivery_lead_time_days', 7)) if data.get('delivery_lead_time_days') else None
            }
            conditions_command = CreateSupplierConditionsCommand(**conditions_data)
            mediator.dispatch(conditions_command)
        
        flash(_('Supplier created successfully'), 'success')
        
        if request.is_json:
            return jsonify({
                'status': 'success',
                'message': _('Supplier created successfully'),
                'data': {'id': supplier.id}
            }), 201
        else:
            return redirect(url_for('purchases_frontend.list_suppliers'))
            
    except ValueError as e:
        error_msg = str(e)
        if request.is_json:
            return jsonify({'status': 'error', 'message': error_msg}), 400
        flash(error_msg, 'error')
        return redirect(url_for('purchases_frontend.new_supplier'))
    except Exception as e:
        error_msg = _('Failed to create supplier: {}').format(str(e))
        if request.is_json:
            return jsonify({'status': 'error', 'message': error_msg}), 500
        flash(error_msg, 'error')
        return redirect(url_for('purchases_frontend.new_supplier'))


@purchases_routes.route('/suppliers/<int:supplier_id>', methods=['PUT', 'POST'])
@require_roles_or_redirect('admin', 'commercial')
def update_supplier(supplier_id: int):
    """Handle supplier update form submission."""
    try:
        # Get current user from session
        current_user = get_current_user()
        if not current_user:
            return jsonify({'status': 'error', 'message': _('Authentication required')}), 401
        
        # Get form data
        data = request.get_json() if request.is_json else request.form.to_dict()
        
        # Extract supplier data
        from app.application.purchases.commands.commands import UpdateSupplierCommand
        update_data = {}
        if 'name' in data:
            update_data['name'] = data.get('name')
        if 'email' in data:
            update_data['email'] = data.get('email')
        if 'phone' in data:
            update_data['phone'] = data.get('phone') or None
        if 'mobile' in data:
            update_data['mobile'] = data.get('mobile') or None
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
        if 'category' in data:
            update_data['category'] = data.get('category') or None
        if 'notes' in data:
            update_data['notes'] = data.get('notes') or None
        
        # Update supplier
        command = UpdateSupplierCommand(id=supplier_id, **update_data)
        mediator.dispatch(command)
        
        flash(_('Supplier updated successfully'), 'success')
        
        if request.is_json:
            return jsonify({
                'status': 'success',
                'message': _('Supplier updated successfully')
            })
        else:
            return redirect(url_for('purchases_frontend.list_suppliers'))
            
    except ValueError as e:
        error_msg = str(e)
        if request.is_json:
            return jsonify({'status': 'error', 'message': error_msg}), 400
        flash(error_msg, 'error')
        return redirect(url_for('purchases_frontend.edit_supplier', supplier_id=supplier_id))
    except Exception as e:
        error_msg = _('Failed to update supplier: {}').format(str(e))
        if request.is_json:
            return jsonify({'status': 'error', 'message': error_msg}), 500
        flash(error_msg, 'error')
        return redirect(url_for('purchases_frontend.edit_supplier', supplier_id=supplier_id))


@purchases_routes.route('/suppliers/<int:supplier_id>/activate', methods=['POST'])
@require_roles_or_redirect('admin', 'commercial')
def activate_supplier(supplier_id: int):
    """Activate a supplier."""
    try:
        from app.application.purchases.commands.commands import ActivateSupplierCommand
        command = ActivateSupplierCommand(id=supplier_id)
        mediator.dispatch(command)
        
        if request.is_json:
            return jsonify({'status': 'success', 'message': _('Supplier activated successfully')})
        flash(_('Supplier activated successfully'), 'success')
        return redirect(url_for('purchases_frontend.list_suppliers'))
    except Exception as e:
        error_msg = str(e)
        if request.is_json:
            return jsonify({'status': 'error', 'message': error_msg}), 400
        flash(error_msg, 'error')
        return redirect(url_for('purchases_frontend.list_suppliers'))


@purchases_routes.route('/suppliers/<int:supplier_id>/deactivate', methods=['POST'])
@require_roles_or_redirect('admin', 'commercial')
def deactivate_supplier(supplier_id: int):
    """Deactivate a supplier."""
    try:
        from app.application.purchases.commands.commands import DeactivateSupplierCommand
        command = DeactivateSupplierCommand(id=supplier_id)
        mediator.dispatch(command)
        
        if request.is_json:
            return jsonify({'status': 'success', 'message': _('Supplier deactivated successfully')})
        flash(_('Supplier deactivated successfully'), 'success')
        return redirect(url_for('purchases_frontend.list_suppliers'))
    except Exception as e:
        error_msg = str(e)
        if request.is_json:
            return jsonify({'status': 'error', 'message': error_msg}), 400
        flash(error_msg, 'error')
        return redirect(url_for('purchases_frontend.list_suppliers'))


@purchases_routes.route('/suppliers/<int:supplier_id>/archive', methods=['POST'])
@require_roles_or_redirect('admin', 'commercial')
def archive_supplier(supplier_id: int):
    """Archive a supplier."""
    try:
        from app.application.purchases.commands.commands import ArchiveSupplierCommand
        command = ArchiveSupplierCommand(id=supplier_id)
        mediator.dispatch(command)
        
        if request.is_json:
            return jsonify({'status': 'success', 'message': _('Supplier archived successfully')})
        flash(_('Supplier archived successfully'), 'success')
        return redirect(url_for('purchases_frontend.list_suppliers'))
    except Exception as e:
        error_msg = str(e)
        if request.is_json:
            return jsonify({'status': 'error', 'message': error_msg}), 400
        flash(error_msg, 'error')
        return redirect(url_for('purchases_frontend.list_suppliers'))


# Purchase Order Routes
@purchases_routes.route('/purchase-orders')
@require_roles_or_redirect('admin', 'commercial', 'direction')
def list_purchase_orders():
    """Render purchase orders list page."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    # Get query parameters
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 20)), 100)
    supplier_id = request.args.get('supplier_id', type=int)
    status = request.args.get('status')
    search = request.args.get('search')
    
    # Fetch purchase orders via query
    query = ListPurchaseOrdersQuery(
        page=page,
        per_page=per_page,
        supplier_id=supplier_id,
        status=status,
        search=search
    )
    orders = mediator.dispatch(query)
    
    return render_template(
        'purchases/orders/list.html',
        orders=orders,
        page=page,
        per_page=per_page,
        supplier_id=supplier_id,
        status=status,
        search=search,
        locale=locale,
        direction=direction
    )


@purchases_routes.route('/purchase-orders/new')
@require_roles_or_redirect('admin', 'commercial')
def new_purchase_order():
    """Render new purchase order form page."""
    from datetime import date as date_type
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    # Fetch suppliers for dropdown
    suppliers_query = ListSuppliersQuery(page=1, per_page=1000, status='active')
    suppliers = mediator.dispatch(suppliers_query)
    
    # Fetch products for dropdown (we'll use API call in template instead)
    from app.application.products.queries.queries import ListProductsQuery, ListCategoriesQuery
    products_query = ListProductsQuery(page=1, per_page=1000, status='active')
    products = mediator.dispatch(products_query)
    
    # Fetch categories for quick product creation
    categories_query = ListCategoriesQuery()
    categories = mediator.dispatch(categories_query)
    
    # Fetch locations for receiving (warehouse locations only)
    from app.application.stock.queries.queries import GetLocationHierarchyQuery
    locations_query = GetLocationHierarchyQuery(
        location_type='warehouse',
        include_inactive=False
    )
    locations = mediator.dispatch(locations_query)
    
    return render_template(
        'purchases/orders/form.html',
        order=None,
        suppliers=suppliers,
        products=products,
        categories=categories,
        locations=locations,
        today=date_type.today().strftime('%Y-%m-%d'),
        locale=locale,
        direction=direction
    )


@purchases_routes.route('/purchase-orders/<int:order_id>/edit')
@require_roles_or_redirect('admin', 'commercial')
def edit_purchase_order(order_id: int):
    """Render edit purchase order form page."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    # Fetch purchase order
    order_dto = mediator.dispatch(GetPurchaseOrderByIdQuery(id=order_id))
    
    # Fetch suppliers for dropdown
    suppliers_query = ListSuppliersQuery(page=1, per_page=1000, status='active')
    suppliers = mediator.dispatch(suppliers_query)
    
    # Fetch products for dropdown
    from app.application.products.queries.queries import ListProductsQuery, ListCategoriesQuery
    products_query = ListProductsQuery(page=1, per_page=1000, status='active')
    products = mediator.dispatch(products_query)
    
    # Fetch categories for quick product creation
    categories_query = ListCategoriesQuery()
    categories = mediator.dispatch(categories_query)
    
    # Fetch locations for receiving (warehouse locations only)
    from app.application.stock.queries.queries import GetLocationHierarchyQuery
    locations_query = GetLocationHierarchyQuery(
        location_type='warehouse',
        include_inactive=False
    )
    locations = mediator.dispatch(locations_query)
    
    return render_template(
        'purchases/orders/form.html',
        order=order_dto,
        suppliers=suppliers,
        products=products,
        categories=categories,
        locations=locations,
        locale=locale,
        direction=direction
    )


@purchases_routes.route('/purchase-orders', methods=['POST'])
@require_roles_or_redirect('admin', 'commercial')
def create_purchase_order():
    """Handle purchase order creation form submission."""
    from flask import session, jsonify
    from app.security.session_auth import get_current_user
    from app.application.purchases.commands.commands import CreatePurchaseOrderCommand, AddPurchaseOrderLineCommand
    from app.application.purchases.queries.queries import GetPurchaseOrderByIdQuery
    
    try:
        # Get current user from session
        current_user = get_current_user()
        if not current_user:
            return jsonify({'status': 'error', 'message': _('Authentication required')}), 401
        
        # Get form data
        data = request.get_json() if request.is_json else request.form.to_dict()
        
        # Extract order data
        from datetime import datetime
        
        # Validate required fields
        if 'supplier_id' not in data or not data.get('supplier_id'):
            raise ValueError(_('Supplier ID is required'))
        
        supplier_id = int(data.get('supplier_id'))
        order_date_str = data.get('order_date')
        expected_delivery_date_str = data.get('expected_delivery_date') or None
        notes = data.get('notes') or None
        internal_notes = data.get('internal_notes') or None
        
        # Convert date strings to date objects
        if not order_date_str:
            raise ValueError(_('Order date is required'))
        
        try:
            order_date = datetime.strptime(order_date_str, '%Y-%m-%d').date()
        except ValueError:
            raise ValueError(_('Invalid order date format. Expected YYYY-MM-DD'))
        
        if expected_delivery_date_str:
            try:
                expected_delivery_date = datetime.strptime(expected_delivery_date_str, '%Y-%m-%d').date()
            except ValueError:
                raise ValueError(_('Invalid expected delivery date format. Expected YYYY-MM-DD'))
        else:
            expected_delivery_date = None
        
        # Create purchase order
        command = CreatePurchaseOrderCommand(
            supplier_id=supplier_id,
            order_date=order_date,
            expected_delivery_date=expected_delivery_date,
            notes=notes,
            internal_notes=internal_notes,
            created_by=current_user.id
        )
        order_result = mediator.dispatch(command)
        
        # Get order ID from result (handler returns SimpleNamespace with ID)
        order_id = order_result.id
        
        # Add lines if provided
        from decimal import Decimal
        lines = data.get('lines', [])
        for line_data in lines:
            if 'product_id' not in line_data or not line_data.get('product_id'):
                raise ValueError(_('Product ID is required for each line'))
            if 'quantity' not in line_data or not line_data.get('quantity'):
                raise ValueError(_('Quantity is required for each line'))
            if 'unit_price' not in line_data or line_data.get('unit_price') is None:
                raise ValueError(_('Unit price is required for each line'))
            
            line_command = AddPurchaseOrderLineCommand(
                purchase_order_id=order_id,
                product_id=int(line_data.get('product_id')),
                quantity=Decimal(str(line_data.get('quantity'))),
                unit_price=Decimal(str(line_data.get('unit_price'))),
                discount_percent=Decimal(str(line_data.get('discount_percent', 0))),
                tax_rate=Decimal(str(line_data.get('tax_rate', 20.0)))
            )
            mediator.dispatch(line_command)
        
        flash(_('Purchase order created successfully'), 'success')
        
        if request.is_json:
            order_dto = mediator.dispatch(GetPurchaseOrderByIdQuery(id=order_id))
            return jsonify({
                'status': 'success',
                'message': _('Purchase order created successfully'),
                'data': {'id': order_dto.id}
            }), 201
        else:
            return redirect(url_for('purchases_frontend.list_purchase_orders'))
            
    except ValueError as e:
        error_msg = str(e)
        if request.is_json:
            return jsonify({'status': 'error', 'message': error_msg}), 400
        flash(error_msg, 'error')
        return redirect(url_for('purchases_frontend.new_purchase_order'))
    except Exception as e:
        error_msg = _('Failed to create purchase order: {}').format(str(e))
        if request.is_json:
            return jsonify({'status': 'error', 'message': error_msg}), 500
        flash(error_msg, 'error')
        return redirect(url_for('purchases_frontend.new_purchase_order'))


@purchases_routes.route('/purchase-orders/<int:order_id>', methods=['PUT', 'POST'])
@require_roles_or_redirect('admin', 'commercial')
def update_purchase_order(order_id: int):
    """Handle purchase order update form submission."""
    try:
        # Get current user from session
        current_user = get_current_user()
        if not current_user:
            return jsonify({'status': 'error', 'message': _('Authentication required')}), 401
        
        # Get form data
        data = request.get_json() if request.is_json else request.form.to_dict()
        
        # Extract order data
        from app.application.purchases.commands.commands import UpdatePurchaseOrderCommand
        from datetime import datetime
        update_data = {}
        if 'supplier_id' in data:
            update_data['supplier_id'] = int(data.get('supplier_id'))
        if 'order_date' in data:
            order_date_str = data.get('order_date')
            update_data['order_date'] = datetime.strptime(order_date_str, '%Y-%m-%d').date() if order_date_str else None
        if 'expected_delivery_date' in data:
            expected_delivery_date_str = data.get('expected_delivery_date') or None
            update_data['expected_delivery_date'] = datetime.strptime(expected_delivery_date_str, '%Y-%m-%d').date() if expected_delivery_date_str else None
        if 'notes' in data:
            update_data['notes'] = data.get('notes') or None
        if 'internal_notes' in data:
            update_data['internal_notes'] = data.get('internal_notes') or None
        
        # Update purchase order
        command = UpdatePurchaseOrderCommand(id=order_id, **update_data)
        mediator.dispatch(command)
        
        flash(_('Purchase order updated successfully'), 'success')
        
        if request.is_json:
            return jsonify({
                'status': 'success',
                'message': _('Purchase order updated successfully')
            })
        else:
            return redirect(url_for('purchases_frontend.list_purchase_orders'))
            
    except ValueError as e:
        error_msg = str(e)
        if request.is_json:
            return jsonify({'status': 'error', 'message': error_msg}), 400
        flash(error_msg, 'error')
        return redirect(url_for('purchases_frontend.edit_purchase_order', order_id=order_id))
    except Exception as e:
        error_msg = _('Failed to update purchase order: {}').format(str(e))
        if request.is_json:
            return jsonify({'status': 'error', 'message': error_msg}), 500
        flash(error_msg, 'error')
        return redirect(url_for('purchases_frontend.edit_purchase_order', order_id=order_id))


@purchases_routes.route('/purchase-orders/<int:order_id>/confirm', methods=['POST'])
@require_roles_or_redirect('admin', 'commercial')
def confirm_purchase_order(order_id: int):
    """Confirm a purchase order."""
    try:
        current_user = get_current_user()
        if not current_user:
            flash(_('Authentication required'), 'error')
            return redirect(url_for('purchases_frontend.edit_purchase_order', order_id=order_id))
        
        from app.application.purchases.commands.commands import ConfirmPurchaseOrderCommand
        
        command = ConfirmPurchaseOrderCommand(id=order_id, confirmed_by=current_user.id)
        mediator.dispatch(command)
        
        flash(_('Purchase order confirmed successfully'), 'success')
        return redirect(url_for('purchases_frontend.edit_purchase_order', order_id=order_id))
    except ValueError as e:
        error_msg = str(e)
        flash(error_msg, 'error')
        return redirect(url_for('purchases_frontend.edit_purchase_order', order_id=order_id))
    except Exception as e:
        flash(str(e), 'error')
        return redirect(url_for('purchases_frontend.edit_purchase_order', order_id=order_id))


@purchases_routes.route('/purchase-orders/<int:order_id>/cancel', methods=['POST'])
@require_roles_or_redirect('admin', 'commercial')
def cancel_purchase_order(order_id: int):
    """Cancel a purchase order."""
    try:
        from app.application.purchases.commands.commands import CancelPurchaseOrderCommand
        
        command = CancelPurchaseOrderCommand(id=order_id)
        mediator.dispatch(command)
        
        flash(_('Purchase order canceled successfully'), 'success')
        return redirect(url_for('purchases_frontend.edit_purchase_order', order_id=order_id))
    except ValueError as e:
        error_msg = str(e)
        flash(error_msg, 'error')
        return redirect(url_for('purchases_frontend.edit_purchase_order', order_id=order_id))
    except Exception as e:
        flash(str(e), 'error')
        return redirect(url_for('purchases_frontend.edit_purchase_order', order_id=order_id))


@purchases_routes.route('/purchase-orders/<int:order_id>/receive-line', methods=['POST'])
@require_roles_or_redirect('admin', 'commercial', 'logistics')
def receive_purchase_order_line(order_id: int):
    """Receive a purchase order line (update quantity_received)."""
    try:
        from app.application.purchases.commands.commands import ReceivePurchaseOrderLineCommand
        from decimal import Decimal
        
        data = request.form.to_dict()
        line_id = int(data.get('line_id'))
        quantity_received = Decimal(str(data.get('quantity_received', 0)))
        location_id = int(data.get('location_id')) if data.get('location_id') else None
        
        command = ReceivePurchaseOrderLineCommand(
            purchase_order_id=order_id,
            line_id=line_id,
            quantity_received=quantity_received,
            location_id=location_id
        )
        mediator.dispatch(command)
        
        flash(_('Line received successfully. Stock has been updated immediately.'), 'success')
        return redirect(url_for('purchases_frontend.edit_purchase_order', order_id=order_id))
    except ValueError as e:
        error_msg = str(e)
        flash(error_msg, 'error')
        return redirect(url_for('purchases_frontend.edit_purchase_order', order_id=order_id))
    except Exception as e:
        flash(str(e), 'error')
        return redirect(url_for('purchases_frontend.edit_purchase_order', order_id=order_id))

