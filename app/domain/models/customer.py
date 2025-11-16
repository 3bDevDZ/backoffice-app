"""Customer domain model for customer management."""
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
class CustomerCreatedDomainEvent(DomainEvent):
    """Domain event raised when a customer is created."""
    customer_id: int = 0
    customer_code: str = ""
    customer_name: str = ""


@dataclass
class CustomerUpdatedDomainEvent(DomainEvent):
    """Domain event raised when a customer is updated."""
    customer_id: int = 0
    customer_code: str = ""
    changes: dict = field(default_factory=dict)


@dataclass
class CustomerArchivedDomainEvent(DomainEvent):
    """Domain event raised when a customer is archived."""
    customer_id: int = 0
    customer_code: str = ""


class Address(Base):
    """Address entity for customer billing and delivery addresses."""
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    type = Column(String(20), nullable=False)  # 'billing', 'delivery', 'both'
    is_default_billing = Column(Boolean, default=False)
    is_default_delivery = Column(Boolean, default=False)
    street = Column(String(200), nullable=False)
    city = Column(String(100), nullable=False)
    postal_code = Column(String(20), nullable=False)
    country = Column(String(100), nullable=False, default="France")
    state = Column(String(100), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relationships
    customer = relationship("Customer", back_populates="addresses")

    @staticmethod
    def create(
        customer_id: int,
        type: str,
        street: str,
        city: str,
        postal_code: str,
        country: str = "France",
        state: str = None,
        is_default_billing: bool = False,
        is_default_delivery: bool = False
    ):
        """Factory method to create a new Address."""
        if not street or not street.strip():
            raise ValueError("Street address is required.")
        if not city or not city.strip():
            raise ValueError("City is required.")
        if not postal_code or not postal_code.strip():
            raise ValueError("Postal code is required.")
        if type not in ['billing', 'delivery', 'both']:
            raise ValueError("Address type must be 'billing', 'delivery', or 'both'.")
        
        return Address(
            customer_id=customer_id,
            type=type.strip(),
            street=street.strip(),
            city=city.strip(),
            postal_code=postal_code.strip(),
            country=country.strip() if country else "France",
            state=state.strip() if state else None,
            is_default_billing=is_default_billing,
            is_default_delivery=is_default_delivery
        )

    def update_details(
        self,
        type: str = None,
        street: str = None,
        city: str = None,
        postal_code: str = None,
        country: str = None,
        state: str = None,
        is_default_billing: bool = None,
        is_default_delivery: bool = None
    ):
        """Update address details."""
        if type is not None:
            if type not in ['billing', 'delivery', 'both']:
                raise ValueError("Address type must be 'billing', 'delivery', or 'both'.")
            self.type = type.strip()
        
        if street is not None:
            if not street.strip():
                raise ValueError("Street address cannot be empty.")
            self.street = street.strip()
        
        if city is not None:
            if not city.strip():
                raise ValueError("City cannot be empty.")
            self.city = city.strip()
        
        if postal_code is not None:
            if not postal_code.strip():
                raise ValueError("Postal code cannot be empty.")
            self.postal_code = postal_code.strip()
        
        if country is not None:
            self.country = country.strip()
        
        if state is not None:
            self.state = state.strip() if state else None
        
        if is_default_billing is not None:
            self.is_default_billing = is_default_billing
        
        if is_default_delivery is not None:
            self.is_default_delivery = is_default_delivery


class Contact(Base):
    """Contact entity for customer contacts (primarily B2B)."""
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    function = Column(String(100), nullable=True)  # Job title
    email = Column(String(200), nullable=True)
    phone = Column(String(20), nullable=True)
    mobile = Column(String(20), nullable=True)
    is_primary = Column(Boolean, default=False)
    receives_quotes = Column(Boolean, default=True)
    receives_invoices = Column(Boolean, default=False)
    receives_orders = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relationships
    customer = relationship("Customer", back_populates="contacts")

    @staticmethod
    def create(
        customer_id: int,
        first_name: str,
        last_name: str,
        function: str = None,
        email: str = None,
        phone: str = None,
        mobile: str = None,
        is_primary: bool = False,
        receives_quotes: bool = True,
        receives_invoices: bool = False,
        receives_orders: bool = False
    ):
        """Factory method to create a new Contact."""
        if not first_name or not first_name.strip():
            raise ValueError("First name is required.")
        if not last_name or not last_name.strip():
            raise ValueError("Last name is required.")
        
        return Contact(
            customer_id=customer_id,
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            function=function.strip() if function else None,
            email=email.strip() if email else None,
            phone=phone.strip() if phone else None,
            mobile=mobile.strip() if mobile else None,
            is_primary=is_primary,
            receives_quotes=receives_quotes,
            receives_invoices=receives_invoices,
            receives_orders=receives_orders
        )

    def update_details(
        self,
        first_name: str = None,
        last_name: str = None,
        function: str = None,
        email: str = None,
        phone: str = None,
        mobile: str = None,
        is_primary: bool = None,
        receives_quotes: bool = None,
        receives_invoices: bool = None,
        receives_orders: bool = None
    ):
        """Update contact details."""
        if first_name is not None:
            if not first_name.strip():
                raise ValueError("First name cannot be empty.")
            self.first_name = first_name.strip()
        
        if last_name is not None:
            if not last_name.strip():
                raise ValueError("Last name cannot be empty.")
            self.last_name = last_name.strip()
        
        if function is not None:
            self.function = function.strip() if function else None
        
        if email is not None:
            self.email = email.strip() if email else None
        
        if phone is not None:
            self.phone = phone.strip() if phone else None
        
        if mobile is not None:
            self.mobile = mobile.strip() if mobile else None
        
        if is_primary is not None:
            self.is_primary = is_primary
        
        if receives_quotes is not None:
            self.receives_quotes = receives_quotes
        
        if receives_invoices is not None:
            self.receives_invoices = receives_invoices
        
        if receives_orders is not None:
            self.receives_orders = receives_orders


class CommercialConditions(Base):
    """Commercial conditions entity for customer payment terms, credit limits, and pricing."""
    __tablename__ = "commercial_conditions"

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), unique=True, nullable=False)
    payment_terms_days = Column(Integer, default=30)  # 30, 60, 90 days
    price_list_id = Column(Integer, ForeignKey("price_lists.id"), nullable=True)  # FK to price_lists
    default_discount_percent = Column(Numeric(5, 2), default=Decimal(0))  # 0-100%
    credit_limit = Column(Numeric(12, 2), default=Decimal(0))  # ≥ 0
    block_on_credit_exceeded = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    customer = relationship("Customer", back_populates="commercial_conditions", uselist=False)
    price_list = relationship("PriceList", foreign_keys=[price_list_id])

    def check_credit_available(self, used_credit: Decimal = Decimal(0)) -> Decimal:
        """Calculate available credit (limit - used)."""
        return max(Decimal(0), self.credit_limit - used_credit)

    def is_credit_exceeded(self, used_credit: Decimal = Decimal(0)) -> bool:
        """Check if credit limit is exceeded."""
        if not self.block_on_credit_exceeded:
            return False
        return used_credit > self.credit_limit


