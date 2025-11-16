"""DTOs for purchase queries."""
from dataclasses import dataclass
from decimal import Decimal
from datetime import date
from typing import List, Optional


@dataclass
class SupplierAddressDTO:
    id: int
    supplier_id: int
    type: str
    is_default_billing: bool
    is_default_delivery: bool
    street: str
    city: str
    postal_code: str
    country: str
    state: Optional[str] = None


@dataclass
class SupplierContactDTO:
    id: int
    supplier_id: int
    first_name: str
    last_name: str
    function: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    is_primary: bool = False
    receives_orders: bool = True
    receives_invoices: bool = False


@dataclass
class SupplierConditionsDTO:
    id: int
    supplier_id: int
    payment_terms_days: int
    default_discount_percent: Decimal
    minimum_order_amount: Decimal
    delivery_lead_time_days: int


@dataclass
class SupplierDTO:
    id: int
    code: str
    name: str
    email: str
    phone: Optional[str] = None
    mobile: Optional[str] = None
    category: Optional[str] = None
    status: str = 'active'
    notes: Optional[str] = None
    company_name: Optional[str] = None
    siret: Optional[str] = None
    vat_number: Optional[str] = None
    rcs: Optional[str] = None
    legal_form: Optional[str] = None
    # Relationships
    addresses: List[SupplierAddressDTO] = None
    contacts: List[SupplierContactDTO] = None
    conditions: Optional[SupplierConditionsDTO] = None


@dataclass
class PurchaseOrderLineDTO:
    id: int
    purchase_order_id: int
    product_id: int
    product_code: Optional[str] = None
    product_name: Optional[str] = None
    quantity: Decimal = Decimal(0)
    unit_price: Decimal = Decimal(0)
    discount_percent: Decimal = Decimal(0)
    tax_rate: Decimal = Decimal(20.0)
    line_total_ht: Decimal = Decimal(0)
    line_total_ttc: Decimal = Decimal(0)
    quantity_received: Decimal = Decimal(0)
    sequence: int = 1
    notes: Optional[str] = None


@dataclass
class PurchaseOrderDTO:
    id: int
    number: str
    supplier_id: int
    supplier_code: Optional[str] = None
    supplier_name: Optional[str] = None
    order_date: date = None
    expected_delivery_date: Optional[date] = None
    received_date: Optional[date] = None
    status: str = 'draft'
    subtotal_ht: Decimal = Decimal(0)
    total_tax: Decimal = Decimal(0)
    total_ttc: Decimal = Decimal(0)
    notes: Optional[str] = None
    internal_notes: Optional[str] = None
    created_by: int = 0
    confirmed_by: Optional[int] = None
    confirmed_at: Optional[date] = None
    created_at: Optional[date] = None
    # Relationships
    lines: List[PurchaseOrderLineDTO] = None

