"""Celery tasks for sending emails."""
from celery import Task
from flask import current_app
from app.tasks.outbox_worker import celery_app
from app.services.email_service import email_service
from app.services.pdf_service import pdf_service
from app.application.common.mediator import mediator
from app.application.sales.quotes.queries.queries import GetQuoteByIdQuery
from app.infrastructure.db import get_session
from app.domain.models.quote import Quote
from app.domain.models.customer import Customer


class FlaskContextTask(Task):
    """Celery task with Flask application context."""
    def __call__(self, *args, **kwargs):
        with current_app.app_context():
            return self.run(*args, **kwargs)


# Update Celery app to use Flask context
celery_app.Task = FlaskContextTask


@celery_app.task(bind=True, max_retries=3)
def send_quote_email_task(self, quote_id: int, recipient_email: str, locale: str = 'fr'):
    """
    Celery task to send a quote email with PDF attachment.
    
    Args:
        quote_id: Quote ID
        recipient_email: Recipient email address
        locale: Locale for email content ('fr' or 'ar')
    """
    try:
        # Get quote data
        with get_session() as session:
            quote = session.get(Quote, quote_id)
            if not quote:
                raise ValueError(f"Quote with ID {quote_id} not found.")
            
            # Load customer
            customer = session.get(Customer, quote.customer_id)
            if not customer:
                raise ValueError(f"Customer with ID {quote.customer_id} not found.")
        
        # Get full quote DTO for PDF generation
        quote_dto = mediator.dispatch(GetQuoteByIdQuery(id=quote_id, include_lines=True))
        
        # Prepare quote data for PDF template
        quote_data = {
            'id': quote_dto.id,
            'number': quote_dto.number,
            'version': quote_dto.version,
            'customer': {
                'id': quote_dto.customer_id,
                'code': quote_dto.customer_code,
                'name': quote_dto.customer_name
            },
            'status': quote_dto.status,
            'valid_until': quote_dto.valid_until,
            'created_at': quote_dto.created_at,
            'subtotal': float(quote_dto.subtotal),
            'tax_amount': float(quote_dto.tax_amount),
            'total': float(quote_dto.total),
            'discount_percent': float(quote_dto.discount_percent),
            'discount_amount': float(quote_dto.discount_amount),
            'notes': quote_dto.notes,
            'lines': [
                {
                    'product_code': line.product_code,
                    'product_name': line.product_name,
                    'quantity': float(line.quantity),
                    'unit_price': float(line.unit_price),
                    'discount_percent': float(line.discount_percent),
                    'discount_amount': float(line.discount_amount),
                    'tax_rate': float(line.tax_rate),
                    'line_total_ht': float(line.line_total_ht),
                    'line_total_ttc': float(line.line_total_ttc)
                }
                for line in quote_dto.lines
            ] if quote_dto.lines else []
        }
        
        # Generate PDF
        quote_pdf = pdf_service.generate_quote_pdf(quote_data)
        
        # Send email
        email_service.send_quote_email(
            to=recipient_email,
            quote_number=quote_dto.number,
            quote_pdf=quote_pdf,
            customer_name=quote_dto.customer_name,
            locale=locale
        )
        
        return {'status': 'success', 'quote_id': quote_id, 'recipient': recipient_email}
        
    except Exception as e:
        # Log error
        current_app.logger.error(f"Failed to send quote email for quote {quote_id}: {e}")
        
        # Retry if not exceeded max retries
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=60 * (self.request.retries + 1))  # Exponential backoff
        
        # If max retries exceeded, return error
        return {'status': 'error', 'quote_id': quote_id, 'error': str(e)}


@celery_app.task(bind=True, max_retries=3)
def expire_quotes_task(self):
    """
    Celery task to automatically expire quotes that have passed their valid_until date.
    This should be scheduled to run daily (e.g., via Celery Beat).
    """
    try:
        from datetime import date
        from app.domain.models.quote import Quote
        
        with get_session() as session:
            # Find quotes that should be expired
            today = date.today()
            quotes_to_expire = session.query(Quote).filter(
                Quote.status.in_(['draft', 'sent']),
                Quote.valid_until < today
            ).all()
            
            expired_count = 0
            for quote in quotes_to_expire:
                try:
                    quote.expire()
                    expired_count += 1
                except Exception as e:
                    current_app.logger.error(f"Failed to expire quote {quote.id}: {e}")
            
            session.commit()
            
            return {'status': 'success', 'expired_count': expired_count}
            
    except Exception as e:
        current_app.logger.error(f"Failed to expire quotes: {e}")
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=300)  # Retry after 5 minutes
        return {'status': 'error', 'error': str(e)}

