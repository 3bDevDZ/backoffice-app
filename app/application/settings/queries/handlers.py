"""Settings query handlers."""
from app.application.common.cqrs import QueryHandler
from app.application.settings.queries.queries import (
    GetCompanySettingsQuery,
    GetAppSettingsQuery
)
from app.application.settings.queries.settings_dto import (
    CompanySettingsDTO,
    AppSettingsDTO
)
from app.domain.models.settings import CompanySettings, AppSettings
from app.infrastructure.db import get_session


class GetCompanySettingsHandler(QueryHandler):
    """Handler for GetCompanySettingsQuery."""
    
    def handle(self, query: GetCompanySettingsQuery) -> CompanySettingsDTO:
        """Get company settings."""
        with get_session() as session:
            company_settings = session.query(CompanySettings).first()
            
            if not company_settings:
                # Return default DTO if no settings exist
                return CompanySettingsDTO(
                    id=0,
                    name="CommerceFlow",
                    country="France"
                )
            
            return CompanySettingsDTO(
                id=company_settings.id,
                name=company_settings.name,
                legal_name=company_settings.legal_name,
                siret=company_settings.siret,
                vat_number=company_settings.vat_number,
                rcs=company_settings.rcs,
                legal_form=company_settings.legal_form,
                address=company_settings.address,
                postal_code=company_settings.postal_code,
                city=company_settings.city,
                country=company_settings.country,
                phone=company_settings.phone,
                email=company_settings.email,
                website=company_settings.website,
                logo_path=company_settings.logo_path
            )


class GetAppSettingsHandler(QueryHandler):
    """Handler for GetAppSettingsQuery."""
    
    def handle(self, query: GetAppSettingsQuery) -> AppSettingsDTO:
        """Get application settings."""
        with get_session() as session:
            app_settings = session.query(AppSettings).first()
            
            if not app_settings:
                # Return default DTO if no settings exist
                return AppSettingsDTO(
                    id=0,
                    stock_management_mode='simple',
                    default_currency='EUR',
                    default_tax_rate=None,
                    default_language='fr'
                )
            
            return AppSettingsDTO(
                id=app_settings.id,
                stock_management_mode=app_settings.stock_management_mode,
                default_currency=app_settings.default_currency,
                default_tax_rate=app_settings.default_tax_rate,
                default_language=app_settings.default_language,
                invoice_prefix=app_settings.invoice_prefix,
                invoice_footer=app_settings.invoice_footer,
                purchase_order_prefix=app_settings.purchase_order_prefix,
                receipt_prefix=app_settings.receipt_prefix,
                quote_prefix=app_settings.quote_prefix,
                quote_validity_days=app_settings.quote_validity_days,
                email_notifications_enabled=app_settings.email_notifications_enabled,
                email_order_confirmation=app_settings.email_order_confirmation,
                email_invoice_sent=app_settings.email_invoice_sent
            )

