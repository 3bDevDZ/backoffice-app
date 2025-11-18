"""Query handlers for supplier invoice management."""
from app.application.common.cqrs import QueryHandler
from app.domain.models.purchase import SupplierInvoice
from app.infrastructure.db import get_session
from .queries import ListSupplierInvoicesQuery, GetSupplierInvoiceByIdQuery
from .invoice_dto import SupplierInvoiceDTO


class ListSupplierInvoicesHandler(QueryHandler):
    """Handler for listing supplier invoices."""
    
    def handle(self, query: ListSupplierInvoicesQuery) -> list[SupplierInvoiceDTO]:
        """
        List supplier invoices with optional filters.
        
        Args:
            query: ListSupplierInvoicesQuery with filters
            
        Returns:
            List of SupplierInvoiceDTO
        """
        with get_session() as session:
            # Build query
            q = session.query(SupplierInvoice)
            
            # Apply filters
            if query.supplier_id:
                q = q.filter(SupplierInvoice.supplier_id == query.supplier_id)
            
            if query.status:
                q = q.filter(SupplierInvoice.status == query.status)
            
            if query.matching_status:
                q = q.filter(SupplierInvoice.matching_status == query.matching_status)
            
            if query.date_from:
                q = q.filter(SupplierInvoice.invoice_date >= query.date_from)
            
            if query.date_to:
                q = q.filter(SupplierInvoice.invoice_date <= query.date_to)
            
            # Order by invoice date descending
            q = q.order_by(SupplierInvoice.invoice_date.desc(), SupplierInvoice.number.desc())
            
            # Pagination
            offset = (query.page - 1) * query.per_page
            invoices = q.offset(offset).limit(query.per_page).all()
            
            # Convert to DTOs
            result = []
            for invoice in invoices:
                # Load relationships
                session.refresh(invoice, ['supplier', 'matched_po', 'matched_receipt', 'creator', 'matcher'])
                
                # Get supplier name
                supplier_name = None
                if invoice.supplier:
                    supplier_name = getattr(invoice.supplier, 'name', None) or \
                                   getattr(invoice.supplier, 'company_name', None)
                
                # Get matched PO number
                po_number = None
                if invoice.matched_po:
                    po_number = invoice.matched_po.number
                
                # Get matched receipt number
                receipt_number = None
                if invoice.matched_receipt:
                    receipt_number = invoice.matched_receipt.number
                
                # Get creator name
                creator_name = None
                if invoice.creator:
                    creator_name = getattr(invoice.creator, 'name', None) or \
                                  getattr(invoice.creator, 'username', None)
                
                # Get matcher name
                matcher_name = None
                if invoice.matcher:
                    matcher_name = getattr(invoice.matcher, 'name', None) or \
                                  getattr(invoice.matcher, 'username', None)
                
                result.append(SupplierInvoiceDTO(
                    id=invoice.id,
                    number=invoice.number,
                    supplier_id=invoice.supplier_id,
                    supplier_name=supplier_name,
                    invoice_date=invoice.invoice_date,
                    due_date=invoice.due_date,
                    received_date=invoice.received_date,
                    subtotal_ht=invoice.subtotal_ht,
                    tax_amount=invoice.tax_amount,
                    total_ttc=invoice.total_ttc,
                    paid_amount=invoice.paid_amount,
                    remaining_amount=invoice.remaining_amount,
                    status=invoice.status,
                    matched_purchase_order_id=invoice.matched_purchase_order_id,
                    matched_purchase_order_number=po_number,
                    matched_purchase_receipt_id=invoice.matched_purchase_receipt_id,
                    matched_purchase_receipt_number=receipt_number,
                    matching_status=invoice.matching_status,
                    matching_notes=invoice.matching_notes,
                    matched_by=invoice.matched_by,
                    matched_by_name=matcher_name,
                    matched_at=invoice.matched_at,
                    notes=invoice.notes,
                    internal_notes=invoice.internal_notes,
                    created_by=invoice.created_by,
                    created_by_name=creator_name,
                    created_at=invoice.created_at,
                    updated_at=invoice.updated_at
                ))
            
            return result


class GetSupplierInvoiceByIdHandler(QueryHandler):
    """Handler for getting a supplier invoice by ID."""
    
    def handle(self, query: GetSupplierInvoiceByIdQuery) -> SupplierInvoiceDTO:
        """
        Get a supplier invoice by ID.
        
        Args:
            query: GetSupplierInvoiceByIdQuery with invoice ID
            
        Returns:
            SupplierInvoiceDTO or None if not found
        """
        with get_session() as session:
            invoice = session.get(SupplierInvoice, query.id)
            if not invoice:
                return None
            
            # Load relationships
            session.refresh(invoice, ['supplier', 'matched_po', 'matched_receipt', 'creator', 'matcher'])
            
            # Get supplier name
            supplier_name = None
            if invoice.supplier:
                supplier_name = getattr(invoice.supplier, 'name', None) or \
                               getattr(invoice.supplier, 'company_name', None)
            
            # Get matched PO number
            po_number = None
            if invoice.matched_po:
                po_number = invoice.matched_po.number
            
            # Get matched receipt number
            receipt_number = None
            if invoice.matched_receipt:
                receipt_number = invoice.matched_receipt.number
            
            # Get creator name
            creator_name = None
            if invoice.creator:
                creator_name = getattr(invoice.creator, 'name', None) or \
                              getattr(invoice.creator, 'username', None)
            
            # Get matcher name
            matcher_name = None
            if invoice.matcher:
                matcher_name = getattr(invoice.matcher, 'name', None) or \
                             getattr(invoice.matcher, 'username', None)
            
            return SupplierInvoiceDTO(
                id=invoice.id,
                number=invoice.number,
                supplier_id=invoice.supplier_id,
                supplier_name=supplier_name,
                invoice_date=invoice.invoice_date,
                due_date=invoice.due_date,
                received_date=invoice.received_date,
                subtotal_ht=invoice.subtotal_ht,
                tax_amount=invoice.tax_amount,
                total_ttc=invoice.total_ttc,
                paid_amount=invoice.paid_amount,
                remaining_amount=invoice.remaining_amount,
                status=invoice.status,
                matched_purchase_order_id=invoice.matched_purchase_order_id,
                matched_purchase_order_number=po_number,
                matched_purchase_receipt_id=invoice.matched_purchase_receipt_id,
                matched_purchase_receipt_number=receipt_number,
                matching_status=invoice.matching_status,
                matching_notes=invoice.matching_notes,
                matched_by=invoice.matched_by,
                matched_by_name=matcher_name,
                matched_at=invoice.matched_at,
                notes=invoice.notes,
                internal_notes=invoice.internal_notes,
                created_by=invoice.created_by,
                created_by_name=creator_name,
                created_at=invoice.created_at,
                updated_at=invoice.updated_at
            )




