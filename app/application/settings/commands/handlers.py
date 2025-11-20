"""Settings command handlers."""
from app.application.common.cqrs import CommandHandler
from app.application.settings.commands.commands import (
    UpdateCompanySettingsCommand,
    UpdateAppSettingsCommand
)
from app.domain.models.settings import CompanySettings, AppSettings
from app.infrastructure.db import get_session


class UpdateCompanySettingsHandler(CommandHandler):
    """Handler for UpdateCompanySettingsCommand."""
    
    def handle(self, command: UpdateCompanySettingsCommand) -> int:
        """Update company settings."""
        with get_session() as session:
            # Get or create company settings (singleton pattern)
            company_settings = session.query(CompanySettings).first()
            
            if not company_settings:
                # Create default settings
                company_settings = CompanySettings.create()
                session.add(company_settings)
                session.flush()
            
            # Update settings
            company_settings.update(
                name=command.name,
                legal_name=command.legal_name,
                siret=command.siret,
                vat_number=command.vat_number,
                rcs=command.rcs,
                legal_form=command.legal_form,
                address=command.address,
                postal_code=command.postal_code,
                city=command.city,
                country=command.country,
                phone=command.phone,
                email=command.email,
                website=command.website,
                logo_path=command.logo_path
            )
            
            session.commit()
            return company_settings.id


class UpdateAppSettingsHandler(CommandHandler):
    """Handler for UpdateAppSettingsCommand."""
    
    def handle(self, command: UpdateAppSettingsCommand) -> int:
        """Update application settings."""
        with get_session() as session:
            # Get or create app settings (singleton pattern)
            app_settings = session.query(AppSettings).first()
            
            if not app_settings:
                # Create default settings
                app_settings = AppSettings.create()
                session.add(app_settings)
                session.flush()
            
            # Update settings
            app_settings.update(
                stock_management_mode=command.stock_management_mode,
                default_currency=command.default_currency,
                default_tax_rate=command.default_tax_rate,
                default_language=command.default_language,
                invoice_prefix=command.invoice_prefix,
                invoice_footer=command.invoice_footer,
                purchase_order_prefix=command.purchase_order_prefix,
                receipt_prefix=command.receipt_prefix,
                quote_prefix=command.quote_prefix,
                quote_validity_days=command.quote_validity_days,
                email_notifications_enabled=command.email_notifications_enabled,
                email_order_confirmation=command.email_order_confirmation,
                email_invoice_sent=command.email_invoice_sent
            )
            
            session.commit()
            return app_settings.id

