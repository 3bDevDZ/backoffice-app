"""Purchase API endpoints."""
from flask import Blueprint, request
from flask_babel import get_locale, gettext as _
from app.application.common.mediator import mediator
from app.application.purchases.commands.commands import (
    CreateSupplierCommand, UpdateSupplierCommand, ArchiveSupplierCommand,
    ActivateSupplierCommand, DeactivateSupplierCommand,
    CreateSupplierAddressCommand, UpdateSupplierAddressCommand, DeleteSupplierAddressCommand,
    CreateSupplierContactCommand, UpdateSupplierContactCommand, DeleteSupplierContactCommand,
    CreatePurchaseOrderCommand, UpdatePurchaseOrderCommand, ConfirmPurchaseOrderCommand,
    CancelPurchaseOrderCommand, AddPurchaseOrderLineCommand, UpdatePurchaseOrderLineCommand,
    RemovePurchaseOrderLineCommand
)
from app.application.purchases.queries.queries import (
    GetSupplierByIdQuery, ListSuppliersQuery, SearchSuppliersQuery,
    GetPurchaseOrderByIdQuery, ListPurchaseOrdersQuery
)
from app.api.schemas.purchase_schema import (
    SupplierCreateSchema, SupplierUpdateSchema, SupplierSchema,
    SupplierAddressCreateSchema, SupplierAddressUpdateSchema, SupplierAddressSchema,
    SupplierContactCreateSchema, SupplierContactUpdateSchema, SupplierContactSchema,
    PurchaseOrderCreateSchema, PurchaseOrderUpdateSchema, PurchaseOrderSchema,
    PurchaseOrderLineCreateSchema, PurchaseOrderLineUpdateSchema, PurchaseOrderLineSchema
)
from app.security.rbac import require_roles
from app.utils.response import success_response, error_response, paginated_response
from flask_jwt_extended import get_jwt_identity

purchases_bp = Blueprint("purchases", __name__)


# Helper to convert SupplierDTO to dict
def _supplier_dto_to_dict(supplier_dto):
    return {
        'id': supplier_dto.id,
        'code': supplier_dto.code,
        'name': supplier_dto.name,
        'email': supplier_dto.email,
        'phone': supplier_dto.phone,
        'mobile': supplier_dto.mobile,
        'category': supplier_dto.category,
        'status': supplier_dto.status,
        'notes': supplier_dto.notes,
        'company_name': supplier_dto.company_name,
        'siret': supplier_dto.siret,
        'vat_number': supplier_dto.vat_number,
        'rcs': supplier_dto.rcs,
        'legal_form': supplier_dto.legal_form,
        'addresses': [
            {
                'id': a.id, 'supplier_id': a.supplier_id, 'type': a.type,
                'is_default_billing': a.is_default_billing, 'is_default_delivery': a.is_default_delivery,
                'street': a.street, 'city': a.city, 'postal_code': a.postal_code,
                'country': a.country, 'state': a.state
            }
            for a in (supplier_dto.addresses or [])
        ],
        'contacts': [
            {
                'id': c.id, 'supplier_id': c.supplier_id, 'first_name': c.first_name,
                'last_name': c.last_name, 'function': c.function, 'email': c.email,
                'phone': c.phone, 'mobile': c.mobile, 'is_primary': c.is_primary,
                'receives_orders': c.receives_orders, 'receives_invoices': c.receives_invoices
            }
            for c in (supplier_dto.contacts or [])
        ],
        'conditions': {
            'id': supplier_dto.conditions.id,
            'supplier_id': supplier_dto.conditions.supplier_id,
            'payment_terms_days': supplier_dto.conditions.payment_terms_days,
            'default_discount_percent': float(supplier_dto.conditions.default_discount_percent),
            'minimum_order_amount': float(supplier_dto.conditions.minimum_order_amount),
            'delivery_lead_time_days': supplier_dto.conditions.delivery_lead_time_days
        } if supplier_dto.conditions else None
    }


# Supplier Endpoints
@purchases_bp.get("/suppliers")
@require_roles("admin", "commercial", "direction")
def list_suppliers():
    """List suppliers with pagination, search, and filters."""
    try:
        page = int(request.args.get("page", 1))
        per_page = min(int(request.args.get("page_size", 20)), 100)
        search = request.args.get("search")
        status = request.args.get("status")
        category = request.args.get("category")
        
        query = ListSuppliersQuery(
            page=page,
            per_page=per_page,
            search=search,
            status=status,
            category=category
        )
        suppliers = mediator.dispatch(query)
        
        suppliers_data = [_supplier_dto_to_dict(s) for s in suppliers]
        
        total = len(suppliers_data)  # Simplified - should query total count
        return paginated_response(
            items=suppliers_data,
            total=total,
            page=page,
            page_size=per_page
        )
    except Exception as e:
        return error_response(_(str(e)), status_code=400)


