"""Sales API endpoints for quotes."""
from flask import Blueprint, request
from flask_babel import get_locale, gettext as _
from datetime import date, datetime
from decimal import Decimal

from app.application.common.mediator import mediator
from app.application.sales.quotes.commands.commands import (
    CreateQuoteCommand, UpdateQuoteCommand, AddQuoteLineCommand,
    UpdateQuoteLineCommand, RemoveQuoteLineCommand,
    SendQuoteCommand, AcceptQuoteCommand, RejectQuoteCommand,
    CancelQuoteCommand, ConvertQuoteToOrderCommand,
    QuoteLineInput
)
from app.application.sales.quotes.queries.queries import (
    ListQuotesQuery, GetQuoteByIdQuery, GetQuoteHistoryQuery
)
from app.application.sales.orders.commands.commands import (
    CreateOrderCommand, UpdateOrderCommand, ConfirmOrderCommand,
    CancelOrderCommand, UpdateOrderStatusCommand,
    AddOrderLineCommand, UpdateOrderLineCommand, RemoveOrderLineCommand
)
from app.application.sales.orders.queries.queries import (
    ListOrdersQuery, GetOrderByIdQuery, GetOrderHistoryQuery
)
from app.security.rbac import require_roles
from app.utils.response import success_response, error_response, paginated_response
from flask_jwt_extended import get_jwt_identity
from app.utils.locale import get_user_locale

sales_bp = Blueprint("sales", __name__)


# Helper to convert DTOs to dict
def _quote_line_dto_to_dict(dto):
    """Convert QuoteLineDTO to dict."""
    return {
        'id': dto.id,
        'quote_id': dto.quote_id,
        'product_id': dto.product_id,
        'product_code': dto.product_code,
        'product_name': dto.product_name,
        'variant_id': dto.variant_id,
        'quantity': float(dto.quantity),
        'unit_price': float(dto.unit_price),
        'discount_percent': float(dto.discount_percent),
        'discount_amount': float(dto.discount_amount),
        'tax_rate': float(dto.tax_rate),
        'line_total_ht': float(dto.line_total_ht),
        'line_total_ttc': float(dto.line_total_ttc),
        'sequence': dto.sequence
    }


def _quote_dto_to_dict(dto):
    """Convert QuoteDTO to dict."""
    return {
        'id': dto.id,
        'number': dto.number,
        'version': dto.version,
        'customer_id': dto.customer_id,
        'customer_code': dto.customer_code,
        'customer_name': dto.customer_name,
        'status': dto.status,
        'valid_until': dto.valid_until.isoformat() if dto.valid_until else None,
        'subtotal': float(dto.subtotal),
        'tax_amount': float(dto.tax_amount),
        'total': float(dto.total),
        'discount_percent': float(dto.discount_percent),
        'discount_amount': float(dto.discount_amount),
        'notes': dto.notes,
        'internal_notes': dto.internal_notes,
        'sent_at': dto.sent_at.isoformat() if dto.sent_at else None,
        'sent_by': dto.sent_by,
        'sent_by_username': dto.sent_by_username,
        'accepted_at': dto.accepted_at.isoformat() if dto.accepted_at else None,
        'created_by': dto.created_by,
        'created_by_username': dto.created_by_username,
        'created_at': dto.created_at.isoformat() if dto.created_at else None,
        'updated_at': dto.updated_at.isoformat() if dto.updated_at else None,
        'lines': [_quote_line_dto_to_dict(line) for line in dto.lines] if dto.lines else None,
        'versions': [
            {
                'id': v.id,
                'quote_id': v.quote_id,
                'version_number': v.version_number,
                'created_by': v.created_by,
                'created_by_username': v.created_by_username,
                'created_at': v.created_at.isoformat() if v.created_at else None,
                'data': v.data
            }
            for v in dto.versions
        ] if dto.versions else None
    }


# Quote Endpoints
@sales_bp.get("/quotes")
@require_roles("admin", "commercial", "direction")
def list_quotes():
    """List quotes with pagination and filters. Supports locale parameter (?locale=fr|ar)."""
    try:
        locale = get_user_locale()
        
        page = int(request.args.get("page", 1))
        per_page = min(int(request.args.get("page_size", 20)), 100)
        status = request.args.get("status")
        customer_id = request.args.get("customer_id", type=int)
        search = request.args.get("search")
        
        query = ListQuotesQuery(
            page=page,
            per_page=per_page,
            status=status,
            customer_id=customer_id,
            search=search
        )
        result = mediator.dispatch(query)
        
        return paginated_response(
            items=[_quote_dto_to_dict(quote) for quote in result['items']],
            total=result['total'],
            page=result['page'],
            page_size=result['per_page']
        )
    except ValueError as e:
        error_msg = str(e).lower()
        if 'not found' in error_msg:
            return error_response(_('Quote not found'), status_code=404)
        return error_response(_('Invalid request parameters: %(error)s', error=str(e)), status_code=400)
    except Exception as e:
        return error_response(_('An error occurred: %(error)s', error=str(e)), status_code=500)


