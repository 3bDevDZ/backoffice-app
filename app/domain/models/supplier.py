"""Supplier domain model for supplier management."""
from dataclasses import dataclass, field
from decimal import Decimal
from datetime import date, datetime
from typing import List, Optional
from sqlalchemy import Column, Integer, String, Text, Boolean, Numeric, ForeignKey, Date, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ...infrastructure.db import Base
from ...domain.primitives.aggregate_root import AggregateRoot
from ...domain.events.domain_event import DomainEvent


@dataclass
class SupplierCreatedDomainEvent(DomainEvent):
    """Domain event raised when a supplier is created."""
    supplier_id: int = 0
    supplier_code: str = ""
    supplier_name: str = ""


@dataclass
class SupplierUpdatedDomainEvent(DomainEvent):
    """Domain event raised when a supplier is updated."""
    supplier_id: int = 0
    supplier_code: str = ""
    changes: dict = field(default_factory=dict)


@dataclass
class SupplierArchivedDomainEvent(DomainEvent):
    """Domain event raised when a supplier is archived."""
    supplier_id: int = 0
    supplier_code: str = ""


class SupplierAddress(Base):
    """Address entity for supplier locations."""
    __tablename__ = "supplier_addresses"

    id = Column(Integer, primary_key=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    type = Column(String(20), nullable=False)  # 'headquarters', 'warehouse', 'billing', 'delivery'
    is_default_billing = Column(Boolean, default=False)
    is_default_delivery = Column(Boolean, default=False)
    street = Column(String(200), nullable=False)
    city = Column(String(100), nullable=False)
    postal_code = Column(String(20), nullable=False)
    country = Column(String(100), nullable=False, default="France")
    state = Column(String(100), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relationships
    supplier = relationship("Supplier", back_populates="addresses")

    @staticmethod
    def create(
        supplier_id: int,
        type: str,
        street: str,
        city: str,
        postal_code: str,
        country: str = "France",
        state: str = None,
        is_default_billing: bool = False,
        is_default_delivery: bool = False
    ):
        """Factory method to create a new SupplierAddress."""
        if not street or not street.strip():
            raise ValueError("Street address is required.")
        if not city or not city.strip():
            raise ValueError("City is required.")
        if not postal_code or not postal_code.strip():
            raise ValueError("Postal code is required.")
        if type not in ['headquarters', 'warehouse', 'billing', 'delivery']:
            raise ValueError("Address type must be 'headquarters', 'warehouse', 'billing', or 'delivery'.")
        
        return SupplierAddress(
            supplier_id=supplier_id,
            type=type.strip(),
            street=street.strip(),
            city=city.strip(),
            postal_code=postal_code.strip(),
            country=country.strip() if country else "France",
            state=state.strip() if state else None,
            is_default_billing=is_default_billing,
            is_default_delivery=is_default_delivery
        )


class SupplierContact(Base):
    """Contact entity for supplier contacts."""
    __tablename__ = "supplier_contacts"

    id = Column(Integer, primary_key=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    function = Column(String(100), nullable=True)  # Job title
    email = Column(String(200), nullable=True)
    phone = Column(String(20), nullable=True)
    mobile = Column(String(20), nullable=True)
    is_primary = Column(Boolean, default=False)
    receives_orders = Column(Boolean, default=True)
    receives_invoices = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relationships
    supplier = relationship("Supplier", back_populates="contacts")

    @staticmethod
    def create(
        supplier_id: int,
        first_name: str,
        last_name: str,
        function: str = None,
        email: str = None,
        phone: str = None,
        mobile: str = None,
        is_primary: bool = False,
        receives_orders: bool = True,
        receives_invoices: bool = False
    ):
        """Factory method to create a new SupplierContact."""
        if not first_name or not first_name.strip():
            raise ValueError("First name is required.")
        if not last_name or not last_name.strip():
            raise ValueError("Last name is required.")
        
        return SupplierContact(
            supplier_id=supplier_id,
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            function=function.strip() if function else None,
            email=email.strip().lower() if email else None,
            phone=phone.strip() if phone else None,
            mobile=mobile.strip() if mobile else None,
            is_primary=is_primary,
            receives_orders=receives_orders,
            receives_invoices=receives_invoices
        )


class SupplierConditions(Base):
    """Commercial conditions for suppliers (payment terms, discounts, etc.)."""
    __tablename__ = "supplier_conditions"

    id = Column(Integer, primary_key=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), unique=True, nullable=False)
    payment_terms_days = Column(Integer, nullable=False, default=30)  # Payment terms in days
    default_discount_percent = Column(Numeric(5, 2), nullable=False, default=Decimal(0))  # Default discount %
    minimum_order_amount = Column(Numeric(12, 2), nullable=False, default=Decimal(0))  # Minimum order value
    delivery_lead_time_days = Column(Integer, nullable=False, default=7)  # Typical delivery time
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    supplier = relationship("Supplier", back_populates="conditions", uselist=False)


class Supplier(Base, AggregateRoot):
    """Supplier aggregate root for supplier management."""
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    
    # Basic information
    name = Column(String(200), nullable=False)  # Company name
    email = Column(String(200), unique=True, nullable=False)
    phone = Column(String(20), nullable=True)
    mobile = Column(String(20), nullable=True)
    category = Column(String(50), nullable=True)  # e.g., 'Primary', 'Secondary', 'Backup'
    status = Column(String(20), nullable=False, default='active')  # 'active', 'inactive', 'archived', 'blocked'
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Company information
    company_name = Column(String(200), nullable=True)  # Raison sociale
    siret = Column(String(14), unique=True, nullable=True)  # 14 digits
    vat_number = Column(String(50), nullable=True)  # TVA intracommunautaire
    rcs = Column(String(50), nullable=True)  # RCS number
    legal_form = Column(String(50), nullable=True)  # Forme juridique

    # Relationships
    addresses = relationship("SupplierAddress", back_populates="supplier", cascade="all, delete-orphan")
    contacts = relationship("SupplierContact", back_populates="supplier", cascade="all, delete-orphan")
    conditions = relationship("SupplierConditions", back_populates="supplier", uselist=False, cascade="all, delete-orphan")

    @staticmethod
    def _generate_code() -> str:
        """Generate unique supplier code in format FOUR-XXXXXX."""
        import random
        import string
        from app.infrastructure.db import get_session
        
        # Try to generate a unique code
        max_attempts = 10
        for _ in range(max_attempts):
            suffix = ''.join(random.choices(string.digits, k=6))
            code = f"FOUR-{suffix}"
            
            # Check if code exists
            with get_session() as session:
                existing = session.query(Supplier).filter_by(code=code).first()
                if not existing:
                    return code
        
        # Fallback: use timestamp-based code
        import time
        timestamp = int(time.time()) % 1000000
        return f"FOUR-{timestamp:06d}"

    @staticmethod
    def create(
        name: str,
        email: str,
        code: str = None,
        phone: str = None,
        mobile: str = None,
        category: str = None,
        notes: str = None,
        company_name: str = None,
        siret: str = None,
        vat_number: str = None,
        rcs: str = None,
        legal_form: str = None,
        payment_terms_days: int = 30,
        default_discount_percent: Decimal = Decimal(0),
        minimum_order_amount: Decimal = Decimal(0),
        delivery_lead_time_days: int = 7
    ):
        """
        Factory method to create a new Supplier.
        
        Args:
            name: Supplier name
            email: Email address (must be unique)
            code: Optional supplier code (auto-generated if not provided)
            phone: Phone number
            mobile: Mobile number
            category: Supplier category
            notes: Internal notes
            company_name: Company name
            siret: SIRET number (14 digits)
            vat_number: VAT number
            rcs: RCS number
            legal_form: Legal form
            payment_terms_days: Payment terms in days
            default_discount_percent: Default discount percentage
            minimum_order_amount: Minimum order amount
            delivery_lead_time_days: Typical delivery lead time in days
            
        Returns:
            Supplier instance
            
        Raises:
            ValueError: If validation fails
        """
        if not name or not name.strip():
            raise ValueError("Supplier name is required.")
        
        if not email or not email.strip():
            raise ValueError("Supplier email is required.")
        
        # Validate email format (basic)
        if '@' not in email:
            raise ValueError("Invalid email format.")
        
        if siret and len(siret.replace(' ', '')) != 14:
            raise ValueError("SIRET must be 14 digits.")
        
        supplier = Supplier(
            code=code.strip() if code else Supplier._generate_code(),
            name=name.strip(),
            email=email.strip().lower(),
            phone=phone.strip() if phone else None,
            mobile=mobile.strip() if mobile else None,
            category=category.strip() if category else None,
            notes=notes.strip() if notes else None,
            company_name=company_name.strip() if company_name else None,
            siret=siret.replace(' ', '') if siret else None,
            vat_number=vat_number.strip() if vat_number else None,
            rcs=rcs.strip() if rcs else None,
            legal_form=legal_form.strip() if legal_form else None
        )
        
        # Raise domain event
        supplier.raise_domain_event(SupplierCreatedDomainEvent(
            supplier_id=supplier.id,
            supplier_code=supplier.code,
            supplier_name=supplier.name
        ))
        
        return supplier

    def update_details(
        self,
        name: str = None,
        email: str = None,
        phone: str = None,
        mobile: str = None,
        category: str = None,
        notes: str = None,
        company_name: str = None,
        siret: str = None,
        vat_number: str = None,
        rcs: str = None,
        legal_form: str = None
    ):
        """Update supplier details."""
        changes = {}
        
        if name is not None:
            if not name.strip():
                raise ValueError("Supplier name cannot be empty.")
            if self.name != name.strip():
                changes['name'] = {'old': self.name, 'new': name.strip()}
                self.name = name.strip()
        
        if email is not None:
            if not email.strip():
                raise ValueError("Supplier email cannot be empty.")
            if '@' not in email:
                raise ValueError("Invalid email format.")
            if self.email != email.strip().lower():
                changes['email'] = {'old': self.email, 'new': email.strip().lower()}
                self.email = email.strip().lower()
        
        if phone is not None:
            self.phone = phone.strip() if phone else None
        
        if mobile is not None:
            self.mobile = mobile.strip() if mobile else None
        
        if category is not None:
            self.category = category.strip() if category else None
        
        if notes is not None:
            self.notes = notes.strip() if notes else None
        
        if company_name is not None:
            self.company_name = company_name.strip() if company_name else None
        
        if siret is not None:
            if siret and len(siret.replace(' ', '')) != 14:
                raise ValueError("SIRET must be 14 digits.")
            self.siret = siret.replace(' ', '') if siret else None
        
        if vat_number is not None:
            self.vat_number = vat_number.strip() if vat_number else None
        
        if rcs is not None:
            self.rcs = rcs.strip() if rcs else None
        
        if legal_form is not None:
            self.legal_form = legal_form.strip() if legal_form else None
        
        self.updated_at = datetime.utcnow()
        
        if changes:
            self.raise_domain_event(SupplierUpdatedDomainEvent(
                supplier_id=self.id,
                supplier_code=self.code,
                changes=changes
            ))

    def archive(self):
        """Archive the supplier."""
        if self.status == 'archived':
            return
        
        self.status = 'archived'
        self.updated_at = datetime.utcnow()
        self.raise_domain_event(SupplierArchivedDomainEvent(
            supplier_id=self.id,
            supplier_code=self.code
        ))

    def activate(self):
        """Activate the supplier."""
        self.status = 'active'
        self.updated_at = datetime.utcnow()

    def deactivate(self):
        """Deactivate the supplier."""
        self.status = 'inactive'
        self.updated_at = datetime.utcnow()

