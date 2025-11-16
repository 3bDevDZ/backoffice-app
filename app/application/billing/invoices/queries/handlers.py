"""Query handlers for invoice management."""
from decimal import Decimal
from datetime import datetime
from typing import List, Optional
from sqlalchemy import or_, and_
from app.application.common.cqrs import QueryHandler
from app.domain.models.invoice import Invoice, InvoiceLine, CreditNote
from app.infrastructure.db import get_session
from .queries import ListInvoicesQuery, GetInvoiceByIdQuery, GetInvoiceHistoryQuery
from .invoice_dto import InvoiceDTO, InvoiceLineDTO, CreditNoteDTO


class ListInvoicesHandler(QueryHandler):
    """Handler for listing invoices."""
    
    def handle(self, query: ListInvoicesQuery) -> List[InvoiceDTO]:
        """
        List invoices with optional filters.
        
        Args:
            query: ListInvoicesQuery with filters
            
        Returns:
            List of InvoiceDTO
        """
        with get_session() as session:
            # Build query
            q = session.query(Invoice)
            
            # Apply filters
            if query.status:
                q = q.filter(Invoice.status == query.status)
            
            if query.customer_id:
                q = q.filter(Invoice.customer_id == query.customer_id)
            
            if query.order_id:
                q = q.filter(Invoice.order_id == query.order_id)
            
            if query.date_from:
                q = q.filter(Invoice.invoice_date >= query.date_from)
            
            if query.date_to:
                q = q.filter(Invoice.invoice_date <= query.date_to)
            
            if query.search:
                search_term = f"%{query.search}%"
                q = q.filter(
                    or_(
                        Invoice.number.ilike(search_term),
                        Invoice.customer.has(company_name=search_term) if hasattr(Invoice.customer, 'company_name') else False,
                        Invoice.customer.has(name=search_term)
                    )
                )
            
            # Order by invoice date descending
            q = q.order_by(Invoice.invoice_date.desc(), Invoice.number.desc())
            
            # Pagination
            offset = (query.page - 1) * query.per_page
            invoices = q.offset(offset).limit(query.per_page).all()
            
            # Convert to DTOs
            result = []
            for invoice in invoices:
                # Load relationships
                session.refresh(invoice, ['customer', 'order', 'lines', 'credit_notes', 'creator', 'validated_by_user', 'sent_by_user'])
                
                # Get customer info
                customer_code = None
                customer_name = None
                if invoice.customer:
                    customer_code = getattr(invoice.customer, 'code', None)
                    if hasattr(invoice.customer, 'company_name') and invoice.customer.company_name:
                        customer_name = invoice.customer.company_name
                    elif hasattr(invoice.customer, 'name'):
                        customer_name = invoice.customer.name
                
                # Get order number
                order_number = None
                if invoice.order:
                    order_number = invoice.order.number
                
                # Convert lines
                lines_dto = []
                for line in invoice.lines:
                    # Load product and variant
                    session.refresh(line, ['product', 'variant'])
                    
                    product_code = None
                    product_name = None
                    if line.product:
                        product_code = line.product.code
                        product_name = line.product.name
                    
                    variant_code = None
                    variant_name = None
                    if line.variant:
                        variant_code = line.variant.code
                        variant_name = line.variant.name
                    
                    lines_dto.append(InvoiceLineDTO(
                        id=line.id,
                        product_id=line.product_id,
                        product_code=product_code,
                        product_name=product_name,
                        variant_id=line.variant_id,
                        variant_code=variant_code,
                        variant_name=variant_name,
                        order_line_id=line.order_line_id,
                        description=line.description,
                        quantity=line.quantity,
                        unit_price=line.unit_price,
                        discount_percent=line.discount_percent,
                        discount_amount=line.discount_amount,
                        tax_rate=line.tax_rate,
                        line_total_ht=line.line_total_ht,
                        line_total_ttc=line.line_total_ttc,
                        sequence=line.sequence
                    ))
                
                # Convert credit notes
                credit_notes_dto = []
                for credit_note in invoice.credit_notes:
                    session.refresh(credit_note, ['customer', 'creator', 'validator'])
                    
                    cn_customer_code = None
                    cn_customer_name = None
                    if credit_note.customer:
                        cn_customer_code = getattr(credit_note.customer, 'code', None)
                        if hasattr(credit_note.customer, 'company_name') and credit_note.customer.company_name:
                            cn_customer_name = credit_note.customer.company_name
                        elif hasattr(credit_note.customer, 'name'):
                            cn_customer_name = credit_note.customer.name
                    
                    created_by_name = None
                    if credit_note.creator:
                        created_by_name = getattr(credit_note.creator, 'username', None) or getattr(credit_note.creator, 'name', None)
                    
                    validated_by_name = None
                    if credit_note.validator:
                        validated_by_name = getattr(credit_note.validator, 'username', None) or getattr(credit_note.validator, 'name', None)
                    
                    credit_notes_dto.append(CreditNoteDTO(
                        id=credit_note.id,
                        number=credit_note.number,
                        invoice_id=credit_note.invoice_id,
                        invoice_number=invoice.number,
                        customer_id=credit_note.customer_id,
                        customer_code=cn_customer_code,
                        customer_name=cn_customer_name,
                        reason=credit_note.reason,
                        total_amount=credit_note.total_amount,
                        tax_amount=credit_note.tax_amount,
                        total_ttc=credit_note.total_ttc,
                        status=credit_note.status,
                        created_by=credit_note.created_by,
                        created_by_name=created_by_name,
                        validated_by=credit_note.validated_by,
                        validated_by_name=validated_by_name,
                        validated_at=credit_note.validated_at,
                        created_at=credit_note.created_at,
                        updated_at=credit_note.updated_at
                    ))
                
                # Get user names
                created_by_name = None
                if invoice.creator:
                    created_by_name = getattr(invoice.creator, 'username', None) or getattr(invoice.creator, 'name', None)
                
                validated_by_name = None
                if invoice.validated_by_user:
                    validated_by_name = getattr(invoice.validated_by_user, 'username', None) or getattr(invoice.validated_by_user, 'name', None)
                
                sent_by_name = None
                if invoice.sent_by_user:
                    sent_by_name = getattr(invoice.sent_by_user, 'username', None) or getattr(invoice.sent_by_user, 'name', None)
                
                result.append(InvoiceDTO(
                    id=invoice.id,
                    number=invoice.number,
                    order_id=invoice.order_id,
                    order_number=order_number,
                    customer_id=invoice.customer_id,
                    customer_code=customer_code,
                    customer_name=customer_name,
                    invoice_date=invoice.invoice_date,
                    due_date=invoice.due_date,
                    status=invoice.status,
                    subtotal=invoice.subtotal,
                    discount_percent=invoice.discount_percent,
                    discount_amount=invoice.discount_amount,
                    tax_amount=invoice.tax_amount,
                    total=invoice.total,
                    paid_amount=invoice.paid_amount,
                    remaining_amount=invoice.remaining_amount,
                    vat_number=invoice.vat_number,
                    siret=invoice.siret,
                    legal_mention=invoice.legal_mention,
                    notes=invoice.notes,
                    internal_notes=invoice.internal_notes,
                    sent_at=invoice.sent_at,
                    sent_by=invoice.sent_by,
                    sent_by_name=sent_by_name,
                    email_sent=invoice.email_sent,
                    validated_at=invoice.validated_at,
                    validated_by=invoice.validated_by,
                    validated_by_name=validated_by_name,
                    created_by=invoice.created_by,
                    created_by_name=created_by_name,
                    created_at=invoice.created_at,
                    updated_at=invoice.updated_at,
                    lines=lines_dto,
                    credit_notes=credit_notes_dto
                ))
            
            return result


