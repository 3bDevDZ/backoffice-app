"""Marshmallow schemas for customer API."""
from marshmallow import Schema, fields, validate
from typing import List


class AddressCreateSchema(Schema):
    type = fields.Str(required=True, validate=validate.OneOf(['billing', 'delivery', 'both']))
    street = fields.Str(required=True, validate=validate.Length(max=200))
    city = fields.Str(required=True, validate=validate.Length(max=100))
    postal_code = fields.Str(required=True, validate=validate.Length(max=20))
    country = fields.Str(required=False, load_default='France', validate=validate.Length(max=100))
    state = fields.Str(required=False, allow_none=True, validate=validate.Length(max=100))
    is_default_billing = fields.Bool(required=False, load_default=False)
    is_default_delivery = fields.Bool(required=False, load_default=False)


class AddressUpdateSchema(Schema):
    type = fields.Str(required=False, validate=validate.OneOf(['billing', 'delivery', 'both']))
    street = fields.Str(required=False, validate=validate.Length(max=200))
    city = fields.Str(required=False, validate=validate.Length(max=100))
    postal_code = fields.Str(required=False, validate=validate.Length(max=20))
    country = fields.Str(required=False, validate=validate.Length(max=100))
    state = fields.Str(required=False, allow_none=True, validate=validate.Length(max=100))
    is_default_billing = fields.Bool(required=False)
    is_default_delivery = fields.Bool(required=False)


class AddressSchema(Schema):
    id = fields.Int()
    customer_id = fields.Int()
    type = fields.Str()
    is_default_billing = fields.Bool()
    is_default_delivery = fields.Bool()
    street = fields.Str()
    city = fields.Str()
    postal_code = fields.Str()
    country = fields.Str()
    state = fields.Str(allow_none=True)


class ContactCreateSchema(Schema):
    first_name = fields.Str(required=True, validate=validate.Length(max=100))
    last_name = fields.Str(required=True, validate=validate.Length(max=100))
    function = fields.Str(required=False, allow_none=True, validate=validate.Length(max=100))
    email = fields.Email(required=False, allow_none=True)
    phone = fields.Str(required=False, allow_none=True, validate=validate.Length(max=20))
    mobile = fields.Str(required=False, allow_none=True, validate=validate.Length(max=20))
    is_primary = fields.Bool(required=False, load_default=False)
    receives_quotes = fields.Bool(required=False, load_default=True)
    receives_invoices = fields.Bool(required=False, load_default=False)
    receives_orders = fields.Bool(required=False, load_default=False)


class ContactUpdateSchema(Schema):
    first_name = fields.Str(required=False, validate=validate.Length(max=100))
    last_name = fields.Str(required=False, validate=validate.Length(max=100))
    function = fields.Str(required=False, allow_none=True, validate=validate.Length(max=100))
    email = fields.Email(required=False, allow_none=True)
    phone = fields.Str(required=False, allow_none=True, validate=validate.Length(max=20))
    mobile = fields.Str(required=False, allow_none=True, validate=validate.Length(max=20))
    is_primary = fields.Bool(required=False)
    receives_quotes = fields.Bool(required=False)
    receives_invoices = fields.Bool(required=False)
    receives_orders = fields.Bool(required=False)


class ContactSchema(Schema):
    id = fields.Int()
    customer_id = fields.Int()
    first_name = fields.Str()
    last_name = fields.Str()
    function = fields.Str(allow_none=True)
    email = fields.Email(allow_none=True)
    phone = fields.Str(allow_none=True)
    mobile = fields.Str(allow_none=True)
    is_primary = fields.Bool()
    receives_quotes = fields.Bool()
    receives_invoices = fields.Bool()
    receives_orders = fields.Bool()


class CommercialConditionsSchema(Schema):
    id = fields.Int()
    customer_id = fields.Int()
    payment_terms_days = fields.Int()
    default_discount_percent = fields.Decimal()
    credit_limit = fields.Decimal()
    block_on_credit_exceeded = fields.Bool()


class CustomerCreateSchema(Schema):
    type = fields.Str(required=True, validate=validate.OneOf(['B2B', 'B2C']))
    name = fields.Str(required=True, validate=validate.Length(max=200))
    email = fields.Email(required=True)
    code = fields.Str(required=False, allow_none=True, validate=validate.Length(max=50))
    phone = fields.Str(required=False, allow_none=True, validate=validate.Length(max=20))
    mobile = fields.Str(required=False, allow_none=True, validate=validate.Length(max=20))
    category = fields.Str(required=False, allow_none=True, validate=validate.Length(max=50))
    notes = fields.Str(required=False, allow_none=True)
    # B2B fields
    company_name = fields.Str(required=False, allow_none=True, validate=validate.Length(max=200))
    siret = fields.Str(required=False, allow_none=True, validate=validate.Length(max=14))
    vat_number = fields.Str(required=False, allow_none=True, validate=validate.Length(max=50))
    rcs = fields.Str(required=False, allow_none=True, validate=validate.Length(max=50))
    legal_form = fields.Str(required=False, allow_none=True, validate=validate.Length(max=50))
    # B2C fields
    first_name = fields.Str(required=False, allow_none=True, validate=validate.Length(max=100))
    last_name = fields.Str(required=False, allow_none=True, validate=validate.Length(max=100))
    birth_date = fields.Date(required=False, allow_none=True)
    # Commercial conditions
    payment_terms_days = fields.Int(required=False, load_default=30)
    default_discount_percent = fields.Decimal(required=False, load_default=0)
    credit_limit = fields.Decimal(required=False, load_default=0)
    block_on_credit_exceeded = fields.Bool(required=False, load_default=True)


class CustomerUpdateSchema(Schema):
    name = fields.Str(required=False, validate=validate.Length(max=200))
    email = fields.Email(required=False)
    phone = fields.Str(required=False, allow_none=True, validate=validate.Length(max=20))
    mobile = fields.Str(required=False, allow_none=True, validate=validate.Length(max=20))
    category = fields.Str(required=False, allow_none=True, validate=validate.Length(max=50))
    notes = fields.Str(required=False, allow_none=True)
    company_name = fields.Str(required=False, allow_none=True, validate=validate.Length(max=200))
    siret = fields.Str(required=False, allow_none=True, validate=validate.Length(max=14))
    vat_number = fields.Str(required=False, allow_none=True, validate=validate.Length(max=50))
    rcs = fields.Str(required=False, allow_none=True, validate=validate.Length(max=50))
    legal_form = fields.Str(required=False, allow_none=True, validate=validate.Length(max=50))
    first_name = fields.Str(required=False, allow_none=True, validate=validate.Length(max=100))
    last_name = fields.Str(required=False, allow_none=True, validate=validate.Length(max=100))
    birth_date = fields.Date(required=False, allow_none=True)


class CustomerSchema(Schema):
    id = fields.Int()
    code = fields.Str()
    type = fields.Str()
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
    first_name = fields.Str(allow_none=True)
    last_name = fields.Str(allow_none=True)
    birth_date = fields.Date(allow_none=True)
    addresses = fields.List(fields.Nested(AddressSchema), allow_none=True)
    contacts = fields.List(fields.Nested(ContactSchema), allow_none=True)
    commercial_conditions = fields.Nested(CommercialConditionsSchema, allow_none=True)
