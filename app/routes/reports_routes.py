"""Frontend routes for reports and analytics."""
from flask import Blueprint, render_template, request, jsonify, session, send_file, current_app as app
from flask_babel import gettext as _
from datetime import date, datetime, timedelta
from decimal import Decimal
from io import BytesIO

from app.security.session_auth import require_roles_or_redirect
from app.application.common.mediator import mediator
from app.application.reports.queries.queries import (
    GetSalesReportQuery, GetMarginReportQuery, GetStockReportQuery,
    GetCustomerReportQuery, GetPurchaseReportQuery, GetCustomReportQuery,
    GetSalesForecastQuery, GetStockForecastQuery
)
from app.services.report_export_service import ReportExportService

reports_routes = Blueprint('reports', __name__)


def _convert_to_json_serializable(obj):
    """Convert Decimal and other non-serializable types to JSON-serializable formats."""
    from decimal import Decimal
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, (date, datetime)):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: _convert_to_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [_convert_to_json_serializable(item) for item in obj]
    else:
        return obj


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


# ============================================================================
# HTML Page Routes
# ============================================================================

@reports_routes.route('/reports', methods=['GET'])
@require_roles_or_redirect('admin', 'direction', 'commercial')
def list_reports():
    """Display reports list page."""
    return render_template('reports/list.html')


@reports_routes.route('/reports/builder', methods=['GET'])
@require_roles_or_redirect('admin', 'direction', 'commercial')
def report_builder():
    """Display report builder page."""
    report_type = request.args.get('type', 'sales')
    template_id = request.args.get('template_id', type=int)
    
    return render_template('reports/builder.html', report_type=report_type, template_id=template_id)


@reports_routes.route('/reports/analytics/sales', methods=['GET'])
@require_roles_or_redirect('admin', 'direction', 'commercial')
def sales_report():
    """Display sales report page."""
    # Get default date range (last 30 days)
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    
    # Get parameters from query string
    start_date_str = request.args.get('start_date', start_date.isoformat())
    end_date_str = request.args.get('end_date', end_date.isoformat())
    group_by = request.args.get('group_by', 'day')
    
    try:
        start_date = date.fromisoformat(start_date_str)
        end_date = date.fromisoformat(end_date_str)
    except:
        start_date = date.today() - timedelta(days=30)
        end_date = date.today()
    
    return render_template(
        'reports/sales.html',
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat(),
        group_by=group_by
    )


@reports_routes.route('/reports/margins', methods=['GET'])
@require_roles_or_redirect('admin', 'direction', 'commercial')
def margins_report():
    """Display margin report page."""
    # Get default date range (last 30 days)
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    
    # Get parameters from query string
    start_date_str = request.args.get('start_date', start_date.isoformat())
    end_date_str = request.args.get('end_date', end_date.isoformat())
    
    try:
        start_date = date.fromisoformat(start_date_str)
        end_date = date.fromisoformat(end_date_str)
    except:
        start_date = date.today() - timedelta(days=30)
        end_date = date.today()
    
    return render_template(
        'reports/margins.html',
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat()
    )


@reports_routes.route('/reports/forecast', methods=['GET'])
@require_roles_or_redirect('admin', 'direction', 'commercial')
def forecast_report():
    """Display forecast report page."""
    forecast_type = request.args.get('type', 'sales')  # 'sales' or 'stock'
    product_id = request.args.get('product_id', type=int)
    
    return render_template(
        'reports/forecast.html',
        forecast_type=forecast_type,
        product_id=product_id
    )


@reports_routes.route('/reports/stock', methods=['GET'])
@require_roles_or_redirect('admin', 'direction', 'warehouse')
def stock_report():
    """Display stock report page."""
    return render_template('reports/stock.html')


@reports_routes.route('/reports/analytics/customers', methods=['GET'])
@require_roles_or_redirect('admin', 'direction', 'commercial')
def customers_report():
    """Display customer report page."""
    # Get default date range (last 30 days)
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    
    # Get parameters from query string
    start_date_str = request.args.get('start_date', start_date.isoformat())
    end_date_str = request.args.get('end_date', end_date.isoformat())
    
    try:
        start_date = date.fromisoformat(start_date_str)
        end_date = date.fromisoformat(end_date_str)
    except:
        start_date = date.today() - timedelta(days=30)
        end_date = date.today()
    
    return render_template(
        'reports/customers.html',
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat()
    )


