"""Frontend route handlers for purchase management pages."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_babel import get_locale, gettext as _
from app.application.common.mediator import mediator
from app.application.purchases.queries.queries import (
    ListSuppliersQuery, GetSupplierByIdQuery,
    ListPurchaseOrdersQuery, GetPurchaseOrderByIdQuery
)
from app.application.purchases.requests.queries.queries import (
    ListPurchaseRequestsQuery, GetPurchaseRequestByIdQuery
)
from app.application.purchases.receipts.queries.queries import (
    ListPurchaseReceiptsQuery, GetPurchaseReceiptByIdQuery
)
from app.application.purchases.invoices.queries.queries import (
    ListSupplierInvoicesQuery, GetSupplierInvoiceByIdQuery
)
from app.application.stock.queries.queries import GetLocationHierarchyQuery
from app.application.products.queries.queries import ListProductsQuery
from app.application.purchases.queries.queries import ListSuppliersQuery
from app.security.session_auth import require_roles_or_redirect, get_current_user
from datetime import date, datetime
from decimal import Decimal
import re

purchases_routes = Blueprint('purchases_frontend', __name__)


# ============================================================================
# Supplier Routes
# ============================================================================

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
    
    # Ensure suppliers is a list (not None)
    if suppliers is None:
        suppliers = []
    
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
    supplier = mediator.dispatch(GetSupplierByIdQuery(id=supplier_id))
    if not supplier:
        flash(_('Supplier not found'), 'error')
        return redirect(url_for('purchases_frontend.list_suppliers'))
    
    return render_template(
        'purchases/suppliers/form.html',
        supplier=supplier,
        locale=locale,
        direction=direction
    )


@purchases_routes.route('/suppliers', methods=['POST'])
@require_roles_or_redirect('admin', 'commercial')
def create_supplier():
    """Handle supplier creation form submission."""
    try:
        from app.application.purchases.commands.commands import CreateSupplierCommand
        
        # Get form data
        command = CreateSupplierCommand(
            name=request.form.get('name', '').strip(),
            email=request.form.get('email', '').strip(),
            code=request.form.get('code', '').strip() or None,
            phone=request.form.get('phone', '').strip() or None,
            mobile=request.form.get('mobile', '').strip() or None,
            category=request.form.get('category') or None,
            notes=request.form.get('notes') or None,
            company_name=request.form.get('company_name', '').strip() or None,
            siret=request.form.get('siret', '').strip() or None,
            vat_number=request.form.get('vat_number', '').strip() or None,
            rcs=request.form.get('rcs', '').strip() or None,
            legal_form=request.form.get('legal_form') or None,
            payment_terms_days=int(request.form.get('payment_terms_days', 30)),
            default_discount_percent=Decimal(str(request.form.get('default_discount_percent', 0))),
            minimum_order_amount=Decimal(str(request.form.get('minimum_order_amount', 0))),
            delivery_lead_time_days=int(request.form.get('delivery_lead_time_days', 7))
        )
        
        supplier = mediator.dispatch(command)
        
        flash(_('Supplier created successfully'), 'success')
        return redirect(url_for('purchases_frontend.edit_supplier', supplier_id=supplier.id))
    except Exception as e:
        flash(_('An error occurred: %(error)s', error=str(e)), 'error')
        return redirect(url_for('purchases_frontend.new_supplier'))


@purchases_routes.route('/suppliers/<int:supplier_id>', methods=['POST'])
@require_roles_or_redirect('admin', 'commercial')
def update_supplier(supplier_id: int):
    """Handle supplier update form submission."""
    try:
        from app.application.purchases.commands.commands import UpdateSupplierCommand
        
        # Get form data
        command = UpdateSupplierCommand(
            id=supplier_id,
            name=request.form.get('name', '').strip() or None,
            email=request.form.get('email', '').strip() or None,
            phone=request.form.get('phone', '').strip() or None,
            mobile=request.form.get('mobile', '').strip() or None,
            category=request.form.get('category') or None,
            notes=request.form.get('notes') or None,
            company_name=request.form.get('company_name', '').strip() or None,
            siret=request.form.get('siret', '').strip() or None,
            vat_number=request.form.get('vat_number', '').strip() or None,
            rcs=request.form.get('rcs', '').strip() or None,
            legal_form=request.form.get('legal_form') or None
        )
        
        supplier = mediator.dispatch(command)
        
        flash(_('Supplier updated successfully'), 'success')
        return redirect(url_for('purchases_frontend.edit_supplier', supplier_id=supplier_id))
    except Exception as e:
        flash(_('An error occurred: %(error)s', error=str(e)), 'error')
        return redirect(url_for('purchases_frontend.edit_supplier', supplier_id=supplier_id))


@purchases_routes.route('/suppliers/<int:supplier_id>/activate', methods=['POST'])
@require_roles_or_redirect('admin', 'commercial')
def activate_supplier(supplier_id: int):
    """Activate a supplier."""
    try:
        from app.application.purchases.commands.commands import ActivateSupplierCommand
        
        command = ActivateSupplierCommand(id=supplier_id)
        mediator.dispatch(command)
        
        if request.is_json or request.content_type == 'application/json':
            return jsonify({'status': 'success', 'message': _('Supplier activated successfully')})
        else:
            flash(_('Supplier activated successfully'), 'success')
            return redirect(url_for('purchases_frontend.list_suppliers'))
    except Exception as e:
        if request.is_json or request.content_type == 'application/json':
            return jsonify({'status': 'error', 'message': str(e)}), 400
        else:
            flash(_('An error occurred: %(error)s', error=str(e)), 'error')
            return redirect(url_for('purchases_frontend.list_suppliers'))


@purchases_routes.route('/suppliers/<int:supplier_id>/deactivate', methods=['POST'])
@require_roles_or_redirect('admin', 'commercial')
def deactivate_supplier(supplier_id: int):
    """Deactivate a supplier."""
    try:
        from app.application.purchases.commands.commands import DeactivateSupplierCommand
        
        command = DeactivateSupplierCommand(id=supplier_id)
        mediator.dispatch(command)
        
        if request.is_json or request.content_type == 'application/json':
            return jsonify({'status': 'success', 'message': _('Supplier deactivated successfully')})
        else:
            flash(_('Supplier deactivated successfully'), 'success')
            return redirect(url_for('purchases_frontend.list_suppliers'))
    except Exception as e:
        if request.is_json or request.content_type == 'application/json':
            return jsonify({'status': 'error', 'message': str(e)}), 400
        else:
            flash(_('An error occurred: %(error)s', error=str(e)), 'error')
            return redirect(url_for('purchases_frontend.list_suppliers'))


@purchases_routes.route('/suppliers/<int:supplier_id>/archive', methods=['POST'])
@require_roles_or_redirect('admin', 'commercial')
def archive_supplier(supplier_id: int):
    """Archive a supplier."""
    try:
        from app.application.purchases.commands.commands import ArchiveSupplierCommand
        
        command = ArchiveSupplierCommand(id=supplier_id)
        mediator.dispatch(command)
        
        if request.is_json or request.content_type == 'application/json':
            return jsonify({'status': 'success', 'message': _('Supplier archived successfully')})
        else:
            flash(_('Supplier archived successfully'), 'success')
            return redirect(url_for('purchases_frontend.list_suppliers'))
    except Exception as e:
        if request.is_json or request.content_type == 'application/json':
            return jsonify({'status': 'error', 'message': str(e)}), 400
        else:
            flash(_('An error occurred: %(error)s', error=str(e)), 'error')
            return redirect(url_for('purchases_frontend.list_suppliers'))


# ============================================================================
# Purchase Order Routes
# ============================================================================

@purchases_routes.route('/purchase-orders')
@require_roles_or_redirect('admin', 'commercial', 'direction')
def list_purchase_orders():
    """Render purchase orders list page."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    # Get query parameters
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 20)), 100)
    search = request.args.get('search')
    supplier_id = request.args.get('supplier_id', type=int)
    status = request.args.get('status')
    
    # Fetch purchase orders via query
    query = ListPurchaseOrdersQuery(
        page=page,
        per_page=per_page,
        search=search,
        supplier_id=supplier_id,
        status=status
    )
    orders = mediator.dispatch(query)
    
    return render_template(
        'purchases/orders/list.html',
        orders=orders,
        page=page,
        per_page=per_page,
        search=search,
        supplier_id=supplier_id,
        status=status,
        locale=locale,
        direction=direction
    )


