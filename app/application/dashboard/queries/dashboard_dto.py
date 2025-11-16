"""DTOs for dashboard responses."""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from decimal import Decimal


@dataclass
class RevenueDataPoint:
    """Data point for revenue chart."""
    date: date
    revenue: Decimal
    orders_count: int


@dataclass
class KPIDTO:
    """DTO for dashboard KPIs."""
    total_revenue: Decimal
    total_revenue_period: str  # 'This month', 'This week', etc.
    total_orders: int
    total_orders_period: str
    active_customers: int
    products_in_stock: int
    revenue_change_percent: Optional[Decimal] = None
    orders_change_percent: Optional[Decimal] = None
    customers_change_percent: Optional[Decimal] = None
    products_change_percent: Optional[Decimal] = None
    stock_alerts_count: int = 0
    active_orders_count: int = 0
    revenue_trend: Optional[List[RevenueDataPoint]] = None
    orders_trend: Optional[List[Dict[str, Any]]] = None
    top_products: Optional[List[Dict[str, Any]]] = None
    recent_orders: Optional[List[Dict[str, Any]]] = None


@dataclass
class RevenueDTO:
    """DTO for revenue statistics."""
    total: Decimal
    period: str
    change_percent: Optional[Decimal] = None
    trend_data: Optional[List[RevenueDataPoint]] = None


@dataclass
class StockAlertsDTO:
    """DTO for stock alerts."""
    total_count: int
    low_stock_count: int
    out_of_stock_count: int
    overstock_count: int
    alerts: Optional[List[Dict[str, Any]]] = None


@dataclass
class ActiveOrdersDTO:
    """DTO for active orders."""
    total_count: int
    by_status: Optional[Dict[str, int]] = None
    orders: Optional[List[Dict[str, Any]]] = None