@reports_routes.route('/reports/purchases', methods=['GET'])
@require_roles_or_redirect('admin', 'direction', 'purchasing')
def purchases_report():
    """Display purchase report page."""
    # Get default date range (last 30 days)
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    
    # Get parameters from query string
    start_date_str = request.args.get('start_date', start_date.isoformat())
    end_date_str = request.args.get('end_date', end_date.isoformat())
    
    try:
        start_date = date.fromisoformat(start_date_str)
        end_date = date.fromisoformat(end_date_str)
    except:
        start_date = date.today() - timedelta(days=30)
        end_date = date.today()
    
    return render_template(
        'reports/purchases.html',
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat()
    )


@reports_routes.route('/reports/custom/<int:template_id>', methods=['GET'])
@require_roles_or_redirect('admin', 'direction', 'commercial')
def custom_report(template_id: int):
    """Display custom report page."""
    # Get default date range (last 30 days)
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    
    # Get parameters from query string
    start_date_str = request.args.get('start_date', start_date.isoformat())
    end_date_str = request.args.get('end_date', end_date.isoformat())
    
    try:
        start_date = date.fromisoformat(start_date_str)
        end_date = date.fromisoformat(end_date_str)
    except:
        start_date = date.today() - timedelta(days=30)
        end_date = date.today()
    
    return render_template(
        'reports/custom.html',
        template_id=template_id,
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat()
    )


# ============================================================================
# JSON Data Routes (replacing API endpoints - using sessions)
# ============================================================================

@reports_routes.route('/reports/data/analytics/sales', methods=['GET'])
@require_roles_or_redirect('admin', 'direction', 'commercial')
def get_sales_report_data():
    """Get sales report data as JSON."""
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
        
        # Convert all data to JSON-serializable format
        data_dict = {
            'title': report_dto.title,
            'report_type': report_dto.report_type,
            'period_start': report_dto.period_start if report_dto.period_start else None,
            'period_end': report_dto.period_end if report_dto.period_end else None,
            'data': _convert_to_json_serializable(report_dto.data or []),
            'summary': _convert_to_json_serializable(report_dto.summary or {}),
            'metadata': _convert_to_json_serializable(report_dto.metadata if hasattr(report_dto, 'metadata') else {})
        }
        
        return jsonify({
            'success': True,
            'data': data_dict
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@reports_routes.route('/reports/data/margins', methods=['GET'])
@require_roles_or_redirect('admin', 'direction', 'commercial')
def get_margins_report_data():
    """Get margins report data as JSON."""
    try:
        start_date = _parse_date(request.args.get('start_date'))
        end_date = _parse_date(request.args.get('end_date'))
        min_margin_percent = request.args.get('min_margin_percent')
        min_margin = Decimal(min_margin_percent) if min_margin_percent else None
        
        query = GetMarginReportQuery(
            start_date=start_date,
            end_date=end_date,
            min_margin_percent=min_margin
        )
        
        report_dto = mediator.dispatch(query)
        
        # Convert all data to JSON-serializable format
        data_dict = {
            'title': report_dto.title,
            'report_type': report_dto.report_type,
            'period_start': report_dto.period_start if report_dto.period_start else None,
            'period_end': report_dto.period_end if report_dto.period_end else None,
            'data': _convert_to_json_serializable(report_dto.data or []),
            'summary': _convert_to_json_serializable(report_dto.summary or {}),
            'metadata': _convert_to_json_serializable(report_dto.metadata if hasattr(report_dto, 'metadata') else {})
        }
        
        return jsonify({
            'success': True,
            'data': data_dict
        })
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        app.logger.error(f"Error in get_margins_report_data: {str(e)}")
        app.logger.error(f"Traceback: {error_trace}")
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': error_trace if app.config.get('DEBUG', False) else None
        }), 500


