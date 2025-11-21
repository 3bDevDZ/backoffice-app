"""Settings command DTOs."""
from dataclasses import dataclass
from typing import Optional
from decimal import Decimal

from app.application.common.cqrs import Command


@dataclass
class UpdateCompanySettingsCommand(Command):
    """Command to update company settings."""
    name: Optional[str] = None
    legal_name: Optional[str] = None
    siret: Optional[str] = None
    vat_number: Optional[str] = None
    rcs: Optional[str] = None
    legal_form: Optional[str] = None
    address: Optional[str] = None
    postal_code: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    logo_path: Optional[str] = None


@dataclass
class UpdateAppSettingsCommand(Command):
    """Command to update application settings."""
    stock_management_mode: Optional[str] = None
    default_currency: Optional[str] = None
    default_tax_rate: Optional[float] = None
    default_language: Optional[str] = None
    invoice_prefix: Optional[str] = None
    invoice_footer: Optional[str] = None
    purchase_order_prefix: Optional[str] = None
    receipt_prefix: Optional[str] = None
    quote_prefix: Optional[str] = None
    quote_validity_days: Optional[int] = None
    email_notifications_enabled: Optional[bool] = None
    email_order_confirmation: Optional[bool] = None
    email_invoice_sent: Optional[bool] = None

