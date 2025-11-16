"""Dashboard API endpoints."""
from flask import Blueprint, request
from flask_babel import get_locale, gettext as _
from datetime import datetime, date
from decimal import Decimal

from app.application.common.mediator import mediator
from app.application.dashboard.queries.queries import (
    GetKPIsQuery, GetRevenueQuery, GetStockAlertsQuery, GetActiveOrdersQuery
)
from app.security.rbac import require_roles
from app.utils.response import success_response, error_response
from app.utils.locale import get_user_locale

dashboard_bp = Blueprint("dashboard", __name__)


def _kpi_dto_to_dict(dto):
    """Convert KPIDTO to dict."""
    return {
        'total_revenue': float(dto.total_revenue),
        'total_revenue_period': dto.total_revenue_period,
        'revenue_change_percent': float(dto.revenue_change_percent) if dto.revenue_change_percent else None,
        'total_orders': dto.total_orders,
        'total_orders_period': dto.total_orders_period,
        'orders_change_percent': float(dto.orders_change_percent) if dto.orders_change_percent else None,
        'active_customers': dto.active_customers,
        'customers_change_percent': float(dto.customers_change_percent) if dto.customers_change_percent else None,
        'products_in_stock': dto.products_in_stock,
        'products_change_percent': float(dto.products_change_percent) if dto.products_change_percent else None,
        'stock_alerts_count': dto.stock_alerts_count,
        'active_orders_count': dto.active_orders_count,
        'revenue_trend': [
            {
                'date': point.date.isoformat(),
                'revenue': float(point.revenue),
                'orders_count': point.orders_count
            }
            for point in (dto.revenue_trend or [])
        ],
        'orders_trend': dto.orders_trend or [],
        'top_products': dto.top_products or [],
        'recent_orders': dto.recent_orders or []
    }


def _revenue_dto_to_dict(dto):
    """Convert RevenueDTO to dict."""
    return {
        'total': float(dto.total),
        'period': dto.period,
        'change_percent': float(dto.change_percent) if dto.change_percent else None,
        'trend_data': [
            {
                'date': point.date.isoformat(),
                'revenue': float(point.revenue),
                'orders_count': point.orders_count
            }
            for point in (dto.trend_data or [])
        ]
    }


def _stock_alerts_dto_to_dict(dto):
    """Convert StockAlertsDTO to dict."""
    return {
        'total_count': dto.total_count,
        'low_stock_count': dto.low_stock_count,
        'out_of_stock_count': dto.out_of_stock_count,
        'overstock_count': dto.overstock_count,
        'alerts': dto.alerts or []
    }


def _active_orders_dto_to_dict(dto):
    """Convert ActiveOrdersDTO to dict."""
    return {
        'total_count': dto.total_count,
        'by_status': dto.by_status or {},
        'orders': dto.orders or []
    }


