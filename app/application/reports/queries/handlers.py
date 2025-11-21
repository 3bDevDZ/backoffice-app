"""Report query handlers for CQRS pattern."""
from datetime import date, timedelta
from typing import Optional

from app.application.common.cqrs import QueryHandler
from app.services.report_service import ReportService
from app.services.report_builder_service import ReportBuilderService
from app.services.forecast_service import ForecastService
from app.services.analytics_service import AnalyticsService
from .queries import (
    GetSalesReportQuery,
    GetMarginReportQuery,
    GetStockReportQuery,
    GetCustomerReportQuery,
    GetPurchaseReportQuery,
    GetCustomReportQuery,
    GetSalesForecastQuery,
    GetStockForecastQuery
)
from .report_dto import (
    ReportDataDTO,
    SalesForecastDTO,
    StockForecastDTO,
    ForecastDataPointDTO
)


class GetSalesReportHandler(QueryHandler):
    """Handler for getting sales report."""
    
    def __init__(self):
        self.report_service = ReportService()
    
    def handle(self, query: GetSalesReportQuery) -> ReportDataDTO:
        """Get sales report."""
        # Default to last 30 days if dates not provided
        end_date = query.end_date or date.today()
        start_date = query.start_date or (end_date - timedelta(days=30))
        
        report_data = self.report_service.generate_sales_report(
            start_date=start_date,
            end_date=end_date,
            group_by=query.group_by,
            include_top_products=query.include_top_products,
            include_top_customers=query.include_top_customers,
            limit=query.limit
        )
        
        return ReportDataDTO(
            title=report_data.title,
            report_type=report_data.report_type,
            period_start=str(report_data.period_start),
            period_end=str(report_data.period_end),
            data=report_data.data,
            summary=report_data.summary,
            metadata=report_data.metadata
        )


class GetMarginReportHandler(QueryHandler):
    """Handler for getting margin report."""
    
    def __init__(self):
        self.report_service = ReportService()
    
    def handle(self, query: GetMarginReportQuery) -> ReportDataDTO:
        """Get margin report."""
        # Default to last 30 days if dates not provided
        end_date = query.end_date or date.today()
        start_date = query.start_date or (end_date - timedelta(days=30))
        
        report_data = self.report_service.generate_margin_report(
            start_date=start_date,
            end_date=end_date,
            min_margin_percent=query.min_margin_percent
        )
        
        return ReportDataDTO(
            title=report_data.title,
            report_type=report_data.report_type,
            period_start=str(report_data.period_start),
            period_end=str(report_data.period_end),
            data=report_data.data,
            summary=report_data.summary,
            metadata=report_data.metadata
        )


class GetStockReportHandler(QueryHandler):
    """Handler for getting stock report."""
    
    def __init__(self):
        self.report_service = ReportService()
    
    def handle(self, query: GetStockReportQuery) -> ReportDataDTO:
        """Get stock report."""
        report_data = self.report_service.generate_stock_report(
            include_slow_moving=query.include_slow_moving,
            include_fast_moving=query.include_fast_moving,
            slow_moving_days=query.slow_moving_days,
            fast_moving_threshold=query.fast_moving_threshold
        )
        
        return ReportDataDTO(
            title=report_data.title,
            report_type=report_data.report_type,
            period_start=str(report_data.period_start),
            period_end=str(report_data.period_end),
            data=report_data.data,
            summary=report_data.summary,
            metadata=report_data.metadata
        )


class GetCustomerReportHandler(QueryHandler):
    """Handler for getting customer report."""
    
    def __init__(self):
        self.report_service = ReportService()
    
    def handle(self, query: GetCustomerReportQuery) -> ReportDataDTO:
        """Get customer report."""
        # Default to last 30 days if dates not provided
        end_date = query.end_date or date.today()
        start_date = query.start_date or (end_date - timedelta(days=30))
        
        report_data = self.report_service.generate_customer_report(
            start_date=start_date,
            end_date=end_date,
            limit=query.limit
        )
        
        return ReportDataDTO(
            title=report_data.title,
            report_type=report_data.report_type,
            period_start=str(report_data.period_start),
            period_end=str(report_data.period_end),
            data=report_data.data,
            summary=report_data.summary,
            metadata=report_data.metadata
        )


