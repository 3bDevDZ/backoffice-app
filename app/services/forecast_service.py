"""Forecast service for generating sales and stock forecasts."""
from typing import List, Dict, Any, Optional
from decimal import Decimal
from datetime import date, datetime, timedelta
from dataclasses import dataclass
import statistics

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.domain.models.order import Order, OrderLine
from app.domain.models.product import Product
from app.domain.models.stock import StockItem
from app.infrastructure.db import get_session


@dataclass
class ForecastDataPoint:
    """Data point for forecast visualization."""
    date: date
    forecast_value: Decimal
    lower_bound: Decimal  # Confidence interval lower bound
    upper_bound: Decimal  # Confidence interval upper bound
    confidence: Decimal  # Confidence level (0-100)


@dataclass
class SalesForecast:
    """Sales forecast result."""
    product_id: Optional[int]
    product_code: Optional[str]
    product_name: Optional[str]
    forecast_periods: List[ForecastDataPoint]
    historical_average: Decimal
    trend: str  # 'increasing', 'decreasing', 'stable'
    confidence_score: Decimal  # Overall confidence (0-100)


@dataclass
class StockForecast:
    """Stock forecast result."""
    product_id: int
    product_code: str
    product_name: str
    current_stock: Decimal
    forecast_demand: Decimal  # Forecasted demand for next period
    days_until_out_of_stock: Optional[int]
    recommended_reorder_quantity: Decimal
    confidence_score: Decimal


