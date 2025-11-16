"""Purchase commands for CQRS pattern."""
from dataclasses import dataclass
from decimal import Decimal
from datetime import date
from typing import List, Optional
from app.application.common.cqrs import Command


# Supplier Commands
@dataclass
class CreateSupplierCommand(Command):
    name: str
    email: str
    code: str = None
    phone: str = None
    mobile: str = None
    category: str = None
    notes: str = None
    company_name: str = None
    siret: str = None
    vat_number: str = None
    rcs: str = None
    legal_form: str = None
    payment_terms_days: int = 30
    default_discount_percent: Decimal = Decimal(0)
    minimum_order_amount: Decimal = Decimal(0)
    delivery_lead_time_days: int = 7


@dataclass
class UpdateSupplierCommand(Command):
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


@dataclass
class ArchiveSupplierCommand(Command):
    id: int


@dataclass
class ActivateSupplierCommand(Command):
    id: int


@dataclass
class DeactivateSupplierCommand(Command):
    id: int


# Supplier Address Commands
@dataclass
class CreateSupplierAddressCommand(Command):
    supplier_id: int
    type: str  # 'headquarters', 'warehouse', 'billing', 'delivery'
    street: str
    city: str
    postal_code: str
    country: str = "France"
    state: str = None
    is_default_billing: bool = False
    is_default_delivery: bool = False


@dataclass
class UpdateSupplierAddressCommand(Command):
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
class DeleteSupplierAddressCommand(Command):
    id: int


# Supplier Contact Commands
@dataclass
class CreateSupplierContactCommand(Command):
    supplier_id: int
    first_name: str
    last_name: str
    function: str = None
    email: str = None
    phone: str = None
    mobile: str = None
    is_primary: bool = False
    receives_orders: bool = True
    receives_invoices: bool = False


@dataclass
class UpdateSupplierContactCommand(Command):
    id: int
    first_name: str = None
    last_name: str = None
    function: str = None
    email: str = None
    phone: str = None
    mobile: str = None
    is_primary: bool = None
    receives_orders: bool = None
    receives_invoices: bool = None


@dataclass
class DeleteSupplierContactCommand(Command):
    id: int


# Purchase Order Commands
@dataclass
class CreatePurchaseOrderCommand(Command):
    supplier_id: int
    created_by: int
    number: str = None
    order_date: date = None
    expected_delivery_date: date = None
    notes: str = None
    internal_notes: str = None


@dataclass
class UpdatePurchaseOrderCommand(Command):
    id: int
    expected_delivery_date: date = None
    notes: str = None
    internal_notes: str = None


@dataclass
class ConfirmPurchaseOrderCommand(Command):
    id: int
    confirmed_by: int


@dataclass
class CancelPurchaseOrderCommand(Command):
    id: int


@dataclass
class AddPurchaseOrderLineCommand(Command):
    purchase_order_id: int
    product_id: int
    quantity: Decimal
    unit_price: Decimal
    discount_percent: Decimal = Decimal(0)
    tax_rate: Decimal = Decimal(20.0)
    notes: str = None


@dataclass
class UpdatePurchaseOrderLineCommand(Command):
    purchase_order_id: int
    line_id: int
    quantity: Decimal = None
    unit_price: Decimal = None
    discount_percent: Decimal = None
    notes: str = None


@dataclass
class RemovePurchaseOrderLineCommand(Command):
    purchase_order_id: int
    line_id: int


@dataclass
class ReceivePurchaseOrderLineCommand(Command):
    """Command to mark a purchase order line as received (updates quantity_received)."""
    purchase_order_id: int
    line_id: int
    quantity_received: Decimal
    location_id: int = None  # Optional: specify location for stock entry

