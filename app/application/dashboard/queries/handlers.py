"""Query handlers for dashboard KPIs and statistics."""
from app.application.common.cqrs import QueryHandler
from app.domain.models.order import Order
from app.domain.models.customer import Customer
from app.domain.models.product import Product
from app.domain.models.stock import StockItem
from app.infrastructure.db import get_session
from .queries import (
    GetKPIsQuery,
    GetRevenueQuery,
    GetStockAlertsQuery,
    GetActiveOrdersQuery
)
from .dashboard_dto import (
    KPIDTO, RevenueDTO, RevenueDataPoint,
    StockAlertsDTO, ActiveOrdersDTO
)
from typing import List, Dict, Any
from sqlalchemy import func, and_, or_, case
from sqlalchemy.orm import joinedload
from datetime import datetime, date, timedelta
from decimal import Decimal


class GetKPIsHandler(QueryHandler):
    """Handler for getting all dashboard KPIs."""
    
    def handle(self, query: GetKPIsQuery) -> KPIDTO:
        """Get all dashboard KPIs."""
        with get_session() as session:
            # Calculate date range
            end_date = query.end_date or date.today()
            if query.start_date:
                start_date = query.start_date
            else:
                # Calculate start date based on period
                if query.period == "day":
                    start_date = end_date
                elif query.period == "week":
                    start_date = end_date - timedelta(days=7)
                elif query.period == "month":
                    start_date = end_date.replace(day=1)
                elif query.period == "year":
                    start_date = end_date.replace(month=1, day=1)
                else:
                    start_date = end_date.replace(day=1)
            
            # Previous period for comparison
            period_days = (end_date - start_date).days
            prev_start_date = start_date - timedelta(days=period_days + 1)
            prev_end_date = start_date - timedelta(days=1)
            
            # Total Revenue (from confirmed/delivered orders)
            revenue_query = session.query(
                func.sum(Order.total).label('total')
            ).filter(
                Order.status.in_(['confirmed', 'ready', 'shipped', 'delivered', 'invoiced']),
                func.date(Order.created_at) >= start_date,
                func.date(Order.created_at) <= end_date
            )
            total_revenue = revenue_query.scalar() or Decimal('0')
            
            # Previous period revenue
            prev_revenue_query = session.query(
                func.sum(Order.total).label('total')
            ).filter(
                Order.status.in_(['confirmed', 'ready', 'shipped', 'delivered', 'invoiced']),
                func.date(Order.created_at) >= prev_start_date,
                func.date(Order.created_at) <= prev_end_date
            )
            prev_revenue = prev_revenue_query.scalar() or Decimal('0')
            
            # Calculate revenue change percent
            revenue_change = None
            if prev_revenue > 0:
                revenue_change = ((total_revenue - prev_revenue) / prev_revenue) * 100
            
            # Total Orders
            orders_query = session.query(
                func.count(Order.id).label('count')
            ).filter(
                func.date(Order.created_at) >= start_date,
                func.date(Order.created_at) <= end_date
            )
            total_orders = orders_query.scalar() or 0
            
            # Previous period orders
            prev_orders_query = session.query(
                func.count(Order.id).label('count')
            ).filter(
                func.date(Order.created_at) >= prev_start_date,
                func.date(Order.created_at) <= prev_end_date
            )
            prev_orders = prev_orders_query.scalar() or 0
            
            # Calculate orders change percent
            orders_change = None
            if prev_orders > 0:
                orders_change = ((total_orders - prev_orders) / prev_orders) * 100
            
            # Active Customers
            active_customers_query = session.query(
                func.count(Customer.id).label('count')
            ).filter(
                Customer.status == 'active'
            )
            active_customers = active_customers_query.scalar() or 0
            
            # Products in Stock (active products)
            products_query = session.query(
                func.count(Product.id).label('count')
            ).filter(
                Product.status == 'active'
            )
            products_in_stock = products_query.scalar() or 0
            
            # Stock Alerts Count
            stock_alerts_query = session.query(
                func.count(StockItem.id).label('count')
            ).filter(
                StockItem.physical_quantity < StockItem.min_stock,
                StockItem.min_stock.isnot(None)
            )
            stock_alerts_count = stock_alerts_query.scalar() or 0
            
            # Active Orders Count
            active_orders_query = session.query(
                func.count(Order.id).label('count')
            ).filter(
                Order.status.in_(['confirmed', 'ready', 'shipped'])
            )
            active_orders_count = active_orders_query.scalar() or 0
            
            # Period label
            period_label = self._get_period_label(query.period, start_date, end_date)
            
            return KPIDTO(
                total_revenue=total_revenue,
                total_revenue_period=period_label,
                revenue_change_percent=revenue_change,
                total_orders=total_orders,
                total_orders_period=period_label,
                orders_change_percent=orders_change,
                active_customers=active_customers,
                products_in_stock=products_in_stock,
                stock_alerts_count=stock_alerts_count,
                active_orders_count=active_orders_count
            )
    
    def _get_period_label(self, period: str, start_date: date, end_date: date) -> str:
        """Get human-readable period label."""
        if period == "day":
            return "Today"
        elif period == "week":
            return "This week"
        elif period == "month":
            return "This month"
        elif period == "year":
            return "This year"
        else:
            return f"{start_date} to {end_date}"