@sales_bp.get("/quotes/<int:quote_id>")
@require_roles("admin", "commercial", "direction")
def get_quote(quote_id: int):
    """Get quote by ID. Supports locale parameter (?locale=fr|ar)."""
    try:
        locale = get_user_locale()
        include_lines = request.args.get("include_lines", "true").lower() == "true"
        include_versions = request.args.get("include_versions", "false").lower() == "true"
        
        query = GetQuoteByIdQuery(
            id=quote_id,
            include_lines=include_lines,
            include_versions=include_versions
        )
        quote_dto = mediator.dispatch(query)
        
        return success_response(_quote_dto_to_dict(quote_dto))
    except ValueError as e:
        error_msg = str(e).lower()
        if 'not found' in error_msg:
            return error_response(_('Quote not found'), status_code=404)
        return error_response(_('Invalid request: %(error)s', error=str(e)), status_code=400)
    except Exception as e:
        return error_response(_('An error occurred: %(error)s', error=str(e)), status_code=500)


@sales_bp.post("/quotes")
@require_roles("admin", "commercial")
def create_quote():
    """Create a new quote. Supports locale parameter (?locale=fr|ar)."""
    try:
        locale = get_user_locale()
        data = request.get_json()
        
        if not data:
            return error_response(_('Request body is required'), status_code=400)
        
        customer_id = data.get('customer_id')
        if not customer_id:
            return error_response(_('Customer ID is required'), status_code=400)
        
        # Get current user ID from JWT
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return error_response(_('Authentication required'), status_code=401)
        
        # Parse lines
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
        
        # Parse valid_until
        valid_until = None
        if data.get('valid_until'):
            valid_until = datetime.fromisoformat(data['valid_until'].replace('Z', '+00:00')).date()
        
        command = CreateQuoteCommand(
            customer_id=customer_id,
            created_by=current_user_id,
            number=data.get('number'),
            valid_until=valid_until,
            discount_percent=Decimal(str(data.get('discount_percent', 0))),
            notes=data.get('notes'),
            internal_notes=data.get('internal_notes'),
            lines=lines
        )
        
        quote = mediator.dispatch(command)
        
        # Get full quote with lines
        quote_dto = mediator.dispatch(GetQuoteByIdQuery(id=quote.id, include_lines=True))
        
        return success_response(_quote_dto_to_dict(quote_dto), status_code=201)
    except ValueError as e:
        error_msg = str(e).lower()
        if 'not found' in error_msg:
            return error_response(_('Resource not found: %(error)s', error=str(e)), status_code=404)
        if 'invalid' in error_msg or 'must be' in error_msg:
            return error_response(_('Invalid request: %(error)s', error=str(e)), status_code=400)
        return error_response(_('Invalid request: %(error)s', error=str(e)), status_code=400)
    except Exception as e:
        return error_response(_('An error occurred: %(error)s', error=str(e)), status_code=500)


@sales_bp.put("/quotes/<int:quote_id>")
@require_roles("admin", "commercial")
def update_quote(quote_id: int):
    """Update a quote. Supports locale parameter (?locale=fr|ar)."""
    try:
        locale = get_user_locale()
        data = request.get_json()
        
        if not data:
            return error_response(_('Request body is required'), status_code=400)
        
        # Parse valid_until
        valid_until = None
        if data.get('valid_until'):
            valid_until = datetime.fromisoformat(data['valid_until'].replace('Z', '+00:00')).date()
        
        command = UpdateQuoteCommand(
            id=quote_id,
            valid_until=valid_until,
            discount_percent=Decimal(str(data['discount_percent'])) if data.get('discount_percent') is not None else None,
            notes=data.get('notes'),
            internal_notes=data.get('internal_notes')
        )
        
        quote = mediator.dispatch(command)
        
        # Get full quote with lines
        quote_dto = mediator.dispatch(GetQuoteByIdQuery(id=quote.id, include_lines=True))
        
        return success_response(_quote_dto_to_dict(quote_dto))
    except ValueError as e:
        error_msg = str(e).lower()
        if 'not found' in error_msg:
            return error_response(_('Quote not found'), status_code=404)
        if 'invalid' in error_msg or 'must be' in error_msg:
            return error_response(_('Invalid request: %(error)s', error=str(e)), status_code=400)
        return error_response(_('Invalid request: %(error)s', error=str(e)), status_code=400)
    except Exception as e:
        return error_response(_('An error occurred: %(error)s', error=str(e)), status_code=500)


