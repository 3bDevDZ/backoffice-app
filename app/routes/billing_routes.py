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
from app.application.billing.payments.commands.commands import (
    CreatePaymentCommand, AllocatePaymentCommand, ReconcilePaymentCommand, ImportBankStatementCommand,
    ConfirmPaymentCommand, PaymentAllocationInput
)
from app.application.billing.payments.queries.queries import (
    ListPaymentsQuery, GetPaymentByIdQuery, GetOverdueInvoicesQuery, GetAgingReportQuery
)
from app.application.sales.orders.queries.queries import GetOrderByIdQuery
from app.application.customers.queries.queries import ListCustomersQuery
from app.services.invoice_pdf_service import InvoicePDFService
from app.services.invoice_email_service import InvoiceEmailService
from app.services.fec_export_service import FECExportService
from app.infrastructure.db import get_session
from app.security.session_auth import require_roles_or_redirect

billing_routes = Blueprint('billing', __name__)


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


@billing_routes.route('/invoices-new', methods=['GET', 'POST'])
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


@billing_routes.route('/invoices-fec')
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


# ==================== PAYMENT ROUTES ====================

@billing_routes.route('/payments')
@require_roles_or_redirect('admin', 'commercial', 'accountant', 'direction')
def payments_list():
    """List all payments."""
    try:
        # Get filters from query parameters
        customer_id = request.args.get('customer_id', type=int)
        status = request.args.get('status')
        payment_method = request.args.get('payment_method')
        reconciled = request.args.get('reconciled')
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
        
        # Parse reconciled boolean
        reconciled_bool = None
        if reconciled:
            reconciled_bool = reconciled.lower() == 'true'
        
        # Query payments
        query = ListPaymentsQuery(
            page=page,
            per_page=per_page,
            customer_id=customer_id,
            status=status,
            payment_method=payment_method,
            reconciled=reconciled_bool,
            date_from=date_from_parsed,
            date_to=date_to_parsed,
            search=search
        )
        
        payments = mediator.dispatch(query)
        
        # Get customers for filter dropdown
        customers_query = ListCustomersQuery(page=1, per_page=1000, status='active')
        customers = mediator.dispatch(customers_query)
        
        return render_template(
            'billing/payments_list.html',
            payments=payments,
            customers=customers,
            filters={
                'customer_id': customer_id,
                'status': status,
                'payment_method': payment_method,
                'reconciled': reconciled,
                'search': search,
                'date_from': date_from,
                'date_to': date_to
            }
        )
    except Exception as e:
        flash(_('An error occurred: %(error)s', error=str(e)), 'error')
        return render_template('billing/payments_list.html', payments=[], customers=[], filters={})


