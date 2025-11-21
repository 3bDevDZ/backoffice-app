"""Settings DTOs."""
from dataclasses import dataclass
from typing import Optional
from decimal import Decimal


@dataclass
class CompanySettingsDTO:
    """DTO for company settings."""
    id: int
    name: str
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
class AppSettingsDTO:
    """DTO for application settings."""
    id: int
    stock_management_mode: str
    default_currency: str
    default_tax_rate: Optional[Decimal] = None
    default_language: str = 'fr'
    invoice_prefix: Optional[str] = None
    invoice_footer: Optional[str] = None
    purchase_order_prefix: Optional[str] = None
    receipt_prefix: Optional[str] = None
    quote_prefix: Optional[str] = None
    quote_validity_days: Optional[int] = None
    email_notifications_enabled: bool = True
    email_order_confirmation: bool = True
    email_invoice_sent: bool = True

