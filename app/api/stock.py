"""Stock API endpoints."""
from flask import Blueprint, request
from flask_babel import get_locale, gettext as _
from datetime import datetime
from decimal import Decimal

from app.application.common.mediator import mediator
from app.application.stock.queries.queries import (
    GetStockLevelsQuery, GetStockAlertsQuery, GetStockMovementsQuery,
    GetLocationHierarchyQuery, GetStockItemByIdQuery, GetLocationByIdQuery
)
from app.application.stock.commands.commands import (
    CreateLocationCommand, UpdateLocationCommand,
    CreateStockItemCommand, UpdateStockItemCommand,
    CreateStockMovementCommand,
    ReserveStockCommand, ReleaseStockCommand, AdjustStockCommand
)
from app.security.rbac import require_roles
from app.utils.response import success_response, error_response, paginated_response
from flask_jwt_extended import get_jwt_identity

stock_bp = Blueprint("stock", __name__)


# Helper to convert DTOs to dict
def _stock_item_dto_to_dict(dto):
    """Convert StockItemDTO to dict."""
    return {
        'id': dto.id,
        'product_id': dto.product_id,
        'location_id': dto.location_id,
        'physical_quantity': float(dto.physical_quantity),
        'reserved_quantity': float(dto.reserved_quantity),
        'available_quantity': float(dto.available_quantity),
        'product_code': dto.product_code,
        'product_name': dto.product_name,
        'variant_id': dto.variant_id,
        'location_code': dto.location_code,
        'location_name': dto.location_name,
        'min_stock': float(dto.min_stock) if dto.min_stock else None,
        'max_stock': float(dto.max_stock) if dto.max_stock else None,
        'reorder_point': float(dto.reorder_point) if dto.reorder_point else None,
        'reorder_quantity': float(dto.reorder_quantity) if dto.reorder_quantity else None,
        'valuation_method': dto.valuation_method,
        'last_movement_at': dto.last_movement_at.isoformat() if dto.last_movement_at else None,
        'created_at': dto.created_at.isoformat() if dto.created_at else None,
        'updated_at': dto.updated_at.isoformat() if dto.updated_at else None,
        'is_below_minimum': dto.is_below_minimum,
        'is_out_of_stock': dto.is_out_of_stock,
        'is_overstock': dto.is_overstock
    }


def _stock_movement_dto_to_dict(dto):
    """Convert StockMovementDTO to dict."""
    return {
        'id': dto.id,
        'stock_item_id': dto.stock_item_id,
        'product_id': dto.product_id,
        'quantity': float(dto.quantity),
        'type': dto.type,
        'user_id': dto.user_id,
        'created_at': dto.created_at.isoformat(),
        'product_code': dto.product_code,
        'product_name': dto.product_name,
        'variant_id': dto.variant_id,
        'location_from_id': dto.location_from_id,
        'location_from_code': dto.location_from_code,
        'location_from_name': dto.location_from_name,
        'location_to_id': dto.location_to_id,
        'location_to_code': dto.location_to_code,
        'location_to_name': dto.location_to_name,
        'reason': dto.reason,
        'user_name': dto.user_name,
        'related_document_type': dto.related_document_type,
        'related_document_id': dto.related_document_id
    }


def _stock_alert_dto_to_dict(dto):
    """Convert StockAlertDTO to dict."""
    return {
        'stock_item_id': dto.stock_item_id,
        'product_id': dto.product_id,
        'product_code': dto.product_code,
        'product_name': dto.product_name,
        'location_id': dto.location_id,
        'location_code': dto.location_code,
        'location_name': dto.location_name,
        'alert_type': dto.alert_type,
        'current_quantity': float(dto.current_quantity),
        'message': dto.message,
        'threshold': float(dto.threshold) if dto.threshold else None
    }


def _location_dto_to_dict(dto):
    """Convert LocationDTO to dict recursively."""
    return {
        'id': dto.id,
        'code': dto.code,
        'name': dto.name,
        'type': dto.type,
        'parent_id': dto.parent_id,
        'parent_name': dto.parent_name,
        'capacity': float(dto.capacity) if dto.capacity else None,
        'is_active': dto.is_active,
        'children': [_location_dto_to_dict(child) for child in dto.children] if dto.children else None,
        'created_at': dto.created_at.isoformat() if dto.created_at else None
    }