@billing_routes.route('/payments-new', methods=['GET', 'POST'])
@require_roles_or_redirect('admin', 'accountant', 'direction')
def create_payment():
    """Create a new payment."""
    try:
        from flask import g
        created_by = g.user.id if g.user else 1
        
        if request.method == 'POST':
            # Get form data
            customer_id = request.form.get('customer_id', type=int)
            payment_method = request.form.get('payment_method')
            amount = Decimal(request.form.get('amount', '0'))
            payment_date_str = request.form.get('payment_date')
            value_date_str = request.form.get('value_date')
            reference = request.form.get('reference', '').strip()
            notes = request.form.get('notes', '').strip()
            internal_notes = request.form.get('internal_notes', '').strip()
            
            # Parse dates
            payment_date = datetime.strptime(payment_date_str, '%Y-%m-%d').date() if payment_date_str else date.today()
            value_date = datetime.strptime(value_date_str, '%Y-%m-%d').date() if value_date_str else payment_date
            
            # Get auto-allocation strategy
            auto_allocation_enabled = request.form.get('auto_allocation_enabled') == 'on'
            auto_allocation_strategy = request.form.get('auto_allocation_strategy') if auto_allocation_enabled else None
            
            # Get manual allocations from form (only if auto-allocation is disabled)
            allocations = []
            if not auto_allocation_enabled:
                allocation_invoice_ids = request.form.getlist('allocation_invoice_id[]')
                allocation_amounts = request.form.getlist('allocation_amount[]')
                
                for invoice_id_str, amount_str in zip(allocation_invoice_ids, allocation_amounts):
                    try:
                        invoice_id = int(invoice_id_str)
                        alloc_amount = Decimal(amount_str)
                        if invoice_id > 0 and alloc_amount > 0:
                            allocations.append({
                                'invoice_id': invoice_id,
                                'amount': alloc_amount
                            })
                    except (ValueError, TypeError):
                        continue
            
            # Create payment command
            command = CreatePaymentCommand(
                customer_id=customer_id,
                payment_method=payment_method,
                amount=amount,
                payment_date=payment_date,
                value_date=value_date if value_date != payment_date else None,
                reference=reference or None,
                notes=notes or None,
                internal_notes=internal_notes or None,
                created_by=created_by,
                allocations=[PaymentAllocationInput(**alloc) for alloc in allocations],
                auto_allocation_strategy=auto_allocation_strategy
            )
            
            payment_id = mediator.dispatch(command)
            
            flash(_('Payment created successfully'), 'success')
            return redirect(url_for('billing.payment_view', payment_id=payment_id))
        
        # GET - show form
        # Get customers
        customers_query = ListCustomersQuery(page=1, per_page=1000, status='active')
        customers = mediator.dispatch(customers_query)
        
        # Get overdue invoices for default customer (if any)
        overdue_invoices = []
        default_customer_id = request.args.get('customer_id', type=int)
        if default_customer_id:
            overdue_query = GetOverdueInvoicesQuery(
                customer_id=default_customer_id,
                days_overdue=None,
                page=1,
                per_page=100
            )
            overdue_invoices = mediator.dispatch(overdue_query)
            # Convert to dict for JSON serialization
            overdue_invoices = [
                {
                    'id': inv.id,
                    'number': inv.invoice_number,
                    'remaining_amount': float(inv.remaining_amount),
                    'due_date': inv.due_date.isoformat() if inv.due_date else None,
                    'days_overdue': inv.days_overdue
                }
                for inv in overdue_invoices
            ]
        
        return render_template(
            'billing/payment_form.html',
            customers=customers,
            overdue_invoices=overdue_invoices,
            default_customer_id=default_customer_id,
            default_date=date.today()
        )
    except Exception as e:
        flash(_('An error occurred: %(error)s', error=str(e)), 'error')
        return redirect(url_for('billing.payments_list'))


@billing_routes.route('/payments/<int:payment_id>')
@require_roles_or_redirect('admin', 'commercial', 'accountant', 'direction')
def payment_view(payment_id: int):
    """View payment details."""
    try:
        query = GetPaymentByIdQuery(id=payment_id, include_allocations=True, include_invoices=True)
        payment = mediator.dispatch(query)
        
        if not payment:
            flash(_('Payment not found'), 'error')
            return redirect(url_for('billing.payments_list'))
        
        return render_template('billing/payment_view.html', payment=payment)
    except Exception as e:
        flash(_('An error occurred: %(error)s', error=str(e)), 'error')
        return redirect(url_for('billing.payments_list'))


@billing_routes.route('/payments/<int:payment_id>/confirm', methods=['POST'])
@require_roles_or_redirect('admin', 'accountant', 'direction')
def confirm_payment(payment_id: int):
    """Confirm a pending payment."""
    try:
        from flask import g
        confirmed_by = g.user.id if g.user else 1
        
        command = ConfirmPaymentCommand(
            payment_id=payment_id,
            confirmed_by=confirmed_by
        )
        
        mediator.dispatch(command)
        
        flash(_('Payment confirmed successfully'), 'success')
        return redirect(url_for('billing.payment_view', payment_id=payment_id))
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('billing.payment_view', payment_id=payment_id))
    except Exception as e:
        flash(_('An error occurred: %(error)s', error=str(e)), 'error')
        return redirect(url_for('billing.payment_view', payment_id=payment_id))


@billing_routes.route('/payments/<int:payment_id>/allocate', methods=['POST'])
@require_roles_or_redirect('admin', 'accountant', 'direction')
def allocate_payment(payment_id: int):
    """Allocate payment to invoices."""
    try:
        from flask import g
        created_by = g.user.id if g.user else 1
        
        # Get allocations from form
        allocation_invoice_ids = request.form.getlist('allocation_invoice_id[]')
        allocation_amounts = request.form.getlist('allocation_amount[]')
        
        allocations = []
        for invoice_id_str, amount_str in zip(allocation_invoice_ids, allocation_amounts):
            try:
                invoice_id = int(invoice_id_str)
                alloc_amount = Decimal(amount_str)
                if invoice_id > 0 and alloc_amount > 0:
                    allocations.append({
                        'invoice_id': invoice_id,
                        'amount': alloc_amount
                    })
            except (ValueError, TypeError):
                continue
        
        if not allocations:
            flash(_('No valid allocations provided'), 'error')
            return redirect(url_for('billing.payment_view', payment_id=payment_id))
        
        # Create allocation command
        command = AllocatePaymentCommand(
            payment_id=payment_id,
            allocations=[PaymentAllocationInput(**alloc) for alloc in allocations],
            created_by=created_by
        )
        
        mediator.dispatch(command)
        
        flash(_('Payment allocated successfully'), 'success')
        return redirect(url_for('billing.payment_view', payment_id=payment_id))
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('billing.payment_view', payment_id=payment_id))
    except Exception as e:
        flash(_('An error occurred: %(error)s', error=str(e)), 'error')
        return redirect(url_for('billing.payment_view', payment_id=payment_id))


