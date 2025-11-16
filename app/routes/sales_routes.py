"""Frontend route handlers for sales/quotes and orders pages."""
import re
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_babel import get_locale, gettext as _
from app.application.common.mediator import mediator
from app.application.sales.quotes.queries.queries import ListQuotesQuery, GetQuoteByIdQuery
from app.application.sales.quotes.commands.commands import (
    CreateQuoteCommand, UpdateQuoteCommand, SendQuoteCommand,
    AcceptQuoteCommand, RejectQuoteCommand, CancelQuoteCommand, DeleteQuoteCommand,
    AddQuoteLineCommand, UpdateQuoteLineCommand, RemoveQuoteLineCommand,
    QuoteLineInput
)
from app.application.sales.orders.queries.queries import ListOrdersQuery, GetOrderByIdQuery
from app.application.sales.orders.commands.commands import (
    CreateOrderCommand, UpdateOrderCommand, ConfirmOrderCommand,
    CancelOrderCommand, UpdateOrderStatusCommand,
    AddOrderLineCommand, UpdateOrderLineCommand, RemoveOrderLineCommand
)
from app.application.customers.queries.queries import ListCustomersQuery
from app.security.session_auth import require_roles_or_redirect, get_current_user
from decimal import Decimal
from datetime import date, datetime, timedelta

sales_routes = Blueprint('sales', __name__)


# Quote Routes
@sales_routes.route('/quotes')
@require_roles_or_redirect('admin', 'commercial', 'direction')
def quotes_list():
    """Render quotes list page."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    # Get query parameters
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 20)), 100)
    search = request.args.get('search')
    status = request.args.get('status')
    customer_id = request.args.get('customer_id', type=int)
    
    # Fetch quotes via query
    query = ListQuotesQuery(
        page=page,
        per_page=per_page,
        search=search,
        status=status,
        customer_id=customer_id
    )
    result = mediator.dispatch(query)
    
    return render_template(
        'sales/quotes_list.html',
        quotes=result['items'],
        pagination={
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        },
        search=search,
        status=status,
        customer_id=customer_id,
        locale=locale,
        direction=direction
    )


@sales_routes.route('/quotes/data/customers')
@require_roles_or_redirect('admin', 'commercial')
def get_customers_json():
    """Get customers list as JSON for quote form (uses session auth, not JWT)."""
    try:
        query = ListCustomersQuery(
            page=1,
            per_page=1000,
            status='active'
        )
        customers = mediator.dispatch(query)
        
        # Convert to simple dict format
        customers_data = []
        for c in customers:
            customers_data.append({
                'id': c.id,
                'code': c.code,
                'name': c.company_name or (f"{c.first_name} {c.last_name}" if c.first_name and c.last_name else c.name),
                'company_name': c.company_name,
                'first_name': c.first_name,
                'last_name': c.last_name
            })
        
        return jsonify({
            'success': True,
            'data': {
                'items': customers_data
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@sales_routes.route('/quotes/data/customer/<int:customer_id>/commercial-conditions')
@require_roles_or_redirect('admin', 'commercial')
def get_customer_commercial_conditions(customer_id: int):
    """Get customer commercial conditions (discount info) for quote form."""
    try:
        from app.application.customers.queries.queries import GetCustomerByIdQuery
        from app.infrastructure.db import get_session
        from app.domain.models.customer import Customer
        
        with get_session() as session:
            customer = session.get(Customer, customer_id)
            if not customer:
                return jsonify({
                    'success': False,
                    'error': 'Customer not found'
                }), 404
            
            commercial_conditions = None
            if customer.commercial_conditions:
                cc = customer.commercial_conditions
                commercial_conditions = {
                    'default_discount_percent': float(cc.default_discount_percent) if cc.default_discount_percent else 0.0,
                    'price_list_id': cc.price_list_id,
                    'price_list_name': cc.price_list.name if cc.price_list else None,
                    'payment_terms_days': cc.payment_terms_days,
                    'credit_limit': float(cc.credit_limit) if cc.credit_limit else None
                }
            
            return jsonify({
                'success': True,
                'data': {
                    'customer_id': customer.id,
                    'customer_code': customer.code,
                    'customer_name': customer.company_name or (f"{customer.first_name} {customer.last_name}" if customer.first_name and customer.last_name else customer.name),
                    'commercial_conditions': commercial_conditions
                }
            })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@sales_routes.route('/quotes/data/products')
@require_roles_or_redirect('admin', 'commercial')
def get_products_json():
    """Get products list as JSON for quote form (uses session auth, not JWT)."""
    try:
        from app.application.products.queries.queries import ListProductsQuery
        
        query = ListProductsQuery(
            page=1,
            per_page=1000,
            status='active'
        )
        products = mediator.dispatch(query)
        
        # Convert to simple dict format
        products_data = []
        for p in products:
            products_data.append({
                'id': p.id,
                'code': p.code,
                'name': p.name,
                'price': float(p.price) if p.price else 0.0
            })
        
        return jsonify({
            'success': True,
            'data': {
                'items': products_data
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@sales_routes.route('/quotes/data/price-for-customer')
@require_roles_or_redirect('admin', 'commercial')
def get_price_for_customer_json():
    """Get price for a product considering customer's commercial conditions (uses session auth, not JWT)."""
    try:
        product_id = request.args.get('product_id', type=int)
        customer_id = request.args.get('customer_id', type=int)
        quantity = request.args.get('quantity', type=float, default=1.0)
        
        if not product_id or not customer_id:
            return jsonify({
                'success': False,
                'error': 'product_id and customer_id are required'
            }), 400
        
        from app.infrastructure.db import get_session
        from app.services.pricing_service import PricingService
        from decimal import Decimal
        
        with get_session() as session:
            pricing_service = PricingService(session)
            price_result = pricing_service.get_price_for_customer(
                product_id=product_id,
                customer_id=customer_id,
                quantity=Decimal(str(quantity))
            )
            
            return jsonify({
                'success': True,
                'data': {
                    'base_price': float(price_result.base_price),
                    'customer_price': float(price_result.customer_price),
                    'applied_discount_percent': float(price_result.applied_discount_percent),
                    'final_price': float(price_result.final_price),
                    'discount_amount': float(price_result.discount_amount),
                    'source': price_result.source
                }
            })
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@sales_routes.route('/quotes/new')
@require_roles_or_redirect('admin', 'commercial')
def create_quote():
    """Render new quote form page."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    # Default valid_until: 30 days from today
    default_valid_until = (date.today() + timedelta(days=30)).isoformat()
    
    return render_template(
        'sales/quote_form.html',
        quote=None,
        default_valid_until=default_valid_until,
        locale=locale,
        direction=direction
    )


@sales_routes.route('/quotes/<int:quote_id>')
@require_roles_or_redirect('admin', 'commercial', 'direction')
def view_quote(quote_id: int):
    """Render quote detail/view page."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    # Fetch quote
    quote_dto = mediator.dispatch(GetQuoteByIdQuery(id=quote_id, include_lines=True, include_versions=False))
    
    return render_template(
        'sales/quote_view.html',
        quote=quote_dto,
        locale=locale,
        direction=direction
    )


