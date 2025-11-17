"""Query handlers for payment management."""
from decimal import Decimal
from datetime import date, datetime, timedelta
from typing import List, Optional
from sqlalchemy import or_, and_, func, case
from app.application.common.cqrs import QueryHandler
from app.domain.models.payment import Payment, PaymentAllocation, PaymentStatus, PaymentMethod
from app.domain.models.invoice import Invoice
from app.domain.models.customer import Customer
from app.infrastructure.db import get_session
from .queries import (
    ListPaymentsQuery, GetPaymentByIdQuery, GetOverdueInvoicesQuery, GetAgingReportQuery
)
from .payment_dto import (
    PaymentDTO, PaymentAllocationDTO, OverdueInvoiceDTO, AgingBucketDTO, AgingReportDTO
)


class ListPaymentsHandler(QueryHandler):
    """Handler for listing payments."""
    
    def handle(self, query: ListPaymentsQuery) -> List[PaymentDTO]:
        """
        List payments with optional filters.
        
        Args:
            query: ListPaymentsQuery with filters
            
        Returns:
            List of PaymentDTO
        """
        with get_session() as session:
            # Build query
            q = session.query(Payment)
            
            # Apply filters
            if query.customer_id:
                q = q.filter(Payment.customer_id == query.customer_id)
            
            if query.status:
                try:
                    status_enum = PaymentStatus(query.status)
                    q = q.filter(Payment.status == status_enum)
                except ValueError:
                    pass  # Invalid status, ignore filter
            
            if query.payment_method:
                try:
                    method_enum = PaymentMethod(query.payment_method)
                    q = q.filter(Payment.payment_method == method_enum)
                except ValueError:
                    pass  # Invalid method, ignore filter
            
            if query.reconciled is not None:
                q = q.filter(Payment.reconciled == query.reconciled)
            
            if query.date_from:
                q = q.filter(Payment.payment_date >= query.date_from)
            
            if query.date_to:
                q = q.filter(Payment.payment_date <= query.date_to)
            
            if query.search:
                search_term = f"%{query.search}%"
                q = q.filter(
                    or_(
                        Payment.reference.ilike(search_term),
                        Payment.bank_reference.ilike(search_term)
                    )
                )
            
            # Order by payment date descending
            q = q.order_by(Payment.payment_date.desc(), Payment.id.desc())
            
            # Pagination
            offset = (query.page - 1) * query.per_page
            payments = q.offset(offset).limit(query.per_page).all()
            
            # Convert to DTOs
            result = []
            for payment in payments:
                # Load relationships
                session.refresh(payment, ['customer', 'allocations'])
                
                # Get customer info
                customer_code = None
                customer_name = None
                if payment.customer:
                    customer_code = getattr(payment.customer, 'code', None)
                    if hasattr(payment.customer, 'company_name') and payment.customer.company_name:
                        customer_name = payment.customer.company_name
                    elif hasattr(payment.customer, 'name'):
                        customer_name = payment.customer.name
                
                # Calculate totals
                total_allocated = payment.get_total_allocated()
                unallocated_amount = payment.get_unallocated_amount()
                
                # Get allocations
                allocations = []
                if payment.allocations:
                    for alloc in payment.allocations:
                        invoice = session.get(Invoice, alloc.invoice_id)
                        allocations.append(PaymentAllocationDTO(
                            id=alloc.id,
                            invoice_id=alloc.invoice_id,
                            invoice_number=invoice.number if invoice else None,
                            allocated_amount=alloc.allocated_amount,
                            created_at=alloc.created_at
                        ))
                
                result.append(PaymentDTO(
                    id=payment.id,
                    customer_id=payment.customer_id,
                    customer_code=customer_code,
                    customer_name=customer_name,
                    payment_method=payment.payment_method.value,
                    amount=payment.amount,
                    payment_date=payment.payment_date,
                    value_date=payment.value_date,
                    status=payment.status.value,
                    reference=payment.reference,
                    bank_reference=payment.bank_reference,
                    bank_account=payment.bank_account,
                    reconciled=payment.reconciled,
                    reconciled_at=payment.reconciled_at,
                    notes=payment.notes,
                    internal_notes=payment.internal_notes,
                    total_allocated=total_allocated,
                    unallocated_amount=unallocated_amount,
                    allocations=allocations,
                    created_at=payment.created_at,
                    created_by=payment.created_by
                ))
            
            return result


