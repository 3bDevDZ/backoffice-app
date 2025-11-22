"""Report DTOs for API responses."""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from decimal import Decimal
from datetime import date


@dataclass
class ReportDataDTO:
    """DTO for report data."""
    title: str
    report_type: str
    period_start: str
    period_end: str
    data: List[Dict[str, Any]]
    summary: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ForecastDataPointDTO:
    """DTO for forecast data point."""
    date: str
    forecast_value: float
    lower_bound: float
    upper_bound: float
    confidence: float


@dataclass
class SalesForecastDTO:
    """DTO for sales forecast."""
    product_id: Optional[int]
    product_code: Optional[str]
    product_name: Optional[str]
    forecast_periods: List[ForecastDataPointDTO]
    historical_average: float
    trend: str  # 'increasing', 'decreasing', 'stable'
    confidence_score: float


@dataclass
class StockForecastDTO:
    """DTO for stock forecast."""
    product_id: int
    product_code: str
    product_name: str
    current_stock: float
    forecast_demand: float
    days_until_out_of_stock: Optional[int]
    recommended_reorder_quantity: float
    confidence_score: float

