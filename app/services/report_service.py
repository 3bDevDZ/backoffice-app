"""Report service for generating standard and custom reports."""
from typing import List, Dict, Any, Optional
from decimal import Decimal
from datetime import date, datetime, timedelta
from dataclasses import dataclass

from app.services.analytics_service import AnalyticsService
from app.services.forecast_service import ForecastService
from app.domain.models.report import ReportTemplate
from app.infrastructure.db import get_session


@dataclass
class ReportData:
    """Generic report data structure."""
    title: str
    report_type: str
    period_start: date
    period_end: date
    data: List[Dict[str, Any]]
    summary: Dict[str, Any]
    metadata: Dict[str, Any]


class ReportService:
    """Service for generating standard and custom reports."""
    
    def __init__(self):
        self.analytics_service = AnalyticsService()
        self.forecast_service = ForecastService()
    
    def generate_sales_report(
        self,
        start_date: date,
        end_date: date,
        group_by: str = 'day',
        include_top_products: bool = True,
        include_top_customers: bool = True,
        limit: int = 10
    ) -> ReportData:
        """
        Generate standard sales report.
        
        Args:
            start_date: Start date for report
            end_date: End date for report
            group_by: Grouping period ('day', 'week', 'month', 'year')
            include_top_products: Whether to include top products
            include_top_customers: Whether to include top customers
            limit: Number of top items to include
            
        Returns:
            ReportData object
        """
        # Get sales by period
        sales_by_period = self.analytics_service.get_sales_by_period(
            start_date, end_date, group_by
        )
        
        # Convert to dict format
        period_data = [
            {
                'date': str(dp.date),
                'revenue': float(dp.revenue),
                'orders_count': dp.orders_count,
                'average_order_value': float(dp.average_order_value)
            }
            for dp in sales_by_period
        ]
        
        # Calculate summary
        total_revenue = sum(dp.revenue for dp in sales_by_period)
        total_orders = sum(dp.orders_count for dp in sales_by_period)
        avg_order_value = total_revenue / Decimal(total_orders) if total_orders > 0 else Decimal('0')
        
        summary = {
            'total_revenue': float(total_revenue),
            'total_orders': total_orders,
            'average_order_value': float(avg_order_value),
            'period_start': str(start_date),
            'period_end': str(end_date)
        }
        
        # Add top products if requested
        top_products_data = []
        if include_top_products:
            top_products = self.analytics_service.get_top_products(start_date, end_date, limit)
            top_products_data = [
                {
                    'product_id': p.product_id,
                    'product_code': p.product_code,
                    'product_name': p.product_name,
                    'quantity_sold': float(p.quantity_sold),
                    'revenue': float(p.revenue),
                    'average_price': float(p.average_price),
                    'orders_count': p.orders_count
                }
                for p in top_products
            ]
            summary['top_products'] = top_products_data
        
        # Add top customers if requested
        top_customers_data = []
        if include_top_customers:
            top_customers = self.analytics_service.get_top_customers(start_date, end_date, limit)
            top_customers_data = [
                {
                    'customer_id': c.customer_id,
                    'customer_name': c.customer_name,
                    'revenue': float(c.revenue),
                    'orders_count': c.orders_count,
                    'average_order_value': float(c.average_order_value),
                    'last_order_date': str(c.last_order_date) if c.last_order_date else None
                }
                for c in top_customers
            ]
            summary['top_customers'] = top_customers_data
        
        return ReportData(
            title='Sales Report',
            report_type='sales',
            period_start=start_date,
            period_end=end_date,
            data=period_data,
            summary=summary,
            metadata={
                'group_by': group_by,
                'include_top_products': include_top_products,
                'include_top_customers': include_top_customers
            }
        )
    
    def generate_margin_report(
        self,
        start_date: date,
        end_date: date,
        min_margin_percent: Optional[Decimal] = None
    ) -> ReportData:
        """
        Generate standard margin report.
        
        Args:
            start_date: Start date for report
            end_date: End date for report
            min_margin_percent: Optional minimum margin percent filter
            
        Returns:
            ReportData object
        """
        margins = self.analytics_service.calculate_margins(start_date, end_date)
        
        # Filter by minimum margin if specified
        if min_margin_percent is not None:
            margins = [m for m in margins if m.margin_percent >= min_margin_percent]
        
        # Convert to dict format
        margin_data = [
            {
                'product_id': m.product_id,
                'product_code': m.product_code,
                'product_name': m.product_name,
                'revenue': float(m.revenue),
                'cost': float(m.cost),
                'margin': float(m.margin),
                'margin_percent': float(m.margin_percent),
                'quantity_sold': float(m.quantity_sold)
            }
            for m in margins
        ]
        
        # Calculate summary
        total_revenue = sum(m.revenue for m in margins)
        total_cost = sum(m.cost for m in margins)
        total_margin = total_revenue - total_cost
        overall_margin_percent = (total_margin / total_revenue * Decimal(100)) if total_revenue > 0 else Decimal('0')
        
        summary = {
            'total_revenue': float(total_revenue),
            'total_cost': float(total_cost),
            'total_margin': float(total_margin),
            'overall_margin_percent': float(overall_margin_percent),
            'products_count': len(margins),
            'period_start': str(start_date),
            'period_end': str(end_date)
        }
        
        return ReportData(
            title='Margin Report',
            report_type='margins',
            period_start=start_date,
            period_end=end_date,
            data=margin_data,
            summary=summary,
            metadata={
                'min_margin_percent': float(min_margin_percent) if min_margin_percent else None
            }
        )
    
    def generate_stock_report(
        self,
        include_slow_moving: bool = True,
        include_fast_moving: bool = True,
        slow_moving_days: int = 90,
        fast_moving_threshold: Decimal = Decimal('100')
    ) -> ReportData:
        """
        Generate standard stock report.
        
        Args:
            include_slow_moving: Whether to include slow-moving products
            include_fast_moving: Whether to include fast-moving products
            slow_moving_days: Days threshold for slow-moving products
            fast_moving_threshold: Revenue threshold for fast-moving products
            
        Returns:
            ReportData object
        """
        from app.domain.models.stock import StockItem
        from app.domain.models.product import Product
        from sqlalchemy import func
        from datetime import timedelta
        
        with get_session() as session:
            # Get stock items with product info
            stock_query = session.query(
                StockItem,
                Product.code,
                Product.name,
                Product.cost
            ).join(
                Product, Product.id == StockItem.product_id
            ).filter(
                Product.status == 'active'
            ).all()
            
            stock_data = []
            total_stock_value = Decimal('0')
            
            for stock_item, product_code, product_name, product_cost in stock_query:
                stock_value = stock_item.physical_quantity * (product_cost or Decimal('0'))
                total_stock_value += stock_value
                
                stock_data.append({
                    'product_id': stock_item.product_id,
                    'product_code': product_code,
                    'product_name': product_name,
                    'location_id': stock_item.location_id,
                    'physical_quantity': float(stock_item.physical_quantity),
                    'reserved_quantity': float(stock_item.reserved_quantity),
                    'available_quantity': float(stock_item.physical_quantity - stock_item.reserved_quantity),
                    'unit_cost': float(product_cost or Decimal('0')),
                    'stock_value': float(stock_value),
                    'min_stock': float(stock_item.min_stock) if stock_item.min_stock else None,
                    'max_stock': float(stock_item.max_stock) if stock_item.max_stock else None
                })
            
            # Calculate turnover (simplified - would need sales history)
            # For now, we'll just include basic stock info
            
            summary = {
                'total_stock_value': float(total_stock_value),
                'products_count': len(stock_data),
                'report_date': str(date.today())
            }
            
            return ReportData(
                title='Stock Report',
                report_type='stock',
                period_start=date.today(),
                period_end=date.today(),
                data=stock_data,
                summary=summary,
                metadata={
                    'include_slow_moving': include_slow_moving,
                    'include_fast_moving': include_fast_moving
                }
            )
    
    def generate_customer_report(
        self,
        start_date: date,
        end_date: date,
        limit: int = 50
    ) -> ReportData:
        """
        Generate standard customer report.
        
        Args:
            start_date: Start date for report
            end_date: End date for report
            limit: Maximum number of customers to include
            
        Returns:
            ReportData object
        """
        top_customers = self.analytics_service.get_top_customers(start_date, end_date, limit)
        
        customer_data = [
            {
                'customer_id': c.customer_id,
                'customer_name': c.customer_name,
                'revenue': float(c.revenue),
                'orders_count': c.orders_count,
                'average_order_value': float(c.average_order_value),
                'last_order_date': str(c.last_order_date) if c.last_order_date else None
            }
            for c in top_customers
        ]
        
        total_revenue = sum(c.revenue for c in top_customers)
        total_orders = sum(c.orders_count for c in top_customers)
        avg_order_value = total_revenue / Decimal(total_orders) if total_orders > 0 else Decimal('0')
        
        summary = {
            'total_revenue': float(total_revenue),
            'total_orders': total_orders,
            'average_order_value': float(avg_order_value),
            'customers_count': len(customer_data),
            'period_start': str(start_date),
            'period_end': str(end_date)
        }
        
        return ReportData(
            title='Customer Report',
            report_type='customers',
            period_start=start_date,
            period_end=end_date,
            data=customer_data,
            summary=summary,
            metadata={}
        )
    
    def generate_purchase_report(
        self,
        start_date: date,
        end_date: date
    ) -> ReportData:
        """
        Generate standard purchase report.
        
        Args:
            start_date: Start date for report
            end_date: End date for report
            
        Returns:
            ReportData object
        """
        from app.domain.models.purchase import PurchaseOrder, PurchaseOrderLine
        from app.domain.models.supplier import Supplier
        from sqlalchemy import func
        
        with get_session() as session:
            # Get purchase orders with supplier info
            purchases = session.query(
                PurchaseOrder,
                Supplier.name.label('supplier_name')
            ).join(
                Supplier, Supplier.id == PurchaseOrder.supplier_id
            ).filter(
                PurchaseOrder.status.in_(['confirmed', 'partially_received', 'received']),
                func.date(PurchaseOrder.created_at) >= start_date,
                func.date(PurchaseOrder.created_at) <= end_date
            ).all()
            
            purchase_data = []
            supplier_totals = {}
            
            for purchase_order, supplier_name in purchases:
                purchase_data.append({
                    'purchase_order_id': purchase_order.id,
                    'purchase_order_number': purchase_order.number,
                    'supplier_id': purchase_order.supplier_id,
                    'supplier_name': supplier_name,
                    'order_date': str(purchase_order.order_date) if purchase_order.order_date else None,
                    'expected_delivery_date': str(purchase_order.expected_delivery_date) if purchase_order.expected_delivery_date else None,
                    'status': purchase_order.status.value if hasattr(purchase_order.status, 'value') else str(purchase_order.status),
                    'total_ht': float(purchase_order.total_ht),
                    'total_ttc': float(purchase_order.total_ttc)
                })
                
                # Aggregate by supplier
                if purchase_order.supplier_id not in supplier_totals:
                    supplier_totals[purchase_order.supplier_id] = {
                        'supplier_name': supplier_name,
                        'total_ht': Decimal('0'),
                        'orders_count': 0
                    }
                supplier_totals[purchase_order.supplier_id]['total_ht'] += purchase_order.total_ht
                supplier_totals[purchase_order.supplier_id]['orders_count'] += 1
            
            # Convert supplier totals
            supplier_summary = [
                {
                    'supplier_id': sid,
                    'supplier_name': data['supplier_name'],
                    'total_ht': float(data['total_ht']),
                    'orders_count': data['orders_count']
                }
                for sid, data in supplier_totals.items()
            ]
            
            total_purchases = sum(po.total_ht for po, _ in purchases)
            total_orders = len(purchases)
            
            summary = {
                'total_purchases': float(total_purchases),
                'total_orders': total_orders,
                'suppliers_count': len(supplier_summary),
                'suppliers_summary': supplier_summary,
                'period_start': str(start_date),
                'period_end': str(end_date)
            }
            
            return ReportData(
                title='Purchase Report',
                report_type='purchases',
                period_start=start_date,
                period_end=end_date,
                data=purchase_data,
                summary=summary,
                metadata={}
            )
    
    def generate_custom_report(
        self,
        template_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> ReportData:
        """
        Generate custom report from template.
        
        Args:
            template_id: ReportTemplate ID
            start_date: Optional start date override
            end_date: Optional end date override
            
        Returns:
            ReportData object
        """
        with get_session() as session:
            template = session.get(ReportTemplate, template_id)
            if not template:
                raise ValueError(f"ReportTemplate with ID {template_id} not found")
            
            # Use template dates if not provided
            if not start_date or not end_date:
                # Default to last 30 days
                end_date = end_date or date.today()
                start_date = start_date or (end_date - timedelta(days=30))
            
            # Generate base report based on type
            if template.report_type == 'sales':
                report = self.generate_sales_report(start_date, end_date)
            elif template.report_type == 'margins':
                report = self.generate_margin_report(start_date, end_date)
            elif template.report_type == 'stock':
                report = self.generate_stock_report()
            elif template.report_type == 'customers':
                report = self.generate_customer_report(start_date, end_date)
            elif template.report_type == 'purchases':
                report = self.generate_purchase_report(start_date, end_date)
            else:
                raise ValueError(f"Unsupported report type: {template.report_type}")
            
            # Apply template filters, sorting, grouping, etc.
            # This would be handled by ReportBuilderService
            # For now, return the base report
            
            return report

