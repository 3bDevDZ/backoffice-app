"""Frontend route handlers for stock management pages."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_babel import get_locale, gettext as _
from app.application.common.mediator import mediator
from app.application.stock.queries.queries import (
    GetStockLevelsQuery, GetStockAlertsQuery, GetStockMovementsQuery,
    GetLocationHierarchyQuery, GetStockItemByIdQuery, GlobalStockQuery
)
from app.application.stock.sites.queries import (
    ListSitesQuery, GetSiteByIdQuery, GetSiteStockQuery
)
from app.application.stock.sites.commands import (
    CreateSiteCommand, UpdateSiteCommand, DeactivateSiteCommand
)
from app.application.stock.transfers.queries import (
    ListStockTransfersQuery, GetStockTransferByIdQuery
)
from app.application.stock.transfers.commands import (
    CreateStockTransferCommand, ShipStockTransferCommand,
    ReceiveStockTransferCommand, CancelStockTransferCommand,
    StockTransferLineInput
)
from app.application.products.queries.queries import ListProductsQuery
from app.security.session_auth import require_roles_or_redirect, get_current_user
from app.infrastructure.db import get_session
from app.domain.models.user import User
from decimal import Decimal
from datetime import datetime
import re

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
    site_id = request.args.get('site_id', type=int)
    min_quantity = request.args.get('min_quantity', type=float)
    include_zero = request.args.get('include_zero', 'false').lower() == 'true'
    view_mode = request.args.get('view_mode', 'standard')  # 'standard' or 'global'
    
    # Fetch sites for filter
    sites = mediator.dispatch(ListSitesQuery(page=1, per_page=1000, status='active'))
    
    # Fetch locations for filter
    locations_query = GetLocationHierarchyQuery(include_inactive=False)
    locations = mediator.dispatch(locations_query)
    
    # Fetch alerts count
    alerts_query = GetStockAlertsQuery(page=1, per_page=10)
    alerts = mediator.dispatch(alerts_query)
    
    # Use GlobalStockQuery for consolidated view, GetStockLevelsQuery for standard view
    if view_mode == 'global':
        # Consolidated view across sites
        global_query = GlobalStockQuery(
            product_id=product_id,
            variant_id=None,
            site_id=site_id,
            page=page,
            per_page=per_page,
            search=search,
            include_zero=include_zero
        )
        stock_items = mediator.dispatch(global_query)
        is_global_view = True
    else:
        # Standard view (by location)
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
        is_global_view = False
    
    return render_template(
        'stock/index.html',
        stock_items=stock_items,
        locations=locations,
        sites=sites,
        alerts=alerts,
        page=page,
        per_page=per_page,
        search=search,
        product_id=product_id,
        location_id=location_id,
        site_id=site_id,
        min_quantity=min_quantity,
        include_zero=include_zero,
        view_mode=view_mode,
        is_global_view=is_global_view,
        locale=locale,
        direction=direction
    )


@stock_routes.route('/alerts')
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


@stock_routes.route('/movements')
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


@stock_routes.route('/locations')
@require_roles_or_redirect('admin', 'commercial', 'direction', 'warehouse')
def locations():
    """Render locations hierarchy page."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    # Get stock management mode
    from app.utils.settings_helper import get_stock_management_mode
    stock_mode = get_stock_management_mode()
    
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
    
    # Fetch sites only in advanced mode
    sites = []
    if stock_mode == 'advanced':
        sites = mediator.dispatch(ListSitesQuery(page=1, per_page=1000, status='active'))
    
    return render_template(
        'stock/locations.html',
        locations=locations_list,
        sites=sites,
        stock_mode=stock_mode,
        parent_id=parent_id,
        location_type=location_type,
        include_inactive=include_inactive,
        locale=locale,
        direction=direction
    )