# Stock Levels Endpoints
@stock_bp.get("/levels")
@require_roles("admin", "commercial", "direction", "warehouse")
def get_stock_levels():
    """Get stock levels with pagination and filters. Supports locale parameter (?locale=fr|ar)."""
    try:
        page = int(request.args.get("page", 1))
        per_page = min(int(request.args.get("page_size", 50)), 100)
        product_id = request.args.get("product_id", type=int)
        location_id = request.args.get("location_id", type=int)
        variant_id = request.args.get("variant_id", type=int)
        search = request.args.get("search")
        min_quantity = request.args.get("min_quantity", type=float)
        include_zero = request.args.get("include_zero", "false").lower() == "true"
        
        query = GetStockLevelsQuery(
            product_id=product_id,
            location_id=location_id,
            variant_id=variant_id,
            page=page,
            per_page=per_page,
            search=search,
            min_quantity=Decimal(str(min_quantity)) if min_quantity is not None else None,
            include_zero=include_zero
        )
        stock_items = mediator.dispatch(query)
        
        # TODO: Get total count for pagination
        total = len(stock_items)  # Simplified - should query total count
        return paginated_response(
            items=[_stock_item_dto_to_dict(item) for item in stock_items],
            total=total,
            page=page,
            page_size=per_page
        )
    except ValueError as e:
        return error_response(_('Invalid request parameters: %(error)s', error=str(e)), status_code=400)
    except Exception as e:
        return error_response(_('An error occurred while retrieving stock levels: %(error)s', error=str(e)), status_code=500)


@stock_bp.get("/levels/<int:stock_item_id>")
@require_roles("admin", "commercial", "direction", "warehouse")
def get_stock_item(stock_item_id: int):
    """Get stock item by ID. Supports locale parameter (?locale=fr|ar)."""
    try:
        stock_item = mediator.dispatch(GetStockItemByIdQuery(id=stock_item_id))
        return success_response(_stock_item_dto_to_dict(stock_item))
    except ValueError as e:
        return error_response(_('Stock item not found'), status_code=404)
    except Exception as e:
        return error_response(_('An error occurred while retrieving stock item: %(error)s', error=str(e)), status_code=500)


# Stock Alerts Endpoints
@stock_bp.get("/alerts")
@require_roles("admin", "commercial", "direction", "warehouse")
def get_stock_alerts():
    """Get stock alerts (low stock, out of stock, overstock). Supports locale parameter (?locale=fr|ar)."""
    try:
        page = int(request.args.get("page", 1))
        per_page = min(int(request.args.get("page_size", 50)), 100)
        location_id = request.args.get("location_id", type=int)
        alert_type = request.args.get("alert_type")  # 'low_stock', 'out_of_stock', 'overstock'
        
        query = GetStockAlertsQuery(
            location_id=location_id,
            alert_type=alert_type,
            page=page,
            per_page=per_page
        )
        alerts = mediator.dispatch(query)
        
        # TODO: Get total count for pagination
        total = len(alerts)  # Simplified - should query total count
        return paginated_response(
            items=[_stock_alert_dto_to_dict(alert) for alert in alerts],
            total=total,
            page=page,
            page_size=per_page
        )
    except ValueError as e:
        return error_response(_('Invalid request parameters: %(error)s', error=str(e)), status_code=400)
    except Exception as e:
        return error_response(_('An error occurred while retrieving stock alerts: %(error)s', error=str(e)), status_code=500)


# Stock Movements Endpoints
@stock_bp.get("/movements")
@require_roles("admin", "commercial", "direction", "warehouse")
def get_stock_movements():
    """Get stock movements history. Supports locale parameter (?locale=fr|ar)."""
    try:
        page = int(request.args.get("page", 1))
        per_page = min(int(request.args.get("page_size", 50)), 100)
        stock_item_id = request.args.get("stock_item_id", type=int)
        product_id = request.args.get("product_id", type=int)
        location_id = request.args.get("location_id", type=int)
        movement_type = request.args.get("movement_type")  # 'entry', 'exit', 'transfer', 'adjustment'
        related_document_type = request.args.get("related_document_type")
        related_document_id = request.args.get("related_document_id", type=int)
        date_from = request.args.get("date_from")
        date_to = request.args.get("date_to")
        
        # Parse dates if provided
        parsed_date_from = None
        parsed_date_to = None
        if date_from:
            try:
                parsed_date_from = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
            except:
                parsed_date_from = datetime.strptime(date_from, '%Y-%m-%d')
        if date_to:
            try:
                parsed_date_to = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
            except:
                parsed_date_to = datetime.strptime(date_to, '%Y-%m-%d')
        
        query = GetStockMovementsQuery(
            stock_item_id=stock_item_id,
            product_id=product_id,
            location_id=location_id,
            movement_type=movement_type,
            related_document_type=related_document_type,
            related_document_id=related_document_id,
            date_from=parsed_date_from,
            date_to=parsed_date_to,
            page=page,
            per_page=per_page
        )
        movements = mediator.dispatch(query)
        
        # TODO: Get total count for pagination
        total = len(movements)  # Simplified - should query total count
        return paginated_response(
            items=[_stock_movement_dto_to_dict(movement) for movement in movements],
            total=total,
            page=page,
            page_size=per_page
        )
    except ValueError as e:
        return error_response(_('Invalid request parameters: %(error)s', error=str(e)), status_code=400)
    except Exception as e:
        return error_response(_('An error occurred while retrieving stock movements: %(error)s', error=str(e)), status_code=500)


