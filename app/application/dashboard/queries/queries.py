"""Queries for dashboard KPIs and statistics."""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime, date
from decimal import Decimal

from app.application.common.cqrs import Query


@dataclass
class GetKPIsQuery(Query):
    """Query to get all dashboard KPIs."""
    period: str = "month"  # 'day', 'week', 'month', 'year'
    start_date: Optional[date] = None
    end_date: Optional[date] = None


@dataclass
class GetRevenueQuery(Query):
    """Query to get revenue statistics."""
    period: str = "month"  # 'day', 'week', 'month', 'year'
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    group_by: str = "day"  # 'day', 'week', 'month'


@dataclass
class GetStockAlertsQuery(Query):
    """Query to get stock alerts count."""
    location_id: Optional[int] = None
    alert_type: Optional[str] = None  # 'low_stock', 'out_of_stock', 'overstock'


@dataclass
class GetActiveOrdersQuery(Query):
    """Query to get active orders count."""
    status: Optional[str] = None  # Filter by specific status
    customer_id: Optional[int] = None

