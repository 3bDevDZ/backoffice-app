"""Query handlers for purchase management."""
from app.application.common.cqrs import QueryHandler
from app.domain.models.supplier import Supplier, SupplierAddress, SupplierContact, SupplierConditions
from app.domain.models.purchase import PurchaseOrder, PurchaseOrderLine
from app.domain.models.product import Product
from app.infrastructure.db import get_session
from .queries import (
    GetSupplierByIdQuery,
    ListSuppliersQuery,
    SearchSuppliersQuery,
    GetPurchaseOrderByIdQuery,
    ListPurchaseOrdersQuery
)
from .purchase_dto import (
    SupplierDTO, SupplierAddressDTO, SupplierContactDTO, SupplierConditionsDTO,
    PurchaseOrderDTO, PurchaseOrderLineDTO
)
from typing import List
from sqlalchemy import or_


class GetSupplierByIdHandler(QueryHandler):
    def handle(self, query: GetSupplierByIdQuery) -> SupplierDTO:
        with get_session() as session:
            supplier = session.get(Supplier, query.id)
            if not supplier:
                raise ValueError("Supplier not found")
            
            # Load addresses
            address_dtos = [
                SupplierAddressDTO(
                    id=addr.id,
                    supplier_id=addr.supplier_id,
                    type=addr.type,
                    is_default_billing=addr.is_default_billing,
                    is_default_delivery=addr.is_default_delivery,
                    street=addr.street,
                    city=addr.city,
                    postal_code=addr.postal_code,
                    country=addr.country,
                    state=addr.state
                )
                for addr in supplier.addresses
            ]
            
            # Load contacts
            contact_dtos = [
                SupplierContactDTO(
                    id=contact.id,
                    supplier_id=contact.supplier_id,
                    first_name=contact.first_name,
                    last_name=contact.last_name,
                    function=contact.function,
                    email=contact.email,
                    phone=contact.phone,
                    mobile=contact.mobile,
                    is_primary=contact.is_primary,
                    receives_orders=contact.receives_orders,
                    receives_invoices=contact.receives_invoices
                )
                for contact in supplier.contacts
            ]
            
            # Load conditions
            conditions_dto = None
            if supplier.conditions:
                cond = supplier.conditions
                conditions_dto = SupplierConditionsDTO(
                    id=cond.id,
                    supplier_id=cond.supplier_id,
                    payment_terms_days=cond.payment_terms_days,
                    default_discount_percent=cond.default_discount_percent,
                    minimum_order_amount=cond.minimum_order_amount,
                    delivery_lead_time_days=cond.delivery_lead_time_days
                )
            
            return SupplierDTO(
                id=supplier.id,
                code=supplier.code,
                name=supplier.name,
                email=supplier.email,
                phone=supplier.phone,
                mobile=supplier.mobile,
                category=supplier.category,
                status=supplier.status,
                notes=supplier.notes,
                company_name=supplier.company_name,
                siret=supplier.siret,
                vat_number=supplier.vat_number,
                rcs=supplier.rcs,
                legal_form=supplier.legal_form,
                addresses=address_dtos,
                contacts=contact_dtos,
                conditions=conditions_dto
            )


class ListSuppliersHandler(QueryHandler):
    def handle(self, query: ListSuppliersQuery) -> List[SupplierDTO]:
        with get_session() as session:
            # Build query with filters
            q = session.query(Supplier)
            
            if query.search:
                search_term = f"%{query.search}%"
                q = q.filter(
                    or_(
                        Supplier.name.ilike(search_term),
                        Supplier.email.ilike(search_term),
                        Supplier.code.ilike(search_term),
                        Supplier.company_name.ilike(search_term)
                    )
                )
            
            if query.status:
                q = q.filter(Supplier.status == query.status)
            
            if query.category:
                q = q.filter(Supplier.category == query.category)
            
            # Order by name
            q = q.order_by(Supplier.name.asc())
            
            # Pagination
            suppliers = q.offset((query.page - 1) * query.per_page).limit(query.per_page).all()
            
            return [
                SupplierDTO(
                    id=s.id,
                    code=s.code,
                    name=s.name,
                    email=s.email,
                    phone=s.phone,
                    mobile=s.mobile,
                    category=s.category,
                    status=s.status,
                    notes=s.notes,
                    company_name=s.company_name,
                    siret=s.siret,
                    vat_number=s.vat_number,
                    rcs=s.rcs,
                    legal_form=s.legal_form,
                    addresses=[],
                    contacts=[],
                    conditions=None
                )
                for s in suppliers
            ]