@sales_bp.post("/quotes/<int:quote_id>/send")
@require_roles("admin", "commercial")
def send_quote(quote_id: int):
    """Send a quote to customer. Supports locale parameter (?locale=fr|ar)."""
    try:
        locale = get_user_locale()
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return error_response(_('Authentication required'), status_code=401)
        
        command = SendQuoteCommand(id=quote_id, sent_by=current_user_id)
        quote = mediator.dispatch(command)
        
        # Get full quote with lines
        quote_dto = mediator.dispatch(GetQuoteByIdQuery(id=quote.id, include_lines=True))
        
        return success_response(_quote_dto_to_dict(quote_dto))
    except ValueError as e:
        error_msg = str(e).lower()
        if 'not found' in error_msg:
            return error_response(_('Quote not found'), status_code=404)
        if 'cannot' in error_msg or 'must be' in error_msg:
            return error_response(_('Invalid operation: %(error)s', error=str(e)), status_code=400)
        return error_response(_('Invalid request: %(error)s', error=str(e)), status_code=400)
    except Exception as e:
        return error_response(_('An error occurred: %(error)s', error=str(e)), status_code=500)


@sales_bp.post("/quotes/<int:quote_id>/accept")
@require_roles("admin", "commercial", "direction")
def accept_quote(quote_id: int):
    """Accept a quote. Supports locale parameter (?locale=fr|ar)."""
    try:
        locale = get_user_locale()
        command = AcceptQuoteCommand(id=quote_id)
        quote = mediator.dispatch(command)
        
        # Get full quote with lines
        quote_dto = mediator.dispatch(GetQuoteByIdQuery(id=quote.id, include_lines=True))
        
        return success_response(_quote_dto_to_dict(quote_dto))
    except ValueError as e:
        error_msg = str(e).lower()
        if 'not found' in error_msg:
            return error_response(_('Quote not found'), status_code=404)
        if 'cannot' in error_msg or 'must be' in error_msg or 'expired' in error_msg:
            return error_response(_('Invalid operation: %(error)s', error=str(e)), status_code=400)
        return error_response(_('Invalid request: %(error)s', error=str(e)), status_code=400)
    except Exception as e:
        return error_response(_('An error occurred: %(error)s', error=str(e)), status_code=500)


@sales_bp.post("/quotes/<int:quote_id>/reject")
@require_roles("admin", "commercial", "direction")
def reject_quote(quote_id: int):
    """Reject a quote. Supports locale parameter (?locale=fr|ar)."""
    try:
        locale = get_user_locale()
        command = RejectQuoteCommand(id=quote_id)
        quote = mediator.dispatch(command)
        
        # Get full quote with lines
        quote_dto = mediator.dispatch(GetQuoteByIdQuery(id=quote.id, include_lines=True))
        
        return success_response(_quote_dto_to_dict(quote_dto))
    except ValueError as e:
        error_msg = str(e).lower()
        if 'not found' in error_msg:
            return error_response(_('Quote not found'), status_code=404)
        if 'cannot' in error_msg or 'must be' in error_msg:
            return error_response(_('Invalid operation: %(error)s', error=str(e)), status_code=400)
        return error_response(_('Invalid request: %(error)s', error=str(e)), status_code=400)
    except Exception as e:
        return error_response(_('An error occurred: %(error)s', error=str(e)), status_code=500)


@sales_bp.post("/quotes/<int:quote_id>/cancel")
@require_roles("admin", "commercial")
def cancel_quote(quote_id: int):
    """Cancel a quote. Supports locale parameter (?locale=fr|ar)."""
    try:
        locale = get_user_locale()
        command = CancelQuoteCommand(id=quote_id)
        quote = mediator.dispatch(command)
        
        # Get full quote with lines
        quote_dto = mediator.dispatch(GetQuoteByIdQuery(id=quote.id, include_lines=True))
        
        return success_response(_quote_dto_to_dict(quote_dto))
    except ValueError as e:
        error_msg = str(e).lower()
        if 'not found' in error_msg:
            return error_response(_('Quote not found'), status_code=404)
        if 'cannot' in error_msg:
            return error_response(_('Invalid operation: %(error)s', error=str(e)), status_code=400)
        return error_response(_('Invalid request: %(error)s', error=str(e)), status_code=400)
    except Exception as e:
        return error_response(_('An error occurred: %(error)s', error=str(e)), status_code=500)


@sales_bp.post("/quotes/<int:quote_id>/convert-to-order")
@require_roles("admin", "commercial")
def convert_quote_to_order(quote_id: int):
    """Convert an accepted quote to an order. Supports locale parameter (?locale=fr|ar)."""
    try:
        locale = get_user_locale()
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return error_response(_('Authentication required'), status_code=401)
        
        command = ConvertQuoteToOrderCommand(id=quote_id, created_by=current_user_id)
        result = mediator.dispatch(command)
        
        # TODO: Return order when Order model is created (User Story 5)
        return success_response({
            'quote': _quote_dto_to_dict(mediator.dispatch(GetQuoteByIdQuery(id=quote_id, include_lines=True))),
            'order': None  # Will be created in US5
        })
    except ValueError as e:
        error_msg = str(e).lower()
        if 'not found' in error_msg:
            return error_response(_('Quote not found'), status_code=404)
        if 'cannot' in error_msg or 'must be' in error_msg:
            return error_response(_('Invalid operation: %(error)s', error=str(e)), status_code=400)
        return error_response(_('Invalid request: %(error)s', error=str(e)), status_code=400)
    except Exception as e:
        return error_response(_('An error occurred: %(error)s', error=str(e)), status_code=500)