class GetPurchaseReportHandler(QueryHandler):
    """Handler for getting purchase report."""
    
    def __init__(self):
        self.report_service = ReportService()
    
    def handle(self, query: GetPurchaseReportQuery) -> ReportDataDTO:
        """Get purchase report."""
        # Default to last 30 days if dates not provided
        end_date = query.end_date or date.today()
        start_date = query.start_date or (end_date - timedelta(days=30))
        
        report_data = self.report_service.generate_purchase_report(
            start_date=start_date,
            end_date=end_date
        )
        
        return ReportDataDTO(
            title=report_data.title,
            report_type=report_data.report_type,
            period_start=str(report_data.period_start),
            period_end=str(report_data.period_end),
            data=report_data.data,
            summary=report_data.summary,
            metadata=report_data.metadata
        )


class GetCustomReportHandler(QueryHandler):
    """Handler for getting custom report from template."""
    
    def __init__(self):
        self.report_service = ReportService()
        self.report_builder = ReportBuilderService()
    
    def handle(self, query: GetCustomReportQuery) -> ReportDataDTO:
        """Get custom report from template."""
        from app.infrastructure.db import get_session
        from app.domain.models.report import ReportTemplate
        
        with get_session() as session:
            template = session.get(ReportTemplate, query.template_id)
            if not template:
                raise ValueError(f"ReportTemplate with ID {query.template_id} not found")
            
            # Build report from template
            report_data = self.report_builder.build_from_template(
                template=template,
                start_date=query.start_date,
                end_date=query.end_date
            )
            
            return ReportDataDTO(
                title=report_data.title,
                report_type=report_data.report_type,
                period_start=str(report_data.period_start),
                period_end=str(report_data.period_end),
                data=report_data.data,
                summary=report_data.summary,
                metadata=report_data.metadata
            )


class GetSalesForecastHandler(QueryHandler):
    """Handler for getting sales forecast."""
    
    def __init__(self):
        self.forecast_service = ForecastService()
    
    def handle(self, query: GetSalesForecastQuery) -> SalesForecastDTO:
        """Get sales forecast."""
        # Default to last 90 days if dates not provided
        end_date = query.end_date or date.today()
        start_date = query.start_date or (end_date - timedelta(days=90))
        
        forecast = self.forecast_service.forecast_sales(
            start_date=start_date,
            end_date=end_date,
            forecast_periods=query.forecast_periods,
            product_id=query.product_id,
            method=query.method
        )
        
        return SalesForecastDTO(
            product_id=forecast.product_id,
            product_code=forecast.product_code,
            product_name=forecast.product_name,
            forecast_periods=[
                ForecastDataPointDTO(
                    date=str(dp.date),
                    forecast_value=float(dp.forecast_value),
                    lower_bound=float(dp.lower_bound),
                    upper_bound=float(dp.upper_bound),
                    confidence=float(dp.confidence)
                )
                for dp in forecast.forecast_periods
            ],
            historical_average=float(forecast.historical_average),
            trend=forecast.trend,
            confidence_score=float(forecast.confidence_score)
        )


class GetStockForecastHandler(QueryHandler):
    """Handler for getting stock forecast."""
    
    def __init__(self):
        self.forecast_service = ForecastService()
    
    def handle(self, query: GetStockForecastQuery) -> StockForecastDTO:
        """Get stock forecast."""
        forecast = self.forecast_service.forecast_stock_needs(
            product_id=query.product_id,
            forecast_days=query.forecast_days
        )
        
        return StockForecastDTO(
            product_id=forecast.product_id,
            product_code=forecast.product_code,
            product_name=forecast.product_name,
            current_stock=float(forecast.current_stock),
            forecast_demand=float(forecast.forecast_demand),
            days_until_out_of_stock=forecast.days_until_out_of_stock,
            recommended_reorder_quantity=float(forecast.recommended_reorder_quantity),
            confidence_score=float(forecast.confidence_score)
        )