@billing_routes.route('/payments-reconcile', methods=['GET', 'POST'])
@require_roles_or_redirect('admin', 'accountant', 'direction')
def reconcile_payments():
    """Bank reconciliation page."""
    try:
        if request.method == 'POST':
            from flask import g
            reconciled_by = g.user.id if g.user else 1
            
            # Check if it's a single payment reconciliation or bank statement import
            if request.form.get('action') == 'import_statement':
                # Import bank statement
                bank_account = request.form.get('bank_account', '').strip()
                statement_date_str = request.form.get('statement_date')
                
                if not bank_account or not statement_date_str:
                    flash(_('Bank account and statement date are required'), 'error')
                    return redirect(url_for('billing.reconcile_payments'))
                
                statement_date = datetime.strptime(statement_date_str, '%Y-%m-%d').date()
                
                # Parse transactions from JSON or form
                transactions_json = request.form.get('transactions')
                if transactions_json:
                    import json
                    transactions = json.loads(transactions_json)
                else:
                    # Parse from form fields
                    transactions = []
                    refs = request.form.getlist('transaction_reference[]')
                    amounts = request.form.getlist('transaction_amount[]')
                    dates = request.form.getlist('transaction_date[]')
                    
                    for ref, amount_str, date_str in zip(refs, amounts, dates):
                        if ref and amount_str and date_str:
                            try:
                                transactions.append({
                                    'reference': ref,
                                    'amount': Decimal(amount_str),
                                    'date': datetime.strptime(date_str, '%Y-%m-%d').date()
                                })
                            except (ValueError, TypeError):
                                continue
                
                command = ImportBankStatementCommand(
                    bank_account=bank_account,
                    statement_date=statement_date,
                    transactions=transactions,
                    imported_by=reconciled_by
                )
                
                result = mediator.dispatch(command)
                flash(_('Bank statement imported: %(matched)s matched, %(unmatched)s unmatched', 
                       matched=result.get('matched', 0), unmatched=result.get('unmatched', 0)), 'success')
                return redirect(url_for('billing.reconcile_payments'))
            else:
                # Single payment reconciliation
                payment_id = request.form.get('payment_id', type=int)
                bank_reference = request.form.get('bank_reference', '').strip()
                bank_account = request.form.get('bank_account', '').strip()
                
                if not payment_id or not bank_reference:
                    flash(_('Payment ID and bank reference are required'), 'error')
                    return redirect(url_for('billing.reconcile_payments'))
                
                command = ReconcilePaymentCommand(
                    payment_id=payment_id,
                    bank_reference=bank_reference,
                    bank_account=bank_account or None,
                    reconciled_by=reconciled_by
                )
                
                mediator.dispatch(command)
                flash(_('Payment reconciled successfully'), 'success')
                return redirect(url_for('billing.payment_view', payment_id=payment_id))
        
        # GET - show reconciliation page
        # Get unreconciled payments
        payments_query = ListPaymentsQuery(
            page=1,
            per_page=100,
            reconciled=False,
            status='confirmed'
        )
        unreconciled_payments = mediator.dispatch(payments_query)
        
        return render_template(
            'billing/reconciliation.html',
            unreconciled_payments=unreconciled_payments
        )
    except Exception as e:
        flash(_('An error occurred: %(error)s', error=str(e)), 'error')
        return redirect(url_for('billing.payments_list'))