@reports_routes.route('/reports/data/stock', methods=['GET'])
@require_roles_or_redirect('admin', 'direction', 'warehouse')
def get_stock_report_data():
    """Get stock report data as JSON."""
    try:
        include_slow_moving = request.args.get('include_slow_moving', 'true').lower() == 'true'
        include_fast_moving = request.args.get('include_fast_moving', 'true').lower() == 'true'
        slow_moving_days = int(request.args.get('slow_moving_days', 90))
        fast_moving_threshold = Decimal(request.args.get('fast_moving_threshold', '100'))
        
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
                'period_start': report_dto.period_start if report_dto.period_start else None,
                'period_end': report_dto.period_end if report_dto.period_end else None,
                'data': _convert_to_json_serializable(report_dto.data or []),
                'summary': _convert_to_json_serializable(report_dto.summary or {}),
                'metadata': _convert_to_json_serializable(report_dto.metadata if hasattr(report_dto, 'metadata') else {})
            }
        })
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        app.logger.error(f"Error in get_stock_report_data: {str(e)}")
        app.logger.error(f"Traceback: {error_trace}")
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': error_trace if app.config.get('DEBUG', False) else None
        }), 500


@reports_routes.route('/reports/data/analytics/customers', methods=['GET'])
@require_roles_or_redirect('admin', 'direction', 'commercial')
def get_customers_report_data():
    """Get customer report data as JSON."""
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
        
        # Convert all data to JSON-serializable format
        data_dict = {
            'title': report_dto.title,
            'report_type': report_dto.report_type,
            'period_start': report_dto.period_start if report_dto.period_start else None,
            'period_end': report_dto.period_end if report_dto.period_end else None,
            'data': _convert_to_json_serializable(report_dto.data or []),
            'summary': _convert_to_json_serializable(report_dto.summary or {}),
            'metadata': _convert_to_json_serializable(report_dto.metadata if hasattr(report_dto, 'metadata') else {})
        }
        
        return jsonify({
            'success': True,
            'data': data_dict
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@reports_routes.route('/reports/data/purchases', methods=['GET'])
@require_roles_or_redirect('admin', 'direction', 'purchasing')
def get_purchases_report_data():
    """Get purchase report data as JSON."""
    try:
        start_date = _parse_date(request.args.get('start_date'))
        end_date = _parse_date(request.args.get('end_date'))
        supplier_id = request.args.get('supplier_id', type=int)
        limit = int(request.args.get('limit', 50))
        
        query = GetPurchaseReportQuery(
            start_date=start_date,
            end_date=end_date,
            supplier_id=supplier_id,
            limit=limit
        )
        
        report_dto = mediator.dispatch(query)
        
        # Convert all data to JSON-serializable format
        data_dict = {
            'title': report_dto.title,
            'report_type': report_dto.report_type,
            'period_start': report_dto.period_start if report_dto.period_start else None,
            'period_end': report_dto.period_end if report_dto.period_end else None,
            'data': _convert_to_json_serializable(report_dto.data or []),
            'summary': _convert_to_json_serializable(report_dto.summary or {}),
            'metadata': _convert_to_json_serializable(report_dto.metadata if hasattr(report_dto, 'metadata') else {})
        }
        
        return jsonify({
            'success': True,
            'data': data_dict
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@reports_routes.route('/reports/data/custom/<int:template_id>', methods=['GET'])
@require_roles_or_redirect('admin', 'direction', 'commercial')
def get_custom_report_data(template_id: int):
    """Get custom report data as JSON."""
    try:
        start_date = _parse_date(request.args.get('start_date'))
        end_date = _parse_date(request.args.get('end_date'))
        
        query = GetCustomReportQuery(
            template_id=template_id,
            start_date=start_date,
            end_date=end_date
        )
        
        report_dto = mediator.dispatch(query)
        
        # Convert all data to JSON-serializable format
        data_dict = {
            'title': report_dto.title,
            'report_type': report_dto.report_type,
            'period_start': report_dto.period_start if report_dto.period_start else None,
            'period_end': report_dto.period_end if report_dto.period_end else None,
            'data': _convert_to_json_serializable(report_dto.data or []),
            'summary': _convert_to_json_serializable(report_dto.summary or {}),
            'metadata': _convert_to_json_serializable(report_dto.metadata if hasattr(report_dto, 'metadata') else {})
        }
        
        return jsonify({
            'success': True,
            'data': data_dict
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@reports_routes.route('/reports/data/forecast/sales', methods=['GET'])
@require_roles_or_redirect('admin', 'direction', 'commercial')
def get_sales_forecast_data():
    """Get sales forecast data as JSON."""
    try:
        start_date = _parse_date(request.args.get('start_date'))
        end_date = _parse_date(request.args.get('end_date'))
        product_id = request.args.get('product_id', type=int)
        forecast_periods = int(request.args.get('forecast_periods', 12))
        method = request.args.get('method', 'moving_average')
        
        query = GetSalesForecastQuery(
            start_date=start_date,
            end_date=end_date,
            product_id=product_id,
            forecast_periods=forecast_periods,
            method=method
        )
        
        forecast_dto = mediator.dispatch(query)
        
        # Convert forecast_periods to list of dicts for JSON serialization
        forecast_data = [
            {
                'date': dp.date,
                'forecast_value': dp.forecast_value,
                'lower_bound': dp.lower_bound,
                'upper_bound': dp.upper_bound,
                'confidence': dp.confidence
            }
            for dp in forecast_dto.forecast_periods
        ]
        
        return jsonify({
            'success': True,
            'data': {
                'forecast_type': 'sales',
                'product_id': forecast_dto.product_id,
                'product_code': forecast_dto.product_code,
                'product_name': forecast_dto.product_name,
                'forecast_periods': _convert_to_json_serializable(forecast_data),
                'historical_average': _convert_to_json_serializable(forecast_dto.historical_average),
                'trend': forecast_dto.trend,
                'confidence_score': _convert_to_json_serializable(forecast_dto.confidence_score)
            }
        })
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        app.logger.error(f"Error in get_sales_forecast_data: {str(e)}")
        app.logger.error(f"Traceback: {error_trace}")
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': error_trace if app.config.get('DEBUG', False) else None
        }), 500


@reports_routes.route('/reports/data/forecast/stock', methods=['GET'])
@require_roles_or_redirect('admin', 'direction', 'warehouse')
def get_stock_forecast_data():
    """Get stock forecast data as JSON."""
    try:
        product_id = request.args.get('product_id', type=int)
        forecast_days = int(request.args.get('forecast_days', 30))
        location_id = request.args.get('location_id', type=int)
        
        query = GetStockForecastQuery(
            product_id=product_id,
            forecast_days=forecast_days,
            location_id=location_id
        )
        
        forecast_dto = mediator.dispatch(query)
        
        return jsonify({
            'success': True,
            'data': {
                'title': forecast_dto.title,
                'forecast_type': forecast_dto.forecast_type,
                'data': forecast_dto.data,
                'summary': forecast_dto.summary,
                'metadata': forecast_dto.metadata
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@reports_routes.route('/reports/export', methods=['POST'])
@require_roles_or_redirect('admin', 'direction', 'commercial')
def export_report():
    """Export report to Excel, PDF, or CSV."""
    try:
        data = request.get_json() if request.is_json else request.form.to_dict()
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
                location_id=data.get('location_id'),
                site_id=data.get('site_id'),
                low_stock_only=data.get('low_stock_only', False)
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
                end_date=end_date,
                supplier_id=data.get('supplier_id'),
                limit=data.get('limit', 50)
            )
        else:
            return jsonify({
                'success': False,
                'error': f'Unknown report type: {report_type}'
            }), 400
        
        # Generate report
        report_dto = mediator.dispatch(query)
        
        # Export using service
        export_service = ReportExportService()
        
        if format_type == 'excel':
            file_data = export_service.export_to_excel(report_dto)
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            filename = f'{report_type}_report.xlsx'
        elif format_type == 'pdf':
            file_data = export_service.export_to_pdf(report_dto)
            mimetype = 'application/pdf'
            filename = f'{report_type}_report.pdf'
        elif format_type == 'csv':
            file_data = export_service.export_to_csv(report_dto)
            mimetype = 'text/csv'
            filename = f'{report_type}_report.csv'
        else:
            return jsonify({
                'success': False,
                'error': f'Unsupported format: {format_type}'
            }), 400
        
        return send_file(
            BytesIO(file_data),
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
