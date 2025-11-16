"""Frontend routes for billing and invoicing."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_babel import gettext as _
from datetime import date, datetime, timedelta
from decimal import Decimal
from io import BytesIO

from app.application.common.mediator import mediator
from app.application.billing.invoices.commands.commands import (
    CreateInvoiceCommand, ValidateInvoiceCommand, SendInvoiceCommand, CreateCreditNoteCommand
)
from app.application.billing.invoices.queries.queries import (
    ListInvoicesQuery, GetInvoiceByIdQuery, GetInvoiceHistoryQuery
)
from app.application.sales.orders.queries.queries import GetOrderByIdQuery
from app.services.invoice_pdf_service import InvoicePDFService
from app.services.invoice_email_service import InvoiceEmailService
from app.services.fec_export_service import FECExportService
from app.infrastructure.db import get_session
from app.security.session_auth import require_roles_or_redirect

billing_routes = Blueprint('billing', __name__, url_prefix='/billing')


@billing_routes.route('/invoices')
@require_roles_or_redirect('admin', 'commercial', 'accountant', 'direction')
def invoices_list():
    """List all invoices."""
    try:
        # Get filters from query parameters
        status = request.args.get('status')
        customer_id = request.args.get('customer_id', type=int)
        order_id = request.args.get('order_id', type=int)
        search = request.args.get('search')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        
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
        
        # Query invoices
        query = ListInvoicesQuery(
            page=page,
            per_page=per_page,
            status=status,
            customer_id=customer_id,
            order_id=order_id,
            search=search,
            date_from=date_from_parsed,
            date_to=date_to_parsed
        )
        
        invoices = mediator.dispatch(query)
        
        return render_template('billing/invoices_list.html', invoices=invoices)
    except Exception as e:
        flash(_('An error occurred: %(error)s', error=str(e)), 'error')
        return render_template('billing/invoices_list.html', invoices=[])


@billing_routes.route('/invoices/new', methods=['GET', 'POST'])
@require_roles_or_redirect('admin', 'accountant', 'direction')
def create_invoice():
    """Create invoice from order - show form or create directly."""
    order_id = request.args.get('order_id', type=int)
    
    if not order_id:
        flash(_('Order ID is required'), 'error')
        return redirect(url_for('sales.orders_list'))
    
    try:
        # Get order
        order = mediator.dispatch(GetOrderByIdQuery(order_id=order_id, include_lines=True, include_reservations=False))
        
        if not order:
            flash(_('Order not found'), 'error')
            return redirect(url_for('sales.orders_list'))
        
        # Check if order is delivered
        if order.status != 'delivered':
            flash(_('Order must be delivered before creating invoice'), 'error')
            return redirect(url_for('sales.view_order', order_id=order_id))
        
        # Check if invoice already exists
        existing_invoice_query = ListInvoicesQuery(order_id=order_id, status=None, page=1, per_page=10)
        existing_invoices = mediator.dispatch(existing_invoice_query)
        if existing_invoices:
            # Check if there's a non-canceled invoice
            for inv in existing_invoices:
                if inv.status != 'canceled':
                    flash(_('An invoice already exists for this order: %(number)s', number=inv.number), 'warning')
                    return redirect(url_for('billing.invoice_view', invoice_id=inv.id))
        
        # If POST, create invoice
        if request.method == 'POST':
            from flask import g
            created_by = g.user.id if g.user else 1
            
            invoice_date_str = request.form.get('invoice_date')
            due_date_str = request.form.get('due_date')
            notes = request.form.get('notes', '').strip()
            internal_notes = request.form.get('internal_notes', '').strip()
            discount_percent = Decimal(request.form.get('discount_percent', '0'))
            
            # Parse dates
            invoice_date = datetime.strptime(invoice_date_str, '%Y-%m-%d').date() if invoice_date_str else date.today()
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date() if due_date_str else invoice_date + timedelta(days=30)
            
            # Create invoice
            command = CreateInvoiceCommand(
                order_id=order_id,
                customer_id=order.customer_id,
                invoice_date=invoice_date,
                due_date=due_date,
                created_by=created_by,
                notes=notes,
                internal_notes=internal_notes,
                discount_percent=discount_percent
            )
            
            invoice_id = mediator.dispatch(command)
            
            flash(_('Invoice created successfully'), 'success')
            return redirect(url_for('billing.invoice_view', invoice_id=invoice_id))
        
        # GET - show form
        default_invoice_date = date.today()
        default_due_date = default_invoice_date + timedelta(days=30)
        
        return render_template(
            'billing/invoice_form.html',
            order=order,
            default_invoice_date=default_invoice_date,
            default_due_date=default_due_date
        )
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('sales.view_order', order_id=order_id))
    except Exception as e:
        flash(_('An error occurred: %(error)s', error=str(e)), 'error')
        return redirect(url_for('sales.view_order', order_id=order_id))


@billing_routes.route('/invoices/<int:invoice_id>')
@require_roles_or_redirect('admin', 'commercial', 'accountant', 'direction')
def invoice_view(invoice_id: int):
    """View invoice details."""
    try:
        query = GetInvoiceByIdQuery(id=invoice_id)
        invoice = mediator.dispatch(query)
        
        if not invoice:
            flash(_('Invoice not found'), 'error')
            return redirect(url_for('billing.invoices_list'))
        
        return render_template('billing/invoice_view.html', invoice=invoice)
    except Exception as e:
        flash(_('An error occurred: %(error)s', error=str(e)), 'error')
        return redirect(url_for('billing.invoices_list'))


@billing_routes.route('/invoices/<int:invoice_id>/pdf')
@require_roles_or_redirect('admin', 'commercial', 'accountant', 'direction')
def invoice_pdf(invoice_id: int):
    """Download invoice PDF."""
    try:
        query = GetInvoiceByIdQuery(id=invoice_id)
        invoice = mediator.dispatch(query)
        
        if not invoice:
            flash(_('Invoice not found'), 'error')
            return redirect(url_for('billing.invoices_list'))
        
        # Generate PDF
        pdf_service = InvoicePDFService()
        pdf_buffer = pdf_service.generate_invoice_pdf(invoice)
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"Facture_{invoice.number}.pdf"
        )
    except Exception as e:
        flash(_('An error occurred: %(error)s', error=str(e)), 'error')
        return redirect(url_for('billing.invoice_view', invoice_id=invoice_id))


@billing_routes.route('/invoices/<int:invoice_id>/validate', methods=['POST'])
@require_roles_or_redirect('admin', 'accountant', 'direction')
def validate_invoice(invoice_id: int):
    """Validate an invoice."""
    try:
        from flask import g
        validated_by = g.user.id if g.user else 1
        
        command = ValidateInvoiceCommand(id=invoice_id, validated_by=validated_by)
        mediator.dispatch(command)
        
        flash(_('Invoice validated successfully'), 'success')
        
        if request.is_json:
            return jsonify({'status': 'success'})
        else:
            return redirect(url_for('billing.invoice_view', invoice_id=invoice_id))
    except ValueError as e:
        error_msg = str(e)
        if request.is_json:
            return jsonify({'status': 'error', 'message': error_msg}), 400
        else:
            flash(error_msg, 'error')
            return redirect(url_for('billing.invoice_view', invoice_id=invoice_id))
    except Exception as e:
        error_msg = _('An error occurred: %(error)s', error=str(e))
        if request.is_json:
            return jsonify({'status': 'error', 'message': error_msg}), 500
        else:
            flash(error_msg, 'error')
            return redirect(url_for('billing.invoice_view', invoice_id=invoice_id))


@billing_routes.route('/invoices/<int:invoice_id>/send', methods=['POST'])
@require_roles_or_redirect('admin', 'commercial', 'accountant', 'direction')
def send_invoice(invoice_id: int):
    """Send invoice via email."""
    try:
        from flask import g
        sent_by = g.user.id if g.user else 1
        
        # Get invoice
        query = GetInvoiceByIdQuery(id=invoice_id)
        invoice = mediator.dispatch(query)
        
        if not invoice:
            flash(_('Invoice not found'), 'error')
            return redirect(url_for('billing.invoices_list'))
        
        # Get customer email
        from app.domain.models.customer import Customer
        with get_session() as session:
            customer = session.get(Customer, invoice.customer_id)
            if not customer or not customer.email:
                flash(_('Customer email not found'), 'error')
                return redirect(url_for('billing.invoice_view', invoice_id=invoice_id))
            
            # Send invoice
            email_service = InvoiceEmailService()
            success = email_service.send_invoice(invoice, customer.email)
            
            if success:
                # Update invoice status
                command = SendInvoiceCommand(id=invoice_id, sent_by=sent_by)
                mediator.dispatch(command)
                flash(_('Invoice sent successfully'), 'success')
            else:
                flash(_('Failed to send invoice email'), 'error')
        
        if request.is_json:
            return jsonify({'status': 'success' if success else 'error'})
        else:
            return redirect(url_for('billing.invoice_view', invoice_id=invoice_id))
    except Exception as e:
        error_msg = _('An error occurred: %(error)s', error=str(e))
        if request.is_json:
            return jsonify({'status': 'error', 'message': error_msg}), 500
        else:
            flash(error_msg, 'error')
            return redirect(url_for('billing.invoice_view', invoice_id=invoice_id))


@billing_routes.route('/invoices/<int:invoice_id>/credit-note', methods=['GET', 'POST'])
@require_roles_or_redirect('admin', 'accountant', 'direction')
def create_credit_note(invoice_id: int):
    """Create a credit note for an invoice."""
    try:
        # Get invoice
        query = GetInvoiceByIdQuery(id=invoice_id)
        invoice = mediator.dispatch(query)
        
        if not invoice:
            flash(_('Invoice not found'), 'error')
            return redirect(url_for('billing.invoices_list'))
        
        if request.method == 'POST':
            from flask import g
            created_by = g.user.id if g.user else 1
            
            reason = request.form.get('reason', '').strip()
            total_amount = Decimal(request.form.get('total_amount', '0'))
            tax_amount = Decimal(request.form.get('tax_amount', '0'))
            
            if not reason:
                flash(_('Reason is required for credit note'), 'error')
                return render_template('billing/credit_note_form.html', invoice=invoice)
            
            if total_amount <= 0:
                flash(_('Credit note amount must be greater than 0'), 'error')
                return render_template('billing/credit_note_form.html', invoice=invoice)
            
            command = CreateCreditNoteCommand(
                invoice_id=invoice_id,
                customer_id=invoice.customer_id,
                reason=reason,
                total_amount=total_amount,
                tax_amount=tax_amount,
                created_by=created_by
            )
            
            credit_note_id = mediator.dispatch(command)
            
            flash(_('Credit note created successfully'), 'success')
            return redirect(url_for('billing.invoice_view', invoice_id=invoice_id))
        
        # GET request - show form
        return render_template('billing/credit_note_form.html', invoice=invoice)
    except ValueError as e:
        error_msg = str(e)
        flash(error_msg, 'error')
        return redirect(url_for('billing.invoice_view', invoice_id=invoice_id))
    except Exception as e:
        error_msg = _('An error occurred: %(error)s', error=str(e))
        flash(error_msg, 'error')
        return redirect(url_for('billing.invoice_view', invoice_id=invoice_id))


@billing_routes.route('/invoices/fec')
@require_roles_or_redirect('admin', 'accountant', 'direction')
def export_fec():
    """Export FEC file."""
    try:
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
        
        # Export FEC
        with get_session() as session:
            fec_service = FECExportService(session)
            fec_buffer = fec_service.export_invoices_to_fec(
                date_from=date_from_parsed,
                date_to=date_to_parsed
            )
            
            # Generate filename
            filename = f"FEC_{date_from_parsed or 'all'}_{date_to_parsed or 'all'}.txt"
            if not date_from_parsed and not date_to_parsed:
                filename = f"FEC_{datetime.now().strftime('%Y%m%d')}.txt"
            
            return send_file(
                fec_buffer,
                mimetype='text/plain; charset=utf-8',
                as_attachment=True,
                download_name=filename
            )
    except Exception as e:
        flash(_('An error occurred: %(error)s', error=str(e)), 'error')
        return redirect(url_for('billing.invoices_list'))
