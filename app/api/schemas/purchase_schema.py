"""Marshmallow schemas for purchase API."""
from marshmallow import Schema, fields, validate
from decimal import Decimal


class SupplierAddressCreateSchema(Schema):
    type = fields.Str(required=True, validate=validate.OneOf(['headquarters', 'warehouse', 'billing', 'delivery']))
    street = fields.Str(required=True, validate=validate.Length(max=200))
    city = fields.Str(required=True, validate=validate.Length(max=100))
    postal_code = fields.Str(required=True, validate=validate.Length(max=20))
    country = fields.Str(required=False, load_default='France', validate=validate.Length(max=100))
    state = fields.Str(required=False, allow_none=True, validate=validate.Length(max=100))
    is_default_billing = fields.Bool(required=False, load_default=False)
    is_default_delivery = fields.Bool(required=False, load_default=False)


class SupplierAddressUpdateSchema(Schema):
    type = fields.Str(required=False, validate=validate.OneOf(['headquarters', 'warehouse', 'billing', 'delivery']))
    street = fields.Str(required=False, validate=validate.Length(max=200))
    city = fields.Str(required=False, validate=validate.Length(max=100))
    postal_code = fields.Str(required=False, validate=validate.Length(max=20))
    country = fields.Str(required=False, validate=validate.Length(max=100))
    state = fields.Str(required=False, allow_none=True, validate=validate.Length(max=100))
    is_default_billing = fields.Bool(required=False)
    is_default_delivery = fields.Bool(required=False)


class SupplierAddressSchema(Schema):
    id = fields.Int()
    supplier_id = fields.Int()
    type = fields.Str()
    is_default_billing = fields.Bool()
    is_default_delivery = fields.Bool()
    street = fields.Str()
    city = fields.Str()
    postal_code = fields.Str()
    country = fields.Str()
    state = fields.Str(allow_none=True)


class SupplierContactCreateSchema(Schema):
    first_name = fields.Str(required=True, validate=validate.Length(max=100))
    last_name = fields.Str(required=True, validate=validate.Length(max=100))
    function = fields.Str(required=False, allow_none=True, validate=validate.Length(max=100))
    email = fields.Email(required=False, allow_none=True)
    phone = fields.Str(required=False, allow_none=True, validate=validate.Length(max=20))
    mobile = fields.Str(required=False, allow_none=True, validate=validate.Length(max=20))
    is_primary = fields.Bool(required=False, load_default=False)
    receives_orders = fields.Bool(required=False, load_default=True)
    receives_invoices = fields.Bool(required=False, load_default=False)


class SupplierContactUpdateSchema(Schema):
    first_name = fields.Str(required=False, validate=validate.Length(max=100))
    last_name = fields.Str(required=False, validate=validate.Length(max=100))
    function = fields.Str(required=False, allow_none=True, validate=validate.Length(max=100))
    email = fields.Email(required=False, allow_none=True)
    phone = fields.Str(required=False, allow_none=True, validate=validate.Length(max=20))
    mobile = fields.Str(required=False, allow_none=True, validate=validate.Length(max=20))
    is_primary = fields.Bool(required=False)
    receives_orders = fields.Bool(required=False)
    receives_invoices = fields.Bool(required=False)


class SupplierContactSchema(Schema):
    id = fields.Int()
    supplier_id = fields.Int()
    first_name = fields.Str()
    last_name = fields.Str()
    function = fields.Str(allow_none=True)
    email = fields.Email(allow_none=True)
    phone = fields.Str(allow_none=True)
    mobile = fields.Str(allow_none=True)
    is_primary = fields.Bool()
    receives_orders = fields.Bool()
    receives_invoices = fields.Bool()


class SupplierConditionsSchema(Schema):
    id = fields.Int()
    supplier_id = fields.Int()
    payment_terms_days = fields.Int()
    default_discount_percent = fields.Decimal(as_string=True)
    minimum_order_amount = fields.Decimal(as_string=True)
    delivery_lead_time_days = fields.Int()


class SupplierCreateSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(max=200))
    email = fields.Email(required=True)
    code = fields.Str(required=False, allow_none=True, validate=validate.Length(max=50))
    phone = fields.Str(required=False, allow_none=True, validate=validate.Length(max=20))
    mobile = fields.Str(required=False, allow_none=True, validate=validate.Length(max=20))
    category = fields.Str(required=False, allow_none=True, validate=validate.Length(max=50))
    notes = fields.Str(required=False, allow_none=True)
    company_name = fields.Str(required=False, allow_none=True, validate=validate.Length(max=200))
    siret = fields.Str(required=False, allow_none=True, validate=validate.Length(equal=14))
    vat_number = fields.Str(required=False, allow_none=True, validate=validate.Length(max=50))
    rcs = fields.Str(required=False, allow_none=True, validate=validate.Length(max=50))
    legal_form = fields.Str(required=False, allow_none=True, validate=validate.Length(max=50))
    payment_terms_days = fields.Int(required=False, load_default=30)
    default_discount_percent = fields.Decimal(required=False, load_default=Decimal(0), as_string=True)
    minimum_order_amount = fields.Decimal(required=False, load_default=Decimal(0), as_string=True)
    delivery_lead_time_days = fields.Int(required=False, load_default=7)


