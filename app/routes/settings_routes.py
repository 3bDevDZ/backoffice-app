"""Settings routes for configuration management."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_babel import gettext as _
from decimal import Decimal

from app.security.session_auth import require_roles_or_redirect, get_current_user
from app.utils.locale import get_locale
from app.application.common.mediator import mediator
from app.application.settings.commands.commands import (
    UpdateCompanySettingsCommand,
    UpdateAppSettingsCommand
)
from app.application.settings.queries.queries import (
    GetCompanySettingsQuery,
    GetAppSettingsQuery
)

settings_routes = Blueprint('settings', __name__)


@settings_routes.route('/settings')
@require_roles_or_redirect('admin', 'direction')
def index():
    """Settings index page - show tabs for different settings."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    try:
        # Get current settings
        company_settings = mediator.dispatch(GetCompanySettingsQuery())
        app_settings = mediator.dispatch(GetAppSettingsQuery())
        
        return render_template(
            'settings/index.html',
            company_settings=company_settings,
            app_settings=app_settings,
            locale=locale,
            direction=direction
        )
    except Exception as e:
        flash(_('An error occurred: %(error)s', error=str(e)), 'error')
        return redirect(url_for('dashboard.index'))


@settings_routes.route('/settings/company', methods=['GET', 'POST'])
@require_roles_or_redirect('admin', 'direction')
def company_settings():
    """Company information settings."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    try:
        if request.method == 'POST':
            current_user = get_current_user()
            if not current_user:
                flash(_('Authentication required'), 'error')
                return redirect(url_for('settings.index'))
            
            # Get form data
            command = UpdateCompanySettingsCommand(
                name=request.form.get('name'),
                legal_name=request.form.get('legal_name') or None,
                siret=request.form.get('siret') or None,
                vat_number=request.form.get('vat_number') or None,
                rcs=request.form.get('rcs') or None,
                legal_form=request.form.get('legal_form') or None,
                address=request.form.get('address') or None,
                postal_code=request.form.get('postal_code') or None,
                city=request.form.get('city') or None,
                country=request.form.get('country') or 'France',
                phone=request.form.get('phone') or None,
                email=request.form.get('email') or None,
                website=request.form.get('website') or None,
                logo_path=request.form.get('logo_path') or None
            )
            
            mediator.dispatch(command)
            flash(_('Company settings updated successfully'), 'success')
            return redirect(url_for('settings.company_settings'))
        
        # GET - show form
        company_settings = mediator.dispatch(GetCompanySettingsQuery())
        
        return render_template(
            'settings/company.html',
            company_settings=company_settings,
            locale=locale,
            direction=direction
        )
    except Exception as e:
        flash(_('An error occurred: %(error)s', error=str(e)), 'error')
        return redirect(url_for('settings.index'))


@settings_routes.route('/settings/app', methods=['GET', 'POST'])
@require_roles_or_redirect('admin', 'direction')
def app_settings():
    """Application settings."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    try:
        if request.method == 'POST':
            current_user = get_current_user()
            if not current_user:
                flash(_('Authentication required'), 'error')
                return redirect(url_for('settings.index'))
            
            # Get form data
            stock_mode = request.form.get('stock_management_mode', 'simple')
            default_tax_rate = request.form.get('default_tax_rate', type=float)
            
            command = UpdateAppSettingsCommand(
                stock_management_mode=stock_mode,
                default_currency=request.form.get('default_currency') or 'EUR',
                default_tax_rate=default_tax_rate,
                default_language=request.form.get('default_language') or 'fr',
                invoice_prefix=request.form.get('invoice_prefix') or None,
                invoice_footer=request.form.get('invoice_footer') or None,
                purchase_order_prefix=request.form.get('purchase_order_prefix') or None,
                receipt_prefix=request.form.get('receipt_prefix') or None,
                quote_prefix=request.form.get('quote_prefix') or None,
                quote_validity_days=request.form.get('quote_validity_days', type=int),
                email_notifications_enabled=request.form.get('email_notifications_enabled') == 'on',
                email_order_confirmation=request.form.get('email_order_confirmation') == 'on',
                email_invoice_sent=request.form.get('email_invoice_sent') == 'on'
            )
            
            mediator.dispatch(command)
            
            flash(_('Application settings updated successfully'), 'success')
            return redirect(url_for('settings.app_settings'))
        
        # GET - show form
        app_settings = mediator.dispatch(GetAppSettingsQuery())
        
        return render_template(
            'settings/app.html',
            app_settings=app_settings,
            locale=locale,
            direction=direction
        )
    except Exception as e:
        flash(_('An error occurred: %(error)s', error=str(e)), 'error')
        return redirect(url_for('settings.index'))