@sales_bp.get("/quotes/<int:quote_id>/history")
@require_roles("admin", "commercial", "direction")
def get_quote_history(quote_id: int):
    """Get quote version history. Supports locale parameter (?locale=fr|ar)."""
    try:
        locale = get_user_locale()
        page = int(request.args.get("page", 1))
        per_page = min(int(request.args.get("page_size", 20)), 100)
        
        query = GetQuoteHistoryQuery(quote_id=quote_id, page=page, per_page=per_page)
        result = mediator.dispatch(query)
        
        return paginated_response(
            items=[
                {
                    'id': v.id,
                    'quote_id': v.quote_id,
                    'version_number': v.version_number,
                    'created_by': v.created_by,
                    'created_by_username': v.created_by_username,
                    'created_at': v.created_at.isoformat() if v.created_at else None,
                    'data': v.data
                }
                for v in result['items']
            ],
            total=result['total'],
            page=result['page'],
            page_size=result['per_page']
        )
    except ValueError as e:
        error_msg = str(e).lower()
        if 'not found' in error_msg:
            return error_response(_('Quote not found'), status_code=404)
        return error_response(_('Invalid request: %(error)s', error=str(e)), status_code=400)
    except Exception as e:
        return error_response(_('An error occurred: %(error)s', error=str(e)), status_code=500)


@sales_bp.get("/quotes/<int:quote_id>/suggestions")
@require_roles("admin", "commercial")
def get_quote_suggestions(quote_id: int):
    """Get pricing suggestions for a quote (discounts, margins). Supports locale parameter (?locale=fr|ar)."""
    try:
        locale = get_user_locale()
        
        # Get quote
        quote_dto = mediator.dispatch(GetQuoteByIdQuery(id=quote_id, include_lines=True))
        
        # Use Pricing Service
        from app.infrastructure.db import get_session
        from app.services.pricing_service import PricingService
        
        with get_session() as session:
            # Get quote entity for service
            from app.domain.models.quote import Quote
            quote = session.get(Quote, quote_id)
            if not quote:
                return error_response(_('Quote not found'), status_code=404)
            
            pricing_service = PricingService(session)
            
            # Get discount suggestions
            discount_suggestions = pricing_service.suggest_discounts(quote)
            
            # Calculate margin
            margin = pricing_service.calculate_margin(quote)
            profitability = pricing_service.calculate_profitability(quote)
            
            # Get volume discount suggestions
            volume_discounts = pricing_service.apply_volume_discounts(quote.lines, quote.customer_id)
            
            return success_response({
                'discount_suggestions': [
                    {
                        'type': s.type,
                        'description': s.description,
                        'discount_percent': float(s.discount_percent),
                        'condition': s.condition,
                        'current_value': float(s.current_value),
                        'threshold_value': float(s.threshold_value)
                    }
                    for s in discount_suggestions
                ],
                'margin': {
                    'total_cost': float(margin.total_cost),
                    'total_revenue': float(margin.total_revenue),
                    'gross_margin': float(margin.gross_margin),
                    'gross_margin_percent': float(margin.gross_margin_percent),
                    'net_margin': float(margin.net_margin),
                    'net_margin_percent': float(margin.net_margin_percent)
                },
                'profitability': profitability,
                'volume_discounts': volume_discounts
            })
    except ValueError as e:
        error_msg = str(e).lower()
        if 'not found' in error_msg:
            return error_response(_('Quote not found'), status_code=404)
        return error_response(_('Invalid request: %(error)s', error=str(e)), status_code=400)
    except Exception as e:
        return error_response(_('An error occurred: %(error)s', error=str(e)), status_code=500)


@sales_bp.get("/pricing/price-for-customer")
@require_roles("admin", "commercial")
def get_price_for_customer():
    """Get price for a product considering customer's commercial conditions. Supports locale parameter (?locale=fr|ar)."""
    try:
        locale = get_user_locale()
        product_id = request.args.get("product_id", type=int)
        customer_id = request.args.get("customer_id", type=int)
        quantity = request.args.get("quantity", type=float, default=1.0)
        
        if not product_id or not customer_id:
            return error_response(_('product_id and customer_id are required'), status_code=400)
        
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
            
            return success_response({
                'base_price': float(price_result.base_price),
                'customer_price': float(price_result.customer_price),
                'applied_discount_percent': float(price_result.applied_discount_percent),
                'final_price': float(price_result.final_price),
                'discount_amount': float(price_result.discount_amount),
                'source': price_result.source
            })
    except ValueError as e:
        error_msg = str(e).lower()
        if 'not found' in error_msg:
            return error_response(_('Resource not found: %(error)s', error=str(e)), status_code=404)
        return error_response(_('Invalid request: %(error)s', error=str(e)), status_code=400)
    except Exception as e:
        return error_response(_('An error occurred: %(error)s', error=str(e)), status_code=500)