@purchases_routes.route('/purchase-orders/new')
@require_roles_or_redirect('admin', 'commercial')
def new_purchase_order():
    """Render new purchase order form page."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    # Fetch suppliers for dropdown
    suppliers = mediator.dispatch(ListSuppliersQuery(page=1, per_page=1000, status='active'))
    
    return render_template(
        'purchases/orders/form.html',
        order=None,
        suppliers=suppliers,
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
    order = mediator.dispatch(GetPurchaseOrderByIdQuery(id=order_id))
    if not order:
        flash(_('Purchase order not found'), 'error')
        return redirect(url_for('purchases_frontend.list_purchase_orders'))
    
    # Fetch suppliers for dropdown
    suppliers = mediator.dispatch(ListSuppliersQuery(page=1, per_page=1000, status='active'))
    
    # Fetch products for line items
    products = mediator.dispatch(ListProductsQuery(page=1, per_page=1000, status='active'))
    
    return render_template(
        'purchases/orders/form.html',
        order=order,
        suppliers=suppliers,
        products=products,
        locale=locale,
        direction=direction
    )


@purchases_routes.route('/purchase-orders/<int:order_id>')
@require_roles_or_redirect('admin', 'commercial', 'direction')
def view_purchase_order(order_id: int):
    """View a purchase order (read-only)."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    # Fetch purchase order
    order = mediator.dispatch(GetPurchaseOrderByIdQuery(id=order_id))
    if not order:
        flash(_('Purchase order not found'), 'error')
        return redirect(url_for('purchases_frontend.list_purchase_orders'))
    
    return render_template(
        'purchases/orders/view.html',
        order=order,
        locale=locale,
        direction=direction
    )


