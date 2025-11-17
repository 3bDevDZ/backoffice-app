"""Service for managing payment reminders."""
from decimal import Decimal
from datetime import date, datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from app.domain.models.invoice import Invoice
from app.domain.models.payment import PaymentReminder
from app.infrastructure.db import get_session


class PaymentReminderService:
    """Service for managing payment reminders."""
    
    def __init__(self, session: Optional[Session] = None):
        """
        Initialize the service.
        
        Args:
            session: Optional SQLAlchemy session (if None, will create one)
        """
        self.session = session
    
    def get_invoices_needing_reminder(
        self,
        days_overdue: int = 7,
        reminder_type: str = 'first'
    ) -> List[Invoice]:
        """
        Get invoices that need a reminder.
        
        Args:
            days_overdue: Minimum days overdue to send reminder
            reminder_type: Type of reminder ('first', 'second', 'third', 'final')
            
        Returns:
            List of Invoice objects needing reminder
        """
        if not self.session:
            with get_session() as session:
                return self._get_invoices_needing_reminder_impl(
                    session, days_overdue, reminder_type
                )
        else:
            return self._get_invoices_needing_reminder_impl(
                self.session, days_overdue, reminder_type
            )
    
    def _get_invoices_needing_reminder_impl(
        self,
        session: Session,
        days_overdue: int,
        reminder_type: str
    ) -> List[Invoice]:
        """Internal implementation."""
        today = date.today()
        cutoff_date = today - timedelta(days=days_overdue)
        
        # Get overdue invoices
        invoices = session.query(Invoice).filter(
            Invoice.status.in_(["sent", "partially_paid", "overdue"]),
            Invoice.due_date <= cutoff_date,
            Invoice.remaining_amount > 0
        ).all()
        
        # Filter invoices that haven't received this type of reminder yet
        result = []
        for invoice in invoices:
            # Check if invoice already has this type of reminder
            existing_reminder = session.query(PaymentReminder).filter(
                PaymentReminder.invoice_id == invoice.id,
                PaymentReminder.reminder_type == reminder_type
            ).first()
            
            if not existing_reminder:
                result.append(invoice)
        
        return result
    
    def create_reminder(
        self,
        invoice_id: int,
        reminder_type: str,
        reminder_date: Optional[date] = None,
        sent_by: Optional[int] = None,
        notes: Optional[str] = None
    ) -> PaymentReminder:
        """
        Create a payment reminder.
        
        Args:
            invoice_id: Invoice ID
            reminder_type: Type of reminder ('first', 'second', 'third', 'final')
            reminder_date: Date of reminder (defaults to today)
            sent_by: User ID who sent the reminder
            notes: Additional notes
            
        Returns:
            PaymentReminder instance
        """
        if not self.session:
            with get_session() as session:
                reminder = self._create_reminder_impl(
                    session, invoice_id, reminder_type, reminder_date, sent_by, notes
                )
                session.commit()
                return reminder
        else:
            reminder = self._create_reminder_impl(
                self.session, invoice_id, reminder_type, reminder_date, sent_by, notes
            )
            return reminder
    
    def _create_reminder_impl(
        self,
        session: Session,
        invoice_id: int,
        reminder_type: str,
        reminder_date: Optional[date],
        sent_by: Optional[int],
        notes: Optional[str]
    ) -> PaymentReminder:
        """Internal implementation."""
        if reminder_date is None:
            reminder_date = date.today()
        
        reminder = PaymentReminder.create(
            invoice_id=invoice_id,
            reminder_type=reminder_type,
            reminder_date=reminder_date,
            sent_by=sent_by,
            notes=notes
        )
        
        session.add(reminder)
        session.flush()
        
        return reminder
    
    def mark_reminder_sent(
        self,
        reminder_id: int,
        sent_by: Optional[int] = None,
        email: bool = False,
        letter: bool = False
    ):
        """
        Mark a reminder as sent.
        
        Args:
            reminder_id: Reminder ID
            sent_by: User ID who sent the reminder
            email: Whether email was sent
            letter: Whether letter was sent
        """
        if not self.session:
            with get_session() as session:
                self._mark_reminder_sent_impl(session, reminder_id, sent_by, email, letter)
                session.commit()
        else:
            self._mark_reminder_sent_impl(self.session, reminder_id, sent_by, email, letter)
    
    def _mark_reminder_sent_impl(
        self,
        session: Session,
        reminder_id: int,
        sent_by: Optional[int],
        email: bool,
        letter: bool
    ):
        """Internal implementation."""
        reminder = session.get(PaymentReminder, reminder_id)
        if reminder:
            reminder.mark_sent(sent_by=sent_by, email=email, letter=letter)