@purchases_bp.get("/suppliers/<int:supplier_id>")
@require_roles("admin", "commercial", "direction")
def get_supplier(supplier_id: int):
    """Get supplier by ID."""
    try:
        supplier_dto = mediator.dispatch(GetSupplierByIdQuery(id=supplier_id))
        return success_response(_supplier_dto_to_dict(supplier_dto))
    except ValueError as e:
        return error_response(_('Supplier not found'), status_code=404)
    except Exception as e:
        return error_response(_(str(e)), status_code=400)


@purchases_bp.post("/suppliers")
@require_roles("admin", "commercial")
def create_supplier():
    """Create a new supplier."""
    try:
        data = SupplierCreateSchema().load(request.get_json() or {})
        data.pop('locale', None)
        
        command = CreateSupplierCommand(**data)
        supplier = mediator.dispatch(command)
        
        supplier_dto = mediator.dispatch(GetSupplierByIdQuery(id=supplier.id))
        return success_response(_supplier_dto_to_dict(supplier_dto), message=_('Supplier created successfully'), status_code=201)
    except ValueError as e:
        return error_response(_(str(e)), status_code=400)
    except Exception as e:
        return error_response(_('Failed to create supplier: {}').format(str(e)), status_code=500)


@purchases_bp.put("/suppliers/<int:supplier_id>")
@require_roles("admin", "commercial")
def update_supplier(supplier_id: int):
    """Update a supplier."""
    try:
        data = SupplierUpdateSchema().load(request.get_json() or {})
        data.pop('locale', None)
        
        command = UpdateSupplierCommand(id=supplier_id, **data)
        supplier = mediator.dispatch(command)
        
        supplier_dto = mediator.dispatch(GetSupplierByIdQuery(id=supplier_id))
        return success_response(_supplier_dto_to_dict(supplier_dto), message=_('Supplier updated successfully'))
    except ValueError as e:
        return error_response(_('Supplier not found'), status_code=404)
    except Exception as e:
        return error_response(_(str(e)), status_code=400)


@purchases_bp.post("/suppliers/<int:supplier_id>/archive")
@require_roles("admin")
def archive_supplier(supplier_id: int):
    """Archive a supplier."""
    try:
        command = ArchiveSupplierCommand(id=supplier_id)
        mediator.dispatch(command)
        return success_response(None, message=_('Supplier archived successfully'))
    except ValueError as e:
        return error_response(_('Supplier not found'), status_code=404)
    except Exception as e:
        return error_response(_(str(e)), status_code=400)


@purchases_bp.post("/suppliers/<int:supplier_id>/activate")
@require_roles("admin", "commercial")
def activate_supplier(supplier_id: int):
    """Activate a supplier."""
    try:
        command = ActivateSupplierCommand(id=supplier_id)
        mediator.dispatch(command)
        return success_response(None, message=_('Supplier activated successfully'))
    except ValueError as e:
        return error_response(_('Supplier not found'), status_code=404)
    except Exception as e:
        return error_response(_(str(e)), status_code=400)


@purchases_bp.post("/suppliers/<int:supplier_id>/deactivate")
@require_roles("admin", "commercial")
def deactivate_supplier(supplier_id: int):
    """Deactivate a supplier."""
    try:
        command = DeactivateSupplierCommand(id=supplier_id)
        mediator.dispatch(command)
        return success_response(None, message=_('Supplier deactivated successfully'))
    except ValueError as e:
        return error_response(_('Supplier not found'), status_code=404)
    except Exception as e:
        return error_response(_(str(e)), status_code=400)