# Helper to convert Order DTOs to dict
def _order_line_dto_to_dict(dto):
    """Convert OrderLineDTO to dict."""
    return {
        'id': dto.id,
        'order_id': dto.order_id,
        'product_id': dto.product_id,
        'product_code': dto.product_code,
        'product_name': dto.product_name,
        'variant_id': dto.variant_id,
        'quantity': float(dto.quantity),
        'unit_price': float(dto.unit_price),
        'discount_percent': float(dto.discount_percent),
        'discount_amount': float(dto.discount_amount),
        'tax_rate': float(dto.tax_rate),
        'line_total_ht': float(dto.line_total_ht),
        'line_total_ttc': float(dto.line_total_ttc),
        'quantity_delivered': float(dto.quantity_delivered),
        'quantity_invoiced': float(dto.quantity_invoiced),
        'sequence': dto.sequence
    }


def _stock_reservation_dto_to_dict(dto):
    """Convert StockReservationDTO to dict."""
    return {
        'id': dto.id,
        'order_id': dto.order_id,
        'order_line_id': dto.order_line_id,
        'stock_item_id': dto.stock_item_id,
        'location_id': dto.location_id,
        'location_code': dto.location_code,
        'quantity': float(dto.quantity),
        'status': dto.status,
        'reserved_at': dto.reserved_at.isoformat() if dto.reserved_at else None,
        'released_at': dto.released_at.isoformat() if dto.released_at else None
    }


def _order_dto_to_dict(dto):
    """Convert OrderDTO to dict."""
    return {
        'id': dto.id,
        'number': dto.number,
        'customer_id': dto.customer_id,
        'customer_code': dto.customer_code,
        'customer_name': dto.customer_name,
        'quote_id': dto.quote_id,
        'quote_number': dto.quote_number,
        'status': dto.status,
        'delivery_address_id': dto.delivery_address_id,
        'delivery_date_requested': dto.delivery_date_requested.isoformat() if dto.delivery_date_requested else None,
        'delivery_date_promised': dto.delivery_date_promised.isoformat() if dto.delivery_date_promised else None,
        'delivery_date_actual': dto.delivery_date_actual.isoformat() if dto.delivery_date_actual else None,
        'delivery_instructions': dto.delivery_instructions,
        'subtotal': float(dto.subtotal),
        'tax_amount': float(dto.tax_amount),
        'total': float(dto.total),
        'discount_percent': float(dto.discount_percent),
        'discount_amount': float(dto.discount_amount),
        'notes': dto.notes,
        'confirmed_at': dto.confirmed_at.isoformat() if dto.confirmed_at else None,
        'confirmed_by': dto.confirmed_by,
        'confirmed_by_username': dto.confirmed_by_username,
        'created_by': dto.created_by,
        'created_by_username': dto.created_by_username,
        'created_at': dto.created_at.isoformat() if dto.created_at else None,
        'updated_at': dto.updated_at.isoformat() if dto.updated_at else None,
        'lines': [_order_line_dto_to_dict(line) for line in dto.lines] if dto.lines else None,
        'stock_reservations': [_stock_reservation_dto_to_dict(r) for r in dto.stock_reservations] if dto.stock_reservations else None
    }


# Order Endpoints
@sales_bp.get("/orders")
@require_roles("admin", "commercial", "direction", "logistics")
def list_orders():
    """List orders with pagination and filters. Supports locale parameter (?locale=fr|ar)."""
    try:
        locale = get_user_locale()
        
        page = int(request.args.get("page", 1))
        per_page = min(int(request.args.get("page_size", 20)), 100)
        status = request.args.get("status")
        customer_id = request.args.get("customer_id", type=int)
        search = request.args.get("search")
        date_from = request.args.get("date_from")
        date_to = request.args.get("date_to")
        
        # Parse dates
        parsed_date_from = None
        if date_from:
            parsed_date_from = datetime.fromisoformat(date_from.replace('Z', '+00:00')).date()
        
        parsed_date_to = None
        if date_to:
            parsed_date_to = datetime.fromisoformat(date_to.replace('Z', '+00:00')).date()
        
        query = ListOrdersQuery(
            status=status,
            customer_id=customer_id,
            page=page,
            per_page=per_page,
            search=search,
            date_from=parsed_date_from,
            date_to=parsed_date_to
        )
        
        result = mediator.dispatch(query)
        
        return paginated_response(
            items=[_order_dto_to_dict(dto) for dto in result['items']],
            total=result['total'],
            page=result['page'],
            per_page=result['per_page'],
            pages=result['pages']
        )
    except ValueError as e:
        return error_response(_('Invalid request: %(error)s', error=str(e)), status_code=400)
    except Exception as e:
        return error_response(_('An error occurred: %(error)s', error=str(e)), status_code=500)