@sales_routes.route('/quotes/<int:quote_id>/edit')
@require_roles_or_redirect('admin', 'commercial')
def edit_quote(quote_id: int):
    """Render edit quote form page."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    # Fetch quote
    quote_dto = mediator.dispatch(GetQuoteByIdQuery(id=quote_id, include_lines=True))
    
    # Check if quote can be edited
    if quote_dto.status not in ['draft']:
        flash(_('Only draft quotes can be edited. Creating a new version...'), 'warning')
        # TODO: Implement version creation
    
    return render_template(
        'sales/quote_form.html',
        quote=quote_dto,
        locale=locale,
        direction=direction
    )


@sales_routes.route('/quotes', methods=['POST'])
@require_roles_or_redirect('admin', 'commercial')
def save_quote():
    """Handle quote creation/update form submission."""
    try:
        # Get current user from session
        current_user = get_current_user()
        if not current_user:
            return jsonify({'status': 'error', 'message': _('Authentication required')}), 401
        
        # Get form data
        data = request.get_json() if request.is_json else request.form.to_dict()
        
        # Convert quote_id to int if present
        quote_id = None
        if data.get('id'):
            try:
                quote_id = int(data.get('id'))
            except (ValueError, TypeError):
                quote_id = None
        
        if quote_id:
            # Update existing quote
            valid_until = None
            if data.get('valid_until'):
                valid_until = datetime.fromisoformat(data['valid_until'].replace('Z', '+00:00')).date()
            
            command = UpdateQuoteCommand(
                id=quote_id,
                valid_until=valid_until,
                discount_percent=Decimal(str(data.get('discount_percent', 0))) if data.get('discount_percent') else None,
                notes=data.get('notes'),
                internal_notes=data.get('internal_notes')
            )
            result = mediator.dispatch(command)
            
            # Handle both quote object and quote_id
            if isinstance(result, int):
                quote_id = result
            else:
                quote_id = result.id
            
            flash(_('Quote updated successfully'), 'success')
        else:
            # Create new quote
            lines = []
            for line_data in data.get('lines', []):
                lines.append(QuoteLineInput(
                    product_id=line_data['product_id'],
                    quantity=Decimal(str(line_data['quantity'])),
                    unit_price=Decimal(str(line_data['unit_price'])),
                    variant_id=line_data.get('variant_id'),
                    discount_percent=Decimal(str(line_data.get('discount_percent', 0))),
                    tax_rate=Decimal(str(line_data.get('tax_rate', 20.0)))
                ))
            
            valid_until = None
            if data.get('valid_until'):
                valid_until = datetime.fromisoformat(data['valid_until'].replace('Z', '+00:00')).date()
            
            command = CreateQuoteCommand(
                customer_id=data['customer_id'],
                created_by=current_user.id,
                number=data.get('number'),
                valid_until=valid_until,
                discount_percent=Decimal(str(data.get('discount_percent', 0))),
                notes=data.get('notes'),
                internal_notes=data.get('internal_notes'),
                lines=lines
            )
            result = mediator.dispatch(command)
            
            # Handle both quote object and quote_id (for detached instance safety)
            if isinstance(result, int):
                quote_id = result
            else:
                quote_id = result.id
            
            flash(_('Quote created successfully'), 'success')
        
        if request.is_json:
            return jsonify({'status': 'success', 'quote_id': quote_id})
        else:
            return redirect(url_for('sales.view_quote', quote_id=quote_id))
            
    except ValueError as e:
        error_msg = str(e)
        # Get quote_id from data if not already set
        quote_id = None
        if 'data' in locals() and data.get('id'):
            try:
                quote_id = int(data.get('id'))
            except (ValueError, TypeError):
                pass
        
        if request.is_json:
            return jsonify({'status': 'error', 'message': error_msg}), 400
        else:
            flash(error_msg, 'error')
            if quote_id:
                return redirect(url_for('sales.edit_quote', quote_id=quote_id))
            else:
                return redirect(url_for('sales.create_quote'))
    except Exception as e:
        error_msg = _('An error occurred: %(error)s', error=str(e))
        # Get quote_id from data if not already set
        quote_id = None
        if 'data' in locals() and data.get('id'):
            try:
                quote_id = int(data.get('id'))
            except (ValueError, TypeError):
                pass
        
        if request.is_json:
            return jsonify({'status': 'error', 'message': error_msg}), 500
        else:
            flash(error_msg, 'error')
            if quote_id:
                return redirect(url_for('sales.edit_quote', quote_id=quote_id))
            else:
                return redirect(url_for('sales.create_quote'))


@sales_routes.route('/quotes/<int:quote_id>/send', methods=['POST'])
@require_roles_or_redirect('admin', 'commercial')
def send_quote(quote_id: int):
    """Handle send quote action."""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'status': 'error', 'message': _('Authentication required')}), 401
        
        command = SendQuoteCommand(id=quote_id, sent_by=current_user.id)
        result_quote_id = mediator.dispatch(command)
        
        # Handle both int (new) and Quote object (old) for backward compatibility
        if isinstance(result_quote_id, int):
            quote_id = result_quote_id
        else:
            quote_id = result_quote_id.id
        
        flash(_('Quote sent successfully'), 'success')
        
        if request.is_json:
            return jsonify({'status': 'success', 'quote_id': quote_id})
        else:
            return redirect(url_for('sales.view_quote', quote_id=quote_id))
            
    except ValueError as e:
        error_msg = str(e)
        if request.is_json:
            return jsonify({'status': 'error', 'message': error_msg}), 400
        else:
            flash(error_msg, 'error')
            return redirect(url_for('sales.view_quote', quote_id=quote_id))
    except Exception as e:
        error_msg = _('An error occurred: %(error)s', error=str(e))
        if request.is_json:
            return jsonify({'status': 'error', 'message': error_msg}), 500
        else:
            flash(error_msg, 'error')
            return redirect(url_for('sales.view_quote', quote_id=quote_id))


@sales_routes.route('/quotes/<int:quote_id>/accept', methods=['POST'])
@require_roles_or_redirect('admin', 'commercial', 'direction')
def accept_quote(quote_id: int):
    """Handle accept quote action."""
    try:
        command = AcceptQuoteCommand(id=quote_id)
        result_quote_id = mediator.dispatch(command)
        
        # Handle both int (new) and Quote object (old) for backward compatibility
        if isinstance(result_quote_id, int):
            quote_id = result_quote_id
        else:
            quote_id = result_quote_id.id
        
        flash(_('Quote accepted successfully'), 'success')
        
        if request.is_json:
            return jsonify({'status': 'success', 'quote_id': quote_id})
        else:
            return redirect(url_for('sales.view_quote', quote_id=quote_id))
            
    except ValueError as e:
        error_msg = str(e)
        if request.is_json:
            return jsonify({'status': 'error', 'message': error_msg}), 400
        else:
            flash(error_msg, 'error')
            return redirect(url_for('sales.view_quote', quote_id=quote_id))
    except Exception as e:
        error_msg = _('An error occurred: %(error)s', error=str(e))
        if request.is_json:
            return jsonify({'status': 'error', 'message': error_msg}), 500
        else:
            flash(error_msg, 'error')
            return redirect(url_for('sales.view_quote', quote_id=quote_id))


@sales_routes.route('/quotes/<int:quote_id>/reject', methods=['POST'])
@require_roles_or_redirect('admin', 'commercial', 'direction')
def reject_quote(quote_id: int):
    """Handle reject quote action."""
    try:
        command = RejectQuoteCommand(id=quote_id)
        result_quote_id = mediator.dispatch(command)
        
        # Handle both int (new) and Quote object (old) for backward compatibility
        if isinstance(result_quote_id, int):
            quote_id = result_quote_id
        else:
            quote_id = result_quote_id.id
        
        flash(_('Quote rejected'), 'info')
        
        if request.is_json:
            return jsonify({'status': 'success', 'quote_id': quote_id})
        else:
            return redirect(url_for('sales.view_quote', quote_id=quote_id))
            
    except ValueError as e:
        error_msg = str(e)
        if request.is_json:
            return jsonify({'status': 'error', 'message': error_msg}), 400
        else:
            flash(error_msg, 'error')
            return redirect(url_for('sales.view_quote', quote_id=quote_id))
    except Exception as e:
        error_msg = _('An error occurred: %(error)s', error=str(e))
        if request.is_json:
            return jsonify({'status': 'error', 'message': error_msg}), 500
        else:
            flash(error_msg, 'error')
            return redirect(url_for('sales.view_quote', quote_id=quote_id))


@sales_routes.route('/quotes/<int:quote_id>/delete', methods=['POST'])
@require_roles_or_redirect('admin', 'commercial')
def delete_quote(quote_id: int):
    """Delete a draft quote."""
    try:
        command = DeleteQuoteCommand(id=quote_id)
        mediator.dispatch(command)
        
        flash(_('Quote deleted successfully'), 'success')
        
        if request.is_json:
            return jsonify({'status': 'success'})
        else:
            return redirect(url_for('sales.quotes_list'))
            
    except ValueError as e:
        error_msg = str(e)
        if request.is_json:
            return jsonify({'status': 'error', 'message': error_msg}), 400
        else:
            flash(error_msg, 'error')
            return redirect(url_for('sales.quotes_list'))
    except Exception as e:
        error_msg = _('An error occurred: %(error)s', error=str(e))
        if request.is_json:
            return jsonify({'status': 'error', 'message': error_msg}), 500
        else:
            flash(error_msg, 'error')
            return redirect(url_for('sales.quotes_list'))


@sales_routes.route('/quotes/<int:quote_id>/convert-to-order')
@require_roles_or_redirect('admin', 'commercial')
def convert_quote_to_order(quote_id: int):
    """Convert quote to order - redirects to order creation form with quote pre-filled."""
    try:
        quote = mediator.dispatch(GetQuoteByIdQuery(id=quote_id, include_lines=True))
        if quote.status != 'accepted':
            flash(_('Quote must be accepted before creating an order'), 'error')
            return redirect(url_for('sales.view_quote', quote_id=quote_id))
        
        return redirect(url_for('sales.create_order', quote_id=quote_id))
    except Exception:
        flash(_('Quote not found'), 'error')
        return redirect(url_for('sales.quotes_list'))


# Order Routes
@sales_routes.route('/orders')
@require_roles_or_redirect('admin', 'commercial', 'direction', 'logistics')
def orders_list():
    """Render orders list page."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    # Get query parameters
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 20)), 100)
    search = request.args.get('search')
    status = request.args.get('status')
    customer_id = request.args.get('customer_id', type=int)
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    # Parse dates
    parsed_date_from = None
    if date_from:
        parsed_date_from = datetime.fromisoformat(date_from).date()
    
    parsed_date_to = None
    if date_to:
        parsed_date_to = datetime.fromisoformat(date_to).date()
    
    # Fetch orders via query
    query = ListOrdersQuery(
        page=page,
        per_page=per_page,
        search=search,
        status=status,
        customer_id=customer_id,
        date_from=parsed_date_from,
        date_to=parsed_date_to
    )
    result = mediator.dispatch(query)
    
    return render_template(
        'sales/orders_list.html',
        orders=result['items'],
        pagination={
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        },
        search=search,
        status=status,
        customer_id=customer_id,
        date_from=date_from,
        date_to=date_to,
        locale=locale,
        direction=direction
    )


