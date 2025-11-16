from marshmallow import Schema, fields, validate
from typing import List


class ProductCreateSchema(Schema):
    code = fields.Str(required=True, validate=validate.Length(max=50))
    name = fields.Str(required=True, validate=validate.Length(max=200))
    description = fields.Str(required=False, allow_none=True)
    price = fields.Decimal(required=True)
    cost = fields.Decimal(required=False, allow_none=True)
    unit_of_measure = fields.Str(required=False, allow_none=True, validate=validate.Length(max=20))
    barcode = fields.Str(required=False, allow_none=True, validate=validate.Length(max=50))
    category_ids = fields.List(fields.Int(), required=True, validate=validate.Length(min=1))


class ProductUpdateSchema(Schema):
    name = fields.Str(required=False, validate=validate.Length(max=200))
    description = fields.Str(required=False, allow_none=True)
    price = fields.Decimal(required=False)
    cost = fields.Decimal(required=False, allow_none=True)
    unit_of_measure = fields.Str(required=False, allow_none=True, validate=validate.Length(max=20))
    barcode = fields.Str(required=False, allow_none=True, validate=validate.Length(max=50))
    category_ids = fields.List(fields.Int(), required=False)


class ProductSchema(Schema):
    id = fields.Int()
    code = fields.Str()
    name = fields.Str()
    description = fields.Str(allow_none=True)
    price = fields.Decimal()
    cost = fields.Decimal(allow_none=True)
    unit_of_measure = fields.Str(allow_none=True)
    barcode = fields.Str(allow_none=True)
    status = fields.Str()
    category_ids = fields.List(fields.Int(), allow_none=True)
    categories = fields.List(fields.Dict(), allow_none=True)


class CategoryCreateSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(max=100))
    code = fields.Str(required=False, allow_none=True, validate=validate.Length(max=50))
    parent_id = fields.Int(required=False, allow_none=True)
    description = fields.Str(required=False, allow_none=True)


class CategoryUpdateSchema(Schema):
    name = fields.Str(required=False, validate=validate.Length(max=100))
    code = fields.Str(required=False, allow_none=True, validate=validate.Length(max=50))
    description = fields.Str(required=False, allow_none=True)


class CategorySchema(Schema):
    id = fields.Int()
    name = fields.Str()
    code = fields.Str(allow_none=True)
    parent_id = fields.Int(allow_none=True)
    description = fields.Str(allow_none=True)