@sales_bp.get("/orders/<int:order_id>")
@require_roles("admin", "commercial", "direction", "logistics")
def get_order(order_id: int):
    """Get an order by ID. Supports locale parameter (?locale=fr|ar)."""
    try:
        locale = get_user_locale()
        include_lines = request.args.get("include_lines", "true").lower() == "true"
        include_reservations = request.args.get("include_reservations", "false").lower() == "true"
        
        query = GetOrderByIdQuery(
            order_id=order_id,
            include_lines=include_lines,
            include_reservations=include_reservations
        )
        
        order_dto = mediator.dispatch(query)
        
        return success_response(_order_dto_to_dict(order_dto))
    except ValueError as e:
        error_msg = str(e).lower()
        if 'not found' in error_msg:
            return error_response(_('Order not found'), status_code=404)
        return error_response(_('Invalid request: %(error)s', error=str(e)), status_code=400)
    except Exception as e:
        return error_response(_('An error occurred: %(error)s', error=str(e)), status_code=500)


@sales_bp.post("/orders")
@require_roles("admin", "commercial")
def create_order():
    """Create a new order. Supports locale parameter (?locale=fr|ar)."""
    try:
        locale = get_user_locale()
        data = request.get_json()
        
        if not data:
            return error_response(_('Request body is required'), status_code=400)
        
        customer_id = data.get('customer_id')
        if not customer_id:
            return error_response(_('Customer ID is required'), status_code=400)
        
        # Get current user ID from JWT
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return error_response(_('Authentication required'), status_code=401)
        
        # Parse dates
        delivery_date_requested = None
        if data.get('delivery_date_requested'):
            delivery_date_requested = datetime.fromisoformat(data['delivery_date_requested'].replace('Z', '+00:00')).date()
        
        delivery_date_promised = None
        if data.get('delivery_date_promised'):
            delivery_date_promised = datetime.fromisoformat(data['delivery_date_promised'].replace('Z', '+00:00')).date()
        
        command = CreateOrderCommand(
            customer_id=customer_id,
            created_by=current_user_id,
            quote_id=data.get('quote_id'),
            delivery_address_id=data.get('delivery_address_id'),
            delivery_date_requested=delivery_date_requested,
            delivery_date_promised=delivery_date_promised,
            delivery_instructions=data.get('delivery_instructions'),
            notes=data.get('notes'),
            discount_percent=Decimal(str(data.get('discount_percent', 0)))
        )
        
        order_id = mediator.dispatch(command)
        
        # Get full order with lines
        order_dto = mediator.dispatch(GetOrderByIdQuery(order_id=order_id, include_lines=True))
        
        return success_response(_order_dto_to_dict(order_dto), status_code=201)
    except ValueError as e:
        error_msg = str(e).lower()
        if 'not found' in error_msg:
            return error_response(_('Resource not found: %(error)s', error=str(e)), status_code=404)
        if 'invalid' in error_msg or 'must be' in error_msg:
            return error_response(_('Invalid request: %(error)s', error=str(e)), status_code=400)
        return error_response(_('Invalid request: %(error)s', error=str(e)), status_code=400)
    except Exception as e:
        return error_response(_('An error occurred: %(error)s', error=str(e)), status_code=500)


@sales_bp.put("/orders/<int:order_id>")
@require_roles("admin", "commercial")
def update_order(order_id: int):
    """Update an order. Supports locale parameter (?locale=fr|ar)."""
    try:
        locale = get_user_locale()
        data = request.get_json()
        
        if not data:
            return error_response(_('Request body is required'), status_code=400)
        
        # Parse dates
        delivery_date_requested = None
        if data.get('delivery_date_requested'):
            delivery_date_requested = datetime.fromisoformat(data['delivery_date_requested'].replace('Z', '+00:00')).date()
        
        delivery_date_promised = None
        if data.get('delivery_date_promised'):
            delivery_date_promised = datetime.fromisoformat(data['delivery_date_promised'].replace('Z', '+00:00')).date()
        
        command = UpdateOrderCommand(
            order_id=order_id,
            delivery_address_id=data.get('delivery_address_id'),
            delivery_date_requested=delivery_date_requested,
            delivery_date_promised=delivery_date_promised,
            delivery_instructions=data.get('delivery_instructions'),
            notes=data.get('notes'),
            discount_percent=Decimal(str(data['discount_percent'])) if data.get('discount_percent') is not None else None
        )
        
        mediator.dispatch(command)
        
        # Get full order with lines
        order_dto = mediator.dispatch(GetOrderByIdQuery(order_id=order_id, include_lines=True))
        
        return success_response(_order_dto_to_dict(order_dto))
    except ValueError as e:
        error_msg = str(e).lower()
        if 'not found' in error_msg:
            return error_response(_('Order not found'), status_code=404)
        if 'invalid' in error_msg or 'must be' in error_msg or 'cannot' in error_msg:
            return error_response(_('Invalid request: %(error)s', error=str(e)), status_code=400)
        return error_response(_('Invalid request: %(error)s', error=str(e)), status_code=400)
    except Exception as e:
        return error_response(_('An error occurred: %(error)s', error=str(e)), status_code=500)


