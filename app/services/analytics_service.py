"""Analytics service for calculating sales, margins, and trends."""
from typing import List, Dict, Any, Optional
from decimal import Decimal
from datetime import date, datetime, timedelta
from dataclasses import dataclass

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, case, desc
from sqlalchemy.orm import joinedload

from app.domain.models.order import Order, OrderLine
from app.domain.models.invoice import Invoice, InvoiceLine
from app.domain.models.product import Product
from app.domain.models.customer import Customer
from app.domain.models.purchase import PurchaseOrder, PurchaseOrderLine
from app.domain.models.stock import StockItem
from app.infrastructure.db import get_session


@dataclass
class SalesDataPoint:
    """Data point for sales analytics."""
    date: date
    revenue: Decimal
    orders_count: int
    average_order_value: Decimal


@dataclass
class ProductSalesSummary:
    """Summary of sales by product."""
    product_id: int
    product_code: str
    product_name: str
    quantity_sold: Decimal
    revenue: Decimal
    average_price: Decimal
    orders_count: int


@dataclass
class CustomerSalesSummary:
    """Summary of sales by customer."""
    customer_id: int
    customer_name: str
    revenue: Decimal
    orders_count: int
    average_order_value: Decimal
    last_order_date: Optional[date]


@dataclass
class MarginSummary:
    """Summary of margin calculations."""
    product_id: int
    product_code: str
    product_name: str
    revenue: Decimal
    cost: Decimal
    margin: Decimal
    margin_percent: Decimal
    quantity_sold: Decimal


@dataclass
class TrendAnalysis:
    """Trend analysis results."""
    current_period_value: Decimal
    previous_period_value: Decimal
    change_amount: Decimal
    change_percent: Decimal
    trend: str  # 'up', 'down', 'stable'


