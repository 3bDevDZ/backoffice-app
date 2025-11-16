"""Service for sending invoice PDFs via email."""
from io import BytesIO
from typing import Optional
from flask import current_app, render_template_string
from app.services.email_service import EmailService
from app.services.invoice_pdf_service import InvoicePDFService
from app.application.billing.invoices.queries.invoice_dto import InvoiceDTO


class InvoiceEmailService:
    """Service for sending invoice PDFs via email."""
    
    def __init__(self):
        self.email_service = EmailService()
        self.pdf_service = InvoicePDFService()
    
    def send_invoice(
        self,
        invoice_dto: InvoiceDTO,
        recipient_email: str,
        subject: Optional[str] = None,
        message: Optional[str] = None
    ) -> bool:
        """
        Send an invoice PDF via email.
        
        Args:
            invoice_dto: InvoiceDTO containing invoice information
            recipient_email: Email address of the recipient
            subject: Optional custom email subject
            message: Optional custom email message
            
        Returns:
            True if email sent successfully, False otherwise
        """
        # Generate PDF
        pdf_buffer = self.pdf_service.generate_invoice_pdf(invoice_dto)
        
        # Prepare email subject
        if not subject:
            subject = f"Facture {invoice_dto.number} - {current_app.config.get('COMPANY_NAME', 'GMFlow')}"
        
        # Prepare email body
        if not message:
            message = self._generate_default_message(invoice_dto)
        
        # Prepare HTML body
        html_body = self._generate_html_body(invoice_dto, message)
        
        # Prepare attachment
        pdf_buffer.seek(0)
        attachments = [{
            'filename': f"Facture_{invoice_dto.number}.pdf",
            'content': pdf_buffer
        }]
        
        # Send email
        return self.email_service.send_email(
            to=recipient_email,
            subject=subject,
            body_text=message,
            body_html=html_body,
            attachments=attachments
        )
    
    def _generate_default_message(self, invoice_dto: InvoiceDTO) -> str:
        """Generate default email message."""
        message = f"""Bonjour,

Veuillez trouver ci-joint la facture {invoice_dto.number}.

Détails de la facture:
- Date de facturation: {invoice_dto.invoice_date.strftime('%d/%m/%Y')}
- Date d'échéance: {invoice_dto.due_date.strftime('%d/%m/%Y')}
- Montant TTC: {invoice_dto.total:,.2f} €

"""
        
        if invoice_dto.remaining_amount > 0:
            message += f"Montant restant à payer: {invoice_dto.remaining_amount:,.2f} €\n\n"
        
        message += """Pour toute question concernant cette facture, n'hésitez pas à nous contacter.

Cordialement,
L'équipe GMFlow"""
        
        return message
    
    def _generate_html_body(self, invoice_dto: InvoiceDTO, text_message: str) -> str:
        """Generate HTML email body."""
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .invoice-info { background-color: #f3f4f6; padding: 15px; border-radius: 5px; margin: 20px 0; }
                .invoice-info p { margin: 5px 0; }
                .amount { font-size: 18px; font-weight: bold; color: #1a1a1a; }
            </style>
        </head>
        <body>
            <p>{{ message|replace('\n', '<br>')|safe }}</p>
            
            <div class="invoice-info">
                <p><strong>Facture:</strong> {{ invoice.number }}</p>
                <p><strong>Date de facturation:</strong> {{ invoice.invoice_date.strftime('%d/%m/%Y') }}</p>
                <p><strong>Date d'échéance:</strong> {{ invoice.due_date.strftime('%d/%m/%Y') }}</p>
                <p><strong>Montant TTC:</strong> <span class="amount">{{ invoice.total:,.2f }} €</span></p>
                {% if invoice.remaining_amount > 0 %}
                <p><strong>Montant restant:</strong> <span class="amount">{{ invoice.remaining_amount:,.2f }} €</span></p>
                {% endif %}
            </div>
            
            <p>La facture est jointe à cet email en format PDF.</p>
        </body>
        </html>
        """
        
        return render_template_string(
            html_template,
            message=text_message,
            invoice=invoice_dto
        )