@dashboard_bp.get("/kpi")
@require_roles("admin", "commercial", "direction")
def get_kpis():
    """
    Get all dashboard KPIs.
    
    Query parameters:
    - period: 'day', 'week', 'month', 'year' (default: 'month')
    - start_date: ISO date string (optional)
    - end_date: ISO date string (optional)
    - locale: 'fr' or 'ar' (optional)
    """
    try:
        locale = get_user_locale(request)
        direction = 'rtl' if locale == 'ar' else 'ltr'
        
        # Get query parameters
        period = request.args.get('period', 'month')
        start_date = None
        end_date = None
        
        if request.args.get('start_date'):
            start_date = datetime.fromisoformat(request.args.get('start_date')).date()
        if request.args.get('end_date'):
            end_date = datetime.fromisoformat(request.args.get('end_date')).date()
        
        # Dispatch query
        query = GetKPIsQuery(
            period=period,
            start_date=start_date,
            end_date=end_date
        )
        kpi_dto = mediator.dispatch(query)
        
        # Convert to dict
        data = _kpi_dto_to_dict(kpi_dto)
        
        return success_response(
            data=data,
            message=_('Dashboard KPIs retrieved successfully'),
            locale=locale,
            direction=direction
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return error_response(
            message=_('Error retrieving dashboard KPIs: %(error)s', error=str(e)),
            locale=get_user_locale(request),
            direction='rtl' if get_user_locale(request) == 'ar' else 'ltr'
        )


@dashboard_bp.get("/revenue")
@require_roles("admin", "commercial", "direction")
def get_revenue():
    """
    Get revenue statistics.
    
    Query parameters:
    - period: 'day', 'week', 'month', 'year' (default: 'month')
    - start_date: ISO date string (optional)
    - end_date: ISO date string (optional)
    - group_by: 'day', 'week', 'month' (default: 'day')
    - locale: 'fr' or 'ar' (optional)
    """
    try:
        locale = get_user_locale(request)
        direction = 'rtl' if locale == 'ar' else 'ltr'
        
        # Get query parameters
        period = request.args.get('period', 'month')
        group_by = request.args.get('group_by', 'day')
        start_date = None
        end_date = None
        
        if request.args.get('start_date'):
            start_date = datetime.fromisoformat(request.args.get('start_date')).date()
        if request.args.get('end_date'):
            end_date = datetime.fromisoformat(request.args.get('end_date')).date()
        
        # Dispatch query
        query = GetRevenueQuery(
            period=period,
            start_date=start_date,
            end_date=end_date,
            group_by=group_by
        )
        revenue_dto = mediator.dispatch(query)
        
        # Convert to dict
        data = _revenue_dto_to_dict(revenue_dto)
        
        return success_response(
            data=data,
            message=_('Revenue statistics retrieved successfully'),
            locale=locale,
            direction=direction
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return error_response(
            message=_('Error retrieving revenue statistics: %(error)s', error=str(e)),
            locale=get_user_locale(request),
            direction='rtl' if get_user_locale(request) == 'ar' else 'ltr'
        )


@dashboard_bp.get("/stock-alerts")
@require_roles("admin", "commercial", "direction", "warehouse")
def get_stock_alerts():
    """
    Get stock alerts count.
    
    Query parameters:
    - location_id: Filter by location (optional)
    - alert_type: 'low_stock', 'out_of_stock', 'overstock' (optional)
    - locale: 'fr' or 'ar' (optional)
    """
    try:
        locale = get_user_locale(request)
        direction = 'rtl' if locale == 'ar' else 'ltr'
        
        # Get query parameters
        location_id = request.args.get('location_id', type=int)
        alert_type = request.args.get('alert_type')
        
        # Dispatch query
        query = GetStockAlertsQuery(
            location_id=location_id,
            alert_type=alert_type
        )
        alerts_dto = mediator.dispatch(query)
        
        # Convert to dict
        data = _stock_alerts_dto_to_dict(alerts_dto)
        
        return success_response(
            data=data,
            message=_('Stock alerts retrieved successfully'),
            locale=locale,
            direction=direction
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return error_response(
            message=_('Error retrieving stock alerts: %(error)s', error=str(e)),
            locale=get_user_locale(request),
            direction='rtl' if get_user_locale(request) == 'ar' else 'ltr'
        )


@dashboard_bp.get("/active-orders")
@require_roles("admin", "commercial", "direction")
def get_active_orders():
    """
    Get active orders count.
    
    Query parameters:
    - status: Filter by status (optional)
    - customer_id: Filter by customer (optional)
    - locale: 'fr' or 'ar' (optional)
    """
    try:
        locale = get_user_locale(request)
        direction = 'rtl' if locale == 'ar' else 'ltr'
        
        # Get query parameters
        status = request.args.get('status')
        customer_id = request.args.get('customer_id', type=int)
        
        # Dispatch query
        query = GetActiveOrdersQuery(
            status=status,
            customer_id=customer_id
        )
        orders_dto = mediator.dispatch(query)
        
        # Convert to dict
        data = _active_orders_dto_to_dict(orders_dto)
        
        return success_response(
            data=data,
            message=_('Active orders retrieved successfully'),
            locale=locale,
            direction=direction
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return error_response(
            message=_('Error retrieving active orders: %(error)s', error=str(e)),
            locale=get_user_locale(request),
            direction='rtl' if get_user_locale(request) == 'ar' else 'ltr'
        )