class AnalyticsService:
    """Service for calculating sales, margins, and trends."""
    
    def get_sales_by_period(
        self,
        start_date: date,
        end_date: date,
        group_by: str = 'day'  # 'day', 'week', 'month', 'year'
    ) -> List[SalesDataPoint]:
        """
        Get sales data grouped by time period.
        
        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            group_by: Grouping period ('day', 'week', 'month', 'year')
            
        Returns:
            List of SalesDataPoint objects
        """
        with get_session() as session:
            # Determine date grouping
            if group_by == 'day':
                date_expr = func.date(Order.created_at)
            elif group_by == 'week':
                date_expr = func.date(Order.created_at - func.cast(
                    func.extract('dow', Order.created_at), 
                    func.Integer
                ) * timedelta(days=1))
            elif group_by == 'month':
                date_expr = func.date_trunc('month', Order.created_at)
            elif group_by == 'year':
                date_expr = func.date_trunc('year', Order.created_at)
            else:
                date_expr = func.date(Order.created_at)
            
            # Query sales data
            results = session.query(
                date_expr.label('period_date'),
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
            ).all()
            
            data_points = []
            for row in results:
                period_date = row.period_date
                if isinstance(period_date, datetime):
                    period_date = period_date.date()
                elif not isinstance(period_date, date):
                    period_date = date.fromisoformat(str(period_date))
                
                revenue = row.revenue or Decimal('0')
                orders_count = row.orders_count or 0
                avg_order_value = revenue / Decimal(orders_count) if orders_count > 0 else Decimal('0')
                
                data_points.append(SalesDataPoint(
                    date=period_date,
                    revenue=revenue,
                    orders_count=orders_count,
                    average_order_value=avg_order_value
                ))
            
            return data_points
    
    def get_top_products(
        self,
        start_date: date,
        end_date: date,
        limit: int = 10
    ) -> List[ProductSalesSummary]:
        """
        Get top products by revenue.
        
        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            limit: Number of top products to return
            
        Returns:
            List of ProductSalesSummary objects
        """
        with get_session() as session:
            results = session.query(
                Product.id,
                Product.code,
                Product.name,
                func.sum(OrderLine.quantity).label('quantity_sold'),
                func.sum(OrderLine.line_total_ht).label('revenue'),
                func.avg(OrderLine.unit_price).label('average_price'),
                func.count(OrderLine.order_id.distinct()).label('orders_count')
            ).join(
                OrderLine, OrderLine.product_id == Product.id
            ).join(
                Order, Order.id == OrderLine.order_id
            ).filter(
                Order.status.in_(['confirmed', 'ready', 'shipped', 'delivered', 'invoiced']),
                func.date(Order.created_at) >= start_date,
                func.date(Order.created_at) <= end_date
            ).group_by(
                Product.id, Product.code, Product.name
            ).order_by(
                desc(func.sum(OrderLine.line_total_ht))
            ).limit(limit).all()
            
            summaries = []
            for row in results:
                summaries.append(ProductSalesSummary(
                    product_id=row.id,
                    product_code=row.code,
                    product_name=row.name,
                    quantity_sold=row.quantity_sold or Decimal('0'),
                    revenue=row.revenue or Decimal('0'),
                    average_price=row.average_price or Decimal('0'),
                    orders_count=row.orders_count or 0
                ))
            
            return summaries
    
    def get_top_customers(
        self,
        start_date: date,
        end_date: date,
        limit: int = 10
    ) -> List[CustomerSalesSummary]:
        """
        Get top customers by revenue.
        
        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            limit: Number of top customers to return
            
        Returns:
            List of CustomerSalesSummary objects
        """
        with get_session() as session:
            results = session.query(
                Customer.id,
                Customer.name,
                func.sum(Order.total).label('revenue'),
                func.count(Order.id).label('orders_count'),
                func.max(func.date(Order.created_at)).label('last_order_date')
            ).join(
                Order, Order.customer_id == Customer.id
            ).filter(
                Order.status.in_(['confirmed', 'ready', 'shipped', 'delivered', 'invoiced']),
                func.date(Order.created_at) >= start_date,
                func.date(Order.created_at) <= end_date
            ).group_by(
                Customer.id, Customer.name
            ).order_by(
                desc(func.sum(Order.total))
            ).limit(limit).all()
            
            summaries = []
            for row in results:
                revenue = row.revenue or Decimal('0')
                orders_count = row.orders_count or 0
                avg_order_value = revenue / Decimal(orders_count) if orders_count > 0 else Decimal('0')
                
                summaries.append(CustomerSalesSummary(
                    customer_id=row.id,
                    customer_name=row.name,
                    revenue=revenue,
                    orders_count=orders_count,
                    average_order_value=avg_order_value,
                    last_order_date=row.last_order_date
                ))
            
            return summaries
    
    def calculate_margins(
        self,
        start_date: date,
        end_date: date
    ) -> List[MarginSummary]:
        """
        Calculate margins by product.
        
        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            
        Returns:
            List of MarginSummary objects
        """
        with get_session() as session:
            # Get sales data with product costs
            results = session.query(
                Product.id,
                Product.code,
                Product.name,
                Product.cost,
                func.sum(OrderLine.quantity).label('quantity_sold'),
                func.sum(OrderLine.line_total_ht).label('revenue')
            ).join(
                OrderLine, OrderLine.product_id == Product.id
            ).join(
                Order, Order.id == OrderLine.order_id
            ).filter(
                Order.status.in_(['confirmed', 'ready', 'shipped', 'delivered', 'invoiced']),
                func.date(Order.created_at) >= start_date,
                func.date(Order.created_at) <= end_date
            ).group_by(
                Product.id, Product.code, Product.name, Product.cost
            ).all()
            
            summaries = []
            for row in results:
                revenue = row.revenue or Decimal('0')
                cost_per_unit = row.cost or Decimal('0')
                quantity_sold = row.quantity_sold or Decimal('0')
                total_cost = cost_per_unit * quantity_sold
                margin = revenue - total_cost
                margin_percent = (margin / revenue * Decimal(100)) if revenue > 0 else Decimal('0')
                
                summaries.append(MarginSummary(
                    product_id=row.id,
                    product_code=row.code,
                    product_name=row.name,
                    revenue=revenue,
                    cost=total_cost,
                    margin=margin,
                    margin_percent=margin_percent,
                    quantity_sold=quantity_sold
                ))
            
            return summaries
    
    def calculate_trend(
        self,
        current_value: Decimal,
        previous_value: Decimal
    ) -> TrendAnalysis:
        """
        Calculate trend between two periods.
        
        Args:
            current_value: Current period value
            previous_value: Previous period value
            
        Returns:
            TrendAnalysis object
        """
        change_amount = current_value - previous_value
        change_percent = (
            (change_amount / previous_value * Decimal(100))
            if previous_value > 0 else Decimal('0')
        )
        
        # Determine trend direction
        if abs(change_percent) < Decimal('1'):  # Less than 1% change
            trend = 'stable'
        elif change_percent > 0:
            trend = 'up'
        else:
            trend = 'down'
        
        return TrendAnalysis(
            current_period_value=current_value,
            previous_period_value=previous_value,
            change_amount=change_amount,
            change_percent=change_percent,
            trend=trend
        )