@purchases_routes.route('/purchase-orders', methods=['POST'])
@require_roles_or_redirect('admin', 'commercial')
def create_purchase_order():
    """Handle purchase order creation form submission."""
    try:
        # Debug: Log request info
        from flask import current_app
        current_app.logger.debug("=== CREATE PURCHASE ORDER DEBUG ===")
        current_app.logger.debug(f"Request method: {request.method}")
        current_app.logger.debug(f"Request path: {request.path}")
        current_app.logger.debug(f"Form keys: {list(request.form.keys())}")
        current_app.logger.debug(f"Form data: {dict(request.form)}")
        current_app.logger.debug("===================================")
        
        current_user = get_current_user()
        if not current_user:
            flash(_('Authentication required'), 'error')
            return redirect(url_for('purchases_frontend.list_purchase_orders'))
        
        from app.application.purchases.commands.commands import (
            CreatePurchaseOrderCommand, AddPurchaseOrderLineCommand
        )
        
        # Get form data
        from flask import current_app
        supplier_id = request.form.get('supplier_id', type=int)
        current_app.logger.debug(f"Supplier ID from form: {supplier_id}")
        if not supplier_id:
            flash(_('Supplier is required'), 'error')
            return redirect(url_for('purchases_frontend.new_purchase_order'))
        
        order_date = request.form.get('order_date')
        expected_delivery_date = request.form.get('expected_delivery_date')
        
        order_date_parsed = None
        if order_date:
            try:
                order_date_parsed = datetime.strptime(order_date, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        expected_delivery_date_parsed = None
        if expected_delivery_date:
            try:
                expected_delivery_date_parsed = datetime.strptime(expected_delivery_date, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        # Create purchase order
        from flask import current_app
        current_app.logger.info(f"Creating purchase order with supplier_id={supplier_id}, created_by={current_user.id}")
        command = CreatePurchaseOrderCommand(
            supplier_id=supplier_id,
            created_by=current_user.id,
            order_date=order_date_parsed,
            expected_delivery_date=expected_delivery_date_parsed,
            notes=request.form.get('notes') or None,
            internal_notes=request.form.get('internal_notes') or None
        )
        
        try:
            order = mediator.dispatch(command)
            current_app.logger.info(f"Handler returned: {order}, type: {type(order)}")
        except Exception as handler_error:
            import traceback
            current_app.logger.error(f"Error in mediator.dispatch: {str(handler_error)}")
            current_app.logger.error(traceback.format_exc())
            flash(_('Failed to create purchase order: %(error)s', error=str(handler_error)), 'error')
            return redirect(url_for('purchases_frontend.new_purchase_order'))
        
        if not order:
            current_app.logger.error("ERROR: Handler returned None")
            flash(_('Failed to create purchase order: handler returned None'), 'error')
            return redirect(url_for('purchases_frontend.new_purchase_order'))
        
        # Get order ID (handler returns SimpleNamespace with id attribute)
        order_id = getattr(order, 'id', None)
        current_app.logger.info(f"Extracted order_id: {order_id}")
        if not order_id:
            current_app.logger.error("ERROR: No ID in returned object")
            flash(_('Failed to create purchase order: no ID returned'), 'error')
            return redirect(url_for('purchases_frontend.new_purchase_order'))
        
        # Add lines if provided
        line_indices = []
        for key in request.form.keys():
            if key.startswith('lines[') and key.endswith('][product_id]'):
                match = re.match(r'lines\[(\d+)\]\[product_id\]', key)
                if match:
                    line_indices.append(int(match.group(1)))
        
        for idx in sorted(set(line_indices)):
            product_id = request.form.get(f'lines[{idx}][product_id]', type=int)
            quantity = request.form.get(f'lines[{idx}][quantity]', type=float)
            unit_price = request.form.get(f'lines[{idx}][unit_price]', type=float)
            discount_percent = request.form.get(f'lines[{idx}][discount_percent]', type=float)
            tax_rate = request.form.get(f'lines[{idx}][tax_rate]', type=float)
            notes_line = request.form.get(f'lines[{idx}][notes]')
            
            if product_id and quantity and unit_price:
                try:
                    line_command = AddPurchaseOrderLineCommand(
                        purchase_order_id=order_id,
                        product_id=product_id,
                        quantity=Decimal(str(quantity)),
                        unit_price=Decimal(str(unit_price)),
                        discount_percent=Decimal(str(discount_percent)) if discount_percent else Decimal(0),
                        tax_rate=Decimal(str(tax_rate)) if tax_rate else Decimal(20.0),
                        notes=notes_line
                    )
                    mediator.dispatch(line_command)
                except Exception as line_error:
                    import traceback
                    from flask import current_app
                    current_app.logger.error(f"Error adding line {idx} to purchase order {order_id}: {str(line_error)}")
                    current_app.logger.error(traceback.format_exc())
                    # Continue with other lines even if one fails
        
        flash(_('Purchase order created successfully'), 'success')
        return redirect(url_for('purchases_frontend.edit_purchase_order', order_id=order_id))
    except ValueError as e:
        # Handle domain validation errors
        flash(_('Cannot create purchase order: %(error)s', error=str(e)), 'error')
        return redirect(url_for('purchases_frontend.new_purchase_order'))
    except Exception as e:
        # Log the full error for debugging
        import traceback
        from flask import current_app
        current_app.logger.error(f"Error creating purchase order: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        flash(_('An error occurred: %(error)s', error=str(e)), 'error')
        return redirect(url_for('purchases_frontend.new_purchase_order'))


@purchases_routes.route('/purchase-orders/<int:order_id>', methods=['POST'])
@require_roles_or_redirect('admin', 'commercial')
def update_purchase_order(order_id: int):
    """Handle purchase order update form submission."""
    try:
        from app.application.purchases.commands.commands import UpdatePurchaseOrderCommand
        
        expected_delivery_date = request.form.get('expected_delivery_date')
        expected_delivery_date_parsed = None
        if expected_delivery_date:
            try:
                expected_delivery_date_parsed = datetime.strptime(expected_delivery_date, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        command = UpdatePurchaseOrderCommand(
            id=order_id,
            expected_delivery_date=expected_delivery_date_parsed,
            notes=request.form.get('notes') or None,
            internal_notes=request.form.get('internal_notes') or None
        )
        
        order = mediator.dispatch(command)
        
        flash(_('Purchase order updated successfully'), 'success')
        return redirect(url_for('purchases_frontend.edit_purchase_order', order_id=order_id))
    except ValueError as e:
        # Handle domain validation errors
        flash(_('Cannot update purchase order: %(error)s', error=str(e)), 'error')
        return redirect(url_for('purchases_frontend.edit_purchase_order', order_id=order_id))
    except Exception as e:
        # Log the full error for debugging
        import traceback
        print(f"Error updating purchase order {order_id}: {str(e)}")
        print(traceback.format_exc())
        flash(_('An error occurred: %(error)s', error=str(e)), 'error')
        return redirect(url_for('purchases_frontend.edit_purchase_order', order_id=order_id))


@purchases_routes.route('/purchase-orders/<int:order_id>/confirm', methods=['POST'])
@require_roles_or_redirect('admin', 'commercial', 'direction')
def confirm_purchase_order(order_id: int):
    """Confirm a purchase order."""
    try:
        current_user = get_current_user()
        if not current_user:
            flash(_('Authentication required'), 'error')
            return redirect(url_for('purchases_frontend.edit_purchase_order', order_id=order_id))
        
        from app.application.purchases.commands.commands import ConfirmPurchaseOrderCommand
        
        command = ConfirmPurchaseOrderCommand(
            id=order_id,
            confirmed_by=current_user.id
        )
        
        mediator.dispatch(command)
        
        flash(_('Purchase order confirmed successfully'), 'success')
        return redirect(url_for('purchases_frontend.edit_purchase_order', order_id=order_id))
    except ValueError as e:
        flash(_('Cannot confirm purchase order: %(error)s', error=str(e)), 'error')
        return redirect(url_for('purchases_frontend.edit_purchase_order', order_id=order_id))
    except Exception as e:
        import traceback
        print(f"Error confirming purchase order {order_id}: {str(e)}")
        print(traceback.format_exc())
        flash(_('An error occurred: %(error)s', error=str(e)), 'error')
        return redirect(url_for('purchases_frontend.edit_purchase_order', order_id=order_id))


@purchases_routes.route('/purchase-orders/<int:order_id>/cancel', methods=['POST'])
@require_roles_or_redirect('admin', 'commercial', 'direction')
def cancel_purchase_order(order_id: int):
    """Cancel a purchase order."""
    try:
        from app.application.purchases.commands.commands import CancelPurchaseOrderCommand
        
        command = CancelPurchaseOrderCommand(id=order_id)
        mediator.dispatch(command)
        
        flash(_('Purchase order cancelled successfully'), 'success')
        return redirect(url_for('purchases_frontend.edit_purchase_order', order_id=order_id))
    except ValueError as e:
        flash(_('Cannot cancel purchase order: %(error)s', error=str(e)), 'error')
        return redirect(url_for('purchases_frontend.edit_purchase_order', order_id=order_id))
    except Exception as e:
        import traceback
        print(f"Error cancelling purchase order {order_id}: {str(e)}")
        print(traceback.format_exc())
        flash(_('An error occurred: %(error)s', error=str(e)), 'error')
        return redirect(url_for('purchases_frontend.edit_purchase_order', order_id=order_id))


# ============================================================================
# User Story 9: Purchase Request Routes
# ============================================================================

@purchases_routes.route('/purchase-requests')
@require_roles_or_redirect('admin', 'commercial', 'direction')
def list_purchase_requests():
    """Render purchase requests list page."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    # Get query parameters
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 20)), 100)
    status = request.args.get('status')
    requested_by = request.args.get('requested_by', type=int)
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    # Parse dates
    date_from_parsed = None
    if date_from:
        try:
            date_from_parsed = datetime.strptime(date_from, '%Y-%m-%d').date()
        except ValueError:
            pass
    
    date_to_parsed = None
    if date_to:
        try:
            date_to_parsed = datetime.strptime(date_to, '%Y-%m-%d').date()
        except ValueError:
            pass
    
    # Fetch purchase requests
    query = ListPurchaseRequestsQuery(
        page=page,
        per_page=per_page,
        status=status,
        requested_by=requested_by,
        date_from=date_from_parsed,
        date_to=date_to_parsed
    )
    purchase_requests = mediator.dispatch(query)
    
    return render_template(
        'purchases/requests/list.html',
        purchase_requests=purchase_requests,
        page=page,
        per_page=per_page,
        filters={
            'status': status,
            'requested_by': requested_by,
            'date_from': date_from,
            'date_to': date_to
        },
        locale=locale,
        direction=direction
    )


@purchases_routes.route('/purchase-requests/new', methods=['GET', 'POST'])
@require_roles_or_redirect('admin', 'commercial')
def create_purchase_request():
    """Create a new purchase request."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    try:
        current_user = get_current_user()
        if not current_user:
            flash(_('Authentication required'), 'error')
            return redirect(url_for('purchases_frontend.list_purchase_requests'))
        
        if request.method == 'POST':
            from app.application.purchases.requests.commands.commands import (
                CreatePurchaseRequestCommand, PurchaseRequestLineInput
            )
            
            # Get form data
            requested_date = request.form.get('requested_date')
            required_date = request.form.get('required_date')
            notes = request.form.get('notes')
            internal_notes = request.form.get('internal_notes')
            
            # Parse dates
            requested_date_parsed = None
            if requested_date:
                try:
                    requested_date_parsed = datetime.strptime(requested_date, '%Y-%m-%d').date()
                except ValueError:
                    requested_date_parsed = date.today()
            else:
                requested_date_parsed = date.today()
            
            required_date_parsed = None
            if required_date:
                try:
                    required_date_parsed = datetime.strptime(required_date, '%Y-%m-%d').date()
                except ValueError:
                    pass
            
            # Get lines
            lines = []
            line_indices = []
            for key in request.form.keys():
                if key.startswith('lines[') and key.endswith('][product_id]'):
                    match = re.match(r'lines\[(\d+)\]\[product_id\]', key)
                    if match:
                        line_indices.append(int(match.group(1)))
            
            for idx in sorted(set(line_indices)):
                product_id = request.form.get(f'lines[{idx}][product_id]', type=int)
                quantity = request.form.get(f'lines[{idx}][quantity]', type=float)
                unit_price_estimate = request.form.get(f'lines[{idx}][unit_price_estimate]', type=float)
                notes_line = request.form.get(f'lines[{idx}][notes]')
                
                if product_id and quantity:
                    lines.append(PurchaseRequestLineInput(
                        product_id=product_id,
                        quantity=Decimal(str(quantity)),
                        unit_price_estimate=Decimal(str(unit_price_estimate)) if unit_price_estimate else None,
                        notes=notes_line
                    ))
            
            # Create purchase request
            command = CreatePurchaseRequestCommand(
                requested_by=current_user.id,
                requested_date=requested_date_parsed,
                required_date=required_date_parsed,
                notes=notes,
                internal_notes=internal_notes,
                lines=lines
            )
            
            request_id = mediator.dispatch(command)
            
            flash(_('Purchase request created successfully'), 'success')
            return redirect(url_for('purchases_frontend.view_purchase_request', request_id=request_id))
        
        # GET - show form
        products = mediator.dispatch(ListProductsQuery(page=1, per_page=1000, status='active'))
        
        return render_template(
            'purchases/requests/form.html',
            request=None,
            products=products,
            locale=locale,
            direction=direction
        )
    except Exception as e:
        flash(_('An error occurred: %(error)s', error=str(e)), 'error')
        return redirect(url_for('purchases_frontend.list_purchase_requests'))


@purchases_routes.route('/purchase-requests/<int:request_id>')
@require_roles_or_redirect('admin', 'commercial', 'direction')
def view_purchase_request(request_id: int):
    """View a purchase request."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    try:
        request_dto = mediator.dispatch(GetPurchaseRequestByIdQuery(id=request_id))
        if not request_dto:
            flash(_('Purchase request not found'), 'error')
            return redirect(url_for('purchases_frontend.list_purchase_requests'))
        
        # Fetch suppliers for the convert form (if status is approved)
        suppliers = []
        if request_dto.status == 'approved':
            suppliers = mediator.dispatch(ListSuppliersQuery(page=1, per_page=1000, status='active'))
            if suppliers is None:
                suppliers = []
        
        return render_template(
            'purchases/requests/view.html',
            request=request_dto,
            suppliers=suppliers,
            locale=locale,
            direction=direction
        )
    except Exception as e:
        flash(_('An error occurred: %(error)s', error=str(e)), 'error')
        return redirect(url_for('purchases_frontend.list_purchase_requests'))


@purchases_routes.route('/purchase-requests/<int:request_id>/submit', methods=['POST'])
@require_roles_or_redirect('admin', 'commercial')
def submit_purchase_request(request_id: int):
    """Submit a purchase request for approval."""
    try:
        from app.application.purchases.requests.commands.commands import SubmitPurchaseRequestCommand
        
        command = SubmitPurchaseRequestCommand(purchase_request_id=request_id)
        mediator.dispatch(command)
        
        flash(_('Purchase request submitted for approval'), 'success')
        return redirect(url_for('purchases_frontend.view_purchase_request', request_id=request_id))
    except Exception as e:
        flash(_('An error occurred: %(error)s', error=str(e)), 'error')
        return redirect(url_for('purchases_frontend.view_purchase_request', request_id=request_id))


@purchases_routes.route('/purchase-requests/<int:request_id>/approve', methods=['POST'])
@require_roles_or_redirect('admin', 'direction')
def approve_purchase_request(request_id: int):
    """Approve a purchase request."""
    try:
        current_user = get_current_user()
        if not current_user:
            flash(_('Authentication required'), 'error')
            return redirect(url_for('purchases_frontend.list_purchase_requests'))
        
        from app.application.purchases.requests.commands.commands import ApprovePurchaseRequestCommand
        
        command = ApprovePurchaseRequestCommand(
            purchase_request_id=request_id,
            approved_by=current_user.id
        )
        mediator.dispatch(command)
        
        flash(_('Purchase request approved'), 'success')
        return redirect(url_for('purchases_frontend.view_purchase_request', request_id=request_id))
    except Exception as e:
        flash(_('An error occurred: %(error)s', error=str(e)), 'error')
        return redirect(url_for('purchases_frontend.view_purchase_request', request_id=request_id))


@purchases_routes.route('/purchase-requests/<int:request_id>/reject', methods=['POST'])
@require_roles_or_redirect('admin', 'direction')
def reject_purchase_request(request_id: int):
    """Reject a purchase request."""
    try:
        current_user = get_current_user()
        if not current_user:
            flash(_('Authentication required'), 'error')
            return redirect(url_for('purchases_frontend.list_purchase_requests'))
        
        from app.application.purchases.requests.commands.commands import RejectPurchaseRequestCommand
        
        reason = request.form.get('reason', '')
        if not reason:
            flash(_('Rejection reason is required'), 'error')
            return redirect(url_for('purchases_frontend.view_purchase_request', request_id=request_id))
        
        command = RejectPurchaseRequestCommand(
            purchase_request_id=request_id,
            rejected_by=current_user.id,
            reason=reason
        )
        mediator.dispatch(command)
        
        flash(_('Purchase request rejected'), 'success')
        return redirect(url_for('purchases_frontend.view_purchase_request', request_id=request_id))
    except Exception as e:
        flash(_('An error occurred: %(error)s', error=str(e)), 'error')
        return redirect(url_for('purchases_frontend.view_purchase_request', request_id=request_id))


@purchases_routes.route('/purchase-requests/<int:request_id>/convert', methods=['POST'])
@require_roles_or_redirect('admin', 'commercial')
def convert_purchase_request(request_id: int):
    """Convert an approved purchase request to a purchase order."""
    try:
        current_user = get_current_user()
        if not current_user:
            flash(_('Authentication required'), 'error')
            return redirect(url_for('purchases_frontend.list_purchase_requests'))
        
        from app.application.purchases.requests.commands.commands import ConvertPurchaseRequestCommand
        
        supplier_id = request.form.get('supplier_id', type=int)
        if not supplier_id:
            flash(_('Supplier is required'), 'error')
            return redirect(url_for('purchases_frontend.view_purchase_request', request_id=request_id))
        
        order_date = request.form.get('order_date')
        expected_delivery_date = request.form.get('expected_delivery_date')
        
        order_date_parsed = None
        if order_date:
            try:
                order_date_parsed = datetime.strptime(order_date, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        expected_delivery_date_parsed = None
        if expected_delivery_date:
            try:
                expected_delivery_date_parsed = datetime.strptime(expected_delivery_date, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        command = ConvertPurchaseRequestCommand(
            purchase_request_id=request_id,
            supplier_id=supplier_id,
            created_by=current_user.id,
            order_date=order_date_parsed,
            expected_delivery_date=expected_delivery_date_parsed
        )
        
        po_id = mediator.dispatch(command)
        
        flash(_('Purchase request converted to purchase order'), 'success')
        return redirect(url_for('purchases_frontend.edit_purchase_order', order_id=po_id))
    except Exception as e:
        flash(_('An error occurred: %(error)s', error=str(e)), 'error')
        return redirect(url_for('purchases_frontend.view_purchase_request', request_id=request_id))


# ============================================================================
# User Story 9: Purchase Receipt Routes
# ============================================================================

@purchases_routes.route('/purchase-receipts')
@require_roles_or_redirect('admin', 'commercial', 'direction')
def list_purchase_receipts():
    """Render purchase receipts list page."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    # Get query parameters
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 20)), 100)
    purchase_order_id = request.args.get('purchase_order_id', type=int)
    status = request.args.get('status')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    # Parse dates
    date_from_parsed = None
    if date_from:
        try:
            date_from_parsed = datetime.strptime(date_from, '%Y-%m-%d').date()
        except ValueError:
            pass
    
    date_to_parsed = None
    if date_to:
        try:
            date_to_parsed = datetime.strptime(date_to, '%Y-%m-%d').date()
        except ValueError:
            pass
    
    # Fetch purchase receipts
    query = ListPurchaseReceiptsQuery(
        page=page,
        per_page=per_page,
        purchase_order_id=purchase_order_id,
        status=status,
        date_from=date_from_parsed,
        date_to=date_to_parsed
    )
    purchase_receipts = mediator.dispatch(query)
    
    return render_template(
        'purchases/receipts/list.html',
        purchase_receipts=purchase_receipts,
        page=page,
        per_page=per_page,
        filters={
            'purchase_order_id': purchase_order_id,
            'status': status,
            'date_from': date_from,
            'date_to': date_to
        },
        locale=locale,
        direction=direction
    )


@purchases_routes.route('/purchase-receipts/new', methods=['GET', 'POST'])
@require_roles_or_redirect('admin', 'commercial')
def create_purchase_receipt():
    """Create a new purchase receipt."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    try:
        current_user = get_current_user()
        if not current_user:
            flash(_('Authentication required'), 'error')
            return redirect(url_for('purchases_frontend.list_purchase_receipts'))
        
        # Get purchase_order_id from query params or form
        purchase_order_id = request.args.get('purchase_order_id', type=int) or request.form.get('purchase_order_id', type=int)
        
        if request.method == 'GET' and not purchase_order_id:
            # GET request without purchase_order_id - show form to select PO
            # Fetch purchase orders that can receive goods (confirmed, sent, or partially_received)
            from app.application.purchases.queries.queries import ListPurchaseOrdersQuery
            # Get all orders and filter by allowed statuses
            all_orders = mediator.dispatch(ListPurchaseOrdersQuery(
                page=1,
                per_page=1000
            ))
            # Filter to only show orders with statuses that allow receipt creation
            # ListPurchaseOrdersHandler returns a list of PurchaseOrderDTO
            allowed_statuses = ['confirmed', 'sent', 'partially_received']
            confirmed_orders = []
            if isinstance(all_orders, list):
                confirmed_orders = [order for order in all_orders if hasattr(order, 'status') and order.status in allowed_statuses]
            
            return render_template(
                'purchases/receipts/form.html',
                receipt=None,
                purchase_order=None,
                purchase_orders=confirmed_orders if confirmed_orders else [],
                locations=[],
                locale=locale,
                direction=direction,
                select_po=True  # Flag to show PO selection
            )
        
        if request.method == 'POST':
            if not purchase_order_id:
                flash(_('Purchase order is required'), 'error')
                return redirect(url_for('purchases_frontend.create_purchase_receipt'))
            from app.application.purchases.receipts.commands.commands import (
                CreatePurchaseReceiptCommand, PurchaseReceiptLineInput
            )
            
            # Get form data
            receipt_date = request.form.get('receipt_date')
            notes = request.form.get('notes')
            internal_notes = request.form.get('internal_notes')
            
            # Parse date
            receipt_date_parsed = None
            if receipt_date:
                try:
                    receipt_date_parsed = datetime.strptime(receipt_date, '%Y-%m-%d').date()
                except ValueError:
                    receipt_date_parsed = date.today()
            else:
                receipt_date_parsed = date.today()
            
            # Get lines
            lines = []
            line_indices = []
            for key in request.form.keys():
                if key.startswith('lines[') and key.endswith('][purchase_order_line_id]'):
                    match = re.match(r'lines\[(\d+)\]\[purchase_order_line_id\]', key)
                    if match:
                        line_indices.append(int(match.group(1)))
            
            for idx in sorted(set(line_indices)):
                po_line_id = request.form.get(f'lines[{idx}][purchase_order_line_id]', type=int)
                product_id = request.form.get(f'lines[{idx}][product_id]', type=int)
                quantity_ordered = request.form.get(f'lines[{idx}][quantity_ordered]', type=float)
                quantity_received = request.form.get(f'lines[{idx}][quantity_received]', type=float)
                location_id = request.form.get(f'lines[{idx}][location_id]', type=int)
                discrepancy_reason = request.form.get(f'lines[{idx}][discrepancy_reason]')
                quality_notes = request.form.get(f'lines[{idx}][quality_notes]')
                
                if po_line_id and product_id and quantity_received is not None:
                    lines.append(PurchaseReceiptLineInput(
                        purchase_order_line_id=po_line_id,
                        product_id=product_id,
                        quantity_ordered=Decimal(str(quantity_ordered)) if quantity_ordered else Decimal(0),
                        quantity_received=Decimal(str(quantity_received)),
                        location_id=location_id,
                        discrepancy_reason=discrepancy_reason,
                        quality_notes=quality_notes
                    ))
            
            # Create purchase receipt
            command = CreatePurchaseReceiptCommand(
                purchase_order_id=purchase_order_id,
                received_by=current_user.id,
                receipt_date=receipt_date_parsed,
                notes=notes,
                internal_notes=internal_notes,
                lines=lines
            )
            
            receipt_id = mediator.dispatch(command)
            
            flash(_('Purchase receipt created successfully'), 'success')
            return redirect(url_for('purchases_frontend.view_purchase_receipt', receipt_id=receipt_id))
        
        # GET - show form
        # Get purchase order
        po = mediator.dispatch(GetPurchaseOrderByIdQuery(id=purchase_order_id))
        if not po:
            flash(_('Purchase order not found'), 'error')
            return redirect(url_for('purchases_frontend.list_purchase_orders'))
        
        # Check if purchase order status allows receipt creation
        # Receipts can be created for: confirmed, sent, partially_received
        allowed_statuses = ['confirmed', 'sent', 'partially_received']
        if po.status not in allowed_statuses:
            flash(_('Cannot create receipt for purchase order in status "%(status)s". Order must be confirmed, sent, or partially received.', status=po.status), 'error')
            return redirect(url_for('purchases_frontend.edit_purchase_order', order_id=purchase_order_id))
        
        # Get locations and sites based on stock management mode
        from app.utils.settings_helper import get_stock_management_mode
        stock_mode = get_stock_management_mode()
        
        locations = []
        sites = []
        default_site = None
        default_location = None
        
        if stock_mode == 'advanced':
            # Advanced mode: show sites and locations
            from app.application.stock.sites.queries.queries import ListSitesQuery
            sites = mediator.dispatch(ListSitesQuery(page=1, per_page=1000, status='active'))
            locations = mediator.dispatch(GetLocationHierarchyQuery())
        else:
            # Simple mode: only show default location, hide site/location selection
            locations = mediator.dispatch(GetLocationHierarchyQuery())
            # Get first active warehouse location as default
            from app.infrastructure.db import get_session
            from app.domain.models.stock import Location
            default_location = None
            with get_session() as session:
                location_obj = session.query(Location).filter(
                    Location.type == 'warehouse',
                    Location.is_active == True
                ).first()
                # Convert to dict to avoid DetachedInstanceError
                if location_obj:
                    default_location = {
                        'id': location_obj.id,
                        'code': location_obj.code,
                        'name': location_obj.name,
                        'type': location_obj.type,
                        'site_id': location_obj.site_id if location_obj.site_id else None
                    }
        
        return render_template(
            'purchases/receipts/form.html',
            receipt=None,
            purchase_order=po,
            locations=locations,
            sites=sites,
            default_location=default_location,
            stock_mode=stock_mode,
            locale=locale,
            direction=direction
        )
    except Exception as e:
        flash(_('An error occurred: %(error)s', error=str(e)), 'error')
        return redirect(url_for('purchases_frontend.list_purchase_receipts'))


@purchases_routes.route('/purchase-receipts/<int:receipt_id>')
@require_roles_or_redirect('admin', 'commercial', 'direction')
def view_purchase_receipt(receipt_id: int):
    """View a purchase receipt."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    try:
        receipt_dto = mediator.dispatch(GetPurchaseReceiptByIdQuery(id=receipt_id))
        if not receipt_dto:
            flash(_('Purchase receipt not found'), 'error')
            return redirect(url_for('purchases_frontend.list_purchase_receipts'))
        
        return render_template(
            'purchases/receipts/view.html',
            receipt=receipt_dto,
            locale=locale,
            direction=direction
        )
    except Exception as e:
        flash(_('An error occurred: %(error)s', error=str(e)), 'error')
        return redirect(url_for('purchases_frontend.list_purchase_receipts'))


@purchases_routes.route('/purchase-receipts/<int:receipt_id>/pdf')
@require_roles_or_redirect('admin', 'commercial', 'direction')
def purchase_receipt_pdf(receipt_id: int):
    """Download purchase receipt PDF."""
    try:
        from flask import send_file
        from app.services.purchase_receipt_pdf_service import PurchaseReceiptPDFService
        
        query = GetPurchaseReceiptByIdQuery(id=receipt_id)
        receipt = mediator.dispatch(query)
        
        if not receipt:
            flash(_('Purchase receipt not found'), 'error')
            return redirect(url_for('purchases_frontend.list_purchase_receipts'))
        
        # Generate PDF
        pdf_service = PurchaseReceiptPDFService()
        pdf_buffer = pdf_service.generate_receipt_pdf(receipt)
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"Bon_Reception_{receipt.number}.pdf"
        )
    except Exception as e:
        flash(_('An error occurred: %(error)s', error=str(e)), 'error')
        return redirect(url_for('purchases_frontend.view_purchase_receipt', receipt_id=receipt_id))