class GetInvoiceByIdHandler(QueryHandler):
    """Handler for getting an invoice by ID."""
    
    def handle(self, query: GetInvoiceByIdQuery) -> Optional[InvoiceDTO]:
        """
        Get an invoice by ID.
        
        Args:
            query: GetInvoiceByIdQuery with invoice ID
            
        Returns:
            InvoiceDTO or None if not found
        """
        with get_session() as session:
            invoice = session.get(Invoice, query.id)
            if not invoice:
                return None
            
            # Use ListInvoicesHandler logic to convert to DTO
            # For simplicity, we'll reuse the conversion logic
            list_handler = ListInvoicesHandler()
            list_query = ListInvoicesQuery(page=1, per_page=1)
            # We'll manually convert here to avoid query overhead
            # But for now, let's use a simpler approach
            
            # Load relationships
            session.refresh(invoice, ['customer', 'order', 'lines', 'credit_notes', 'creator', 'validated_by_user', 'sent_by_user'])
            
            # Get customer info
            customer_code = None
            customer_name = None
            if invoice.customer:
                customer_code = getattr(invoice.customer, 'code', None)
                if hasattr(invoice.customer, 'company_name') and invoice.customer.company_name:
                    customer_name = invoice.customer.company_name
                elif hasattr(invoice.customer, 'name'):
                    customer_name = invoice.customer.name
            
            # Get order number
            order_number = None
            if invoice.order:
                order_number = invoice.order.number
            
            # Convert lines
            lines_dto = []
            for line in invoice.lines:
                session.refresh(line, ['product', 'variant'])
                
                product_code = None
                product_name = None
                if line.product:
                    product_code = line.product.code
                    product_name = line.product.name
                
                variant_code = None
                variant_name = None
                if line.variant:
                    variant_code = line.variant.code
                    variant_name = line.variant.name
                
                lines_dto.append(InvoiceLineDTO(
                    id=line.id,
                    product_id=line.product_id,
                    product_code=product_code,
                    product_name=product_name,
                    variant_id=line.variant_id,
                    variant_code=variant_code,
                    variant_name=variant_name,
                    order_line_id=line.order_line_id,
                    description=line.description,
                    quantity=line.quantity,
                    unit_price=line.unit_price,
                    discount_percent=line.discount_percent,
                    discount_amount=line.discount_amount,
                    tax_rate=line.tax_rate,
                    line_total_ht=line.line_total_ht,
                    line_total_ttc=line.line_total_ttc,
                    sequence=line.sequence
                ))
            
            # Convert credit notes
            credit_notes_dto = []
            for credit_note in invoice.credit_notes:
                session.refresh(credit_note, ['customer', 'creator', 'validator'])
                
                cn_customer_code = None
                cn_customer_name = None
                if credit_note.customer:
                    cn_customer_code = getattr(credit_note.customer, 'code', None)
                    if hasattr(credit_note.customer, 'company_name') and credit_note.customer.company_name:
                        cn_customer_name = credit_note.customer.company_name
                    elif hasattr(credit_note.customer, 'name'):
                        cn_customer_name = credit_note.customer.name
                
                created_by_name = None
                if credit_note.creator:
                    created_by_name = getattr(credit_note.creator, 'username', None) or getattr(credit_note.creator, 'name', None)
                
                validated_by_name = None
                if credit_note.validator:
                    validated_by_name = getattr(credit_note.validator, 'username', None) or getattr(credit_note.validator, 'name', None)
                
                credit_notes_dto.append(CreditNoteDTO(
                    id=credit_note.id,
                    number=credit_note.number,
                    invoice_id=credit_note.invoice_id,
                    invoice_number=invoice.number,
                    customer_id=credit_note.customer_id,
                    customer_code=cn_customer_code,
                    customer_name=cn_customer_name,
                    reason=credit_note.reason,
                    total_amount=credit_note.total_amount,
                    tax_amount=credit_note.tax_amount,
                    total_ttc=credit_note.total_ttc,
                    status=credit_note.status,
                    created_by=credit_note.created_by,
                    created_by_name=created_by_name,
                    validated_by=credit_note.validated_by,
                    validated_by_name=validated_by_name,
                    validated_at=credit_note.validated_at,
                    created_at=credit_note.created_at,
                    updated_at=credit_note.updated_at
                ))
            
            # Get user names
            created_by_name = None
            if invoice.creator:
                created_by_name = getattr(invoice.creator, 'username', None) or getattr(invoice.creator, 'name', None)
            
            validated_by_name = None
            if invoice.validated_by_user:
                validated_by_name = getattr(invoice.validated_by_user, 'username', None) or getattr(invoice.validated_by_user, 'name', None)
            
            sent_by_name = None
            if invoice.sent_by_user:
                sent_by_name = getattr(invoice.sent_by_user, 'username', None) or getattr(invoice.sent_by_user, 'name', None)
            
            return InvoiceDTO(
                id=invoice.id,
                number=invoice.number,
                order_id=invoice.order_id,
                order_number=order_number,
                customer_id=invoice.customer_id,
                customer_code=customer_code,
                customer_name=customer_name,
                invoice_date=invoice.invoice_date,
                due_date=invoice.due_date,
                status=invoice.status,
                subtotal=invoice.subtotal,
                discount_percent=invoice.discount_percent,
                discount_amount=invoice.discount_amount,
                tax_amount=invoice.tax_amount,
                total=invoice.total,
                paid_amount=invoice.paid_amount,
                remaining_amount=invoice.remaining_amount,
                vat_number=invoice.vat_number,
                siret=invoice.siret,
                legal_mention=invoice.legal_mention,
                notes=invoice.notes,
                internal_notes=invoice.internal_notes,
                sent_at=invoice.sent_at,
                sent_by=invoice.sent_by,
                sent_by_name=sent_by_name,
                email_sent=invoice.email_sent,
                validated_at=invoice.validated_at,
                validated_by=invoice.validated_by,
                validated_by_name=validated_by_name,
                created_by=invoice.created_by,
                created_by_name=created_by_name,
                created_at=invoice.created_at,
                updated_at=invoice.updated_at,
                lines=lines_dto,
                credit_notes=credit_notes_dto
            )


