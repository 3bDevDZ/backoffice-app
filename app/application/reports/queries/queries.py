"""Report queries for CQRS pattern."""
from dataclasses import dataclass
from datetime import date
from typing import Optional
from decimal import Decimal

from app.application.common.cqrs import Query


@dataclass
class GetSalesReportQuery(Query):
    """Query to get sales report."""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    group_by: str = 'day'  # 'day', 'week', 'month', 'year'
    include_top_products: bool = True
    include_top_customers: bool = True
    limit: int = 10


@dataclass
class GetMarginReportQuery(Query):
    """Query to get margin report."""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    min_margin_percent: Optional[Decimal] = None


@dataclass
class GetStockReportQuery(Query):
    """Query to get stock report."""
    include_slow_moving: bool = True
    include_fast_moving: bool = True
    slow_moving_days: int = 90
    fast_moving_threshold: Decimal = Decimal('100')


@dataclass
class GetCustomerReportQuery(Query):
    """Query to get customer report."""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    limit: int = 50


@dataclass
class GetPurchaseReportQuery(Query):
    """Query to get purchase report."""
    start_date: Optional[date] = None
    end_date: Optional[date] = None


@dataclass
class GetCustomReportQuery(Query):
    """Query to get custom report from template."""
    template_id: int
    start_date: Optional[date] = None
    end_date: Optional[date] = None


@dataclass
class GetSalesForecastQuery(Query):
    """Query to get sales forecast."""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    forecast_periods: int = 12
    product_id: Optional[int] = None
    method: str = 'moving_average'  # 'moving_average', 'exponential_smoothing', 'linear_regression'


@dataclass
class GetStockForecastQuery(Query):
    """Query to get stock forecast."""
    product_id: int
    forecast_days: int = 30