class Customer(Base, AggregateRoot):
    """Customer aggregate root for customer management."""
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    type = Column(String(20), nullable=False)  # 'B2B' or 'B2C'
    
    # Common fields
    name = Column(String(200), nullable=False)  # Company name (B2B) or Full name (B2C)
    email = Column(String(200), unique=True, nullable=False)
    phone = Column(String(20), nullable=True)
    mobile = Column(String(20), nullable=True)
    category = Column(String(50), nullable=True)  # e.g., 'VIP', 'Standard'
    status = Column(String(20), nullable=False, default='active')  # 'active', 'inactive', 'archived', 'blocked'
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # B2B-specific fields
    company_name = Column(String(200), nullable=True)  # Raison sociale
    siret = Column(String(14), unique=True, nullable=True)  # 14 digits
    vat_number = Column(String(50), nullable=True)  # TVA intracommunautaire
    rcs = Column(String(50), nullable=True)  # RCS number
    legal_form = Column(String(50), nullable=True)  # Forme juridique
    
    # B2C-specific fields
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    birth_date = Column(Date, nullable=True)

    # Relationships
    addresses = relationship("Address", back_populates="customer", cascade="all, delete-orphan")
    contacts = relationship("Contact", back_populates="customer", cascade="all, delete-orphan")
    commercial_conditions = relationship("CommercialConditions", back_populates="customer", uselist=False, cascade="all, delete-orphan")

    @staticmethod
    def _generate_code() -> str:
        """Generate unique customer code in format CLI-XXXXXX."""
        import random
        import string
        from app.infrastructure.db import get_session
        
        # Try to generate a unique code
        max_attempts = 10
        for _ in range(max_attempts):
            suffix = ''.join(random.choices(string.digits, k=6))
            code = f"CLI-{suffix}"
            
            # Check if code exists
            with get_session() as session:
                existing = session.query(Customer).filter_by(code=code).first()
                if not existing:
                    return code
        
        # Fallback: use timestamp-based code
        import time
        timestamp = int(time.time()) % 1000000
        return f"CLI-{timestamp:06d}"

    @staticmethod
    def create(
        type: str,
        name: str,
        email: str,
        code: str = None,
        phone: str = None,
        mobile: str = None,
        category: str = None,
        notes: str = None,
        # B2B fields
        company_name: str = None,
        siret: str = None,
        vat_number: str = None,
        rcs: str = None,
        legal_form: str = None,
        # B2C fields
        first_name: str = None,
        last_name: str = None,
        birth_date: date = None
    ):
        """
        Factory method to create a new Customer.
        
        Args:
            type: Customer type ('B2B' or 'B2C')
            name: Company name (B2B) or Full name (B2C)
            email: Email address (must be unique)
            code: Optional customer code (auto-generated if not provided)
            phone: Phone number
            mobile: Mobile number
            category: Customer category
            notes: Internal notes
            company_name: Company name for B2B (required if type='B2B')
            siret: SIRET number (14 digits) for B2B
            vat_number: VAT number for B2B
            rcs: RCS number for B2B
            legal_form: Legal form for B2B
            first_name: First name for B2C (required if type='B2C')
            last_name: Last name for B2C (required if type='B2C')
            birth_date: Birth date for B2C
            
        Returns:
            Customer instance
            
        Raises:
            ValueError: If validation fails
        """
        if type not in ['B2B', 'B2C']:
            raise ValueError("Customer type must be 'B2B' or 'B2C'.")
        
        if not name or not name.strip():
            raise ValueError("Customer name is required.")
        
        if not email or not email.strip():
            raise ValueError("Customer email is required.")
        
        # Validate email format (basic)
        if '@' not in email:
            raise ValueError("Invalid email format.")
        
        # B2B validation
        if type == 'B2B':
            if not company_name or not company_name.strip():
                raise ValueError("Company name is required for B2B customers.")
            if siret and len(siret.replace(' ', '')) != 14:
                raise ValueError("SIRET must be 14 digits.")
        
        # B2C validation
        if type == 'B2C':
            if not first_name or not first_name.strip():
                raise ValueError("First name is required for B2C customers.")
            if not last_name or not last_name.strip():
                raise ValueError("Last name is required for B2C customers.")
        
        customer = Customer(
            code=code.strip() if code else Customer._generate_code(),
            type=type,
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
            legal_form=legal_form.strip() if legal_form else None,
            first_name=first_name.strip() if first_name else None,
            last_name=last_name.strip() if last_name else None,
            birth_date=birth_date,
            status='active'
        )
        
        # Initialize AggregateRoot
        AggregateRoot.__init__(customer)
        
        # Raise domain event
        customer.raise_domain_event(CustomerCreatedDomainEvent(
            customer_id=0,  # Will be set after save
            customer_code=customer.code,
            customer_name=customer.name
        ))
        
        return customer

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
        legal_form: str = None,
        first_name: str = None,
        last_name: str = None,
        birth_date: date = None
    ):
        """Update customer details."""
        changes = {}
        
        if name is not None:
            if not name.strip():
                raise ValueError("Customer name cannot be empty.")
            if self.name != name.strip():
                changes['name'] = {'old': self.name, 'new': name.strip()}
            self.name = name.strip()
        
        if email is not None:
            if not email.strip() or '@' not in email:
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
        
        # B2B fields
        if company_name is not None:
            if self.type == 'B2B' and not company_name.strip():
                raise ValueError("Company name is required for B2B customers.")
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
        
        # B2C fields
        if first_name is not None:
            if self.type == 'B2C' and not first_name.strip():
                raise ValueError("First name is required for B2C customers.")
            self.first_name = first_name.strip() if first_name else None
        
        if last_name is not None:
            if self.type == 'B2C' and not last_name.strip():
                raise ValueError("Last name is required for B2C customers.")
            self.last_name = last_name.strip() if last_name else None
        
        if birth_date is not None:
            self.birth_date = birth_date
        
        # Raise domain event if there were changes
        if changes:
            self.raise_domain_event(CustomerUpdatedDomainEvent(
                customer_id=self.id,
                customer_code=self.code,
                changes=changes
            ))

    def archive(self):
        """Archive the customer (set status to 'archived')."""
        if self.status != 'archived':
            self.status = 'archived'
            # Raise domain event
            self.raise_domain_event(CustomerArchivedDomainEvent(
                customer_id=self.id,
                customer_code=self.code
            ))

    def activate(self):
        """Activate the customer (set status to 'active')."""
        self.status = 'active'

    def block(self):
        """Block the customer (set status to 'blocked')."""
        self.status = 'blocked'

    def unblock(self):
        """Unblock the customer (set status to 'active')."""
        self.status = 'active'

    def can_delete(self) -> bool:
        """
        Check if customer can be safely deleted.
        
        A customer cannot be deleted if it is referenced in quotes or orders.
        """
        # TODO: Check if referenced in quotes or orders
        # For now, allow deletion if not archived
        return self.status != 'archived'
