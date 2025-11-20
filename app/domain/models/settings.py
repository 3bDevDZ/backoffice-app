"""Settings domain models for company and application configuration."""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from ...infrastructure.db import Base
from ...domain.primitives.aggregate_root import AggregateRoot


class CompanySettings(Base, AggregateRoot):
    """Company information settings model."""
    __tablename__ = "company_settings"

    id = Column(Integer, primary_key=True)
    
    # Company identification
    name = Column(String(200), nullable=False, default="CommerceFlow")
    legal_name = Column(String(200), nullable=True)  # Raison sociale
    siret = Column(String(14), nullable=True)  # 14 digits
    vat_number = Column(String(50), nullable=True)  # TVA intracommunautaire
    rcs = Column(String(50), nullable=True)  # RCS number
    legal_form = Column(String(50), nullable=True)  # Forme juridique
    
    # Contact information
    address = Column(Text, nullable=True)
    postal_code = Column(String(20), nullable=True)
    city = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True, default="France")
    phone = Column(String(20), nullable=True)
    email = Column(String(200), nullable=True)
    website = Column(String(200), nullable=True)
    
    # Logo and branding
    logo_path = Column(String(500), nullable=True)  # Path to logo file
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    @staticmethod
    def create(
        name: str = "CommerceFlow",
        legal_name: str = None,
        siret: str = None,
        vat_number: str = None,
        rcs: str = None,
        legal_form: str = None,
        address: str = None,
        postal_code: str = None,
        city: str = None,
        country: str = "France",
        phone: str = None,
        email: str = None,
        website: str = None,
        logo_path: str = None
    ) -> "CompanySettings":
        """Factory method to create company settings."""
        if not name or not name.strip():
            raise ValueError("Company name is required.")
        
        settings = CompanySettings()
        settings.name = name.strip()
        settings.legal_name = legal_name.strip() if legal_name else None
        settings.siret = siret.strip() if siret else None
        settings.vat_number = vat_number.strip() if vat_number else None
        settings.rcs = rcs.strip() if rcs else None
        settings.legal_form = legal_form.strip() if legal_form else None
        settings.address = address.strip() if address else None
        settings.postal_code = postal_code.strip() if postal_code else None
        settings.city = city.strip() if city else None
        settings.country = country.strip() if country else "France"
        settings.phone = phone.strip() if phone else None
        settings.email = email.strip() if email else None
        settings.website = website.strip() if website else None
        settings.logo_path = logo_path.strip() if logo_path else None
        
        return settings

    def update(
        self,
        name: str = None,
        legal_name: str = None,
        siret: str = None,
        vat_number: str = None,
        rcs: str = None,
        legal_form: str = None,
        address: str = None,
        postal_code: str = None,
        city: str = None,
        country: str = None,
        phone: str = None,
        email: str = None,
        website: str = None,
        logo_path: str = None
    ):
        """Update company settings."""
        if name is not None:
            if not name.strip():
                raise ValueError("Company name cannot be empty.")
            self.name = name.strip()
        
        if legal_name is not None:
            self.legal_name = legal_name.strip() if legal_name else None
        if siret is not None:
            self.siret = siret.strip() if siret else None
        if vat_number is not None:
            self.vat_number = vat_number.strip() if vat_number else None
        if rcs is not None:
            self.rcs = rcs.strip() if rcs else None
        if legal_form is not None:
            self.legal_form = legal_form.strip() if legal_form else None
        if address is not None:
            self.address = address.strip() if address else None
        if postal_code is not None:
            self.postal_code = postal_code.strip() if postal_code else None
        if city is not None:
            self.city = city.strip() if city else None
        if country is not None:
            self.country = country.strip() if country else "France"
        if phone is not None:
            self.phone = phone.strip() if phone else None
        if email is not None:
            self.email = email.strip() if email else None
        if website is not None:
            self.website = website.strip() if website else None
        if logo_path is not None:
            self.logo_path = logo_path.strip() if logo_path else None