class GetRevenueHandler(QueryHandler):
    """Handler for getting revenue statistics."""
    
    def handle(self, query: GetRevenueQuery) -> RevenueDTO:
        """Get revenue statistics."""
        with get_session() as session:
            # Calculate date range
            end_date = query.end_date or date.today()
            if query.start_date:
                start_date = query.start_date
            else:
                if query.period == "day":
                    start_date = end_date
                elif query.period == "week":
                    start_date = end_date - timedelta(days=7)
                elif query.period == "month":
                    start_date = end_date.replace(day=1)
                elif query.period == "year":
                    start_date = end_date.replace(month=1, day=1)
                else:
                    start_date = end_date.replace(day=1)
            
            # Total revenue
            revenue_query = session.query(
                func.sum(Order.total).label('total')
            ).filter(
                Order.status.in_(['confirmed', 'ready', 'shipped', 'delivered', 'invoiced']),
                func.date(Order.created_at) >= start_date,
                func.date(Order.created_at) <= end_date
            )
            total = revenue_query.scalar() or Decimal('0')
            
            # Previous period for comparison
            period_days = (end_date - start_date).days
            prev_start_date = start_date - timedelta(days=period_days + 1)
            prev_end_date = start_date - timedelta(days=1)
            
            prev_revenue_query = session.query(
                func.sum(Order.total).label('total')
            ).filter(
                Order.status.in_(['confirmed', 'ready', 'shipped', 'delivered', 'invoiced']),
                func.date(Order.created_at) >= prev_start_date,
                func.date(Order.created_at) <= prev_end_date
            )
            prev_revenue = prev_revenue_query.scalar() or Decimal('0')
            
            change_percent = None
            if prev_revenue > 0:
                change_percent = ((total - prev_revenue) / prev_revenue) * 100
            
            # Trend data
            trend_data = self._get_revenue_trend(session, start_date, end_date, query.group_by)
            
            period_label = self._get_period_label(query.period, start_date, end_date)
            
            return RevenueDTO(
                total=total,
                period=period_label,
                change_percent=change_percent,
                trend_data=trend_data
            )
    
    def _get_revenue_trend(self, session, start_date: date, end_date: date, group_by: str) -> List[RevenueDataPoint]:
        """Get revenue trend data points."""
        # Group by date - use func.date() for SQLite compatibility
        # For PostgreSQL, date_trunc would be better but we'll use date() for compatibility
        if group_by == "day":
            date_expr = func.date(Order.created_at)
        elif group_by == "week":
            # For week grouping, use date() and group by week number
            # This is a simplified approach that works with both SQLite and PostgreSQL
            date_expr = func.date(Order.created_at)
        elif group_by == "month":
            # For month grouping, extract year and month
            date_expr = func.date(Order.created_at)
        else:
            date_expr = func.date(Order.created_at)
        
        trend_query = session.query(
            date_expr.label('date'),
            func.sum(Order.total).label('revenue'),
            func.count(Order.id).label('orders_count')
        ).filter(
            Order.status.in_(['confirmed', 'ready', 'shipped', 'delivered', 'invoiced']),
            func.date(Order.created_at) >= start_date,
            func.date(Order.created_at) <= end_date
        ).group_by(
            date_expr
        ).order_by(
            date_expr
        )
        
        results = trend_query.all()
        trend_data = []
        for row in results:
            trend_data.append(RevenueDataPoint(
                date=row.date if isinstance(row.date, date) else row.date.date(),
                revenue=row.revenue or Decimal('0'),
                orders_count=row.orders_count or 0
            ))
        
        return trend_data
    
    def _get_period_label(self, period: str, start_date: date, end_date: date) -> str:
        """Get human-readable period label."""
        if period == "day":
            return "Today"
        elif period == "week":
            return "This week"
        elif period == "month":
            return "This month"
        elif period == "year":
            return "This year"
        else:
            return f"{start_date} to {end_date}"


