from dataclasses import dataclass
from decimal import Decimal
from datetime import date
from typing import List, Optional
from app.application.common.cqrs import Command


@dataclass
class CreateCustomerCommand(Command):
    type: str  # 'B2B' or 'B2C'
    name: str
    email: str
    code: str = None
    phone: str = None
    mobile: str = None
    category: str = None
    notes: str = None
    # B2B fields
    company_name: str = None
    siret: str = None
    vat_number: str = None
    rcs: str = None
    legal_form: str = None
    # B2C fields
    first_name: str = None
    last_name: str = None
    birth_date: date = None
    # Commercial conditions
    payment_terms_days: int = 30
    default_discount_percent: Decimal = Decimal(0)
    credit_limit: Decimal = Decimal(0)
    block_on_credit_exceeded: bool = True


@dataclass
class UpdateCustomerCommand(Command):
    id: int
    name: str = None
    email: str = None
    phone: str = None
    mobile: str = None
    category: str = None
    notes: str = None
    company_name: str = None
    siret: str = None
    vat_number: str = None
    rcs: str = None
    legal_form: str = None
    first_name: str = None
    last_name: str = None
    birth_date: date = None
    # Commercial conditions
    payment_terms_days: int = None
    default_discount_percent: Decimal = None
    credit_limit: Decimal = None
    block_on_credit_exceeded: bool = None
    price_list_id: Optional[int] = None


@dataclass
class ArchiveCustomerCommand(Command):
    id: int


@dataclass
class ActivateCustomerCommand(Command):
    id: int


@dataclass
class DeactivateCustomerCommand(Command):
    id: int


# Address Commands
@dataclass
class CreateAddressCommand(Command):
    customer_id: int
    type: str  # 'billing', 'delivery', 'both'
    street: str
    city: str
    postal_code: str
    country: str = "France"
    state: str = None
    is_default_billing: bool = False
    is_default_delivery: bool = False


@dataclass
class UpdateAddressCommand(Command):
    id: int
    type: str = None
    street: str = None
    city: str = None
    postal_code: str = None
    country: str = None
    state: str = None
    is_default_billing: bool = None
    is_default_delivery: bool = None


@dataclass
class DeleteAddressCommand(Command):
    id: int


# Contact Commands
@dataclass
class CreateContactCommand(Command):
    customer_id: int
    first_name: str
    last_name: str
    function: str = None
    email: str = None
    phone: str = None
    mobile: str = None
    is_primary: bool = False
    receives_quotes: bool = True
    receives_invoices: bool = False
    receives_orders: bool = False


@dataclass
class UpdateContactCommand(Command):
    id: int
    first_name: str = None
    last_name: str = None
    function: str = None
    email: str = None
    phone: str = None
    mobile: str = None
    is_primary: bool = None
    receives_quotes: bool = None
    receives_invoices: bool = None
    receives_orders: bool = None


@dataclass
class DeleteContactCommand(Command):
    id: int