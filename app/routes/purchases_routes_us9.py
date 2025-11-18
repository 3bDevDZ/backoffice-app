"""Frontend route handlers for User Story 9 - Purchase Requests, Receipts, and Supplier Invoices."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_babel import get_locale, gettext as _
from datetime import date, datetime
from decimal import Decimal
import re

from app.application.common.mediator import mediator
from app.application.purchases.requests.queries.queries import (
    ListPurchaseRequestsQuery, GetPurchaseRequestByIdQuery
)
from app.application.purchases.receipts.queries.queries import (
    ListPurchaseReceiptsQuery, GetPurchaseReceiptByIdQuery
)
from app.application.purchases.invoices.queries.queries import (
    ListSupplierInvoicesQuery, GetSupplierInvoiceByIdQuery
)
from app.application.purchases.queries.queries import GetPurchaseOrderByIdQuery
from app.application.stock.queries.queries import GetLocationHierarchyQuery
from app.application.products.queries.queries import ListProductsQuery
from app.application.purchases.queries.queries import ListSuppliersQuery
from app.security.session_auth import require_roles_or_redirect, get_current_user

# Import the existing purchases_routes blueprint
from app.routes.purchases_routes import purchases_routes


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
        
        return render_template(
            'purchases/requests/view.html',
            request=request_dto,
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
        
        purchase_order_id = request.args.get('purchase_order_id', type=int) or request.form.get('purchase_order_id', type=int)
        if not purchase_order_id:
            flash(_('Purchase order is required'), 'error')
            return redirect(url_for('purchases_frontend.list_purchase_orders'))
        
        if request.method == 'POST':
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
        
        # Get locations
        locations = mediator.dispatch(GetLocationHierarchyQuery())
        
        return render_template(
            'purchases/receipts/form.html',
            receipt=None,
            purchase_order=po,
            locations=locations,
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