@billing_routes.route('/payments-overdue')
@require_roles_or_redirect('admin', 'commercial', 'accountant', 'direction')
def overdue_invoices():
    """List overdue invoices."""
    try:
        customer_id = request.args.get('customer_id', type=int)
        days_overdue = request.args.get('days_overdue', type=int)
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        
        query = GetOverdueInvoicesQuery(
            customer_id=customer_id,
            days_overdue=days_overdue,
            page=page,
            per_page=per_page
        )
        
        overdue_invoices = mediator.dispatch(query)
        
        # Get customers for filter
        customers_query = ListCustomersQuery(page=1, per_page=1000, status='active')
        customers = mediator.dispatch(customers_query)
        
        return render_template(
            'billing/overdue_invoices.html',
            overdue_invoices=overdue_invoices,
            customers=customers,
            filters={
                'customer_id': customer_id,
                'days_overdue': days_overdue
            }
        )
    except Exception as e:
        flash(_('An error occurred: %(error)s', error=str(e)), 'error')
        return render_template('billing/overdue_invoices.html', overdue_invoices=[], customers=[], filters={})


@billing_routes.route('/payments-aging')
@require_roles_or_redirect('admin', 'commercial', 'accountant', 'direction')
def aging_report():
    """Aging report for outstanding invoices."""
    try:
        customer_id = request.args.get('customer_id', type=int)
        as_of_date_str = request.args.get('as_of_date')
        include_paid = request.args.get('include_paid', 'false').lower() == 'true'
        
        as_of_date = None
        if as_of_date_str:
            try:
                as_of_date = datetime.strptime(as_of_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        query = GetAgingReportQuery(
            customer_id=customer_id,
            as_of_date=as_of_date,
            include_paid=include_paid
        )
        
        aging_report = mediator.dispatch(query)
        
        # Get customers for filter
        customers_query = ListCustomersQuery(page=1, per_page=1000, status='active')
        customers = mediator.dispatch(customers_query)
        
        return render_template(
            'billing/aging_report.html',
            aging_report=aging_report,
            customers=customers,
            filters={
                'customer_id': customer_id,
                'as_of_date': as_of_date_str,
                'include_paid': include_paid
            }
        )
    except Exception as e:
        flash(_('An error occurred: %(error)s', error=str(e)), 'error')
        return render_template('billing/aging_report.html', aging_report=[], customers=[], filters={})


@billing_routes.route('/payments/data/customers')
@require_roles_or_redirect('admin', 'commercial', 'accountant', 'direction')
def get_payment_customers_json():
    """Get customers JSON for Select2 AJAX."""
    try:
        search = request.args.get('q', '').strip()
        customers_query = ListCustomersQuery(page=1, per_page=50, status='active', search=search)
        customers = mediator.dispatch(customers_query)
        
        results = []
        for customer in customers:
            results.append({
                'id': customer.id,
                'text': f"{customer.name or customer.company_name} ({customer.code})"
            })
        
        return jsonify({'results': results})
    except Exception as e:
        return jsonify({'results': [], 'error': str(e)}), 500


@billing_routes.route('/payments/data/customer-outstanding')
@require_roles_or_redirect('admin', 'commercial', 'accountant', 'direction')
def get_customer_outstanding_json():
    """Get customer's outstanding invoices and total for payment form."""
    try:
        customer_id = request.args.get('customer_id', type=int)
        if not customer_id:
            return jsonify({'total_outstanding': 0, 'invoice_count': 0, 'invoices': []})
        
        # Get overdue invoices
        overdue_query = GetOverdueInvoicesQuery(
            customer_id=customer_id,
            days_overdue=None,
            page=1,
            per_page=100
        )
        overdue_invoices = mediator.dispatch(overdue_query)
        
        # Calculate total outstanding
        total_outstanding = sum(inv.remaining_amount for inv in overdue_invoices)
        
        # Convert to JSON-serializable format
        invoices = [
            {
                'id': inv.id,
                'number': inv.invoice_number,
                'remaining_amount': float(inv.remaining_amount),
                'due_date': inv.due_date.isoformat() if inv.due_date else None,
                'days_overdue': inv.days_overdue
            }
            for inv in overdue_invoices
        ]
        
        return jsonify({
            'total_outstanding': float(total_outstanding),
            'invoice_count': len(invoices),
            'invoices': invoices
        })
    except Exception as e:
        return jsonify({'total_outstanding': 0, 'invoice_count': 0, 'invoices': [], 'error': str(e)}), 500


@billing_routes.route('/payments-dashboard')
@require_roles_or_redirect('admin', 'commercial', 'accountant', 'direction')
def payments_dashboard():
    """Dashboard for outstanding payments with KPIs and charts."""
    try:
        from datetime import date
        
        # Get aging report for all customers
        aging_query = GetAgingReportQuery(
            customer_id=None,
            as_of_date=date.today(),
            include_paid=False
        )
        aging_report = mediator.dispatch(aging_query)
        
        # Calculate KPIs
        total_outstanding = sum(customer.total_outstanding for customer in aging_report) if aging_report else Decimal(0)
        
        # Calculate by buckets
        bucket_0_30 = Decimal(0)
        bucket_31_60 = Decimal(0)
        bucket_61_90 = Decimal(0)
        bucket_90_plus = Decimal(0)
        
        invoice_count_0_30 = 0
        invoice_count_31_60 = 0
        invoice_count_61_90 = 0
        invoice_count_90_plus = 0
        
        for customer in aging_report:
            if customer.buckets:
                for bucket in customer.buckets:
                    if bucket.bucket_name == '0-30':
                        bucket_0_30 += bucket.total_amount
                        invoice_count_0_30 += bucket.invoice_count
                    elif bucket.bucket_name == '31-60':
                        bucket_31_60 += bucket.total_amount
                        invoice_count_31_60 += bucket.invoice_count
                    elif bucket.bucket_name == '61-90':
                        bucket_61_90 += bucket.total_amount
                        invoice_count_61_90 += bucket.invoice_count
                    elif bucket.bucket_name == '90+':
                        bucket_90_plus += bucket.total_amount
                        invoice_count_90_plus += bucket.invoice_count
        
        # Get overdue invoices count
        overdue_query = GetOverdueInvoicesQuery(
            customer_id=None,
            days_overdue=None,
            page=1,
            per_page=10000
        )
        overdue_invoices = mediator.dispatch(overdue_query)
        total_overdue_count = len(overdue_invoices)
        
        # Calculate total overdue amount
        total_overdue_amount = sum(inv.remaining_amount for inv in overdue_invoices) if overdue_invoices else Decimal(0)
        
        # Get top 10 customers by outstanding amount
        top_customers = sorted(aging_report, key=lambda x: x.total_outstanding, reverse=True)[:10] if aging_report else []
        
        # Calculate percentage distribution
        if total_outstanding > 0:
            pct_0_30 = (bucket_0_30 / total_outstanding * 100).quantize(Decimal('0.01'))
            pct_31_60 = (bucket_31_60 / total_outstanding * 100).quantize(Decimal('0.01'))
            pct_61_90 = (bucket_61_90 / total_outstanding * 100).quantize(Decimal('0.01'))
            pct_90_plus = (bucket_90_plus / total_outstanding * 100).quantize(Decimal('0.01'))
        else:
            pct_0_30 = pct_31_60 = pct_61_90 = pct_90_plus = Decimal(0)
        
        # Prepare chart data
        chart_data = {
            'labels': ['0-30 jours', '31-60 jours', '61-90 jours', '90+ jours'],
            'amounts': [
                float(bucket_0_30),
                float(bucket_31_60),
                float(bucket_61_90),
                float(bucket_90_plus)
            ],
            'counts': [
                invoice_count_0_30,
                invoice_count_31_60,
                invoice_count_61_90,
                invoice_count_90_plus
            ]
        }
        
        # Top customers chart data
        top_customers_chart = {
            'labels': [c.customer_name or c.customer_code or f'Client #{c.customer_id}' for c in top_customers],
            'amounts': [float(c.total_outstanding) for c in top_customers]
        }
        
        # Convert Decimal to float for template rendering
        return render_template(
            'billing/payments_dashboard.html',
            total_outstanding=float(total_outstanding),
            total_overdue_amount=float(total_overdue_amount),
            total_overdue_count=total_overdue_count,
            bucket_0_30=float(bucket_0_30),
            bucket_31_60=float(bucket_31_60),
            bucket_61_90=float(bucket_61_90),
            bucket_90_plus=float(bucket_90_plus),
            invoice_count_0_30=invoice_count_0_30,
            invoice_count_31_60=invoice_count_31_60,
            invoice_count_61_90=invoice_count_61_90,
            invoice_count_90_plus=invoice_count_90_plus,
            pct_0_30=float(pct_0_30),
            pct_31_60=float(pct_31_60),
            pct_61_90=float(pct_61_90),
            pct_90_plus=float(pct_90_plus),
            top_customers=top_customers,
            chart_data=chart_data,
            top_customers_chart=top_customers_chart,
            aging_report=aging_report[:20] if aging_report else []  # Limit to top 20 for table
        )
    except Exception as e:
        flash(_('An error occurred: %(error)s', error=str(e)), 'error')
        return redirect(url_for('billing.payments_list'))