@purchases_routes.route('/purchase-receipts/<int:receipt_id>/validate', methods=['POST'])
@require_roles_or_redirect('admin', 'commercial')
def validate_purchase_receipt(receipt_id: int):
    """Validate a purchase receipt (triggers stock movements)."""
    try:
        current_user = get_current_user()
        if not current_user:
            flash(_('Authentication required'), 'error')
            return redirect(url_for('purchases_frontend.list_purchase_receipts'))
        
        from app.application.purchases.receipts.commands.commands import ValidatePurchaseReceiptCommand
        
        command = ValidatePurchaseReceiptCommand(
            purchase_receipt_id=receipt_id,
            validated_by=current_user.id
        )
        mediator.dispatch(command)
        
        flash(_('Purchase receipt validated. Stock has been updated.'), 'success')
        return redirect(url_for('purchases_frontend.view_purchase_receipt', receipt_id=receipt_id))
    except Exception as e:
        flash(_('An error occurred: %(error)s', error=str(e)), 'error')
        return redirect(url_for('purchases_frontend.view_purchase_receipt', receipt_id=receipt_id))


@purchases_routes.route('/purchase-receipts/<int:receipt_id>/create-invoice', methods=['GET', 'POST'])
@require_roles_or_redirect('admin', 'accountant', 'direction')
def create_invoice_from_receipt(receipt_id: int):
    """
    Create a supplier invoice from a validated purchase receipt.
    This is a best practice in ERP systems: convert PO to invoice after goods are received.
    """
    try:
        current_user = get_current_user()
        if not current_user:
            flash(_('Authentication required'), 'error')
            return redirect(url_for('purchases_frontend.list_purchase_receipts'))
        
        # Get receipt
        receipt_dto = mediator.dispatch(GetPurchaseReceiptByIdQuery(id=receipt_id))
        if not receipt_dto:
            flash(_('Purchase receipt not found'), 'error')
            return redirect(url_for('purchases_frontend.list_purchase_receipts'))
        
        # Check if receipt is validated
        if receipt_dto.status != 'validated':
            flash(_('Can only create invoice from validated receipts'), 'error')
            return redirect(url_for('purchases_frontend.view_purchase_receipt', receipt_id=receipt_id))
        
        # Get purchase order
        po = mediator.dispatch(GetPurchaseOrderByIdQuery(id=receipt_dto.purchase_order_id))
        if not po:
            flash(_('Purchase order not found'), 'error')
            return redirect(url_for('purchases_frontend.view_purchase_receipt', receipt_id=receipt_id))
        
        if request.method == 'POST':
            from app.application.purchases.invoices.commands.commands import (
                CreateSupplierInvoiceCommand, MatchSupplierInvoiceCommand
            )
            
            # Get invoice number from form (required)
            invoice_number = request.form.get('number', '').strip()
            if not invoice_number:
                flash(_('Invoice number is required'), 'error')
                return redirect(url_for('purchases_frontend.create_invoice_from_receipt', receipt_id=receipt_id))
            
            # Calculate invoice amounts based on received quantities
            # We need to load PO lines with receipt lines to calculate correctly
            from app.infrastructure.db import get_session
            from app.domain.models.purchase import PurchaseOrderLine, PurchaseReceiptLine
            
            with get_session() as session:
                # Load receipt with lines
                from app.domain.models.purchase import PurchaseReceipt
                receipt = session.get(PurchaseReceipt, receipt_id)
                if not receipt:
                    flash(_('Purchase receipt not found'), 'error')
                    return redirect(url_for('purchases_frontend.list_purchase_receipts'))
                
                # Calculate totals based on received quantities
                subtotal_ht = Decimal(0)
                total_tax = Decimal(0)
                total_ttc = Decimal(0)
                
                for receipt_line in receipt.lines:
                    po_line = session.get(PurchaseOrderLine, receipt_line.purchase_order_line_id)
                    if po_line:
                        # Calculate line total based on received quantity (not ordered)
                        line_subtotal = receipt_line.quantity_received * po_line.unit_price
                        discount_amount = line_subtotal * (po_line.discount_percent / Decimal(100))
                        line_total_ht = line_subtotal - discount_amount
                        line_tax = line_total_ht * (po_line.tax_rate / Decimal(100))
                        line_total_ttc = line_total_ht + line_tax
                        
                        subtotal_ht += line_total_ht
                        total_tax += line_tax
                        total_ttc += line_total_ttc
                
                # Get invoice date (default to receipt date or today)
                invoice_date_str = request.form.get('invoice_date')
                invoice_date = None
                if invoice_date_str:
                    try:
                        invoice_date = datetime.strptime(invoice_date_str, '%Y-%m-%d').date()
                    except ValueError:
                        pass
                
                if not invoice_date:
                    invoice_date = receipt.receipt_date if receipt.receipt_date else date.today()
                
                # Get due date (optional, can be calculated from invoice date + payment terms)
                due_date_str = request.form.get('due_date')
                due_date = None
                if due_date_str:
                    try:
                        due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
                    except ValueError:
                        pass
                
                # Create supplier invoice
                create_command = CreateSupplierInvoiceCommand(
                    number=invoice_number,
                    supplier_id=po.supplier_id,
                    invoice_date=invoice_date,
                    subtotal_ht=subtotal_ht,
                    tax_amount=total_tax,
                    total_ttc=total_ttc,
                    created_by=current_user.id,
                    due_date=due_date,
                    received_date=receipt.receipt_date if receipt.receipt_date else date.today(),
                    notes=f"Invoice created from receipt {receipt.number} for PO {po.number}",
                    internal_notes=f"Auto-generated from receipt {receipt.number}"
                )
                
                invoice_id = mediator.dispatch(create_command)
                
                if not invoice_id:
                    flash(_('Failed to create supplier invoice. Please try again.'), 'error')
                    return redirect(url_for('purchases_frontend.view_purchase_receipt', receipt_id=receipt_id))
                
                # Automatically match invoice with PO and receipt (3-way matching)
                match_command = MatchSupplierInvoiceCommand(
                    supplier_invoice_id=invoice_id,
                    purchase_order_id=po.id,
                    purchase_receipt_id=receipt_id,
                    matched_by=current_user.id
                )
                
                match_result = mediator.dispatch(match_command)
                
                flash(_('Supplier invoice created and matched successfully with PO and receipt'), 'success')
                return redirect(url_for('purchases_frontend.view_supplier_invoice', invoice_id=invoice_id))
        
        # GET - show form with pre-filled data
        # Pre-fill invoice number suggestion (can be edited)
        suggested_invoice_number = f"INV-{receipt_dto.receipt_date.strftime('%Y%m%d') if receipt_dto.receipt_date else date.today().strftime('%Y%m%d')}-{receipt_dto.number.split('-')[-1] if '-' in receipt_dto.number else receipt_dto.id}"
        
        return render_template(
            'purchases/receipts/create_invoice.html',
            receipt=receipt_dto,
            purchase_order=po,
            suggested_invoice_number=suggested_invoice_number,
            locale=get_locale(),
            direction='rtl' if get_locale() == 'ar' else 'ltr'
        )
    except Exception as e:
        flash(_('An error occurred: %(error)s', error=str(e)), 'error')
        return redirect(url_for('purchases_frontend.view_purchase_receipt', receipt_id=receipt_id))