class SupplierUpdateSchema(Schema):
    name = fields.Str(required=False, validate=validate.Length(max=200))
    email = fields.Email(required=False)
    phone = fields.Str(required=False, allow_none=True, validate=validate.Length(max=20))
    mobile = fields.Str(required=False, allow_none=True, validate=validate.Length(max=20))
    category = fields.Str(required=False, allow_none=True, validate=validate.Length(max=50))
    notes = fields.Str(required=False, allow_none=True)
    company_name = fields.Str(required=False, allow_none=True, validate=validate.Length(max=200))
    siret = fields.Str(required=False, allow_none=True, validate=validate.Length(equal=14))
    vat_number = fields.Str(required=False, allow_none=True, validate=validate.Length(max=50))
    rcs = fields.Str(required=False, allow_none=True, validate=validate.Length(max=50))
    legal_form = fields.Str(required=False, allow_none=True, validate=validate.Length(max=50))


class SupplierSchema(Schema):
    id = fields.Int()
    code = fields.Str()
    name = fields.Str()
    email = fields.Email()
    phone = fields.Str(allow_none=True)
    mobile = fields.Str(allow_none=True)
    category = fields.Str(allow_none=True)
    status = fields.Str()
    notes = fields.Str(allow_none=True)
    company_name = fields.Str(allow_none=True)
    siret = fields.Str(allow_none=True)
    vat_number = fields.Str(allow_none=True)
    rcs = fields.Str(allow_none=True)
    legal_form = fields.Str(allow_none=True)
    addresses = fields.List(fields.Nested(SupplierAddressSchema), dump_only=True)
    contacts = fields.List(fields.Nested(SupplierContactSchema), dump_only=True)
    conditions = fields.Nested(SupplierConditionsSchema, dump_only=True)


class PurchaseOrderLineCreateSchema(Schema):
    product_id = fields.Int(required=True)
    quantity = fields.Decimal(required=True, as_string=True)
    unit_price = fields.Decimal(required=True, as_string=True)
    discount_percent = fields.Decimal(required=False, load_default=Decimal(0), as_string=True)
    tax_rate = fields.Decimal(required=False, load_default=Decimal(20.0), as_string=True)
    notes = fields.Str(required=False, allow_none=True)


class PurchaseOrderLineUpdateSchema(Schema):
    quantity = fields.Decimal(required=False, as_string=True)
    unit_price = fields.Decimal(required=False, as_string=True)
    discount_percent = fields.Decimal(required=False, as_string=True)
    notes = fields.Str(required=False, allow_none=True)


class PurchaseOrderLineSchema(Schema):
    id = fields.Int()
    purchase_order_id = fields.Int()
    product_id = fields.Int()
    product_code = fields.Str(allow_none=True)
    product_name = fields.Str(allow_none=True)
    quantity = fields.Decimal(as_string=True)
    unit_price = fields.Decimal(as_string=True)
    discount_percent = fields.Decimal(as_string=True)
    tax_rate = fields.Decimal(as_string=True)
    line_total_ht = fields.Decimal(as_string=True)
    line_total_ttc = fields.Decimal(as_string=True)
    quantity_received = fields.Decimal(as_string=True)
    sequence = fields.Int()
    notes = fields.Str(allow_none=True)


class PurchaseOrderCreateSchema(Schema):
    supplier_id = fields.Int(required=True)
    number = fields.Str(required=False, allow_none=True, validate=validate.Length(max=50))
    order_date = fields.Date(required=False, allow_none=True)
    expected_delivery_date = fields.Date(required=False, allow_none=True)
    notes = fields.Str(required=False, allow_none=True)
    internal_notes = fields.Str(required=False, allow_none=True)


class PurchaseOrderUpdateSchema(Schema):
    expected_delivery_date = fields.Date(required=False, allow_none=True)
    notes = fields.Str(required=False, allow_none=True)
    internal_notes = fields.Str(required=False, allow_none=True)


class PurchaseOrderSchema(Schema):
    id = fields.Int()
    number = fields.Str()
    supplier_id = fields.Int()
    supplier_code = fields.Str(allow_none=True)
    supplier_name = fields.Str(allow_none=True)
    order_date = fields.Date()
    expected_delivery_date = fields.Date(allow_none=True)
    received_date = fields.Date(allow_none=True)
    status = fields.Str()
    subtotal_ht = fields.Decimal(as_string=True)
    total_tax = fields.Decimal(as_string=True)
    total_ttc = fields.Decimal(as_string=True)
    notes = fields.Str(allow_none=True)
    internal_notes = fields.Str(allow_none=True)
    created_by = fields.Int()
    confirmed_by = fields.Int(allow_none=True)
    confirmed_at = fields.DateTime(allow_none=True)
    created_at = fields.DateTime(allow_none=True)
    lines = fields.List(fields.Nested(PurchaseOrderLineSchema), dump_only=True)