class AppSettings(Base, AggregateRoot):
    """Application settings model."""
    __tablename__ = "app_settings"

    id = Column(Integer, primary_key=True)
    
    # Stock management
    stock_management_mode = Column(String(20), nullable=False, default='simple')  # 'simple' or 'advanced'
    
    # Default values
    default_currency = Column(String(3), nullable=False, default='EUR')
    default_tax_rate = Column(Numeric(5, 2), nullable=True, default=20.00)  # Default VAT rate in %
    default_language = Column(String(5), nullable=False, default='fr')
    
    # Invoice settings
    invoice_prefix = Column(String(10), nullable=True, default='INV')
    invoice_footer = Column(Text, nullable=True)
    
    # Purchase order settings
    purchase_order_prefix = Column(String(10), nullable=True, default='PO')
    
    # Receipt settings
    receipt_prefix = Column(String(10), nullable=True, default='REC')
    
    # Quote settings
    quote_prefix = Column(String(10), nullable=True, default='QUO')
    quote_validity_days = Column(Integer, nullable=True, default=30)
    
    # Email settings
    email_notifications_enabled = Column(Boolean, nullable=False, default=True)
    email_order_confirmation = Column(Boolean, nullable=False, default=True)
    email_invoice_sent = Column(Boolean, nullable=False, default=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    @staticmethod
    def create(
        stock_management_mode: str = 'simple',
        default_currency: str = 'EUR',
        default_tax_rate: float = 20.00,
        default_language: str = 'fr',
        invoice_prefix: str = 'INV',
        invoice_footer: str = None,
        purchase_order_prefix: str = 'PO',
        receipt_prefix: str = 'REC',
        quote_prefix: str = 'QUO',
        quote_validity_days: int = 30,
        email_notifications_enabled: bool = True,
        email_order_confirmation: bool = True,
        email_invoice_sent: bool = True
    ) -> "AppSettings":
        """Factory method to create application settings."""
        if stock_management_mode not in ['simple', 'advanced']:
            raise ValueError("Stock management mode must be 'simple' or 'advanced'.")
        
        settings = AppSettings()
        settings.stock_management_mode = stock_management_mode
        settings.default_currency = default_currency
        settings.default_tax_rate = default_tax_rate
        settings.default_language = default_language
        settings.invoice_prefix = invoice_prefix.strip() if invoice_prefix else 'INV'
        settings.invoice_footer = invoice_footer.strip() if invoice_footer else None
        settings.purchase_order_prefix = purchase_order_prefix.strip() if purchase_order_prefix else 'PO'
        settings.receipt_prefix = receipt_prefix.strip() if receipt_prefix else 'REC'
        settings.quote_prefix = quote_prefix.strip() if quote_prefix else 'QUO'
        settings.quote_validity_days = quote_validity_days
        settings.email_notifications_enabled = email_notifications_enabled
        settings.email_order_confirmation = email_order_confirmation
        settings.email_invoice_sent = email_invoice_sent
        
        return settings

    def update(
        self,
        stock_management_mode: str = None,
        default_currency: str = None,
        default_tax_rate: float = None,
        default_language: str = None,
        invoice_prefix: str = None,
        invoice_footer: str = None,
        purchase_order_prefix: str = None,
        receipt_prefix: str = None,
        quote_prefix: str = None,
        quote_validity_days: int = None,
        email_notifications_enabled: bool = None,
        email_order_confirmation: bool = None,
        email_invoice_sent: bool = None
    ):
        """Update application settings."""
        if stock_management_mode is not None:
            if stock_management_mode not in ['simple', 'advanced']:
                raise ValueError("Stock management mode must be 'simple' or 'advanced'.")
            self.stock_management_mode = stock_management_mode
        
        if default_currency is not None:
            self.default_currency = default_currency
        if default_tax_rate is not None:
            self.default_tax_rate = default_tax_rate
        if default_language is not None:
            self.default_language = default_language
        if invoice_prefix is not None:
            self.invoice_prefix = invoice_prefix.strip() if invoice_prefix else 'INV'
        if invoice_footer is not None:
            self.invoice_footer = invoice_footer.strip() if invoice_footer else None
        if purchase_order_prefix is not None:
            self.purchase_order_prefix = purchase_order_prefix.strip() if purchase_order_prefix else 'PO'
        if receipt_prefix is not None:
            self.receipt_prefix = receipt_prefix.strip() if receipt_prefix else 'REC'
        if quote_prefix is not None:
            self.quote_prefix = quote_prefix.strip() if quote_prefix else 'QUO'
        if quote_validity_days is not None:
            self.quote_validity_days = quote_validity_days
        if email_notifications_enabled is not None:
            self.email_notifications_enabled = email_notifications_enabled
        if email_order_confirmation is not None:
            self.email_order_confirmation = email_order_confirmation
        if email_invoice_sent is not None:
            self.email_invoice_sent = email_invoice_sent