class SearchSuppliersHandler(QueryHandler):
    def handle(self, query: SearchSuppliersQuery) -> List[SupplierDTO]:
        with get_session() as session:
            search_term = f"%{query.search_term}%"
            suppliers = session.query(Supplier).filter(
                or_(
                    Supplier.name.ilike(search_term),
                    Supplier.email.ilike(search_term),
                    Supplier.code.ilike(search_term)
                )
            ).limit(query.limit).all()
            
            return [
                SupplierDTO(
                    id=s.id,
                    code=s.code,
                    name=s.name,
                    email=s.email,
                    phone=s.phone,
                    mobile=s.mobile,
                    category=s.category,
                    status=s.status,
                    notes=s.notes,
                    company_name=s.company_name,
                    siret=s.siret,
                    vat_number=s.vat_number,
                    rcs=s.rcs,
                    legal_form=s.legal_form,
                    addresses=[],
                    contacts=[],
                    conditions=None
                )
                for s in suppliers
            ]


class GetPurchaseOrderByIdHandler(QueryHandler):
    def handle(self, query: GetPurchaseOrderByIdQuery) -> PurchaseOrderDTO:
        with get_session() as session:
            order = session.get(PurchaseOrder, query.id)
            if not order:
                raise ValueError("Purchase order not found")
            
            # Load lines with product info
            line_dtos = []
            for line in order.lines:
                product = session.get(Product, line.product_id)
                line_dtos.append(PurchaseOrderLineDTO(
                    id=line.id,
                    purchase_order_id=line.purchase_order_id,
                    product_id=line.product_id,
                    product_code=product.code if product else None,
                    product_name=product.name if product else None,
                    quantity=line.quantity,
                    unit_price=line.unit_price,
                    discount_percent=line.discount_percent,
                    tax_rate=line.tax_rate,
                    line_total_ht=line.line_total_ht,
                    line_total_ttc=line.line_total_ttc,
                    quantity_received=line.quantity_received,
                    sequence=line.sequence,
                    notes=line.notes
                ))
            
            # Get supplier info
            supplier = session.get(Supplier, order.supplier_id)
            
            return PurchaseOrderDTO(
                id=order.id,
                number=order.number,
                supplier_id=order.supplier_id,
                supplier_code=supplier.code if supplier else None,
                supplier_name=supplier.name if supplier else None,
                order_date=order.order_date,
                expected_delivery_date=order.expected_delivery_date,
                received_date=order.received_date,
                status=order.status,
                subtotal_ht=order.subtotal_ht,
                total_tax=order.total_tax,
                total_ttc=order.total_ttc,
                notes=order.notes,
                internal_notes=order.internal_notes,
                created_by=order.created_by,
                confirmed_by=order.confirmed_by,
                confirmed_at=order.confirmed_at.date() if order.confirmed_at else None,
                created_at=order.created_at.date() if order.created_at else None,
                lines=line_dtos
            )


class ListPurchaseOrdersHandler(QueryHandler):
    def handle(self, query: ListPurchaseOrdersQuery) -> List[PurchaseOrderDTO]:
        with get_session() as session:
            # Build query with filters
            q = session.query(PurchaseOrder)
            
            if query.supplier_id:
                q = q.filter(PurchaseOrder.supplier_id == query.supplier_id)
            
            if query.status:
                q = q.filter(PurchaseOrder.status == query.status)
            
            if query.search:
                search_term = f"%{query.search}%"
                q = q.filter(
                    or_(
                        PurchaseOrder.number.ilike(search_term),
                        PurchaseOrder.notes.ilike(search_term)
                    )
                )
            
            # Order by creation date descending
            q = q.order_by(PurchaseOrder.created_at.desc())
            
            # Pagination
            orders = q.offset((query.page - 1) * query.per_page).limit(query.per_page).all()
            
            # Get supplier info for each order
            result = []
            for order in orders:
                supplier = session.get(Supplier, order.supplier_id)
                result.append(PurchaseOrderDTO(
                    id=order.id,
                    number=order.number,
                    supplier_id=order.supplier_id,
                    supplier_code=supplier.code if supplier else None,
                    supplier_name=supplier.name if supplier else None,
                    order_date=order.order_date,
                    expected_delivery_date=order.expected_delivery_date,
                    received_date=order.received_date,
                    status=order.status,
                    subtotal_ht=order.subtotal_ht,
                    total_tax=order.total_tax,
                    total_ttc=order.total_ttc,
                    notes=order.notes,
                    internal_notes=order.internal_notes,
                    created_by=order.created_by,
                    confirmed_by=order.confirmed_by,
                    confirmed_at=order.confirmed_at.date() if order.confirmed_at else None,
                    created_at=order.created_at.date() if order.created_at else None,
                    lines=[]  # Don't load lines in list view
                ))
            
            return result

