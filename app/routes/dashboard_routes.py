"""Frontend route handlers for dashboard pages."""
from flask import Blueprint, render_template, request, jsonify
from flask_babel import get_locale, gettext as _
from app.security.session_auth import require_roles_or_redirect
from app.application.common.mediator import mediator
from app.application.dashboard.queries.queries import (
    GetKPIsQuery, GetRevenueQuery, GetStockAlertsQuery, GetActiveOrdersQuery
)
from datetime import datetime

dashboard_routes = Blueprint('dashboard', __name__)


@dashboard_routes.route('/')
@dashboard_routes.route('/dashboard')
@require_roles_or_redirect('admin', 'commercial', 'direction')
def index():
    """Render dashboard page."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    return render_template(
        'dashboard/index.html',
        locale=locale,
        direction=direction
    )


@dashboard_routes.route('/dashboard/data/kpi')
@require_roles_or_redirect('admin', 'commercial', 'direction')
def get_kpis_json():
    """Get dashboard KPIs as JSON for frontend AJAX requests (uses session auth)."""
    try:
        from app.application.dashboard.queries.dashboard_dto import KPIDTO
        
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
        data = {
            'total_revenue': float(kpi_dto.total_revenue),
            'total_revenue_period': kpi_dto.total_revenue_period,
            'revenue_change_percent': float(kpi_dto.revenue_change_percent) if kpi_dto.revenue_change_percent else None,
            'total_orders': kpi_dto.total_orders,
            'total_orders_period': kpi_dto.total_orders_period,
            'orders_change_percent': float(kpi_dto.orders_change_percent) if kpi_dto.orders_change_percent else None,
            'active_customers': kpi_dto.active_customers,
            'customers_change_percent': float(kpi_dto.customers_change_percent) if kpi_dto.customers_change_percent else None,
            'products_in_stock': kpi_dto.products_in_stock,
            'products_change_percent': float(kpi_dto.products_change_percent) if kpi_dto.products_change_percent else None,
            'stock_alerts_count': kpi_dto.stock_alerts_count,
            'active_orders_count': kpi_dto.active_orders_count,
            'revenue_trend': [
                {
                    'date': point.date.isoformat(),
                    'revenue': float(point.revenue),
                    'orders_count': point.orders_count
                }
                for point in (kpi_dto.revenue_trend or [])
            ],
            'orders_trend': kpi_dto.orders_trend or [],
            'top_products': kpi_dto.top_products or [],
            'recent_orders': kpi_dto.recent_orders or []
        }
        
        return jsonify({
            'success': True,
            'data': data,
            'message': _('Dashboard KPIs retrieved successfully')
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'message': _('Error retrieving dashboard KPIs: %(error)s', error=str(e))
        }), 500

