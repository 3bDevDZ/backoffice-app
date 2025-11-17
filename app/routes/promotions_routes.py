"""Frontend route handlers for promotional prices management."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_babel import get_locale, gettext as _
from decimal import Decimal
from datetime import datetime
from app.application.common.mediator import mediator
from app.application.products.pricing.queries.queries import (
    GetActivePromotionalPricesQuery, GetPromotionalPricesByProductQuery
)
from app.application.products.pricing.commands.commands import (
    CreatePromotionalPriceCommand, UpdatePromotionalPriceCommand, DeletePromotionalPriceCommand
)
from app.application.products.queries.queries import ListProductsQuery
from app.security.session_auth import require_roles_or_redirect, get_current_user

promotions_routes = Blueprint('promotions', __name__)


@promotions_routes.route('/promotions')
@require_roles_or_redirect('admin', 'commercial', 'direction')
def list():
    """List all promotional prices with filtering."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    # Get query parameters
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 20)), 100)
    status = request.args.get('status', 'all')  # 'active', 'expired', 'upcoming', 'all'
    search = request.args.get('search')
    product_id = request.args.get('product_id', type=int)
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    # Build query with filters
    query = GetActivePromotionalPricesQuery(
        product_id=product_id,
        search=search,
        status=status,
        date_from=date_from,
        date_to=date_to,
        page=page,
        per_page=per_page
    )
    
    result = mediator.dispatch(query)
    
    # Convert to dict format for template
    promotions_data = []
    for promo in result['items']:
        # Determine status
        now = datetime.now()
        promo_status = 'active'
        if promo.end_date < now:
            promo_status = 'expired'
        elif promo.start_date > now:
            promo_status = 'upcoming'
        
        promotions_data.append({
            'id': promo.id,
            'product_id': promo.product_id,
            'product_code': promo.product_code,
            'product_name': promo.product_name,
            'price': float(promo.price),
            'start_date': promo.start_date,
            'end_date': promo.end_date,
            'description': promo.description,
            'is_active': promo.is_active,
            'status': promo_status
        })
    
    return render_template('promotions/list.html', 
                         promotions=promotions_data,
                         pagination={
                             'page': result['page'],
                             'per_page': result['per_page'],
                             'total': result['total'],
                             'pages': result['pages']
                         },
                         direction=direction,
                         locale=locale,
                         status=status,
                         search=search,
                         product_id=product_id,
                         date_from=date_from,
                         date_to=date_to)


@promotions_routes.route('/promotions/new')
@require_roles_or_redirect('admin', 'commercial')
def new():
    """Show form to create a new promotional price."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    return render_template('promotions/form.html',
                         promotion=None,
                         direction=direction,
                         locale=locale)


@promotions_routes.route('/promotions/<int:promo_id>/edit')
@require_roles_or_redirect('admin', 'commercial')
def edit(promo_id: int):
    """Show form to edit a promotional price."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    # Get promotion by ID
    from app.infrastructure.db import get_session
    from app.domain.models.product import ProductPromotionalPrice
    
    with get_session() as session:
        promo = session.get(ProductPromotionalPrice, promo_id)
        if not promo:
            flash(_('Promotional price not found'), 'error')
            return redirect(url_for('promotions.list'))
        
        promotion = {
            'id': promo.id,
            'product_id': promo.product_id,
            'price': float(promo.price),
            'start_date': promo.start_date.isoformat() if promo.start_date else None,
            'end_date': promo.end_date.isoformat() if promo.end_date else None,
            'description': promo.description,
            'is_active': promo.is_active
        }
    
    return render_template('promotions/form.html',
                         promotion=promotion,
                         direction=direction,
                         locale=locale)


@promotions_routes.route('/promotions', methods=['POST'])
@require_roles_or_redirect('admin', 'commercial')
def create():
    """Create a new promotional price."""
    try:
        product_id = request.form.get('product_id', type=int)
        price = Decimal(str(request.form.get('price')))
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        description = request.form.get('description', '').strip()
        
        if not product_id:
            flash(_('Product is required'), 'error')
            return redirect(url_for('promotions.new'))
        
        from flask_login import current_user
        created_by = current_user.id if current_user and current_user.is_authenticated else None
        
        command = CreatePromotionalPriceCommand(
            product_id=product_id,
            price=price,
            start_date=start_date,
            end_date=end_date,
            description=description if description else None,
            created_by=created_by
        )
        mediator.dispatch(command)
        flash(_('Promotional price created successfully'), 'success')
        return redirect(url_for('promotions.list'))
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('promotions.new'))
    except Exception as e:
        flash(_('Failed to create promotional price: {}').format(str(e)), 'error')
        return redirect(url_for('promotions.new'))


@promotions_routes.route('/promotions/<int:promo_id>', methods=['POST'])
@require_roles_or_redirect('admin', 'commercial')
def update(promo_id: int):
    """Update a promotional price."""
    try:
        price = Decimal(str(request.form.get('price')))
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        description = request.form.get('description', '').strip()
        
        command = UpdatePromotionalPriceCommand(
            id=promo_id,
            price=price,
            start_date=start_date,
            end_date=end_date,
            description=description if description else None
        )
        mediator.dispatch(command)
        flash(_('Promotional price updated successfully'), 'success')
        return redirect(url_for('promotions.list'))
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('promotions.edit', promo_id=promo_id))
    except Exception as e:
        flash(_('Failed to update promotional price: {}').format(str(e)), 'error')
        return redirect(url_for('promotions.edit', promo_id=promo_id))


@promotions_routes.route('/promotions/<int:promo_id>/delete', methods=['POST'])
@require_roles_or_redirect('admin', 'commercial')
def delete(promo_id: int):
    """Delete a promotional price."""
    try:
        command = DeletePromotionalPriceCommand(id=promo_id)
        mediator.dispatch(command)
        flash(_('Promotional price deleted successfully'), 'success')
    except ValueError as e:
        flash(str(e), 'error')
    except Exception as e:
        flash(_('Failed to delete promotional price: {}').format(str(e)), 'error')
    
    return redirect(url_for('promotions.list'))


@promotions_routes.route('/promotions/data/products')
@require_roles_or_redirect('admin', 'commercial', 'direction')
def get_products_json():
    """Get products JSON for Select2 (session-based auth, not API)."""
    try:
        search = request.args.get('q', '').strip()
        page = int(request.args.get('page', 1))
        per_page = 20
        
        query = ListProductsQuery(
            page=page,
            per_page=per_page,
            search=search,
            status='active'
        )
        products = mediator.dispatch(query)
        
        # ListProductsHandler returns List[ProductDTO], not a dict
        # Convert to Select2 format
        items = []
        for product in products:
            items.append({
                'id': product.id,
                'text': f"{product.code} - {product.name}",
                'name': product.name,
                'code': product.code
            })
        
        # Check if there are more pages (if we got full page, there might be more)
        has_more = len(items) == per_page
        
        return jsonify({
            'results': items,
            'pagination': {
                'more': has_more
            }
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'results': [],
            'pagination': {'more': False},
            'error': str(e)
        }), 500