class GetInvoiceHistoryHandler(QueryHandler):
    """Handler for getting invoice history."""
    
    def handle(self, query: GetInvoiceHistoryQuery) -> dict:
        """
        Get invoice history (status changes, payments, etc.).
        
        This is a placeholder - actual implementation would track
        status changes, payment events, etc. in a separate history table.
        
        Args:
            query: GetInvoiceHistoryQuery with invoice ID
            
        Returns:
            Dictionary with history information
        """
        with get_session() as session:
            invoice = session.get(Invoice, query.invoice_id)
            if not invoice:
                return {'history': []}
            
            # For now, return basic history from invoice fields
            history = []
            
            if invoice.created_at:
                history.append({
                    'date': invoice.created_at,
                    'event': 'created',
                    'user': getattr(invoice.creator, 'username', None) if invoice.creator else None
                })
            
            if invoice.validated_at:
                history.append({
                    'date': invoice.validated_at,
                    'event': 'validated',
                    'user': getattr(invoice.validated_by_user, 'username', None) if invoice.validated_by_user else None
                })
            
            if invoice.sent_at:
                history.append({
                    'date': invoice.sent_at,
                    'event': 'sent',
                    'user': getattr(invoice.sent_by_user, 'username', None) if invoice.sent_by_user else None
                })
            
            # Sort by date
            history.sort(key=lambda x: x['date'], reverse=True)
            
            return {'history': history}

