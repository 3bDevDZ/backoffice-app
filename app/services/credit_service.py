"""Credit validation service for customer credit limit checking."""
from typing import Optional, Dict, Any
from decimal import Decimal
from dataclasses import dataclass

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.domain.models.customer import Customer, CommercialConditions
from app.domain.models.order import Order


@dataclass
class CreditValidationResult:
    """Result of a credit validation."""
    valid: bool
    current_debt: Decimal
    credit_limit: Decimal
    available_credit: Decimal
    new_debt_after_order: Decimal
    message: str
    customer_id: int
    customer_code: Optional[str] = None
    customer_name: Optional[str] = None


@dataclass
class CreditSummary:
    """Summary of customer credit status."""
    customer_id: int
    customer_code: Optional[str]
    customer_name: Optional[str]
    credit_limit: Decimal
    current_debt: Decimal
    available_credit: Decimal
    credit_utilization_percent: Decimal
    block_on_credit_exceeded: bool
    payment_terms_days: Optional[int] = None


class CreditService:
    """
    Service for credit validation and credit limit checking.
    Contains business logic for credit management that spans multiple aggregates.
    """
    
    def __init__(self, session: Session):
        """
        Initialize the credit service.
        
        Args:
            session: SQLAlchemy session
        """
        self.session = session
    
    # ==================== Credit Calculation Methods ====================
    
    def calculate_current_debt(self, customer_id: int) -> Decimal:
        """
        Calculate current debt for a customer.
        
        This includes:
        - Unpaid invoices (when invoice module is implemented)
        - Confirmed orders not yet invoiced (when invoice module is implemented)
        
        For now, returns 0 as invoice module is not yet implemented.
        
        Args:
            customer_id: Customer ID
            
        Returns:
            Current debt amount
        """
        # TODO: When invoice module is implemented, calculate from:
        # - Unpaid invoices (status != 'paid')
        # - Confirmed orders not yet invoiced
        
        # For now, we can calculate from confirmed orders that are not yet invoiced
        # This is a temporary solution until invoice module is ready
        confirmed_orders_total = self.session.query(
            func.sum(Order.total)
        ).filter(
            Order.customer_id == customer_id,
            Order.status.in_(['confirmed', 'ready', 'shipped', 'delivered'])
            # Note: We don't include 'invoiced' status as those should be in invoices
        ).scalar() or Decimal(0)
        
        return Decimal(str(confirmed_orders_total))
    
    def get_credit_summary(self, customer_id: int) -> CreditSummary:
        """
        Get a summary of customer credit status.
        
        Args:
            customer_id: Customer ID
            
        Returns:
            CreditSummary with credit information
            
        Raises:
            ValueError: If customer not found
        """
        customer = self.session.get(Customer, customer_id)
        if not customer:
            raise ValueError(f"Customer with ID {customer_id} not found.")
        
        commercial_conditions = customer.commercial_conditions
        if not commercial_conditions:
            # No commercial conditions = no credit limit
            return CreditSummary(
                customer_id=customer.id,
                customer_code=customer.code,
                customer_name=customer.company_name or f"{customer.first_name} {customer.last_name}",
                credit_limit=Decimal(0),
                current_debt=Decimal(0),
                available_credit=Decimal(0),
                credit_utilization_percent=Decimal(0),
                block_on_credit_exceeded=False,
                payment_terms_days=None
            )
        
        credit_limit = commercial_conditions.credit_limit or Decimal(0)
        current_debt = self.calculate_current_debt(customer_id)
        available_credit = max(Decimal(0), credit_limit - current_debt)
        
        # Calculate utilization percentage
        if credit_limit > 0:
            credit_utilization_percent = (current_debt / credit_limit) * 100
        else:
            credit_utilization_percent = Decimal(0)
        
        return CreditSummary(
            customer_id=customer.id,
            customer_code=customer.code,
            customer_name=customer.company_name or f"{customer.first_name} {customer.last_name}",
            credit_limit=credit_limit,
            current_debt=current_debt,
            available_credit=available_credit,
            credit_utilization_percent=credit_utilization_percent,
            block_on_credit_exceeded=commercial_conditions.block_on_credit_exceeded,
            payment_terms_days=commercial_conditions.payment_terms_days
        )
    
    # ==================== Credit Validation Methods ====================
    
    def validate_credit_for_order(
        self,
        customer_id: int,
        order_total: Decimal,
        order_id: Optional[int] = None
    ) -> CreditValidationResult:
        """
        Validate if an order can be placed based on customer credit limit.
        
        Args:
            customer_id: Customer ID
            order_total: Total amount of the order
            order_id: Optional order ID (to exclude from debt calculation if updating existing order)
            
        Returns:
            CreditValidationResult with validation details
            
        Raises:
            ValueError: If customer not found
        """
        customer = self.session.get(Customer, customer_id)
        if not customer:
            raise ValueError(f"Customer with ID {customer_id} not found.")
        
        # Get commercial conditions
        commercial_conditions = customer.commercial_conditions
        
        # If no commercial conditions or credit checking disabled, allow the order
        if not commercial_conditions or not commercial_conditions.block_on_credit_exceeded:
            return CreditValidationResult(
                valid=True,
                current_debt=Decimal(0),
                credit_limit=Decimal(0),
                available_credit=Decimal(0),
                new_debt_after_order=order_total,
                message='Credit checking not enabled for this customer',
                customer_id=customer.id,
                customer_code=customer.code,
                customer_name=customer.company_name or f"{customer.first_name} {customer.last_name}"
            )
        
        credit_limit = commercial_conditions.credit_limit or Decimal(0)
        
        # Calculate current debt
        current_debt = self.calculate_current_debt(customer_id)
        
        # If updating an existing order, subtract the old order total from debt
        if order_id:
            existing_order = self.session.get(Order, order_id)
            if existing_order and existing_order.status in ['confirmed', 'ready', 'shipped', 'delivered']:
                current_debt = max(Decimal(0), current_debt - existing_order.total)
        
        # Calculate new debt after order
        new_debt_after_order = current_debt + order_total
        
        # Check if credit limit would be exceeded
        if new_debt_after_order > credit_limit:
            available_credit = max(Decimal(0), credit_limit - current_debt)
            return CreditValidationResult(
                valid=False,
                current_debt=current_debt,
                credit_limit=credit_limit,
                available_credit=available_credit,
                new_debt_after_order=new_debt_after_order,
                message=(
                    f"Credit limit would be exceeded. "
                    f"Current debt: {current_debt:.2f} €, "
                    f"Credit limit: {credit_limit:.2f} €, "
                    f"Order total: {order_total:.2f} €, "
                    f"New debt would be: {new_debt_after_order:.2f} €, "
                    f"Available credit: {available_credit:.2f} €"
                ),
                customer_id=customer.id,
                customer_code=customer.code,
                customer_name=customer.company_name or f"{customer.first_name} {customer.last_name}"
            )
        
        available_credit = max(Decimal(0), credit_limit - new_debt_after_order)
        return CreditValidationResult(
            valid=True,
            current_debt=current_debt,
            credit_limit=credit_limit,
            available_credit=available_credit,
            new_debt_after_order=new_debt_after_order,
            message='Credit limit OK',
            customer_id=customer.id,
            customer_code=customer.code,
            customer_name=customer.company_name or f"{customer.first_name} {customer.last_name}"
        )
    
    def check_credit_available(
        self,
        customer_id: int,
        amount: Decimal
    ) -> bool:
        """
        Quick check if a customer has available credit for an amount.
        
        Args:
            customer_id: Customer ID
            amount: Amount to check
            
        Returns:
            True if credit is available, False otherwise
        """
        try:
            result = self.validate_credit_for_order(customer_id, amount)
            return result.valid
        except ValueError:
            return False
    
    def get_available_credit(self, customer_id: int) -> Decimal:
        """
        Get available credit for a customer.
        
        Args:
            customer_id: Customer ID
            
        Returns:
            Available credit amount
            
        Raises:
            ValueError: If customer not found
        """
        summary = self.get_credit_summary(customer_id)
        return summary.available_credit

