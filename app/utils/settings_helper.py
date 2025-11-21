"""Helper functions for accessing application settings."""
from typing import Optional
from app.application.common.mediator import mediator
from app.application.settings.queries.queries import (
    GetCompanySettingsQuery,
    GetAppSettingsQuery
)


def get_company_settings():
    """Get company settings from database."""
    try:
        return mediator.dispatch(GetCompanySettingsQuery())
    except Exception:
        # Return default DTO if settings not available
        from app.application.settings.queries.settings_dto import CompanySettingsDTO
        return CompanySettingsDTO(
            id=0,
            name="CommerceFlow",
            country="France"
        )


def get_app_settings():
    """Get application settings from database."""
    try:
        return mediator.dispatch(GetAppSettingsQuery())
    except Exception:
        # Return default DTO if settings not available
        from app.application.settings.queries.settings_dto import AppSettingsDTO
        return AppSettingsDTO(
            id=0,
            stock_management_mode='simple',
            default_currency='EUR',
            default_tax_rate=None,
            default_language='fr'
        )


def get_stock_management_mode() -> str:
    """Get stock management mode (simple or advanced)."""
    app_settings = get_app_settings()
    return app_settings.stock_management_mode or 'simple'


def get_default_currency() -> str:
    """Get default currency."""
    app_settings = get_app_settings()
    return app_settings.default_currency or 'EUR'


def get_default_tax_rate() -> Optional[float]:
    """Get default tax rate."""
    app_settings = get_app_settings()
    if app_settings.default_tax_rate:
        return float(app_settings.default_tax_rate)
    return 20.0  # Default to 20%


def get_default_language() -> str:
    """Get default language."""
    app_settings = get_app_settings()
    return app_settings.default_language or 'fr'