@sales_bp.post("/orders/<int:order_id>/confirm")
@require_roles("admin", "commercial", "direction")
def confirm_order(order_id: int):
    """Confirm an order. Supports locale parameter (?locale=fr|ar)."""
    try:
        locale = get_user_locale()
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return error_response(_('Authentication required'), status_code=401)
        
        command = ConfirmOrderCommand(order_id=order_id, confirmed_by=current_user_id)
        mediator.dispatch(command)
        
        # Get full order with lines
        order_dto = mediator.dispatch(GetOrderByIdQuery(order_id=order_id, include_lines=True))
        
        return success_response(_order_dto_to_dict(order_dto))
    except ValueError as e:
        error_msg = str(e).lower()
        if 'not found' in error_msg:
            return error_response(_('Order not found'), status_code=404)
        if 'cannot' in error_msg or 'must be' in error_msg or 'insufficient' in error_msg:
            return error_response(_('Invalid operation: %(error)s', error=str(e)), status_code=400)
        return error_response(_('Invalid request: %(error)s', error=str(e)), status_code=400)
    except Exception as e:
        return error_response(_('An error occurred: %(error)s', error=str(e)), status_code=500)


@sales_bp.post("/orders/<int:order_id>/cancel")
@require_roles("admin", "commercial", "direction")
def cancel_order(order_id: int):
    """Cancel an order. Supports locale parameter (?locale=fr|ar)."""
    try:
        locale = get_user_locale()
        command = CancelOrderCommand(order_id=order_id)
        mediator.dispatch(command)
        
        # Get full order with lines
        order_dto = mediator.dispatch(GetOrderByIdQuery(order_id=order_id, include_lines=True))
        
        return success_response(_order_dto_to_dict(order_dto))
    except ValueError as e:
        error_msg = str(e).lower()
        if 'not found' in error_msg:
            return error_response(_('Order not found'), status_code=404)
        if 'cannot' in error_msg or 'must be' in error_msg:
            return error_response(_('Invalid operation: %(error)s', error=str(e)), status_code=400)
        return error_response(_('Invalid request: %(error)s', error=str(e)), status_code=400)
    except Exception as e:
        return error_response(_('An error occurred: %(error)s', error=str(e)), status_code=500)


@sales_bp.put("/orders/<int:order_id>/status")
@require_roles("admin", "commercial", "logistics")
def update_order_status(order_id: int):
    """Update order status. Supports locale parameter (?locale=fr|ar)."""
    try:
        locale = get_user_locale()
        data = request.get_json()
        
        if not data:
            return error_response(_('Request body is required'), status_code=400)
        
        new_status = data.get('status')
        if not new_status:
            return error_response(_('Status is required'), status_code=400)
        
        current_user_id = get_jwt_identity()
        
        command = UpdateOrderStatusCommand(
            order_id=order_id,
            new_status=new_status,
            updated_by=current_user_id
        )
        
        mediator.dispatch(command)
        
        # Get full order with lines
        order_dto = mediator.dispatch(GetOrderByIdQuery(order_id=order_id, include_lines=True))
        
        return success_response(_order_dto_to_dict(order_dto))
    except ValueError as e:
        error_msg = str(e).lower()
        if 'not found' in error_msg:
            return error_response(_('Order not found'), status_code=404)
        if 'cannot' in error_msg or 'invalid' in error_msg or 'transition' in error_msg:
            return error_response(_('Invalid operation: %(error)s', error=str(e)), status_code=400)
        return error_response(_('Invalid request: %(error)s', error=str(e)), status_code=400)
    except Exception as e:
        return error_response(_('An error occurred: %(error)s', error=str(e)), status_code=500)


