"""Frontend route handlers for stock management pages."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_babel import get_locale, gettext as _
from app.application.common.mediator import mediator
from app.application.stock.queries.queries import (
    GetStockLevelsQuery, GetStockAlertsQuery, GetStockMovementsQuery,
    GetLocationHierarchyQuery, GetStockItemByIdQuery
)
from app.security.session_auth import require_roles_or_redirect, get_current_user

stock_routes = Blueprint('stock', __name__)


@stock_routes.route('/stock')
@require_roles_or_redirect('admin', 'commercial', 'direction', 'warehouse')
def index():
    """Render stock levels page."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    # Get query parameters
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 50)), 100)
    search = request.args.get('search')
    product_id = request.args.get('product_id', type=int)
    location_id = request.args.get('location_id', type=int)
    min_quantity = request.args.get('min_quantity', type=float)
    include_zero = request.args.get('include_zero', 'false').lower() == 'true'
    
    # Fetch stock levels
    query = GetStockLevelsQuery(
        product_id=product_id,
        location_id=location_id,
        page=page,
        per_page=per_page,
        search=search,
        min_quantity=min_quantity,
        include_zero=include_zero
    )
    stock_items = mediator.dispatch(query)
    
    # Fetch locations for filter
    locations_query = GetLocationHierarchyQuery(include_inactive=False)
    locations = mediator.dispatch(locations_query)
    
    # Fetch alerts count
    alerts_query = GetStockAlertsQuery(page=1, per_page=10)
    alerts = mediator.dispatch(alerts_query)
    
    return render_template(
        'stock/index.html',
        stock_items=stock_items,
        locations=locations,
        alerts=alerts,
        page=page,
        per_page=per_page,
        search=search,
        product_id=product_id,
        location_id=location_id,
        min_quantity=min_quantity,
        include_zero=include_zero,
        locale=locale,
        direction=direction
    )


@stock_routes.route('/stock/alerts')
@require_roles_or_redirect('admin', 'commercial', 'direction', 'warehouse')
def alerts():
    """Render stock alerts page."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    # Get query parameters
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 50)), 100)
    location_id = request.args.get('location_id', type=int)
    alert_type = request.args.get('alert_type')
    
    # Fetch alerts
    query = GetStockAlertsQuery(
        location_id=location_id,
        alert_type=alert_type,
        page=page,
        per_page=per_page
    )
    alerts_list = mediator.dispatch(query)
    
    # Fetch locations for filter
    locations_query = GetLocationHierarchyQuery(include_inactive=False)
    locations = mediator.dispatch(locations_query)
    
    return render_template(
        'stock/alerts.html',
        alerts=alerts_list,
        locations=locations,
        page=page,
        per_page=per_page,
        location_id=location_id,
        alert_type=alert_type,
        locale=locale,
        direction=direction
    )


@stock_routes.route('/stock/movements')
@require_roles_or_redirect('admin', 'commercial', 'direction', 'warehouse')
def movements():
    """Render stock movements history page."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    # Get query parameters
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 50)), 100)
    product_id = request.args.get('product_id', type=int)
    location_id = request.args.get('location_id', type=int)
    movement_type = request.args.get('movement_type')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    # Fetch movements
    query = GetStockMovementsQuery(
        product_id=product_id,
        location_id=location_id,
        movement_type=movement_type,
        date_from=date_from,
        date_to=date_to,
        page=page,
        per_page=per_page
    )
    movements = mediator.dispatch(query)
    
    # Fetch locations for filter
    locations_query = GetLocationHierarchyQuery(include_inactive=False)
    locations = mediator.dispatch(locations_query)
    
    return render_template(
        'stock/movements.html',
        movements=movements,
        locations=locations,
        page=page,
        per_page=per_page,
        product_id=product_id,
        location_id=location_id,
        movement_type=movement_type,
        date_from=date_from,
        date_to=date_to,
        locale=locale,
        direction=direction
    )