# Purchase Order Endpoints
@purchases_bp.get("/purchase-orders")
@require_roles("admin", "commercial", "direction")
def list_purchase_orders():
    """List purchase orders with pagination and filters."""
    try:
        page = int(request.args.get("page", 1))
        per_page = min(int(request.args.get("page_size", 20)), 100)
        supplier_id = request.args.get("supplier_id", type=int)
        status = request.args.get("status")
        search = request.args.get("search")
        
        query = ListPurchaseOrdersQuery(
            page=page,
            per_page=per_page,
            supplier_id=supplier_id,
            status=status,
            search=search
        )
        orders = mediator.dispatch(query)
        
        orders_data = []
        for o in orders:
            orders_data.append({
                'id': o.id,
                'number': o.number,
                'supplier_id': o.supplier_id,
                'supplier_code': o.supplier_code,
                'supplier_name': o.supplier_name,
                'order_date': str(o.order_date) if o.order_date else None,
                'expected_delivery_date': str(o.expected_delivery_date) if o.expected_delivery_date else None,
                'received_date': str(o.received_date) if o.received_date else None,
                'status': o.status,
                'subtotal_ht': float(o.subtotal_ht),
                'total_tax': float(o.total_tax),
                'total_ttc': float(o.total_ttc),
                'notes': o.notes,
                'internal_notes': o.internal_notes,
                'created_by': o.created_by,
                'confirmed_by': o.confirmed_by,
                'confirmed_at': str(o.confirmed_at) if o.confirmed_at else None,
                'created_at': str(o.created_at) if o.created_at else None
            })
        
        total = len(orders_data)  # Simplified
        return paginated_response(
            items=orders_data,
            total=total,
            page=page,
            page_size=per_page
        )
    except Exception as e:
        return error_response(_(str(e)), status_code=400)


@purchases_bp.get("/purchase-orders/<int:order_id>")
@require_roles("admin", "commercial", "direction")
def get_purchase_order(order_id: int):
    """Get purchase order by ID."""
    try:
        order_dto = mediator.dispatch(GetPurchaseOrderByIdQuery(id=order_id))
        
        order_dict = {
            'id': order_dto.id,
            'number': order_dto.number,
            'supplier_id': order_dto.supplier_id,
            'supplier_code': order_dto.supplier_code,
            'supplier_name': order_dto.supplier_name,
            'order_date': str(order_dto.order_date) if order_dto.order_date else None,
            'expected_delivery_date': str(order_dto.expected_delivery_date) if order_dto.expected_delivery_date else None,
            'received_date': str(order_dto.received_date) if order_dto.received_date else None,
            'status': order_dto.status,
            'subtotal_ht': float(order_dto.subtotal_ht),
            'total_tax': float(order_dto.total_tax),
            'total_ttc': float(order_dto.total_ttc),
            'notes': order_dto.notes,
            'internal_notes': order_dto.internal_notes,
            'created_by': order_dto.created_by,
            'confirmed_by': order_dto.confirmed_by,
            'confirmed_at': str(order_dto.confirmed_at) if order_dto.confirmed_at else None,
            'created_at': str(order_dto.created_at) if order_dto.created_at else None,
            'lines': [
                {
                    'id': l.id,
                    'purchase_order_id': l.purchase_order_id,
                    'product_id': l.product_id,
                    'product_code': l.product_code,
                    'product_name': l.product_name,
                    'quantity': float(l.quantity),
                    'unit_price': float(l.unit_price),
                    'discount_percent': float(l.discount_percent),
                    'tax_rate': float(l.tax_rate),
                    'line_total_ht': float(l.line_total_ht),
                    'line_total_ttc': float(l.line_total_ttc),
                    'quantity_received': float(l.quantity_received),
                    'sequence': l.sequence,
                    'notes': l.notes
                }
                for l in (order_dto.lines or [])
            ]
        }
        
        return success_response(order_dict)
    except ValueError as e:
        return error_response(_('Purchase order not found'), status_code=404)
    except Exception as e:
        return error_response(_(str(e)), status_code=400)


@purchases_bp.post("/purchase-orders")
@require_roles("admin", "commercial")
def create_purchase_order():
    """Create a new purchase order."""
    try:
        data = PurchaseOrderCreateSchema().load(request.get_json() or {})
        data.pop('locale', None)
        
        # Get current user ID from JWT
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return error_response(_('Authentication required'), status_code=401)
        
        # Convert to int if string
        if isinstance(current_user_id, str):
            current_user_id = int(current_user_id)
        
        command = CreatePurchaseOrderCommand(created_by=current_user_id, **data)
        order = mediator.dispatch(command)
        
        order_dto = mediator.dispatch(GetPurchaseOrderByIdQuery(id=order.id))
        order_dict = {
            'id': order_dto.id,
            'number': order_dto.number,
            'supplier_id': order_dto.supplier_id,
            'status': order_dto.status,
            'subtotal_ht': float(order_dto.subtotal_ht),
            'total_tax': float(order_dto.total_tax),
            'total_ttc': float(order_dto.total_ttc)
        }
        
        return success_response(order_dict, message=_('Purchase order created successfully'), status_code=201)
    except ValueError as e:
        return error_response(_(str(e)), status_code=400)
    except Exception as e:
        return error_response(_('Failed to create purchase order: {}').format(str(e)), status_code=500)