@sales_routes.route('/orders/data/customers')
@require_roles_or_redirect('admin', 'commercial')
def get_order_customers_json():
    """Get customers list as JSON for order form (uses session auth, not JWT)."""
    try:
        query = ListCustomersQuery(
            page=1,
            per_page=1000,
            status='active'
        )
        customers = mediator.dispatch(query)
        
        # Convert to simple dict format
        customers_data = []
        for c in customers:
            customers_data.append({
                'id': c.id,
                'code': c.code,
                'name': c.company_name or (f"{c.first_name} {c.last_name}" if c.first_name and c.last_name else c.name),
                'company_name': c.company_name,
                'first_name': c.first_name,
                'last_name': c.last_name
            })
        
        return jsonify({
            'success': True,
            'data': {
                'items': customers_data
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@sales_routes.route('/orders/data/products')
@require_roles_or_redirect('admin', 'commercial')
def get_order_products_json():
    """Get products list as JSON for order form (uses session auth, not JWT)."""
    try:
        from app.application.products.queries.queries import ListProductsQuery
        
        query = ListProductsQuery(
            page=1,
            per_page=1000,
            status='active'
        )
        products = mediator.dispatch(query)
        
        # Convert to simple dict format
        products_data = []
        for p in products:
            products_data.append({
                'id': p.id,
                'code': p.code,
                'name': p.name,
                'price': float(p.price) if p.price else 0.0
            })
        
        return jsonify({
            'success': True,
            'data': {
                'items': products_data
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@sales_routes.route('/orders/data/price-for-customer')
@require_roles_or_redirect('admin', 'commercial')
def get_order_price_for_customer():
    """Get price for customer and product (uses session auth, not JWT)."""
    try:
        from app.services.pricing_service import PricingService
        from app.infrastructure.db import get_session
        
        customer_id = request.args.get('customer_id', type=int)
        product_id = request.args.get('product_id', type=int)
        quantity = Decimal(str(request.args.get('quantity', 1)))
        
        if not customer_id or not product_id:
            return jsonify({
                'success': False,
                'error': 'customer_id and product_id are required'
            }), 400
        
        with get_session() as session:
            pricing_service = PricingService(session)
            price_result = pricing_service.get_price_for_customer(
                product_id=product_id,
                customer_id=customer_id,
                quantity=quantity
            )
            
            return jsonify({
                'success': True,
                'data': {
                    'base_price': float(price_result.base_price),
                    'customer_price': float(price_result.customer_price),
                    'applied_discount_percent': float(price_result.applied_discount_percent),
                    'final_price': float(price_result.final_price),
                    'discount_amount': float(price_result.discount_amount),
                    'source': price_result.source
                }
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@sales_routes.route('/orders/new')
@require_roles_or_redirect('admin', 'commercial')
def create_order():
    """Render new order form page."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    # Check if creating from quote
    quote_id = request.args.get('quote_id', type=int)
    quote = None
    if quote_id:
        try:
            quote = mediator.dispatch(GetQuoteByIdQuery(id=quote_id, include_lines=True))
            if quote.status != 'accepted':
                flash(_('Quote must be accepted before creating an order'), 'error')
                return redirect(url_for('sales.quotes_list'))
        except Exception:
            flash(_('Quote not found'), 'error')
            return redirect(url_for('sales.quotes_list'))
    
    return render_template(
        'sales/order_form.html',
        order=None,
        quote=quote,
        locale=locale,
        direction=direction
    )


@sales_routes.route('/orders/<int:order_id>')
@require_roles_or_redirect('admin', 'commercial', 'direction', 'logistics')
def view_order(order_id: int):
    """View order details."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    try:
        order = mediator.dispatch(GetOrderByIdQuery(order_id=order_id, include_lines=True, include_reservations=True))
    except ValueError:
        flash(_('Order not found'), 'error')
        return redirect(url_for('sales.orders_list'))
    
    return render_template(
        'sales/order_view.html',
        order=order,
        locale=locale,
        direction=direction
    )


@sales_routes.route('/orders/<int:order_id>/pdf')
@require_roles_or_redirect('admin', 'commercial', 'direction', 'logistics')
def download_order_pdf(order_id: int):
    """Download order PDF."""
    try:
        from app.services.pdf_service import pdf_service
        from flask import make_response
        
        # Fetch order
        order_dto = mediator.dispatch(GetOrderByIdQuery(order_id=order_id, include_lines=True, include_reservations=False))
        
        # Convert DTO to dict for PDF service
        order_data = {
            'number': order_dto.number,
            'status': order_dto.status,
            'created_at': order_dto.created_at,
            'confirmed_at': order_dto.confirmed_at,
            'quote_number': order_dto.quote_number,
            'delivery_date_requested': order_dto.delivery_date_requested,
            'delivery_date_promised': order_dto.delivery_date_promised,
            'customer': {
                'name': order_dto.customer_name,
                'code': order_dto.customer_code
            },
            'customer_name': order_dto.customer_name,
            'customer_code': order_dto.customer_code,
            'subtotal': float(order_dto.subtotal),
            'discount_percent': float(order_dto.discount_percent),
            'discount_amount': float(order_dto.discount_amount),
            'tax_amount': float(order_dto.tax_amount),
            'total': float(order_dto.total),
            'delivery_instructions': order_dto.delivery_instructions,
            'notes': order_dto.notes,
            'lines': [
                {
                    'product_name': line.product_name or 'N/A',
                    'product_code': line.product_code or '',
                    'quantity': float(line.quantity),
                    'unit_price': float(line.unit_price),
                    'discount_percent': float(line.discount_percent),
                    'line_total_ht': float(line.line_total_ht),
                    'tax_rate': float(line.tax_rate),
                    'line_total_ttc': float(line.line_total_ttc)
                }
                for line in (order_dto.lines or [])
            ]
        }
        
        # Generate PDF
        pdf_buffer = pdf_service.generate_order_pdf(order_data)
        
        # Create response
        response = make_response(pdf_buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename=commande-{order_dto.number}.pdf'
        
        return response
    except Exception as e:
        import traceback
        traceback.print_exc()
        flash(_('Error generating PDF: %(error)s', error=str(e)), 'error')
        return redirect(url_for('sales.view_order', order_id=order_id))


@sales_routes.route('/orders/<int:order_id>/edit')
@require_roles_or_redirect('admin', 'commercial')
def edit_order(order_id: int):
    """Edit order form page."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    try:
        order = mediator.dispatch(GetOrderByIdQuery(order_id=order_id, include_lines=True))
        if order.status != 'draft':
            flash(_('Only draft orders can be edited'), 'error')
            return redirect(url_for('sales.view_order', order_id=order_id))
    except ValueError:
        flash(_('Order not found'), 'error')
        return redirect(url_for('sales.orders_list'))
    
    return render_template(
        'sales/order_form.html',
        order=order,
        quote=None,
        locale=locale,
        direction=direction
    )


@sales_routes.route('/orders', methods=['POST'])
@require_roles_or_redirect('admin', 'commercial')
def save_order():
    """Save order (create or update)."""
    try:
        data = request.form.to_dict()
        order_id = data.get('id')
        
        # Get current user
        current_user = get_current_user()
        if not current_user:
            flash(_('Authentication required'), 'error')
            return redirect(url_for('sales.orders_list'))
        
        # Parse dates
        delivery_date_requested = None
        if data.get('delivery_date_requested'):
            delivery_date_requested = datetime.fromisoformat(data['delivery_date_requested']).date()
        
        delivery_date_promised = None
        if data.get('delivery_date_promised'):
            delivery_date_promised = datetime.fromisoformat(data['delivery_date_promised']).date()
        
        if order_id:
            # Update existing order
            command = UpdateOrderCommand(
                order_id=int(order_id),
                delivery_address_id=int(data['delivery_address_id']) if data.get('delivery_address_id') else None,
                delivery_date_requested=delivery_date_requested,
                delivery_date_promised=delivery_date_promised,
                delivery_instructions=data.get('delivery_instructions'),
                notes=data.get('notes'),
                discount_percent=Decimal(str(data.get('discount_percent', 0))) if data.get('discount_percent') else None
            )
            mediator.dispatch(command)
            flash(_('Order updated successfully'), 'success')
            return redirect(url_for('sales.view_order', order_id=int(order_id)))
        else:
            # Create new order
            if not data.get('customer_id'):
                flash(_('Customer is required'), 'error')
                return redirect(url_for('sales.create_order'))
            
            command = CreateOrderCommand(
                customer_id=int(data['customer_id']),
                created_by=current_user.id,
                quote_id=int(data['quote_id']) if data.get('quote_id') else None,
                delivery_address_id=int(data['delivery_address_id']) if data.get('delivery_address_id') else None,
                delivery_date_requested=delivery_date_requested,
                delivery_date_promised=delivery_date_promised,
                delivery_instructions=data.get('delivery_instructions'),
                notes=data.get('notes'),
                discount_percent=Decimal(str(data.get('discount_percent', 0)))
            )
            
            order_id = mediator.dispatch(command)
            
            # Parse lines from form data
            # Flask doesn't automatically parse arrays with indices like lines[0][product_id]
            # We need to manually extract them
            lines_dict = {}
            for key, value in request.form.items():
                if key.startswith('lines[') and ']' in key:
                    # Extract index and field name from keys like "lines[0][product_id]"
                    match = re.match(r'lines\[(\d+)\]\[(\w+)\]', key)
                    if match:
                        idx = int(match.group(1))
                        field = match.group(2)
                        if idx not in lines_dict:
                            lines_dict[idx] = {}
                        lines_dict[idx][field] = value
            
            # Add lines if provided
            # If order was created from quote, lines are already in the form, so we add them here
            # If no lines in form but quote exists, copy from quote (fallback)
            if lines_dict:
                # Add lines from form
                for idx in sorted(lines_dict.keys()):
                    line_data = lines_dict[idx]
                    product_id = line_data.get('product_id')
                    if product_id:
                        line_quantity = Decimal(str(line_data.get('quantity', 0)))
                        line_unit_price = Decimal(str(line_data.get('unit_price', 0)))
                        line_discount = Decimal(str(line_data.get('discount_percent', 0)))
                        line_tax = Decimal(str(line_data.get('tax_rate', 20.0)))
                        
                        if line_quantity > 0 and line_unit_price > 0:
                            add_line_cmd = AddOrderLineCommand(
                                order_id=order_id,
                                product_id=int(product_id),
                                quantity=line_quantity,
                                unit_price=line_unit_price,
                                discount_percent=line_discount,
                                tax_rate=line_tax
                            )
                            mediator.dispatch(add_line_cmd)
            elif command.quote_id:
                # Fallback: if no lines in form but quote exists, copy from quote
                # This should rarely happen, but provides a safety net
                from app.services.pricing_service import PricingService
                from app.domain.models.quote import Quote
                from app.infrastructure.db import get_session
                with get_session() as session:
                    quote = session.get(Quote, command.quote_id)
                    if quote:
                        pricing_service = PricingService(session)
                        for quote_line in quote.lines:
                            try:
                                price_result = pricing_service.get_price_for_customer(
                                    product_id=quote_line.product_id,
                                    customer_id=command.customer_id,
                                    quantity=quote_line.quantity
                                )
                                unit_price = price_result.final_price
                                # Only use discount if source is customer_discount
                                if price_result.source == 'customer_discount':
                                    discount_percent = price_result.applied_discount_percent
                                else:
                                    discount_percent = Decimal(0)  # No discount for price lists, etc.
                            except ValueError:
                                unit_price = quote_line.unit_price
                                discount_percent = quote_line.discount_percent if quote_line.discount_percent > 0 else Decimal(0)
                            
                            add_line_cmd = AddOrderLineCommand(
                                order_id=order_id,
                                product_id=quote_line.product_id,
                                quantity=quote_line.quantity,
                                unit_price=unit_price,
                                discount_percent=discount_percent,
                                tax_rate=quote_line.tax_rate
                            )
                            mediator.dispatch(add_line_cmd)
            
            flash(_('Order created successfully'), 'success')
            return redirect(url_for('sales.view_order', order_id=order_id))
            
    except ValueError as e:
        error_msg = str(e)
        if request.is_json or request.content_type == 'application/json':
            return jsonify({'status': 'error', 'message': error_msg}), 400
        else:
            flash(error_msg, 'error')
            if order_id:
                return redirect(url_for('sales.view_order', order_id=order_id))
            else:
                return redirect(url_for('sales.create_order'))
    except Exception as e:
        error_msg = str(e)
        if request.is_json or request.content_type == 'application/json':
            return jsonify({'status': 'error', 'message': error_msg}), 500
        else:
            flash(error_msg, 'error')
            if order_id:
                return redirect(url_for('sales.view_order', order_id=order_id))
            else:
                return redirect(url_for('sales.create_order'))


@sales_routes.route('/orders/<int:order_id>/confirm', methods=['POST'])
@require_roles_or_redirect('admin', 'commercial', 'direction')
def confirm_order_action(order_id: int):
    """Confirm an order."""
    try:
        current_user = get_current_user()
        if not current_user:
            flash(_('Authentication required'), 'error')
            return redirect(url_for('sales.view_order', order_id=order_id))
        
        # Check if order exists and is in draft status
        from app.application.sales.orders.queries.queries import GetOrderByIdQuery
        try:
            order = mediator.dispatch(GetOrderByIdQuery(order_id=order_id, include_lines=True))
            if order.status != 'draft':
                flash(_('Only draft orders can be confirmed. Current status: %(status)s', status=order.status), 'error')
                return redirect(url_for('sales.view_order', order_id=order_id))
            
            if not order.lines or len(order.lines) == 0:
                flash(_('Cannot confirm order without lines. Please add at least one line to the order.'), 'error')
                return redirect(url_for('sales.view_order', order_id=order_id))
        except ValueError:
            flash(_('Order not found'), 'error')
            return redirect(url_for('sales.orders_list'))
        
        # Dispatch confirmation command
        command = ConfirmOrderCommand(order_id=order_id, confirmed_by=current_user.id)
        mediator.dispatch(command)
        
        flash(_('Order confirmed successfully. Stock has been reserved.'), 'success')
        return redirect(url_for('sales.view_order', order_id=order_id))
    except ValueError as e:
        error_msg = str(e)
        flash(error_msg, 'error')
        return redirect(url_for('sales.view_order', order_id=order_id))
    except Exception as e:
        import traceback
        error_msg = str(e)
        # Log the full traceback for debugging
        print(f"Error confirming order {order_id}: {error_msg}")
        print(traceback.format_exc())
        flash(_('An error occurred while confirming the order: %(error)s', error=error_msg), 'error')
        return redirect(url_for('sales.view_order', order_id=order_id))


@sales_routes.route('/orders/<int:order_id>/cancel', methods=['POST'])
@require_roles_or_redirect('admin', 'commercial', 'direction')
def cancel_order_action(order_id: int):
    """Cancel an order."""
    try:
        command = CancelOrderCommand(order_id=order_id)
        mediator.dispatch(command)
        
        flash(_('Order canceled successfully. Reserved stock has been released.'), 'success')
        return redirect(url_for('sales.view_order', order_id=order_id))
    except ValueError as e:
        error_msg = str(e)
        flash(error_msg, 'error')
        return redirect(url_for('sales.view_order', order_id=order_id))
    except Exception as e:
        flash(str(e), 'error')
        return redirect(url_for('sales.view_order', order_id=order_id))


@sales_routes.route('/orders/<int:order_id>/update-status', methods=['POST'])
@require_roles_or_redirect('admin', 'commercial', 'logistics')
def update_order_status_action(order_id: int):
    """Update order status."""
    try:
        data = request.form.to_dict()
        new_status = data.get('status')
        
        if not new_status:
            flash(_('Status is required'), 'error')
            return redirect(url_for('sales.view_order', order_id=order_id))
        
        current_user = get_current_user()
        
        command = UpdateOrderStatusCommand(
            order_id=order_id,
            new_status=new_status,
            updated_by=current_user.id if current_user else None
        )
        mediator.dispatch(command)
        
        flash(_('Order status updated successfully'), 'success')
        return redirect(url_for('sales.view_order', order_id=order_id))
    except ValueError as e:
        error_msg = str(e)
        flash(error_msg, 'error')
        return redirect(url_for('sales.view_order', order_id=order_id))
    except Exception as e:
        flash(str(e), 'error')
        return redirect(url_for('sales.view_order', order_id=order_id))