@sales_bp.post("/orders/<int:order_id>/lines")
@require_roles("admin", "commercial")
def add_order_line(order_id: int):
    """Add a line to an order. Supports locale parameter (?locale=fr|ar)."""
    try:
        locale = get_user_locale()
        data = request.get_json()
        
        if not data:
            return error_response(_('Request body is required'), status_code=400)
        
        command = AddOrderLineCommand(
            order_id=order_id,
            product_id=data['product_id'],
            quantity=Decimal(str(data['quantity'])),
            unit_price=Decimal(str(data.get('unit_price', 0))),
            variant_id=data.get('variant_id'),
            discount_percent=Decimal(str(data.get('discount_percent', 0))),
            tax_rate=Decimal(str(data.get('tax_rate', 20.0)))
        )
        
        mediator.dispatch(command)
        
        # Get full order with lines
        order_dto = mediator.dispatch(GetOrderByIdQuery(order_id=order_id, include_lines=True))
        
        return success_response(_order_dto_to_dict(order_dto), status_code=201)
    except ValueError as e:
        error_msg = str(e).lower()
        if 'not found' in error_msg:
            return error_response(_('Order not found'), status_code=404)
        if 'cannot' in error_msg or 'must be' in error_msg:
            return error_response(_('Invalid operation: %(error)s', error=str(e)), status_code=400)
        return error_response(_('Invalid request: %(error)s', error=str(e)), status_code=400)
    except Exception as e:
        return error_response(_('An error occurred: %(error)s', error=str(e)), status_code=500)


@sales_bp.put("/orders/<int:order_id>/lines/<int:line_id>")
@require_roles("admin", "commercial")
def update_order_line(order_id: int, line_id: int):
    """Update an order line. Supports locale parameter (?locale=fr|ar)."""
    try:
        locale = get_user_locale()
        data = request.get_json()
        
        if not data:
            return error_response(_('Request body is required'), status_code=400)
        
        command = UpdateOrderLineCommand(
            order_id=order_id,
            line_id=line_id,
            quantity=Decimal(str(data['quantity'])) if data.get('quantity') is not None else None,
            unit_price=Decimal(str(data['unit_price'])) if data.get('unit_price') is not None else None,
            discount_percent=Decimal(str(data['discount_percent'])) if data.get('discount_percent') is not None else None,
            tax_rate=Decimal(str(data['tax_rate'])) if data.get('tax_rate') is not None else None
        )
        
        mediator.dispatch(command)
        
        # Get full order with lines
        order_dto = mediator.dispatch(GetOrderByIdQuery(order_id=order_id, include_lines=True))
        
        return success_response(_order_dto_to_dict(order_dto))
    except ValueError as e:
        error_msg = str(e).lower()
        if 'not found' in error_msg:
            return error_response(_('Order or line not found'), status_code=404)
        if 'cannot' in error_msg or 'must be' in error_msg:
            return error_response(_('Invalid operation: %(error)s', error=str(e)), status_code=400)
        return error_response(_('Invalid request: %(error)s', error=str(e)), status_code=400)
    except Exception as e:
        return error_response(_('An error occurred: %(error)s', error=str(e)), status_code=500)


@sales_bp.delete("/orders/<int:order_id>/lines/<int:line_id>")
@require_roles("admin", "commercial")
def remove_order_line(order_id: int, line_id: int):
    """Remove a line from an order. Supports locale parameter (?locale=fr|ar)."""
    try:
        locale = get_user_locale()
        
        command = RemoveOrderLineCommand(order_id=order_id, line_id=line_id)
        mediator.dispatch(command)
        
        # Get full order with lines
        order_dto = mediator.dispatch(GetOrderByIdQuery(order_id=order_id, include_lines=True))
        
        return success_response(_order_dto_to_dict(order_dto))
    except ValueError as e:
        error_msg = str(e).lower()
        if 'not found' in error_msg:
            return error_response(_('Order or line not found'), status_code=404)
        if 'cannot' in error_msg or 'must be' in error_msg:
            return error_response(_('Invalid operation: %(error)s', error=str(e)), status_code=400)
        return error_response(_('Invalid request: %(error)s', error=str(e)), status_code=400)
    except Exception as e:
        return error_response(_('An error occurred: %(error)s', error=str(e)), status_code=500)


@sales_bp.get("/orders/<int:order_id>/history")
@require_roles("admin", "commercial", "direction", "logistics")
def get_order_history(order_id: int):
    """Get order history. Supports locale parameter (?locale=fr|ar)."""
    try:
        locale = get_user_locale()
        page = int(request.args.get("page", 1))
        per_page = min(int(request.args.get("page_size", 20)), 100)
        
        query = GetOrderHistoryQuery(order_id=order_id, page=page, per_page=per_page)
        result = mediator.dispatch(query)
        
        return paginated_response(
            items=result['items'],
            total=result['total'],
            page=result['page'],
            per_page=result['per_page'],
            pages=result['pages']
        )
    except ValueError as e:
        error_msg = str(e).lower()
        if 'not found' in error_msg:
            return error_response(_('Order not found'), status_code=404)
        return error_response(_('Invalid request: %(error)s', error=str(e)), status_code=400)
    except Exception as e:
        return error_response(_('An error occurred: %(error)s', error=str(e)), status_code=500)

