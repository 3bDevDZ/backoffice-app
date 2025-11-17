"""Service for sending payment reminder emails."""
from io import BytesIO
from typing import Optional
from flask import current_app, render_template_string
from app.services.email_service import EmailService
from app.services.payment_reminder_pdf_service import PaymentReminderPDFService
from app.application.billing.invoices.queries.invoice_dto import InvoiceDTO


class PaymentReminderEmailService:
    """Service for sending payment reminder emails."""
    
    def __init__(self):
        self.email_service = EmailService()
        self.pdf_service = PaymentReminderPDFService()
    
    def send_reminder(
        self,
        invoice_dto: InvoiceDTO,
        reminder_type: str,
        recipient_email: str,
        subject: Optional[str] = None,
        message: Optional[str] = None,
        include_pdf: bool = True
    ) -> bool:
        """
        Send a payment reminder email.
        
        Args:
            invoice_dto: InvoiceDTO containing invoice information
            reminder_type: Type of reminder ('first', 'second', 'third', 'final')
            recipient_email: Email address of the recipient
            subject: Optional custom email subject
            message: Optional custom email message
            include_pdf: Whether to include PDF attachment
            
        Returns:
            True if email sent successfully, False otherwise
        """
        # Generate PDF if needed
        pdf_buffer = None
        if include_pdf:
            pdf_buffer = self.pdf_service.generate_reminder_pdf(invoice_dto, reminder_type)
        
        # Prepare email subject
        if not subject:
            subject = self._generate_subject(invoice_dto, reminder_type)
        
        # Prepare email body
        if not message:
            message = self._generate_default_message(invoice_dto, reminder_type)
        
        # Prepare HTML body
        html_body = self._generate_html_body(invoice_dto, reminder_type, message)
        
        # Prepare attachments
        attachments = []
        if pdf_buffer:
            pdf_buffer.seek(0)
            attachments.append({
                'filename': f"Rappel_Paiement_{invoice_dto.number}.pdf",
                'content': pdf_buffer
            })
        
        # Send email
        return self.email_service.send_email(
            to=recipient_email,
            subject=subject,
            body_text=message,
            body_html=html_body,
            attachments=attachments
        )
    
    def _generate_subject(self, invoice_dto: InvoiceDTO, reminder_type: str) -> str:
        """Generate email subject based on reminder type."""
        company_name = current_app.config.get('COMPANY_NAME', 'GMFlow')
        
        reminder_labels = {
            'first': 'Premier rappel',
            'second': 'Deuxième rappel',
            'third': 'Troisième rappel',
            'final': 'Rappel final'
        }
        
        label = reminder_labels.get(reminder_type, 'Rappel')
        return f"{label} - Facture {invoice_dto.number} - {company_name}"
    
    def _generate_default_message(self, invoice_dto: InvoiceDTO, reminder_type: str) -> str:
        """Generate default email message."""
        from datetime import date
        today = date.today()
        days_overdue = (today - invoice_dto.due_date).days
        
        reminder_labels = {
            'first': 'premier rappel',
            'second': 'deuxième rappel',
            'third': 'troisième rappel',
            'final': 'dernier rappel'
        }
        
        label = reminder_labels.get(reminder_type, 'rappel')
        
        message = f"""Bonjour,

Nous vous contactons concernant le {label} de paiement de la facture {invoice_dto.number}.

Détails de la facture:
- Date de facturation: {invoice_dto.invoice_date.strftime('%d/%m/%Y')}
- Date d'échéance: {invoice_dto.due_date.strftime('%d/%m/%Y')}
- Montant TTC: {invoice_dto.total:,.2f} €
- Montant restant à payer: {invoice_dto.remaining_amount:,.2f} €
"""
        
        if days_overdue > 0:
            message += f"- Jours de retard: {days_overdue} jour(s)\n"
        
        message += f"""
Nous vous remercions de bien vouloir régler cette facture dans les plus brefs délais.

Pour toute question concernant cette facture, n'hésitez pas à nous contacter.

Cordialement,
L'équipe GMFlow"""
        
        return message
    
    def _generate_html_body(self, invoice_dto: InvoiceDTO, reminder_type: str, text_message: str) -> str:
        """Generate HTML email body."""
        from datetime import date
        today = date.today()
        days_overdue = (today - invoice_dto.due_date).days
        
        reminder_labels = {
            'first': 'Premier rappel',
            'second': 'Deuxième rappel',
            'third': 'Troisième rappel',
            'final': 'Rappel final'
        }
        
        label = reminder_labels.get(reminder_type, 'Rappel')
        
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .reminder-header { background-color: #fef3c7; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #f59e0b; }
                .invoice-info { background-color: #f3f4f6; padding: 15px; border-radius: 5px; margin: 20px 0; }
                .invoice-info p { margin: 5px 0; }
                .amount { font-size: 18px; font-weight: bold; color: #dc2626; }
                .overdue { color: #dc2626; font-weight: bold; }
            </style>
        </head>
        <body>
            <div class="reminder-header">
                <h2 style="margin: 0; color: #92400e;">{{ label }}</h2>
            </div>
            
            <p>{{ message|replace('\n', '<br>')|safe }}</p>
            
            <div class="invoice-info">
                <p><strong>Facture:</strong> {{ invoice.number }}</p>
                <p><strong>Date de facturation:</strong> {{ invoice.invoice_date.strftime('%d/%m/%Y') }}</p>
                <p><strong>Date d'échéance:</strong> {{ invoice.due_date.strftime('%d/%m/%Y') }}</p>
                <p><strong>Montant TTC:</strong> {{ invoice.total:,.2f }} €</p>
                <p><strong>Montant restant:</strong> <span class="amount">{{ invoice.remaining_amount:,.2f }} €</span></p>
                {% if days_overdue > 0 %}
                <p class="overdue">Jours de retard: {{ days_overdue }} jour(s)</p>
                {% endif %}
            </div>
            
            {% if include_pdf %}
            <p>Un rappel de paiement est joint à cet email en format PDF.</p>
            {% endif %}
        </body>
        </html>
        """
        
        return render_template_string(
            html_template,
            message=text_message,
            invoice=invoice_dto,
            label=label,
            days_overdue=days_overdue,
            include_pdf=True
        )