@stock_bp.post("/movements")
@require_roles("admin", "warehouse")
def create_stock_movement():
    """Create a new stock movement. Supports locale parameter (?locale=fr|ar)."""
    try:
        data = request.get_json() or {}
        current_user_id = get_jwt_identity()
        
        if not current_user_id:
            return error_response(_('Authentication required. Please log in to perform this action.'), status_code=401)
        
        command = CreateStockMovementCommand(
            stock_item_id=data.get('stock_item_id'),
            product_id=data.get('product_id'),
            quantity=Decimal(str(data.get('quantity', 0))),
            movement_type=data.get('movement_type'),
            user_id=current_user_id,
            location_from_id=data.get('location_from_id'),
            location_to_id=data.get('location_to_id'),
            variant_id=data.get('variant_id'),
            reason=data.get('reason'),
            related_document_type=data.get('related_document_type'),
            related_document_id=data.get('related_document_id')
        )
        
        movement = mediator.dispatch(command)
        # Return movement details (would need to query it back or return from handler)
        return success_response(
            {'id': movement.id, 'message': _('Stock movement created successfully')},
            message=_('Stock movement created successfully'),
            status_code=201
        )
    except ValueError as e:
        error_msg = str(e)
        if 'not found' in error_msg.lower():
            return error_response(_('Resource not found: %(error)s', error=error_msg), status_code=404)
        elif 'insufficient' in error_msg.lower():
            return error_response(_('Insufficient stock: %(error)s', error=error_msg), status_code=400)
        return error_response(_(error_msg), status_code=400)
    except Exception as e:
        return error_response(_('An error occurred while creating stock movement: %(error)s', error=str(e)), status_code=500)


# Location Endpoints
@stock_bp.get("/locations")
@require_roles("admin", "commercial", "direction", "warehouse")
def get_locations():
    """Get location hierarchy. Supports locale parameter (?locale=fr|ar)."""
    try:
        parent_id = request.args.get("parent_id", type=int)
        location_type = request.args.get("type")
        include_inactive = request.args.get("include_inactive", "false").lower() == "true"
        
        query = GetLocationHierarchyQuery(
            parent_id=parent_id,
            location_type=location_type,
            include_inactive=include_inactive
        )
        locations = mediator.dispatch(query)
        
        return success_response(
            [_location_dto_to_dict(loc) for loc in locations]
        )
    except ValueError as e:
        return error_response(_('Invalid request parameters: %(error)s', error=str(e)), status_code=400)
    except Exception as e:
        return error_response(_('An error occurred while retrieving locations: %(error)s', error=str(e)), status_code=500)


@stock_bp.get("/locations/<int:location_id>")
@require_roles("admin", "commercial", "direction", "warehouse")
def get_location(location_id: int):
    """Get location by ID. Supports locale parameter (?locale=fr|ar)."""
    try:
        location = mediator.dispatch(GetLocationByIdQuery(id=location_id))
        return success_response(_location_dto_to_dict(location))
    except ValueError as e:
        error_msg = str(e)
        if 'not found' in error_msg.lower():
            return error_response(_('Location not found'), status_code=404)
        return error_response(_('Invalid request: %(error)s', error=error_msg), status_code=400)
    except Exception as e:
        return error_response(_('An error occurred while retrieving location: %(error)s', error=str(e)), status_code=500)


@stock_bp.post("/locations")
@require_roles("admin", "warehouse")
def create_location():
    """Create a new location. Supports locale parameter (?locale=fr|ar)."""
    try:
        data = request.get_json() or {}
        
        command = CreateLocationCommand(
            code=data.get('code'),
            name=data.get('name'),
            type=data.get('type'),
            parent_id=data.get('parent_id'),
            capacity=Decimal(str(data.get('capacity'))) if data.get('capacity') else None,
            is_active=data.get('is_active', True)
        )
        
        location = mediator.dispatch(command)
        return success_response(
            {'id': location.id, 'code': location.code, 'name': location.name},
            message=_('Location created successfully'),
            status_code=201
        )
    except ValueError as e:
        error_msg = str(e)
        if 'already exists' in error_msg.lower():
            return error_response(_('A location with this code already exists'), status_code=409)
        elif 'not found' in error_msg.lower():
            return error_response(_('Parent location not found'), status_code=404)
        return error_response(_(error_msg), status_code=400)
    except Exception as e:
        return error_response(_('An error occurred while creating location: %(error)s', error=str(e)), status_code=500)