class GetPaymentByIdHandler(QueryHandler):
    """Handler for getting a payment by ID."""
    
    def handle(self, query: GetPaymentByIdQuery) -> Optional[PaymentDTO]:
        """
        Get a payment by ID.
        
        Args:
            query: GetPaymentByIdQuery with payment ID
            
        Returns:
            PaymentDTO or None if not found
        """
        with get_session() as session:
            payment = session.get(Payment, query.id)
            if not payment:
                return None
            
            # Load relationships
            session.refresh(payment, ['customer'])
            if query.include_allocations:
                session.refresh(payment, ['allocations'])
            
            # Get customer info
            customer_code = None
            customer_name = None
            if payment.customer:
                customer_code = getattr(payment.customer, 'code', None)
                if hasattr(payment.customer, 'company_name') and payment.customer.company_name:
                    customer_name = payment.customer.company_name
                elif hasattr(payment.customer, 'name'):
                    customer_name = payment.customer.name
            
            # Calculate totals
            total_allocated = payment.get_total_allocated()
            unallocated_amount = payment.get_unallocated_amount()
            
            # Get allocations
            allocations = []
            if query.include_allocations and payment.allocations:
                for alloc in payment.allocations:
                    invoice = None
                    if query.include_invoices:
                        invoice = session.get(Invoice, alloc.invoice_id)
                    allocations.append(PaymentAllocationDTO(
                        id=alloc.id,
                        invoice_id=alloc.invoice_id,
                        invoice_number=invoice.number if invoice else None,
                        allocated_amount=alloc.allocated_amount,
                        created_at=alloc.created_at
                    ))
            
            return PaymentDTO(
                id=payment.id,
                customer_id=payment.customer_id,
                customer_code=customer_code,
                customer_name=customer_name,
                payment_method=payment.payment_method.value,
                amount=payment.amount,
                payment_date=payment.payment_date,
                value_date=payment.value_date,
                status=payment.status.value,
                reference=payment.reference,
                bank_reference=payment.bank_reference,
                bank_account=payment.bank_account,
                reconciled=payment.reconciled,
                reconciled_at=payment.reconciled_at,
                notes=payment.notes,
                internal_notes=payment.internal_notes,
                total_allocated=total_allocated,
                unallocated_amount=unallocated_amount,
                allocations=allocations,
                created_at=payment.created_at,
                created_by=payment.created_by
            )


class GetOverdueInvoicesHandler(QueryHandler):
    """Handler for getting overdue invoices."""
    
    def handle(self, query: GetOverdueInvoicesQuery) -> List[OverdueInvoiceDTO]:
        """
        Get overdue invoices.
        
        Args:
            query: GetOverdueInvoicesQuery with filters
            
        Returns:
            List of OverdueInvoiceDTO
        """
        with get_session() as session:
            today = date.today()
            
            # Build query for overdue invoices
            q = session.query(Invoice).filter(
                Invoice.status.in_(["validated", "sent", "partially_paid", "overdue"]),
                Invoice.due_date < today,
                Invoice.remaining_amount > 0
            )
            
            # Apply filters
            if query.customer_id:
                q = q.filter(Invoice.customer_id == query.customer_id)
            
            if query.days_overdue:
                cutoff_date = today - timedelta(days=query.days_overdue)
                q = q.filter(Invoice.due_date <= cutoff_date)
            
            # Order by days overdue (most overdue first)
            q = q.order_by(Invoice.due_date.asc())
            
            # Pagination
            offset = (query.page - 1) * query.per_page
            invoices = q.offset(offset).limit(query.per_page).all()
            
            # Convert to DTOs
            result = []
            for invoice in invoices:
                # Load customer
                session.refresh(invoice, ['customer'])
                
                # Calculate days overdue
                days_overdue = (today - invoice.due_date).days
                
                # Get customer info
                customer_code = None
                customer_name = None
                if invoice.customer:
                    customer_code = getattr(invoice.customer, 'code', None)
                    if hasattr(invoice.customer, 'company_name') and invoice.customer.company_name:
                        customer_name = invoice.customer.company_name
                    elif hasattr(invoice.customer, 'name'):
                        customer_name = invoice.customer.name
                
                result.append(OverdueInvoiceDTO(
                    invoice_id=invoice.id,
                    invoice_number=invoice.number,
                    customer_id=invoice.customer_id,
                    customer_code=customer_code,
                    customer_name=customer_name,
                    invoice_date=invoice.invoice_date,
                    due_date=invoice.due_date,
                    total=invoice.total,
                    paid_amount=invoice.paid_amount,
                    remaining_amount=invoice.remaining_amount,
                    days_overdue=days_overdue,
                    status=invoice.status
                ))
            
            return result


