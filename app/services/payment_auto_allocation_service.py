"""Service for automatic payment allocation to invoices."""
from decimal import Decimal
from typing import List, Optional, Literal
from datetime import date

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.domain.models.invoice import Invoice


class PaymentAutoAllocationService:
    """Service for automatically allocating payments to invoices."""
    
    def __init__(self, session: Session):
        """
        Initialize the service.
        
        Args:
            session: SQLAlchemy session
        """
        self.session = session
    
    def allocate_payment(
        self,
        customer_id: int,
        payment_amount: Decimal,
        strategy: Literal['fifo', 'proportional']
    ) -> List[dict]:
        """
        Automatically allocate payment amount to customer's unpaid invoices.
        
        Args:
            customer_id: Customer ID
            payment_amount: Total payment amount to allocate
            strategy: Allocation strategy ('fifo' or 'proportional')
            
        Returns:
            List of allocation dictionaries with 'invoice_id' and 'amount' keys
            
        Raises:
            ValueError: If strategy is invalid or no unpaid invoices found
        """
        if strategy not in ['fifo', 'proportional']:
            raise ValueError(f"Invalid allocation strategy: {strategy}. Must be 'fifo' or 'proportional'.")
        
        # Get all unpaid invoices for the customer
        unpaid_invoices = self.session.query(Invoice).filter(
            Invoice.customer_id == customer_id,
            Invoice.remaining_amount > 0,
            Invoice.status.in_(["sent", "partially_paid", "overdue", "validated"])
        ).order_by(Invoice.due_date.asc()).all()
        
        if not unpaid_invoices:
            return []
        
        if strategy == 'fifo':
            return self._allocate_fifo(unpaid_invoices, payment_amount)
        elif strategy == 'proportional':
            return self._allocate_proportional(unpaid_invoices, payment_amount)
    
    def _allocate_fifo(
        self,
        invoices: List[Invoice],
        payment_amount: Decimal
    ) -> List[dict]:
        """
        Allocate payment using FIFO strategy (First In First Out).
        
        Pays oldest invoices first (by due_date).
        
        Args:
            invoices: List of unpaid invoices (already sorted by due_date)
            payment_amount: Total payment amount to allocate
            
        Returns:
            List of allocation dictionaries
        """
        allocations = []
        remaining_amount = payment_amount
        
        for invoice in invoices:
            if remaining_amount <= 0:
                break
            
            # Calculate how much to allocate to this invoice
            invoice_remaining = invoice.remaining_amount
            allocation_amount = min(invoice_remaining, remaining_amount)
            
            allocations.append({
                'invoice_id': invoice.id,
                'amount': allocation_amount
            })
            
            remaining_amount -= allocation_amount
        
        return allocations
    
    def _allocate_proportional(
        self,
        invoices: List[Invoice],
        payment_amount: Decimal
    ) -> List[dict]:
        """
        Allocate payment proportionally based on remaining amounts.
        
        Each invoice gets: (invoice_remaining / total_remaining) × payment_amount
        
        Args:
            invoices: List of unpaid invoices
            payment_amount: Total payment amount to allocate
            
        Returns:
            List of allocation dictionaries
        """
        # Calculate total remaining amount
        total_remaining = sum(inv.remaining_amount for inv in invoices)
        
        if total_remaining == 0:
            return []
        
        allocations = []
        remaining_amount = payment_amount
        
        # Allocate proportionally, but ensure we don't exceed invoice remaining
        for i, invoice in enumerate(invoices):
            if remaining_amount <= 0:
                break
            
            # Calculate proportional amount
            proportion = invoice.remaining_amount / total_remaining
            proportional_amount = payment_amount * proportion
            
            # Round to 2 decimal places and ensure we don't exceed invoice remaining
            allocation_amount = min(
                round(proportional_amount, 2),
                invoice.remaining_amount,
                remaining_amount
            )
            
            # For the last invoice, allocate any remaining amount to avoid rounding errors
            if i == len(invoices) - 1:
                allocation_amount = min(remaining_amount, invoice.remaining_amount)
            
            if allocation_amount > 0:
                allocations.append({
                    'invoice_id': invoice.id,
                    'amount': allocation_amount
                })
                
                remaining_amount -= allocation_amount
        
        return allocations