class ForecastService:
    """Service for generating sales and stock forecasts."""
    
    def forecast_sales(
        self,
        start_date: date,
        end_date: date,
        forecast_periods: int = 12,  # Number of future periods to forecast
        product_id: Optional[int] = None,
        method: str = 'moving_average'  # 'moving_average', 'exponential_smoothing', 'linear_regression'
    ) -> SalesForecast:
        """
        Generate sales forecast based on historical data.
        
        Args:
            start_date: Start date for historical data
            end_date: End date for historical data
            forecast_periods: Number of future periods to forecast
            product_id: Optional product ID to forecast for specific product
            method: Forecasting method
            
        Returns:
            SalesForecast object
        """
        with get_session() as session:
            # Get historical sales data
            query = session.query(
                func.date(Order.created_at).label('sale_date'),
                func.sum(OrderLine.quantity).label('quantity'),
                func.sum(OrderLine.line_total_ht).label('revenue')
            ).join(
                OrderLine, OrderLine.order_id == Order.id
            ).filter(
                Order.status.in_(['confirmed', 'ready', 'shipped', 'delivered', 'invoiced']),
                func.date(Order.created_at) >= start_date,
                func.date(Order.created_at) <= end_date
            )
            
            if product_id:
                query = query.filter(OrderLine.product_id == product_id)
            
            historical_data = query.group_by(
                func.date(Order.created_at)
            ).order_by(
                func.date(Order.created_at)
            ).all()
            
            if not historical_data:
                # No historical data, return empty forecast
                return SalesForecast(
                    product_id=product_id,
                    product_code=None,
                    product_name=None,
                    forecast_periods=[],
                    historical_average=Decimal('0'),
                    trend='stable',
                    confidence_score=Decimal('0')
                )
            
            # Extract historical values
            historical_values = [Decimal(str(row.revenue or 0)) for row in historical_data]
            historical_average = Decimal(str(statistics.mean([float(v) for v in historical_values])))
            
            # Generate forecast based on method
            forecast_data_points = []
            last_date = end_date
            
            if method == 'moving_average':
                # Simple moving average (using last 3 periods)
                window_size = min(3, len(historical_values))
                if window_size > 0:
                    recent_values = historical_values[-window_size:]
                    base_forecast = Decimal(str(statistics.mean([float(v) for v in recent_values])))
                else:
                    base_forecast = historical_average
                
                # Calculate standard deviation for confidence intervals
                if len(historical_values) > 1:
                    std_dev = Decimal(str(statistics.stdev([float(v) for v in historical_values])))
                else:
                    std_dev = base_forecast * Decimal('0.1')  # 10% default
                
                # Generate forecast for each period
                for i in range(forecast_periods):
                    forecast_date = last_date + timedelta(days=i + 1)
                    forecast_value = base_forecast
                    # Confidence interval: ±2 standard deviations (95% confidence)
                    lower_bound = max(Decimal('0'), forecast_value - (std_dev * Decimal('2')))
                    upper_bound = forecast_value + (std_dev * Decimal('2'))
                    confidence = Decimal('95')  # 95% confidence for moving average
                    
                    forecast_data_points.append(ForecastDataPoint(
                        date=forecast_date,
                        forecast_value=forecast_value,
                        lower_bound=lower_bound,
                        upper_bound=upper_bound,
                        confidence=confidence
                    ))
            
            elif method == 'exponential_smoothing':
                # Exponential smoothing (alpha = 0.3)
                alpha = Decimal('0.3')
                if historical_values:
                    smoothed_value = historical_values[0]
                    for value in historical_values[1:]:
                        smoothed_value = alpha * value + (Decimal('1') - alpha) * smoothed_value
                    
                    base_forecast = smoothed_value
                    std_dev = Decimal(str(statistics.stdev([float(v) for v in historical_values]))) if len(historical_values) > 1 else base_forecast * Decimal('0.1')
                    
                    for i in range(forecast_periods):
                        forecast_date = last_date + timedelta(days=i + 1)
                        forecast_value = base_forecast
                        lower_bound = max(Decimal('0'), forecast_value - (std_dev * Decimal('2')))
                        upper_bound = forecast_value + (std_dev * Decimal('2'))
                        confidence = Decimal('90')  # 90% confidence for exponential smoothing
                        
                        forecast_data_points.append(ForecastDataPoint(
                            date=forecast_date,
                            forecast_value=forecast_value,
                            lower_bound=lower_bound,
                            upper_bound=upper_bound,
                            confidence=confidence
                        ))
                else:
                    base_forecast = historical_average
                    std_dev = base_forecast * Decimal('0.1')
            
            else:  # linear_regression or default
                # Simple linear regression
                if len(historical_values) >= 2:
                    # Calculate trend
                    n = len(historical_values)
                    x_values = list(range(n))
                    y_values = [float(v) for v in historical_values]
                    
                    x_mean = statistics.mean(x_values)
                    y_mean = statistics.mean(y_values)
                    
                    numerator = sum((x_values[i] - x_mean) * (y_values[i] - y_mean) for i in range(n))
                    denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))
                    
                    if denominator != 0:
                        slope = Decimal(str(numerator / denominator))
                        intercept = Decimal(str(y_mean - (float(slope) * x_mean)))
                    else:
                        slope = Decimal('0')
                        intercept = Decimal(str(y_mean))
                    
                    std_dev = Decimal(str(statistics.stdev(y_values))) if len(y_values) > 1 else Decimal(str(y_mean * 0.1))
                    
                    for i in range(forecast_periods):
                        forecast_date = last_date + timedelta(days=i + 1)
                        x_forecast = n + i
                        forecast_value = intercept + slope * Decimal(str(x_forecast))
                        forecast_value = max(Decimal('0'), forecast_value)  # Ensure non-negative
                        lower_bound = max(Decimal('0'), forecast_value - (std_dev * Decimal('2')))
                        upper_bound = forecast_value + (std_dev * Decimal('2'))
                        confidence = Decimal('85')  # 85% confidence for linear regression
                        
                        forecast_data_points.append(ForecastDataPoint(
                            date=forecast_date,
                            forecast_value=forecast_value,
                            lower_bound=lower_bound,
                            upper_bound=upper_bound,
                            confidence=confidence
                        ))
                else:
                    # Fallback to moving average
                    base_forecast = historical_average
                    std_dev = base_forecast * Decimal('0.1')
                    for i in range(forecast_periods):
                        forecast_date = last_date + timedelta(days=i + 1)
                        forecast_value = base_forecast
                        lower_bound = max(Decimal('0'), forecast_value - (std_dev * Decimal('2')))
                        upper_bound = forecast_value + (std_dev * Decimal('2'))
                        confidence = Decimal('80')
                        
                        forecast_data_points.append(ForecastDataPoint(
                            date=forecast_date,
                            forecast_value=forecast_value,
                            lower_bound=lower_bound,
                            upper_bound=upper_bound,
                            confidence=confidence
                        ))
            
            # Determine trend
            if len(historical_values) >= 2:
                recent_trend = historical_values[-1] - historical_values[-2] if len(historical_values) >= 2 else Decimal('0')
                if abs(recent_trend) < historical_average * Decimal('0.05'):  # Less than 5% change
                    trend = 'stable'
                elif recent_trend > 0:
                    trend = 'increasing'
                else:
                    trend = 'decreasing'
            else:
                trend = 'stable'
            
            # Calculate overall confidence score
            confidence_score = Decimal('85') if len(historical_values) >= 10 else (
                Decimal('70') if len(historical_values) >= 5 else Decimal('50')
            )
            
            # Get product info if product_id provided
            product_code = None
            product_name = None
            if product_id:
                product = session.get(Product, product_id)
                if product:
                    product_code = product.code
                    product_name = product.name
            
            return SalesForecast(
                product_id=product_id,
                product_code=product_code,
                product_name=product_name,
                forecast_periods=forecast_data_points,
                historical_average=historical_average,
                trend=trend,
                confidence_score=confidence_score
            )
    
    def forecast_stock_needs(
        self,
        product_id: int,
        forecast_days: int = 30
    ) -> StockForecast:
        """
        Forecast stock needs for a product based on sales history.
        
        Args:
            product_id: Product ID to forecast
            forecast_days: Number of days to forecast ahead
            
        Returns:
            StockForecast object
        """
        with get_session() as session:
            # Get product
            product = session.get(Product, product_id)
            if not product:
                raise ValueError(f"Product with ID {product_id} not found")
            
            # Get current stock
            stock_items = session.query(StockItem).filter(
                StockItem.product_id == product_id
            ).all()
            
            current_stock = sum(item.physical_quantity for item in stock_items)
            
            # Get historical sales (last 90 days)
            end_date = date.today()
            start_date = end_date - timedelta(days=90)
            
            historical_sales = session.query(
                func.sum(OrderLine.quantity).label('total_quantity')
            ).join(
                Order, Order.id == OrderLine.order_id
            ).filter(
                OrderLine.product_id == product_id,
                Order.status.in_(['confirmed', 'ready', 'shipped', 'delivered', 'invoiced']),
                func.date(Order.created_at) >= start_date,
                func.date(Order.created_at) <= end_date
            ).scalar() or Decimal('0')
            
            # Calculate average daily demand
            days_in_period = (end_date - start_date).days or 1
            average_daily_demand = historical_sales / Decimal(str(days_in_period))
            
            # Forecast demand for next period
            forecast_demand = average_daily_demand * Decimal(str(forecast_days))
            
            # Calculate days until out of stock
            days_until_out_of_stock = None
            if average_daily_demand > 0:
                days_until_out_of_stock = int(float(current_stock / average_daily_demand))
            
            # Recommended reorder quantity (forecast demand + safety stock)
            safety_stock_multiplier = Decimal('1.5')  # 50% safety stock
            recommended_reorder_quantity = forecast_demand * safety_stock_multiplier
            
            # Calculate confidence score based on data availability
            confidence_score = Decimal('90') if days_in_period >= 60 else (
                Decimal('70') if days_in_period >= 30 else Decimal('50')
            )
            
            return StockForecast(
                product_id=product_id,
                product_code=product.code,
                product_name=product.name,
                current_stock=current_stock,
                forecast_demand=forecast_demand,
                days_until_out_of_stock=days_until_out_of_stock,
                recommended_reorder_quantity=recommended_reorder_quantity,
                confidence_score=confidence_score
            )

