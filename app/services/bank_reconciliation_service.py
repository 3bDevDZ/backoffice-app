"""Service for automatic bank reconciliation."""
from decimal import Decimal
from datetime import date, datetime
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.domain.models.payment import Payment, PaymentStatus, PaymentMethod
from app.infrastructure.db import get_session


class BankReconciliationService:
    """Service for reconciling payments with bank statements."""
    
    def __init__(self, session: Optional[Session] = None):
        """
        Initialize the service.
        
        Args:
            session: Optional SQLAlchemy session (if None, will create one)
        """
        self.session = session
    
    def reconcile_statement(
        self,
        bank_account: str,
        statement_date: date,
        transactions: List[Dict],
        imported_by: Optional[int] = None
    ) -> Dict:
        """
        Reconcile bank statement transactions with payments.
        
        Args:
            bank_account: Bank account number
            statement_date: Statement date
            transactions: List of transaction dicts with keys:
                - reference: Bank reference (required)
                - amount: Transaction amount (required)
                - date: Transaction date (required)
                - description: Optional description
            imported_by: User ID who imported the statement
            
        Returns:
            dict with reconciliation results:
                - matched: List of matched payments
                - unmatched_transactions: List of unmatched transactions
                - unmatched_payments: List of unmatched payments
        """
        if not self.session:
            with get_session() as session:
                return self._reconcile_statement_impl(
                    session, bank_account, statement_date, transactions, imported_by
                )
        else:
            return self._reconcile_statement_impl(
                self.session, bank_account, statement_date, transactions, imported_by
            )
    
    def _reconcile_statement_impl(
        self,
        session: Session,
        bank_account: str,
        statement_date: date,
        transactions: List[Dict],
        imported_by: Optional[int] = None
    ) -> Dict:
        """Internal implementation of reconciliation."""
        matched = []
        unmatched_transactions = []
        unmatched_payments = []
        
        # Get all unreconciled payments for this bank account
        unreconciled_payments = session.query(Payment).filter(
            Payment.bank_account == bank_account,
            Payment.reconciled == False,
            Payment.status != PaymentStatus.CANCELLED
        ).all()
        
        # Try to match each transaction with a payment
        for transaction in transactions:
            reference = transaction.get('reference', '').strip()
            amount = Decimal(str(transaction.get('amount', 0)))
            trans_date = transaction.get('date')
            
            if not reference or amount <= 0:
                unmatched_transactions.append(transaction)
                continue
            
            # Try to find matching payment by reference
            matched_payment = None
            for payment in unreconciled_payments:
                if payment.reference and payment.reference.strip() == reference:
                    # Check amount match (with tolerance for rounding)
                    if abs(payment.amount - amount) <= Decimal('0.01'):
                        matched_payment = payment
                        break
            
            if matched_payment:
                # Reconcile payment
                matched_payment.reconcile(
                    bank_reference=reference,
                    bank_account=bank_account,
                    reconciled_by=imported_by
                )
                matched.append({
                    'payment_id': matched_payment.id,
                    'transaction': transaction,
                    'matched_by': 'reference'
                })
                unreconciled_payments.remove(matched_payment)
            else:
                unmatched_transactions.append(transaction)
        
        # Add remaining unreconciled payments to unmatched list
        for payment in unreconciled_payments:
            unmatched_payments.append({
                'payment_id': payment.id,
                'amount': float(payment.amount),
                'payment_date': payment.payment_date.isoformat(),
                'reference': payment.reference
            })
        
        return {
            'matched': matched,
            'unmatched_transactions': unmatched_transactions,
            'unmatched_payments': unmatched_payments,
            'statement_date': statement_date.isoformat(),
            'bank_account': bank_account
        }
    
    def auto_match_payment(
        self,
        payment_id: int,
        bank_reference: str,
        bank_account: Optional[str] = None,
        reconciled_by: Optional[int] = None
    ) -> bool:
        """
        Automatically match a payment with a bank reference.
        
        Args:
            payment_id: Payment ID
            bank_reference: Bank statement reference
            bank_account: Bank account number
            reconciled_by: User ID who reconciled
            
        Returns:
            True if matched successfully, False otherwise
        """
        if not self.session:
            with get_session() as session:
                return self._auto_match_payment_impl(
                    session, payment_id, bank_reference, bank_account, reconciled_by
                )
        else:
            return self._auto_match_payment_impl(
                self.session, payment_id, bank_reference, bank_account, reconciled_by
            )
    
    def _auto_match_payment_impl(
        self,
        session: Session,
        payment_id: int,
        bank_reference: str,
        bank_account: Optional[str],
        reconciled_by: Optional[int]
    ) -> bool:
        """Internal implementation of auto-match."""
        payment = session.get(Payment, payment_id)
        if not payment:
            return False
        
        if payment.reconciled:
            return False
        
        # Reconcile payment
        payment.reconcile(
            bank_reference=bank_reference,
            bank_account=bank_account,
            reconciled_by=reconciled_by
        )
        
        return True