# ============================================================================
# User Story 9: Supplier Invoice Routes
# ============================================================================

@purchases_routes.route('/supplier-invoices')
@require_roles_or_redirect('admin', 'commercial', 'accountant', 'direction')
def list_supplier_invoices():
    """Render supplier invoices list page."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    # Get query parameters
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 20)), 100)
    supplier_id = request.args.get('supplier_id', type=int)
    status = request.args.get('status')
    matching_status = request.args.get('matching_status')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    # Parse dates
    date_from_parsed = None
    if date_from:
        try:
            date_from_parsed = datetime.strptime(date_from, '%Y-%m-%d').date()
        except ValueError:
            pass
    
    date_to_parsed = None
    if date_to:
        try:
            date_to_parsed = datetime.strptime(date_to, '%Y-%m-%d').date()
        except ValueError:
            pass
    
    # Fetch supplier invoices
    query = ListSupplierInvoicesQuery(
        page=page,
        per_page=per_page,
        supplier_id=supplier_id,
        status=status,
        matching_status=matching_status,
        date_from=date_from_parsed,
        date_to=date_to_parsed
    )
    supplier_invoices = mediator.dispatch(query)
    
    return render_template(
        'purchases/invoices/list.html',
        supplier_invoices=supplier_invoices,
        page=page,
        per_page=per_page,
        filters={
            'supplier_id': supplier_id,
            'status': status,
            'matching_status': matching_status,
            'date_from': date_from,
            'date_to': date_to
        },
        locale=locale,
        direction=direction
    )


@purchases_routes.route('/supplier-invoices/new', methods=['GET', 'POST'])
@require_roles_or_redirect('admin', 'accountant', 'direction')
def create_supplier_invoice():
    """Create a new supplier invoice."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    try:
        current_user = get_current_user()
        if not current_user:
            flash(_('Authentication required'), 'error')
            return redirect(url_for('purchases_frontend.list_supplier_invoices'))
        
        if request.method == 'POST':
            from app.application.purchases.invoices.commands.commands import CreateSupplierInvoiceCommand
            
            # Get form data
            number = request.form.get('number', '').strip()
            supplier_id = request.form.get('supplier_id', type=int)
            invoice_date = request.form.get('invoice_date')
            due_date = request.form.get('due_date')
            received_date = request.form.get('received_date')
            subtotal_ht = request.form.get('subtotal_ht', type=float)
            tax_amount = request.form.get('tax_amount', type=float)
            total_ttc = request.form.get('total_ttc', type=float)
            notes = request.form.get('notes')
            internal_notes = request.form.get('internal_notes')
            
            if not number:
                flash(_('Invoice number is required'), 'error')
                return redirect(url_for('purchases_frontend.create_supplier_invoice'))
            
            if not supplier_id:
                flash(_('Supplier is required'), 'error')
                return redirect(url_for('purchases_frontend.create_supplier_invoice'))
            
            # Parse dates
            invoice_date_parsed = None
            if invoice_date:
                try:
                    invoice_date_parsed = datetime.strptime(invoice_date, '%Y-%m-%d').date()
                except ValueError:
                    flash(_('Invalid invoice date'), 'error')
                    return redirect(url_for('purchases_frontend.create_supplier_invoice'))
            
            due_date_parsed = None
            if due_date:
                try:
                    due_date_parsed = datetime.strptime(due_date, '%Y-%m-%d').date()
                except ValueError:
                    pass
            
            received_date_parsed = None
            if received_date:
                try:
                    received_date_parsed = datetime.strptime(received_date, '%Y-%m-%d').date()
                except ValueError:
                    received_date_parsed = date.today()
            
            # Create supplier invoice
            command = CreateSupplierInvoiceCommand(
                number=number,
                supplier_id=supplier_id,
                invoice_date=invoice_date_parsed,
                subtotal_ht=Decimal(str(subtotal_ht)) if subtotal_ht else Decimal(0),
                tax_amount=Decimal(str(tax_amount)) if tax_amount else Decimal(0),
                total_ttc=Decimal(str(total_ttc)) if total_ttc else Decimal(0),
                created_by=current_user.id,
                due_date=due_date_parsed,
                received_date=received_date_parsed,
                notes=notes,
                internal_notes=internal_notes
            )
            
            invoice_id = mediator.dispatch(command)
            
            flash(_('Supplier invoice created successfully'), 'success')
            return redirect(url_for('purchases_frontend.view_supplier_invoice', invoice_id=invoice_id))
        
        # GET - show form
        suppliers = mediator.dispatch(ListSuppliersQuery(page=1, per_page=1000, status='active'))
        
        return render_template(
            'purchases/invoices/form.html',
            invoice=None,
            suppliers=suppliers,
            locale=locale,
            direction=direction
        )
    except Exception as e:
        flash(_('An error occurred: %(error)s', error=str(e)), 'error')
        return redirect(url_for('purchases_frontend.list_supplier_invoices'))