@stock_routes.route('/locations', methods=['POST'])
@require_roles_or_redirect('admin', 'warehouse')
def create_location():
    """Create a new location."""
    try:
        from app.application.stock.commands.commands import CreateLocationCommand
        from app.utils.settings_helper import get_stock_management_mode
        from decimal import Decimal
        
        data = request.get_json() or request.form.to_dict()
        
        # In simple mode, site_id is not required (can be None)
        # In advanced mode, site_id can be provided but is optional
        site_id = None
        stock_mode = get_stock_management_mode()
        if stock_mode == 'advanced' and data.get('site_id'):
            site_id = int(data.get('site_id'))
        
        command = CreateLocationCommand(
            code=data.get('code'),
            name=data.get('name'),
            type=data.get('type'),
            parent_id=int(data.get('parent_id')) if data.get('parent_id') else None,
            site_id=site_id,
            capacity=Decimal(str(data.get('capacity'))) if data.get('capacity') else None,
            is_active=data.get('is_active', True) if isinstance(data.get('is_active'), bool) else data.get('is_active', 'true').lower() == 'true'
        )
        
        location = mediator.dispatch(command)
        
        # Query location again to get a fresh instance bound to a session
        # This avoids issues with detached objects
        from app.infrastructure.db import get_session
        from app.domain.models.stock import Location
        with get_session() as session:
            location = session.query(Location).filter(Location.code == command.code).first()
            if not location:
                raise ValueError("Location was created but could not be retrieved")
            location_id = location.id
            location_code = location.code
            location_name = location.name
        
        flash(_('Location created successfully'), 'success')
        return jsonify({
            'success': True,
            'status': 'success',
            'message': _('Location created successfully'),
            'data': {
                'id': location_id,
                'code': location_code,
                'name': location_name
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


@stock_routes.route('/locations/<int:location_id>', methods=['PUT'])
@require_roles_or_redirect('admin', 'warehouse')
def update_location(location_id: int):
    """Update a location."""
    try:
        from app.application.stock.commands.commands import UpdateLocationCommand
        from app.utils.settings_helper import get_stock_management_mode
        from decimal import Decimal
        
        data = request.get_json() or request.form.to_dict()
        
        # Build command with optional fields
        # For site_id, only include it if explicitly provided in the data
        from app.application.stock.commands.commands import _MISSING
        command_data = {
            'id': location_id,
            'code': data.get('code'),
            'name': data.get('name'),
            'type': data.get('type'),
            'parent_id': int(data.get('parent_id')) if data.get('parent_id') else None,
            'capacity': Decimal(str(data.get('capacity'))) if data.get('capacity') else None,
            'is_active': data.get('is_active') if isinstance(data.get('is_active'), bool) else (data.get('is_active', '').lower() == 'true' if data.get('is_active') else None)
        }
        
        # Handle site_id: only include if explicitly provided
        stock_mode = get_stock_management_mode()
        if stock_mode == 'advanced' and 'site_id' in data:
            # site_id was explicitly provided (can be None or an int)
            site_id_value = int(data.get('site_id')) if data.get('site_id') else None
            command_data['site_id'] = site_id_value
        else:
            # site_id not provided, use sentinel to indicate "not provided"
            command_data['site_id'] = _MISSING
        
        command = UpdateLocationCommand(**command_data)
        
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


@stock_routes.route('/locations/<int:location_id>/delete', methods=['POST'])
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
@stock_routes.route('/data/levels')
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


@stock_routes.route('/data/alerts')
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


@stock_routes.route('/data/locations', methods=['POST'])
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


# ============================================================================
# User Story 10: Site Management Routes
# ============================================================================

@stock_routes.route('/sites')
@require_roles_or_redirect('admin', 'warehouse', 'direction')
def list_sites():
    """Render sites list page."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    # Get query parameters
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 20)), 100)
    status = request.args.get('status')
    search = request.args.get('search')
    
    # Fetch sites
    query = ListSitesQuery(
        page=page,
        per_page=per_page,
        status=status,
        search=search
    )
    sites = mediator.dispatch(query)
    
    return render_template(
        'stock/sites/list.html',
        sites=sites,
        page=page,
        per_page=per_page,
        status=status,
        search=search,
        locale=locale,
        direction=direction
    )


@stock_routes.route('/sites/new')
@require_roles_or_redirect('admin', 'warehouse')
def new_site():
    """Render new site form page."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    # Fetch users for manager dropdown
    with get_session() as session:
        users_query = session.query(User).order_by(User.username).all()
        # Convert to list of dicts to avoid DetachedInstanceError
        users = [{'id': u.id, 'username': u.username} for u in users_query]
    
    return render_template(
        'stock/sites/form.html',
        site=None,
        users=users,
        locale=locale,
        direction=direction
    )


@stock_routes.route('/sites/<int:site_id>')
@require_roles_or_redirect('admin', 'warehouse', 'direction')
def view_site(site_id: int):
    """View a site (read-only)."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    # Fetch site
    site = mediator.dispatch(GetSiteByIdQuery(id=site_id))
    if not site:
        flash(_('Site not found'), 'error')
        return redirect(url_for('stock.list_sites'))
    
    # Fetch stock items for this site
    stock_query = GetSiteStockQuery(site_id=site_id, page=1, per_page=100)
    stock_items = mediator.dispatch(stock_query)
    
    return render_template(
        'stock/sites/view.html',
        site=site,
        stock_items=stock_items,
        locale=locale,
        direction=direction
    )


@stock_routes.route('/sites/<int:site_id>/edit')
@require_roles_or_redirect('admin', 'warehouse')
def edit_site(site_id: int):
    """Render edit site form page."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    # Fetch site
    site = mediator.dispatch(GetSiteByIdQuery(id=site_id))
    if not site:
        flash(_('Site not found'), 'error')
        return redirect(url_for('stock.list_sites'))
    
    # Fetch users for manager dropdown
    with get_session() as session:
        users_query = session.query(User).order_by(User.username).all()
        # Convert to list of dicts to avoid DetachedInstanceError
        users = [{'id': u.id, 'username': u.username} for u in users_query]
    
    return render_template(
        'stock/sites/form.html',
        site=site,
        users=users,
        locale=locale,
        direction=direction
    )


@stock_routes.route('/sites', methods=['POST'])
@require_roles_or_redirect('admin', 'warehouse')
def create_site():
    """Handle site creation form submission."""
    try:
        current_user = get_current_user()
        if not current_user:
            flash(_('Authentication required'), 'error')
            return redirect(url_for('stock.new_site'))
        
        manager_id = request.form.get('manager_id', type=int) or None
        status = request.form.get('status', 'active')
        
        command = CreateSiteCommand(
            code=request.form.get('code'),
            name=request.form.get('name'),
            address=request.form.get('address') or None,
            manager_id=manager_id,
            status=status
        )
        
        site = mediator.dispatch(command)
        
        flash(_('Site created successfully'), 'success')
        return redirect(url_for('stock.view_site', site_id=site.id))
    except ValueError as e:
        flash(_('Cannot create site: %(error)s', error=str(e)), 'error')
        return redirect(url_for('stock.new_site'))
    except Exception as e:
        flash(_('An error occurred: %(error)s', error=str(e)), 'error')
        return redirect(url_for('stock.new_site'))


@stock_routes.route('/sites/<int:site_id>', methods=['POST'])
@require_roles_or_redirect('admin', 'warehouse')
def update_site(site_id: int):
    """Handle site update form submission."""
    try:
        manager_id = request.form.get('manager_id', type=int) or None
        status = request.form.get('status', 'active')
        
        command = UpdateSiteCommand(
            id=site_id,
            code=request.form.get('code'),
            name=request.form.get('name'),
            address=request.form.get('address') or None,
            manager_id=manager_id,
            status=status
        )
        
        site = mediator.dispatch(command)
        
        flash(_('Site updated successfully'), 'success')
        return redirect(url_for('stock.view_site', site_id=site_id))
    except ValueError as e:
        flash(_('Cannot update site: %(error)s', error=str(e)), 'error')
        return redirect(url_for('stock.edit_site', site_id=site_id))
    except Exception as e:
        flash(_('An error occurred: %(error)s', error=str(e)), 'error')
        return redirect(url_for('stock.edit_site', site_id=site_id))


@stock_routes.route('/sites/<int:site_id>/deactivate', methods=['POST'])
@require_roles_or_redirect('admin', 'warehouse', 'direction')
def deactivate_site(site_id: int):
    """Deactivate a site."""
    try:
        command = DeactivateSiteCommand(id=site_id)
        mediator.dispatch(command)
        
        flash(_('Site deactivated successfully'), 'success')
        return redirect(url_for('stock.view_site', site_id=site_id))
    except ValueError as e:
        flash(_('Cannot deactivate site: %(error)s', error=str(e)), 'error')
        return redirect(url_for('stock.view_site', site_id=site_id))
    except Exception as e:
        flash(_('An error occurred: %(error)s', error=str(e)), 'error')
        return redirect(url_for('stock.view_site', site_id=site_id))


# ============================================================================
# User Story 10: Stock Transfer Routes
# ============================================================================

@stock_routes.route('/transfers')
@require_roles_or_redirect('admin', 'warehouse', 'direction')
def list_transfers():
    """Render stock transfers list page."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    # Get query parameters
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 20)), 100)
    status = request.args.get('status')
    source_site_id = request.args.get('source_site_id', type=int)
    destination_site_id = request.args.get('destination_site_id', type=int)
    
    # Fetch transfers
    query = ListStockTransfersQuery(
        page=page,
        per_page=per_page,
        status=status,
        source_site_id=source_site_id,
        destination_site_id=destination_site_id
    )
    transfers = mediator.dispatch(query)
    
    # Fetch sites for filters
    sites = mediator.dispatch(ListSitesQuery(page=1, per_page=1000, status='active'))
    
    return render_template(
        'stock/transfers/list.html',
        transfers=transfers,
        sites=sites,
        page=page,
        per_page=per_page,
        status=status,
        source_site_id=source_site_id,
        destination_site_id=destination_site_id,
        locale=locale,
        direction=direction
    )


@stock_routes.route('/transfers/new')
@require_roles_or_redirect('admin', 'warehouse')
def new_transfer():
    """Render new stock transfer form page."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    # Fetch sites for dropdowns
    sites = mediator.dispatch(ListSitesQuery(page=1, per_page=1000, status='active'))
    
    # Fetch products for line items
    products = mediator.dispatch(ListProductsQuery(page=1, per_page=1000, status='active'))
    
    return render_template(
        'stock/transfers/form.html',
        transfer=None,
        sites=sites,
        products=products,
        locale=locale,
        direction=direction
    )


@stock_routes.route('/transfers/<int:transfer_id>')
@require_roles_or_redirect('admin', 'warehouse', 'direction')
def view_transfer(transfer_id: int):
    """View a stock transfer (read-only)."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    # Fetch transfer
    transfer = mediator.dispatch(GetStockTransferByIdQuery(id=transfer_id))
    if not transfer:
        flash(_('Stock transfer not found'), 'error')
        return redirect(url_for('stock.list_transfers'))
    
    return render_template(
        'stock/transfers/view.html',
        transfer=transfer,
        locale=locale,
        direction=direction
    )


@stock_routes.route('/transfers', methods=['POST'])
@require_roles_or_redirect('admin', 'warehouse')
def create_transfer():
    """Handle stock transfer creation form submission."""
    try:
        current_user = get_current_user()
        if not current_user:
            flash(_('Authentication required'), 'error')
            return redirect(url_for('stock.new_transfer'))
        
        source_site_id = request.form.get('source_site_id', type=int)
        destination_site_id = request.form.get('destination_site_id', type=int)
        requested_date = request.form.get('requested_date')
        notes = request.form.get('notes') or None
        
        requested_date_parsed = None
        if requested_date:
            try:
                requested_date_parsed = datetime.strptime(requested_date, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        # Parse lines
        lines = []
        line_indices = []
        for key in request.form.keys():
            if key.startswith('lines[') and key.endswith('][product_id]'):
                match = re.match(r'lines\[(\d+)\]\[product_id\]', key)
                if match:
                    line_indices.append(int(match.group(1)))
        
        for idx in sorted(set(line_indices)):
            product_id = request.form.get(f'lines[{idx}][product_id]', type=int)
            variant_id = request.form.get(f'lines[{idx}][variant_id]', type=int) or None
            quantity = request.form.get(f'lines[{idx}][quantity]', type=float)
            line_notes = request.form.get(f'lines[{idx}][notes]') or None
            
            if product_id and quantity:
                lines.append(StockTransferLineInput(
                    product_id=product_id,
                    variant_id=variant_id,
                    quantity=Decimal(str(quantity)),
                    notes=line_notes
                ))
        
        if not lines:
            flash(_('At least one line is required'), 'error')
            return redirect(url_for('stock.new_transfer'))
        
        command = CreateStockTransferCommand(
            source_site_id=source_site_id,
            destination_site_id=destination_site_id,
            requested_date=requested_date_parsed,
            notes=notes,
            lines=lines,
            created_by=current_user.id
        )
        
        transfer = mediator.dispatch(command)
        
        flash(_('Stock transfer created successfully'), 'success')
        return redirect(url_for('stock.view_transfer', transfer_id=transfer.id))
    except ValueError as e:
        flash(_('Cannot create stock transfer: %(error)s', error=str(e)), 'error')
        return redirect(url_for('stock.new_transfer'))
    except Exception as e:
        flash(_('An error occurred: %(error)s', error=str(e)), 'error')
        return redirect(url_for('stock.new_transfer'))


@stock_routes.route('/transfers/<int:transfer_id>/ship', methods=['POST'])
@require_roles_or_redirect('admin', 'warehouse')
def ship_transfer(transfer_id: int):
    """Ship a stock transfer."""
    try:
        current_user = get_current_user()
        if not current_user:
            flash(_('Authentication required'), 'error')
            return redirect(url_for('stock.view_transfer', transfer_id=transfer_id))
        
        command = ShipStockTransferCommand(
            id=transfer_id,
            shipped_by=current_user.id
        )
        
        mediator.dispatch(command)
        
        flash(_('Stock transfer shipped successfully'), 'success')
        return redirect(url_for('stock.view_transfer', transfer_id=transfer_id))
    except ValueError as e:
        flash(_('Cannot ship stock transfer: %(error)s', error=str(e)), 'error')
        return redirect(url_for('stock.view_transfer', transfer_id=transfer_id))
    except Exception as e:
        flash(_('An error occurred: %(error)s', error=str(e)), 'error')
        return redirect(url_for('stock.view_transfer', transfer_id=transfer_id))


@stock_routes.route('/transfers/<int:transfer_id>/receive', methods=['POST'])
@require_roles_or_redirect('admin', 'warehouse')
def receive_transfer(transfer_id: int):
    """Receive a stock transfer."""
    try:
        current_user = get_current_user()
        if not current_user:
            flash(_('Authentication required'), 'error')
            return redirect(url_for('stock.view_transfer', transfer_id=transfer_id))
        
        # Parse received quantities from form
        received_quantities = {}
        for key in request.form.keys():
            if key.startswith('received_quantity[') and key.endswith(']'):
                match = re.match(r'received_quantity\[(\d+)\]', key)
                if match:
                    line_id = int(match.group(1))
                    quantity = request.form.get(key, type=float)
                    if quantity is not None:
                        received_quantities[line_id] = Decimal(str(quantity))
        
        command = ReceiveStockTransferCommand(
            id=transfer_id,
            received_by=current_user.id,
            received_quantities=received_quantities if received_quantities else None
        )
        
        mediator.dispatch(command)
        
        flash(_('Stock transfer received successfully'), 'success')
        return redirect(url_for('stock.view_transfer', transfer_id=transfer_id))
    except ValueError as e:
        flash(_('Cannot receive stock transfer: %(error)s', error=str(e)), 'error')
        return redirect(url_for('stock.view_transfer', transfer_id=transfer_id))
    except Exception as e:
        flash(_('An error occurred: %(error)s', error=str(e)), 'error')
        return redirect(url_for('stock.view_transfer', transfer_id=transfer_id))


@stock_routes.route('/transfers/<int:transfer_id>/cancel', methods=['POST'])
@require_roles_or_redirect('admin', 'warehouse', 'direction')
def cancel_transfer(transfer_id: int):
    """Cancel a stock transfer."""
    try:
        command = CancelStockTransferCommand(id=transfer_id)
        mediator.dispatch(command)
        
        flash(_('Stock transfer cancelled successfully'), 'success')
        return redirect(url_for('stock.view_transfer', transfer_id=transfer_id))
    except ValueError as e:
        flash(_('Cannot cancel stock transfer: %(error)s', error=str(e)), 'error')
        return redirect(url_for('stock.view_transfer', transfer_id=transfer_id))
    except Exception as e:
        flash(_('An error occurred: %(error)s', error=str(e)), 'error')
        return redirect(url_for('stock.view_transfer', transfer_id=transfer_id))