class GetAgingReportHandler(QueryHandler):
    """Handler for getting aging report."""
    
    def handle(self, query: GetAgingReportQuery) -> List[AgingReportDTO]:
        """
        Get aging report for customers.
        
        Args:
            query: GetAgingReportQuery with filters
            
        Returns:
            List of AgingReportDTO (one per customer)
        """
        with get_session() as session:
            as_of_date = query.as_of_date or date.today()
            
            # Build query for outstanding invoices
            q = session.query(Invoice).filter(
                Invoice.remaining_amount > 0
            )
            
            if not query.include_paid:
                # Include validated, sent, partially_paid, and overdue invoices
                # (validated invoices may not be sent yet but still have outstanding amounts)
                q = q.filter(Invoice.status.in_(["validated", "sent", "partially_paid", "overdue"]))
            
            if query.customer_id:
                q = q.filter(Invoice.customer_id == query.customer_id)
            
            invoices = q.all()
            
            # Group by customer and calculate aging buckets
            customer_data = {}
            
            for invoice in invoices:
                # Load customer
                session.refresh(invoice, ['customer'])
                
                customer_id = invoice.customer_id
                if customer_id not in customer_data:
                    # Get customer info
                    customer_code = None
                    customer_name = None
                    if invoice.customer:
                        customer_code = getattr(invoice.customer, 'code', None)
                        if hasattr(invoice.customer, 'company_name') and invoice.customer.company_name:
                            customer_name = invoice.customer.company_name
                        elif hasattr(invoice.customer, 'name'):
                            customer_name = invoice.customer.name
                    
                    customer_data[customer_id] = {
                        'customer_id': customer_id,
                        'customer_code': customer_code,
                        'customer_name': customer_name,
                        'buckets': {
                            '0-30': Decimal(0),
                            '31-60': Decimal(0),
                            '61-90': Decimal(0),
                            '90+': Decimal(0)
                        },
                        'invoices': []
                    }
                
                # Calculate days overdue (can be negative for future due dates)
                days_overdue = (as_of_date - invoice.due_date).days
                
                # Determine bucket
                # For invoices not yet due (negative days_overdue), place in 0-30 bucket
                if days_overdue <= 30:
                    bucket = '0-30'
                elif days_overdue <= 60:
                    bucket = '31-60'
                elif days_overdue <= 90:
                    bucket = '61-90'
                else:
                    bucket = '90+'
                
                # Add to bucket
                customer_data[customer_id]['buckets'][bucket] += invoice.remaining_amount
                
                # Add invoice to list
                customer_data[customer_id]['invoices'].append(OverdueInvoiceDTO(
                    invoice_id=invoice.id,
                    invoice_number=invoice.number,
                    customer_id=invoice.customer_id,
                    customer_code=customer_data[customer_id]['customer_code'],
                    customer_name=customer_data[customer_id]['customer_name'],
                    invoice_date=invoice.invoice_date,
                    due_date=invoice.due_date,
                    total=invoice.total,
                    paid_amount=invoice.paid_amount,
                    remaining_amount=invoice.remaining_amount,
                    days_overdue=days_overdue,
                    status=invoice.status
                ))
            
            # Convert to DTOs
            result = []
            for customer_id, data in customer_data.items():
                # Calculate total outstanding
                total_outstanding = sum(data['buckets'].values())
                
                # Create bucket DTOs
                buckets = []
                for bucket_name, amount in data['buckets'].items():
                    if amount > 0:
                        # Count invoices that belong to this bucket
                        invoice_count = 0
                        for inv in data['invoices']:
                            days_overdue = (as_of_date - inv.due_date).days
                            if bucket_name == '0-30' and days_overdue <= 30:
                                invoice_count += 1
                            elif bucket_name == '31-60' and 31 <= days_overdue <= 60:
                                invoice_count += 1
                            elif bucket_name == '61-90' and 61 <= days_overdue <= 90:
                                invoice_count += 1
                            elif bucket_name == '90+' and days_overdue > 90:
                                invoice_count += 1
                        buckets.append(AgingBucketDTO(
                            bucket_name=bucket_name,
                            total_amount=amount,
                            invoice_count=invoice_count
                        ))
                
                result.append(AgingReportDTO(
                    customer_id=data['customer_id'],
                    customer_code=data['customer_code'],
                    customer_name=data['customer_name'],
                    total_outstanding=total_outstanding,
                    buckets=buckets,
                    invoices=data['invoices']
                ))
            
            # Sort by total outstanding (highest first)
            result.sort(key=lambda x: x.total_outstanding, reverse=True)
            
            return result