@stock_routes.route('/stock/locations')
@require_roles_or_redirect('admin', 'commercial', 'direction', 'warehouse')
def locations():
    """Render locations hierarchy page."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    # Get query parameters
    parent_id = request.args.get('parent_id', type=int)
    location_type = request.args.get('type')
    include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
    
    # Fetch locations
    query = GetLocationHierarchyQuery(
        parent_id=parent_id,
        location_type=location_type,
        include_inactive=include_inactive
    )
    locations_list = mediator.dispatch(query)
    
    return render_template(
        'stock/locations.html',
        locations=locations_list,
        parent_id=parent_id,
        location_type=location_type,
        include_inactive=include_inactive,
        locale=locale,
        direction=direction
    )


@stock_routes.route('/stock/locations', methods=['POST'])
@require_roles_or_redirect('admin', 'warehouse')
def create_location():
    """Create a new location."""
    try:
        from app.application.stock.commands.commands import CreateLocationCommand
        from decimal import Decimal
        
        data = request.get_json() or request.form.to_dict()
        
        command = CreateLocationCommand(
            code=data.get('code'),
            name=data.get('name'),
            type=data.get('type'),
            parent_id=int(data.get('parent_id')) if data.get('parent_id') else None,
            capacity=Decimal(str(data.get('capacity'))) if data.get('capacity') else None,
            is_active=data.get('is_active', True) if isinstance(data.get('is_active'), bool) else data.get('is_active', 'true').lower() == 'true'
        )
        
        location = mediator.dispatch(command)
        
        flash(_('Location created successfully'), 'success')
        return jsonify({
            'success': True,
            'status': 'success',
            'message': _('Location created successfully'),
            'data': {
                'id': location.id,
                'code': location.code,
                'name': location.name
            }
        })
    except ValueError as e:
        error_msg = str(e)
        flash(error_msg, 'error')
        return jsonify({
            'success': False,
            'status': 'error',
            'message': _(error_msg)
        }), 400
    except Exception as e:
        flash(str(e), 'error')
        return jsonify({
            'success': False,
            'status': 'error',
            'message': _('An error occurred while creating location: %(error)s', error=str(e))
        }), 500


@stock_routes.route('/stock/locations/<int:location_id>', methods=['PUT'])
@require_roles_or_redirect('admin', 'warehouse')
def update_location(location_id: int):
    """Update a location."""
    try:
        from app.application.stock.commands.commands import UpdateLocationCommand
        from decimal import Decimal
        
        data = request.get_json() or request.form.to_dict()
        
        command = UpdateLocationCommand(
            id=location_id,
            code=data.get('code'),
            name=data.get('name'),
            type=data.get('type'),
            parent_id=int(data.get('parent_id')) if data.get('parent_id') else None,
            capacity=Decimal(str(data.get('capacity'))) if data.get('capacity') else None,
            is_active=data.get('is_active') if isinstance(data.get('is_active'), bool) else (data.get('is_active', '').lower() == 'true' if data.get('is_active') else None)
        )
        
        location = mediator.dispatch(command)
        
        flash(_('Location updated successfully'), 'success')
        return jsonify({
            'success': True,
            'status': 'success',
            'message': _('Location updated successfully'),
            'data': {
                'id': location.id,
                'code': location.code,
                'name': location.name
            }
        })
    except ValueError as e:
        error_msg = str(e)
        flash(error_msg, 'error')
        return jsonify({
            'success': False,
            'status': 'error',
            'message': _(error_msg)
        }), 400
    except Exception as e:
        flash(str(e), 'error')
        return jsonify({
            'success': False,
            'status': 'error',
            'message': _('An error occurred while updating location: %(error)s', error=str(e))
        }), 500


@stock_routes.route('/stock/locations/<int:location_id>/delete', methods=['POST'])
@require_roles_or_redirect('admin', 'warehouse')
def delete_location(location_id: int):
    """Delete a location."""
    try:
        from app.infrastructure.db import get_session
        from app.domain.models.stock import Location
        
        with get_session() as session:
            location = session.get(Location, location_id)
            if not location:
                flash(_('Location not found'), 'error')
                return redirect(url_for('stock.locations'))
            
            # Check if location has children
            children = session.query(Location).filter(Location.parent_id == location_id).count()
            if children > 0:
                flash(_('Cannot delete location with child locations'), 'error')
                return redirect(url_for('stock.locations'))
            
            # Check if location has stock items
            if location.stock_items:
                flash(_('Cannot delete location with stock items'), 'error')
                return redirect(url_for('stock.locations'))
            
            session.delete(location)
            session.commit()
        
        flash(_('Location deleted successfully'), 'success')
        return redirect(url_for('stock.locations'))
    except Exception as e:
        flash(str(e), 'error')
        return redirect(url_for('stock.locations'))


# JSON data endpoints for frontend AJAX calls
@stock_routes.route('/stock/data/levels')
@require_roles_or_redirect('admin', 'commercial', 'direction', 'warehouse')
def data_levels():
    """Return stock levels as JSON for AJAX requests."""
    try:
        # Get query parameters
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 50))
        search = request.args.get('search', '')
        location_id = request.args.get('location_id', type=int)
        min_quantity = request.args.get('min_quantity', type=float)
        include_zero = request.args.get('include_zero', 'false').lower() == 'true'
        
        # Fetch stock levels
        query = GetStockLevelsQuery(
            product_id=None,
            location_id=location_id,
            page=page,
            per_page=page_size,
            search=search,
            min_quantity=min_quantity,
            include_zero=include_zero
        )
        items_dto = mediator.dispatch(query)
        
        # Calculate total for pagination (we need to query again without pagination)
        # For now, we'll estimate based on the returned items
        # In a production app, you might want to cache the total or return it from the handler
        total = len(items_dto) if len(items_dto) < page_size else page_size * page
        
        # Convert to JSON-serializable format
        items = []
        for item in items_dto:
            items.append({
                'id': item.id,
                'product_id': item.product_id,
                'product_name': item.product_name,
                'product_code': item.product_code,
                'location_id': item.location_id,
                'location_name': item.location_name,
                'location_code': item.location_code,
                'physical_quantity': float(item.physical_quantity),
                'reserved_quantity': float(item.reserved_quantity),
                'available_quantity': float(item.available_quantity),
                'min_stock': float(item.min_stock) if item.min_stock else None,
                'is_out_of_stock': item.is_out_of_stock,
                'is_below_minimum': item.is_below_minimum,
                'is_overstock': item.is_overstock
            })
        
        return jsonify({
            'success': True,
            'data': {
                'items': items,
                'pagination': {
                    'page': page,
                    'per_page': page_size,
                    'total': total,
                    'pages': (total + page_size - 1) // page_size if page_size > 0 else 1
                }
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@stock_routes.route('/stock/data/alerts')
@require_roles_or_redirect('admin', 'commercial', 'direction', 'warehouse')
def data_alerts():
    """Return stock alerts as JSON for AJAX requests."""
    try:
        # Get query parameters
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))
        location_id = request.args.get('location_id', type=int)
        alert_type = request.args.get('alert_type')
        
        # Fetch alerts
        query = GetStockAlertsQuery(
            location_id=location_id,
            alert_type=alert_type,
            page=page,
            per_page=page_size
        )
        alerts_dto = mediator.dispatch(query)
        
        # Calculate total for pagination
        total = len(alerts_dto) if len(alerts_dto) < page_size else page_size * page
        
        # Convert to JSON-serializable format
        items = []
        for alert in alerts_dto:
            items.append({
                'id': alert.id,
                'product_id': alert.product_id,
                'product_name': alert.product_name,
                'product_code': alert.product_code,
                'location_id': alert.location_id,
                'location_name': alert.location_name,
                'location_code': alert.location_code,
                'alert_type': alert.alert_type,
                'current_quantity': float(alert.current_quantity),
                'min_stock': float(alert.min_stock) if alert.min_stock else None,
                'urgency': alert.urgency
            })
        
        return jsonify({
            'success': True,
            'data': {
                'items': items,
                'pagination': {
                    'page': page,
                    'per_page': page_size,
                    'total': total,
                    'pages': (total + page_size - 1) // page_size if page_size > 0 else 1
                }
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@stock_routes.route('/stock/data/locations', methods=['POST'])
@require_roles_or_redirect('admin', 'warehouse')
def create_location_quick():
    """Create a location quickly (for use in modals)."""
    try:
        from app.application.stock.commands.commands import CreateLocationCommand
        from decimal import Decimal
        
        data = request.get_json() or {}
        
        command = CreateLocationCommand(
            code=data.get('code'),
            name=data.get('name'),
            type=data.get('type', 'warehouse'),
            parent_id=data.get('parent_id'),
            capacity=Decimal(str(data.get('capacity'))) if data.get('capacity') else None,
            is_active=data.get('is_active', True)
        )
        
        location = mediator.dispatch(command)
        
        # Get values before session closes (location is detached after commit)
        location_id = location.id
        location_code = location.code
        location_name = location.name
        location_type = location.type
        
        return jsonify({
            'success': True,
            'status': 'success',
            'data': {
                'id': location_id,
                'code': location_code,
                'name': location_name,
                'type': location_type
            },
            'message': _('Location created successfully')
        })
    except ValueError as e:
        error_msg = str(e)
        if 'already exists' in error_msg.lower():
            return jsonify({
                'success': False,
                'status': 'error',
                'message': _('A location with this code already exists')
            }), 409
        elif 'not found' in error_msg.lower():
            return jsonify({
                'success': False,
                'status': 'error',
                'message': _('Parent location not found')
            }), 404
        return jsonify({
            'success': False,
            'status': 'error',
            'message': _(error_msg)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'error',
            'message': _('An error occurred while creating location: %(error)s', error=str(e))
        }), 500