@purchases_routes.route('/supplier-invoices/<int:invoice_id>')
@require_roles_or_redirect('admin', 'commercial', 'accountant', 'direction')
def view_supplier_invoice(invoice_id: int):
    """View a supplier invoice."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    try:
        invoice_dto = mediator.dispatch(GetSupplierInvoiceByIdQuery(id=invoice_id))
        if not invoice_dto:
            flash(_('Supplier invoice not found'), 'error')
            return redirect(url_for('purchases_frontend.list_supplier_invoices'))
        
        # Get related PO and receipt if matched
        matched_po = None
        matched_receipt = None
        if invoice_dto.matched_purchase_order_id:
            matched_po = mediator.dispatch(GetPurchaseOrderByIdQuery(id=invoice_dto.matched_purchase_order_id))
        if invoice_dto.matched_purchase_receipt_id:
            matched_receipt = mediator.dispatch(GetPurchaseReceiptByIdQuery(id=invoice_dto.matched_purchase_receipt_id))
        
        return render_template(
            'purchases/invoices/view.html',
            invoice=invoice_dto,
            matched_po=matched_po,
            matched_receipt=matched_receipt,
            locale=locale,
            direction=direction
        )
    except Exception as e:
        flash(_('An error occurred: %(error)s', error=str(e)), 'error')
        return redirect(url_for('purchases_frontend.list_supplier_invoices'))


@purchases_routes.route('/supplier-invoices/<int:invoice_id>/match', methods=['POST'])
@require_roles_or_redirect('admin', 'accountant', 'direction')
def match_supplier_invoice(invoice_id: int):
    """Match a supplier invoice with purchase order and receipt (3-way matching)."""
    try:
        current_user = get_current_user()
        if not current_user:
            flash(_('Authentication required'), 'error')
            return redirect(url_for('purchases_frontend.list_supplier_invoices'))
        
        from app.application.purchases.invoices.commands.commands import MatchSupplierInvoiceCommand
        
        purchase_order_id = request.form.get('purchase_order_id', type=int)
        purchase_receipt_id = request.form.get('purchase_receipt_id', type=int) or None
        
        if not purchase_order_id:
            flash(_('Purchase order is required'), 'error')
            return redirect(url_for('purchases_frontend.view_supplier_invoice', invoice_id=invoice_id))
        
        command = MatchSupplierInvoiceCommand(
            supplier_invoice_id=invoice_id,
            purchase_order_id=purchase_order_id,
            purchase_receipt_id=purchase_receipt_id,
            matched_by=current_user.id
        )
        
        result = mediator.dispatch(command)
        
        if result.get('matching_status') == 'matched':
            flash(_('Invoice matched successfully with PO and receipt'), 'success')
        elif result.get('matching_status') == 'partially_matched':
            flash(_('Invoice partially matched. Please review discrepancies.'), 'warning')
        else:
            flash(_('Invoice matching completed with warnings'), 'warning')
        
        return redirect(url_for('purchases_frontend.view_supplier_invoice', invoice_id=invoice_id))
    except Exception as e:
        flash(_('An error occurred: %(error)s', error=str(e)), 'error')
        return redirect(url_for('purchases_frontend.view_supplier_invoice', invoice_id=invoice_id))

