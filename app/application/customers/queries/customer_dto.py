"""DTOs for customer queries."""
from dataclasses import dataclass
from decimal import Decimal
from datetime import date
from typing import List, Optional


@dataclass
class AddressDTO:
    id: int
    customer_id: int
    type: str
    is_default_billing: bool
    is_default_delivery: bool
    street: str
    city: str
    postal_code: str
    country: str
    state: Optional[str] = None


@dataclass
class ContactDTO:
    id: int
    customer_id: int
    first_name: str
    last_name: str
    function: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    is_primary: bool = False
    receives_quotes: bool = True
    receives_invoices: bool = False
    receives_orders: bool = False


@dataclass
class CommercialConditionsDTO:
    id: int
    customer_id: int
    payment_terms_days: int
    default_discount_percent: Decimal
    credit_limit: Decimal
    block_on_credit_exceeded: bool


@dataclass
class CustomerDTO:
    id: int
    code: str
    type: str
    name: str
    email: str
    phone: Optional[str] = None
    mobile: Optional[str] = None
    category: Optional[str] = None
    status: str = 'active'
    notes: Optional[str] = None
    # B2B fields
    company_name: Optional[str] = None
    siret: Optional[str] = None
    vat_number: Optional[str] = None
    rcs: Optional[str] = None
    legal_form: Optional[str] = None
    # B2C fields
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    birth_date: Optional[date] = None
    # Relationships
    addresses: List[AddressDTO] = None
    contacts: List[ContactDTO] = None
    commercial_conditions: Optional[CommercialConditionsDTO] = None