class GetStockAlertsHandler(QueryHandler):
    """Handler for getting stock alerts."""
    
    def handle(self, query: GetStockAlertsQuery) -> StockAlertsDTO:
        """Get stock alerts count."""
        with get_session() as session:
            # Build filter conditions
            conditions = []
            if query.location_id:
                conditions.append(StockItem.location_id == query.location_id)
            
            # Low stock alerts
            low_stock_conditions = conditions + [
                StockItem.physical_quantity < StockItem.min_stock,
                StockItem.min_stock.isnot(None),
                StockItem.physical_quantity > 0
            ]
            
            # Out of stock alerts
            out_of_stock_conditions = conditions + [
                StockItem.physical_quantity <= 0
            ]
            
            # Overstock alerts
            overstock_conditions = conditions + [
                StockItem.physical_quantity > StockItem.max_stock,
                StockItem.max_stock.isnot(None)
            ]
            
            # Count alerts
            low_stock_count = session.query(func.count(StockItem.id)).filter(
                and_(*low_stock_conditions)
            ).scalar() or 0
            
            out_of_stock_count = session.query(func.count(StockItem.id)).filter(
                and_(*out_of_stock_conditions)
            ).scalar() or 0
            
            overstock_count = session.query(func.count(StockItem.id)).filter(
                and_(*overstock_conditions)
            ).scalar() or 0
            
            total_count = low_stock_count + out_of_stock_count + overstock_count
            
            return StockAlertsDTO(
                total_count=total_count,
                low_stock_count=low_stock_count,
                out_of_stock_count=out_of_stock_count,
                overstock_count=overstock_count
            )


class GetActiveOrdersHandler(QueryHandler):
    """Handler for getting active orders count."""
    
    def handle(self, query: GetActiveOrdersQuery) -> ActiveOrdersDTO:
        """Get active orders count."""
        with get_session() as session:
            # Build filter conditions
            conditions = [
                Order.status.in_(['confirmed', 'ready', 'shipped'])
            ]
            
            if query.status:
                conditions = [Order.status == query.status]
            
            if query.customer_id:
                conditions.append(Order.customer_id == query.customer_id)
            
            # Total count
            total_count = session.query(func.count(Order.id)).filter(
                and_(*conditions)
            ).scalar() or 0
            
            # Count by status
            status_counts = session.query(
                Order.status,
                func.count(Order.id).label('count')
            ).filter(
                and_(*conditions) if query.status else True
            ).group_by(
                Order.status
            ).all()
            
            by_status = {status: count for status, count in status_counts}
            
            return ActiveOrdersDTO(
                total_count=total_count,
                by_status=by_status
            )