@purchases_bp.put("/purchase-orders/<int:order_id>")
@require_roles("admin", "commercial")
def update_purchase_order(order_id: int):
    """Update a purchase order."""
    try:
        data = PurchaseOrderUpdateSchema().load(request.get_json() or {})
        data.pop('locale', None)
        
        command = UpdatePurchaseOrderCommand(id=order_id, **data)
        mediator.dispatch(command)
        
        order_dto = mediator.dispatch(GetPurchaseOrderByIdQuery(id=order_id))
        return success_response(None, message=_('Purchase order updated successfully'))
    except ValueError as e:
        return error_response(_('Purchase order not found'), status_code=404)
    except Exception as e:
        return error_response(_(str(e)), status_code=400)


@purchases_bp.post("/purchase-orders/<int:order_id>/confirm")
@require_roles("admin", "commercial")
def confirm_purchase_order(order_id: int):
    """Confirm a purchase order."""
    try:
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return error_response(_('Authentication required'), status_code=401)
        
        # Convert to int if string
        if isinstance(current_user_id, str):
            current_user_id = int(current_user_id)
        
        command = ConfirmPurchaseOrderCommand(id=order_id, confirmed_by=current_user_id)
        mediator.dispatch(command)
        return success_response(None, message=_('Purchase order confirmed successfully'))
    except ValueError as e:
        return error_response(_(str(e)), status_code=400)
    except Exception as e:
        return error_response(_('Failed to confirm purchase order: {}').format(str(e)), status_code=500)


@purchases_bp.post("/purchase-orders/<int:order_id>/cancel")
@require_roles("admin", "commercial")
def cancel_purchase_order(order_id: int):
    """Cancel a purchase order."""
    try:
        command = CancelPurchaseOrderCommand(id=order_id)
        mediator.dispatch(command)
        return success_response(None, message=_('Purchase order cancelled successfully'))
    except ValueError as e:
        return error_response(_(str(e)), status_code=400)
    except Exception as e:
        return error_response(_('Failed to cancel purchase order: {}').format(str(e)), status_code=500)


@purchases_bp.post("/purchase-orders/<int:order_id>/lines")
@require_roles("admin", "commercial")
def add_purchase_order_line(order_id: int):
    """Add a line to a purchase order."""
    try:
        data = PurchaseOrderLineCreateSchema().load(request.get_json() or {})
        data.pop('locale', None)
        
        command = AddPurchaseOrderLineCommand(purchase_order_id=order_id, **data)
        line = mediator.dispatch(command)
        
        return success_response({'id': line.id}, message=_('Line added successfully'), status_code=201)
    except ValueError as e:
        return error_response(_(str(e)), status_code=400)
    except Exception as e:
        return error_response(_('Failed to add line: {}').format(str(e)), status_code=500)


@purchases_bp.put("/purchase-orders/<int:order_id>/lines/<int:line_id>")
@require_roles("admin", "commercial")
def update_purchase_order_line(order_id: int, line_id: int):
    """Update a purchase order line."""
    try:
        data = PurchaseOrderLineUpdateSchema().load(request.get_json() or {})
        data.pop('locale', None)
        
        command = UpdatePurchaseOrderLineCommand(purchase_order_id=order_id, line_id=line_id, **data)
        mediator.dispatch(command)
        
        return success_response(None, message=_('Line updated successfully'))
    except ValueError as e:
        return error_response(_(str(e)), status_code=400)
    except Exception as e:
        return error_response(_('Failed to update line: {}').format(str(e)), status_code=500)


@purchases_bp.delete("/purchase-orders/<int:order_id>/lines/<int:line_id>")
@require_roles("admin", "commercial")
def remove_purchase_order_line(order_id: int, line_id: int):
    """Remove a line from a purchase order."""
    try:
        command = RemovePurchaseOrderLineCommand(purchase_order_id=order_id, line_id=line_id)
        mediator.dispatch(command)
        return success_response(None, message=_('Line removed successfully'))
    except ValueError as e:
        return error_response(_(str(e)), status_code=400)
    except Exception as e:
        return error_response(_('Failed to remove line: {}').format(str(e)), status_code=500)