@stock_bp.put("/locations/<int:location_id>")
@require_roles("admin", "warehouse")
def update_location(location_id: int):
    """Update a location. Supports locale parameter (?locale=fr|ar)."""
    try:
        data = request.get_json() or {}
        
        command = UpdateLocationCommand(
            id=location_id,
            code=data.get('code'),
            name=data.get('name'),
            type=data.get('type'),
            parent_id=data.get('parent_id'),
            capacity=Decimal(str(data.get('capacity'))) if data.get('capacity') else None,
            is_active=data.get('is_active')
        )
        
        location = mediator.dispatch(command)
        return success_response(
            {'id': location.id, 'code': location.code, 'name': location.name},
            message=_('Location updated successfully')
        )
    except ValueError as e:
        error_msg = str(e)
        if 'not found' in error_msg.lower():
            return error_response(_('Location not found'), status_code=404)
        return error_response(_(error_msg), status_code=400)
    except Exception as e:
        return error_response(_('An error occurred while updating location: %(error)s', error=str(e)), status_code=500)


# Stock Operations Endpoints
@stock_bp.post("/reserve")
@require_roles("admin", "commercial", "warehouse")
def reserve_stock():
    """Reserve stock for an order. Supports locale parameter (?locale=fr|ar)."""
    try:
        data = request.get_json() or {}
        
        command = ReserveStockCommand(
            stock_item_id=data.get('stock_item_id'),
            quantity=Decimal(str(data.get('quantity', 0))),
            order_id=data.get('order_id')
        )
        
        stock_item = mediator.dispatch(command)
        return success_response(
            {
                'id': stock_item.id,
                'physical_quantity': float(stock_item.physical_quantity),
                'reserved_quantity': float(stock_item.reserved_quantity),
                'available_quantity': float(stock_item.available_quantity)
            },
            message=_('Stock reserved successfully')
        )
    except ValueError as e:
        error_msg = str(e)
        if 'not found' in error_msg.lower():
            return error_response(_('Stock item not found'), status_code=404)
        elif 'insufficient' in error_msg.lower():
            return error_response(_('Insufficient available stock: %(error)s', error=error_msg), status_code=400)
        return error_response(_(error_msg), status_code=400)
    except Exception as e:
        return error_response(_('An error occurred while reserving stock: %(error)s', error=str(e)), status_code=500)


@stock_bp.post("/release")
@require_roles("admin", "commercial", "warehouse")
def release_stock():
    """Release reserved stock. Supports locale parameter (?locale=fr|ar)."""
    try:
        data = request.get_json() or {}
        
        command = ReleaseStockCommand(
            stock_item_id=data.get('stock_item_id'),
            quantity=Decimal(str(data.get('quantity', 0))),
            order_id=data.get('order_id')
        )
        
        stock_item = mediator.dispatch(command)
        return success_response(
            {
                'id': stock_item.id,
                'physical_quantity': float(stock_item.physical_quantity),
                'reserved_quantity': float(stock_item.reserved_quantity),
                'available_quantity': float(stock_item.available_quantity)
            },
            message=_('Stock released successfully')
        )
    except ValueError as e:
        error_msg = str(e)
        if 'not found' in error_msg.lower():
            return error_response(_('Stock item not found'), status_code=404)
        return error_response(_(error_msg), status_code=400)
    except Exception as e:
        return error_response(_('An error occurred while releasing stock: %(error)s', error=str(e)), status_code=500)


@stock_bp.post("/adjust")
@require_roles("admin", "warehouse")
def adjust_stock():
    """Adjust stock quantity (for inventory adjustments). Supports locale parameter (?locale=fr|ar)."""
    try:
        data = request.get_json() or {}
        current_user_id = get_jwt_identity()
        
        if not current_user_id:
            return error_response(_('Authentication required. Please log in to perform this action.'), status_code=401)
        
        command = AdjustStockCommand(
            stock_item_id=data.get('stock_item_id'),
            quantity=Decimal(str(data.get('quantity', 0))),
            reason=data.get('reason'),
            user_id=current_user_id
        )
        
        stock_item = mediator.dispatch(command)
        return success_response(
            {
                'id': stock_item.id,
                'physical_quantity': float(stock_item.physical_quantity),
                'reserved_quantity': float(stock_item.reserved_quantity),
                'available_quantity': float(stock_item.available_quantity)
            },
            message=_('Stock adjusted successfully')
        )
    except ValueError as e:
        error_msg = str(e)
        if 'not found' in error_msg.lower():
            return error_response(_('Stock item not found'), status_code=404)
        elif 'negative' in error_msg.lower() or 'invalid' in error_msg.lower():
            return error_response(_('Invalid adjustment: %(error)s', error=error_msg), status_code=400)
        return error_response(_(error_msg), status_code=400)
    except Exception as e:
        return error_response(_('An error occurred while adjusting stock: %(error)s', error=str(e)), status_code=500)

