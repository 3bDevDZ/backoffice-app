"""API endpoints for reports and analytics."""
from flask import Blueprint, request, jsonify, send_file
from flask_babel import gettext as _
from datetime import date, datetime
from decimal import Decimal
from io import BytesIO

from app.application.common.mediator import mediator
from app.application.reports.queries.queries import (
    GetSalesReportQuery, GetMarginReportQuery, GetStockReportQuery,
    GetCustomerReportQuery, GetPurchaseReportQuery, GetCustomReportQuery,
    GetSalesForecastQuery, GetStockForecastQuery
)
from app.services.report_export_service import ReportExportService
from app.security.rbac import require_roles

reports_bp = Blueprint('reports', __name__, url_prefix='/api/reports')


def _parse_date(date_str: str) -> date:
    """Parse date string to date object."""
    if not date_str:
        return None
    try:
        if 'T' in date_str:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00')).date()
        return date.fromisoformat(date_str)
    except:
        return None


@reports_bp.route('/sales', methods=['GET'])
@require_roles('admin', 'direction', 'commercial')
def get_sales_report():
    """Get sales report."""
    try:
        start_date = _parse_date(request.args.get('start_date'))
        end_date = _parse_date(request.args.get('end_date'))
        group_by = request.args.get('group_by', 'day')
        include_top_products = request.args.get('include_top_products', 'true').lower() == 'true'
        include_top_customers = request.args.get('include_top_customers', 'true').lower() == 'true'
        limit = int(request.args.get('limit', 10))
        
        query = GetSalesReportQuery(
            start_date=start_date,
            end_date=end_date,
            group_by=group_by,
            include_top_products=include_top_products,
            include_top_customers=include_top_customers,
            limit=limit
        )
        
        report_dto = mediator.dispatch(query)
        
        return jsonify({
            'success': True,
            'data': {
                'title': report_dto.title,
                'report_type': report_dto.report_type,
                'period_start': report_dto.period_start,
                'period_end': report_dto.period_end,
                'data': report_dto.data,
                'summary': report_dto.summary,
                'metadata': report_dto.metadata
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@reports_bp.route('/margins', methods=['GET'])
@require_roles('admin', 'direction', 'commercial')
def get_margin_report():
    """Get margin report."""
    try:
        start_date = _parse_date(request.args.get('start_date'))
        end_date = _parse_date(request.args.get('end_date'))
        min_margin_percent = request.args.get('min_margin_percent')
        min_margin_percent = Decimal(min_margin_percent) if min_margin_percent else None
        
        query = GetMarginReportQuery(
            start_date=start_date,
            end_date=end_date,
            min_margin_percent=min_margin_percent
        )
        
        report_dto = mediator.dispatch(query)
        
        return jsonify({
            'success': True,
            'data': {
                'title': report_dto.title,
                'report_type': report_dto.report_type,
                'period_start': report_dto.period_start,
                'period_end': report_dto.period_end,
                'data': report_dto.data,
                'summary': report_dto.summary,
                'metadata': report_dto.metadata
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@reports_bp.route('/stock', methods=['GET'])
@require_roles('admin', 'direction', 'warehouse')
def get_stock_report():
    """Get stock report."""
    try:
        include_slow_moving = request.args.get('include_slow_moving', 'true').lower() == 'true'
        include_fast_moving = request.args.get('include_fast_moving', 'true').lower() == 'true'
        slow_moving_days = int(request.args.get('slow_moving_days', 90))
        fast_moving_threshold = Decimal(request.args.get('fast_moving_threshold', 100))
        
        query = GetStockReportQuery(
            include_slow_moving=include_slow_moving,
            include_fast_moving=include_fast_moving,
            slow_moving_days=slow_moving_days,
            fast_moving_threshold=fast_moving_threshold
        )
        
        report_dto = mediator.dispatch(query)
        
        return jsonify({
            'success': True,
            'data': {
                'title': report_dto.title,
                'report_type': report_dto.report_type,
                'period_start': report_dto.period_start,
                'period_end': report_dto.period_end,
                'data': report_dto.data,
                'summary': report_dto.summary,
                'metadata': report_dto.metadata
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@reports_bp.route('/customers', methods=['GET'])
@require_roles('admin', 'direction', 'commercial')
def get_customer_report():
    """Get customer report."""
    try:
        start_date = _parse_date(request.args.get('start_date'))
        end_date = _parse_date(request.args.get('end_date'))
        limit = int(request.args.get('limit', 50))
        
        query = GetCustomerReportQuery(
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
        
        report_dto = mediator.dispatch(query)
        
        return jsonify({
            'success': True,
            'data': {
                'title': report_dto.title,
                'report_type': report_dto.report_type,
                'period_start': report_dto.period_start,
                'period_end': report_dto.period_end,
                'data': report_dto.data,
                'summary': report_dto.summary,
                'metadata': report_dto.metadata
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@reports_bp.route('/purchases', methods=['GET'])
@require_roles('admin', 'direction', 'purchasing')
def get_purchase_report():
    """Get purchase report."""
    try:
        start_date = _parse_date(request.args.get('start_date'))
        end_date = _parse_date(request.args.get('end_date'))
        
        query = GetPurchaseReportQuery(
            start_date=start_date,
            end_date=end_date
        )
        
        report_dto = mediator.dispatch(query)
        
        return jsonify({
            'success': True,
            'data': {
                'title': report_dto.title,
                'report_type': report_dto.report_type,
                'period_start': report_dto.period_start,
                'period_end': report_dto.period_end,
                'data': report_dto.data,
                'summary': report_dto.summary,
                'metadata': report_dto.metadata
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@reports_bp.route('/custom/<int:template_id>', methods=['GET'])
@require_roles('admin', 'direction', 'commercial')
def get_custom_report(template_id: int):
    """Get custom report from template."""
    try:
        start_date = _parse_date(request.args.get('start_date'))
        end_date = _parse_date(request.args.get('end_date'))
        
        query = GetCustomReportQuery(
            template_id=template_id,
            start_date=start_date,
            end_date=end_date
        )
        
        report_dto = mediator.dispatch(query)
        
        return jsonify({
            'success': True,
            'data': {
                'title': report_dto.title,
                'report_type': report_dto.report_type,
                'period_start': report_dto.period_start,
                'period_end': report_dto.period_end,
                'data': report_dto.data,
                'summary': report_dto.summary,
                'metadata': report_dto.metadata
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@reports_bp.route('/forecast/sales', methods=['GET'])
@require_roles('admin', 'direction', 'commercial')
def get_sales_forecast():
    """Get sales forecast."""
    try:
        start_date = _parse_date(request.args.get('start_date'))
        end_date = _parse_date(request.args.get('end_date'))
        forecast_periods = int(request.args.get('forecast_periods', 12))
        product_id = request.args.get('product_id', type=int)
        method = request.args.get('method', 'moving_average')
        
        query = GetSalesForecastQuery(
            start_date=start_date,
            end_date=end_date,
            forecast_periods=forecast_periods,
            product_id=product_id,
            method=method
        )
        
        forecast_dto = mediator.dispatch(query)
        
        return jsonify({
            'success': True,
            'data': {
                'product_id': forecast_dto.product_id,
                'product_code': forecast_dto.product_code,
                'product_name': forecast_dto.product_name,
                'forecast_periods': [
                    {
                        'date': dp.date,
                        'forecast_value': dp.forecast_value,
                        'lower_bound': dp.lower_bound,
                        'upper_bound': dp.upper_bound,
                        'confidence': dp.confidence
                    }
                    for dp in forecast_dto.forecast_periods
                ],
                'historical_average': forecast_dto.historical_average,
                'trend': forecast_dto.trend,
                'confidence_score': forecast_dto.confidence_score
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@reports_bp.route('/forecast/stock', methods=['GET'])
@require_roles('admin', 'direction', 'warehouse')
def get_stock_forecast():
    """Get stock forecast."""
    try:
        product_id = request.args.get('product_id', type=int)
        if not product_id:
            return jsonify({
                'success': False,
                'error': 'product_id is required'
            }), 400
        
        forecast_days = int(request.args.get('forecast_days', 30))
        
        query = GetStockForecastQuery(
            product_id=product_id,
            forecast_days=forecast_days
        )
        
        forecast_dto = mediator.dispatch(query)
        
        return jsonify({
            'success': True,
            'data': {
                'product_id': forecast_dto.product_id,
                'product_code': forecast_dto.product_code,
                'product_name': forecast_dto.product_name,
                'current_stock': forecast_dto.current_stock,
                'forecast_demand': forecast_dto.forecast_demand,
                'days_until_out_of_stock': forecast_dto.days_until_out_of_stock,
                'recommended_reorder_quantity': forecast_dto.recommended_reorder_quantity,
                'confidence_score': forecast_dto.confidence_score
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@reports_bp.route('/export', methods=['POST'])
@require_roles('admin', 'direction', 'commercial')
def export_report():
    """Export report to Excel, PDF, or CSV."""
    try:
        data = request.get_json()
        report_type = data.get('report_type')  # 'sales', 'margins', 'stock', 'customers', 'purchases', 'custom'
        format_type = data.get('format', 'excel')  # 'excel', 'pdf', 'csv'
        template_id = data.get('template_id')
        
        # Get report parameters
        start_date = _parse_date(data.get('start_date'))
        end_date = _parse_date(data.get('end_date'))
        
        # Generate report based on type
        if report_type == 'custom' and template_id:
            query = GetCustomReportQuery(
                template_id=template_id,
                start_date=start_date,
                end_date=end_date
            )
        elif report_type == 'sales':
            query = GetSalesReportQuery(
                start_date=start_date,
                end_date=end_date,
                group_by=data.get('group_by', 'day'),
                include_top_products=data.get('include_top_products', True),
                include_top_customers=data.get('include_top_customers', True),
                limit=data.get('limit', 10)
            )
        elif report_type == 'margins':
            query = GetMarginReportQuery(
                start_date=start_date,
                end_date=end_date,
                min_margin_percent=Decimal(data.get('min_margin_percent')) if data.get('min_margin_percent') else None
            )
        elif report_type == 'stock':
            query = GetStockReportQuery(
                include_slow_moving=data.get('include_slow_moving', True),
                include_fast_moving=data.get('include_fast_moving', True),
                slow_moving_days=data.get('slow_moving_days', 90),
                fast_moving_threshold=Decimal(data.get('fast_moving_threshold', 100))
            )
        elif report_type == 'customers':
            query = GetCustomerReportQuery(
                start_date=start_date,
                end_date=end_date,
                limit=data.get('limit', 50)
            )
        elif report_type == 'purchases':
            query = GetPurchaseReportQuery(
                start_date=start_date,
                end_date=end_date
            )
        else:
            return jsonify({
                'success': False,
                'error': f'Invalid report_type: {report_type}'
            }), 400
        
        # Get report data
        report_dto = mediator.dispatch(query)
        
        # Convert DTO to ReportData for export service
        from app.services.report_service import ReportData
        report_data = ReportData(
            title=report_dto.title,
            report_type=report_dto.report_type,
            period_start=date.fromisoformat(report_dto.period_start),
            period_end=date.fromisoformat(report_dto.period_end),
            data=report_dto.data,
            summary=report_dto.summary,
            metadata=report_dto.metadata
        )
        
        # Export based on format
        export_service = ReportExportService()
        
        if format_type == 'excel':
            excel_bytes = export_service.export_to_excel(report_data)
            return send_file(
                BytesIO(excel_bytes),
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f'{report_data.title.replace(" ", "_")}.xlsx'
            )
        elif format_type == 'pdf':
            pdf_buffer = export_service.export_to_pdf(report_data)
            return send_file(
                pdf_buffer,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f'{report_data.title.replace(" ", "_")}.pdf'
            )
        elif format_type == 'csv':
            csv_content = export_service.export_to_csv(report_data)
            return send_file(
                BytesIO(csv_content.encode('utf-8')),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'{report_data.title.replace(" ", "_")}.csv'
            )
        else:
            return jsonify({
                'success': False,
                'error': f'Invalid format: {format_type}'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

