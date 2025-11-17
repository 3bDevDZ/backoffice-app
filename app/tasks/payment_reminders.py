"""Celery tasks for automatic payment reminders."""
from celery import Task
from flask import current_app
from datetime import date, timedelta
from app.tasks.outbox_worker import celery_app
from app.services.payment_reminder_service import PaymentReminderService
from app.services.payment_reminder_email_service import PaymentReminderEmailService
from app.application.common.mediator import mediator
from app.application.billing.invoices.queries.queries import GetInvoiceByIdQuery
from app.infrastructure.db import get_session
from app.domain.models.invoice import Invoice
from app.domain.models.customer import Customer


class FlaskContextTask(Task):
    """Celery task with Flask application context."""
    def __call__(self, *args, **kwargs):
        with current_app.app_context():
            return self.run(*args, **kwargs)


# Update Celery app to use Flask context
celery_app.Task = FlaskContextTask


@celery_app.task(bind=True, max_retries=3)
def send_payment_reminders_task(self):
    """
    Send automatic payment reminders for overdue invoices.
    Runs daily and checks for invoices needing reminders at J+7, J+15, and J+30.
    """
    with get_session() as session:
        reminder_service = PaymentReminderService(session=session)
        email_service = PaymentReminderEmailService()
        
        # Define reminder schedule: (days_overdue, reminder_type)
        reminder_schedule = [
            (7, 'first'),   # J+7: First reminder
            (15, 'second'),  # J+15: Second reminder
            (30, 'third'),  # J+30: Third reminder
            (60, 'final')   # J+60: Final reminder
        ]
        
        results = {
            'sent': [],
            'failed': [],
            'skipped': []
        }
        
        for days_overdue, reminder_type in reminder_schedule:
            # Get invoices needing this type of reminder
            invoices = reminder_service.get_invoices_needing_reminder(
                days_overdue=days_overdue,
                reminder_type=reminder_type
            )
            
            for invoice in invoices:
                try:
                    # Get invoice DTO
                    query = GetInvoiceByIdQuery(id=invoice.id)
                    invoice_dto = mediator.dispatch(query)
                    
                    if not invoice_dto:
                        results['skipped'].append({
                            'invoice_id': invoice.id,
                            'reason': 'Invoice not found'
                        })
                        continue
                    
                    # Get customer email
                    customer = session.get(Customer, invoice.customer_id)
                    if not customer or not customer.email:
                        results['skipped'].append({
                            'invoice_id': invoice.id,
                            'invoice_number': invoice.number,
                            'reason': 'Customer email not found'
                        })
                        continue
                    
                    # Create reminder record
                    reminder = reminder_service.create_reminder(
                        invoice_id=invoice.id,
                        reminder_type=reminder_type,
                        reminder_date=date.today()
                    )
                    
                    # Send reminder email
                    success = email_service.send_reminder(
                        invoice_dto=invoice_dto,
                        reminder_type=reminder_type,
                        recipient_email=customer.email,
                        include_pdf=True
                    )
                    
                    if success:
                        # Mark reminder as sent
                        reminder_service.mark_reminder_sent(
                            reminder_id=reminder.id,
                            email=True
                        )
                        
                        # Update invoice status to overdue if not already
                        if invoice.status == 'sent':
                            invoice.status = 'overdue'
                        
                        results['sent'].append({
                            'invoice_id': invoice.id,
                            'invoice_number': invoice.number,
                            'reminder_type': reminder_type,
                            'customer_email': customer.email
                        })
                    else:
                        results['failed'].append({
                            'invoice_id': invoice.id,
                            'invoice_number': invoice.number,
                            'reminder_type': reminder_type,
                            'reason': 'Email send failed'
                        })
                
                except Exception as e:
                    results['failed'].append({
                        'invoice_id': invoice.id,
                        'invoice_number': getattr(invoice, 'number', 'N/A'),
                        'reminder_type': reminder_type,
                        'reason': str(e)
                    })
                    current_app.logger.error(
                        f"Error sending payment reminder for invoice {invoice.id}: {str(e)}",
                        exc_info=True
                    )
        
        session.commit()
        
        current_app.logger.info(
            f"Payment reminders task completed: "
            f"{len(results['sent'])} sent, "
            f"{len(results['failed'])} failed, "
            f"{len(results['skipped'])} skipped"
        )
        
        return results

