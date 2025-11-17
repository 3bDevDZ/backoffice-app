"""Service for generating payment reminder PDFs."""
from io import BytesIO
from decimal import Decimal
from datetime import date, datetime
from typing import Optional
from flask import current_app
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT, TA_LEFT, TA_CENTER

from app.application.billing.invoices.queries.invoice_dto import InvoiceDTO
from app.services.pdf_service import PDFService


class PaymentReminderPDFService(PDFService):
    """Service for generating payment reminder PDFs."""
    
    def __init__(self):
        super().__init__()
        self._setup_reminder_styles()
    
    def _setup_reminder_styles(self):
        """Setup custom paragraph styles specific to payment reminders."""
        # Reminder type badge styles
        self.styles.add(ParagraphStyle(
            name='ReminderTypeBadge',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#92400e'),
            backColor=colors.HexColor('#fef3c7'),
            borderColor=colors.HexColor('#fbbf24'),
            borderWidth=1,
            borderPadding=4,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            leading=14
        ))
        
        # Overdue warning style
        self.styles.add(ParagraphStyle(
            name='OverdueWarning',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#991b1b'),
            backColor=colors.HexColor('#fee2e2'),
            borderColor=colors.HexColor('#ef4444'),
            borderWidth=1,
            borderPadding=8,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold',
            leading=14
        ))
    
    def generate_reminder_pdf(
        self,
        invoice_dto: InvoiceDTO,
        reminder_type: str
    ) -> BytesIO:
        """
        Generate a payment reminder PDF.
        
        Args:
            invoice_dto: InvoiceDTO containing invoice information
            reminder_type: Type of reminder ('first', 'second', 'third', 'final')
            
        Returns:
            BytesIO buffer containing the PDF
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )
        
        story = []
        
        # Header
        story.extend(self._create_header(invoice_dto, reminder_type))
        story.append(Spacer(1, 10*mm))
        
        # Reminder message
        story.extend(self._create_reminder_message(invoice_dto, reminder_type))
        story.append(Spacer(1, 10*mm))
        
        # Invoice details
        story.extend(self._create_invoice_details(invoice_dto))
        story.append(Spacer(1, 10*mm))
        
        # Payment information
        story.extend(self._create_payment_information(invoice_dto))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer
    
    def _create_header(self, invoice_dto: InvoiceDTO, reminder_type: str) -> list:
        """Create header with company info and reminder type."""
        company_name = current_app.config.get('COMPANY_NAME', 'GMFlow')
        company_address = current_app.config.get('COMPANY_ADDRESS', '')
        company_phone = current_app.config.get('COMPANY_PHONE', '')
        company_email = current_app.config.get('COMPANY_EMAIL', '')
        
        reminder_labels = {
            'first': 'PREMIER RAPPEL DE PAIEMENT',
            'second': 'DEUXIÈME RAPPEL DE PAIEMENT',
            'third': 'TROISIÈME RAPPEL DE PAIEMENT',
            'final': 'RAPPEL FINAL DE PAIEMENT'
        }
        
        reminder_label = reminder_labels.get(reminder_type, 'RAPPEL DE PAIEMENT')
        
        # Company info
        company_data = [
            [Paragraph(f"<b>{company_name}</b>", self.styles['Heading1'])],
            [company_address] if company_address else [],
            [f"Tél: {company_phone}"] if company_phone else [],
            [f"Email: {company_email}"] if company_email else []
        ]
        
        company_table = Table(company_data, colWidths=[150*mm])
        company_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), TA_LEFT),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 0), (0, 0), 16),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        
        # Reminder badge
        reminder_badge = Paragraph(f"<b>{reminder_label}</b>", self.styles['ReminderTypeBadge'])
        reminder_table = Table([[reminder_badge]], colWidths=[150*mm])
        reminder_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), TA_CENTER),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        return [company_table, Spacer(1, 5*mm), reminder_table]
    
    def _create_reminder_message(self, invoice_dto: InvoiceDTO, reminder_type: str) -> list:
        """Create reminder message."""
        from datetime import date
        today = date.today()
        days_overdue = (today - invoice_dto.due_date).days
        
        # Get customer name
        customer_name = invoice_dto.customer_name or f"Client {invoice_dto.customer_code or invoice_dto.customer_id}"
        
        message = f"""Bonjour {customer_name},

Nous vous contactons concernant le paiement de la facture {invoice_dto.number}."""
        
        if days_overdue > 0:
            message += f"\n\nCette facture est en retard de {days_overdue} jour(s)."
        
        message += f"""

Nous vous remercions de bien vouloir régler cette facture dans les plus brefs délais.

Pour toute question concernant cette facture, n'hésitez pas à nous contacter."""
        
        # Add overdue warning if applicable
        story = [Paragraph(message, self.styles['Normal'])]
        
        if days_overdue > 30:
            warning = f"<b>ATTENTION:</b> Cette facture est en retard de {days_overdue} jours. Veuillez procéder au règlement immédiatement."
            story.append(Spacer(1, 5*mm))
            story.append(Paragraph(warning, self.styles['OverdueWarning']))
        
        return story
    
    def _create_invoice_details(self, invoice_dto: InvoiceDTO) -> list:
        """Create invoice details table."""
        data = [
            ['Facture:', invoice_dto.number],
            ['Date de facturation:', invoice_dto.invoice_date.strftime('%d/%m/%Y')],
            ['Date d\'échéance:', invoice_dto.due_date.strftime('%d/%m/%Y')],
            ['Montant TTC:', f"{invoice_dto.total:,.2f} €"],
            ['Montant payé:', f"{invoice_dto.paid_amount:,.2f} €"],
            ['Montant restant:', f"<b>{invoice_dto.remaining_amount:,.2f} €</b>"]
        ]
        
        table = Table(data, colWidths=[60*mm, 90*mm])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), TA_LEFT),
            ('ALIGN', (1, 0), (1, -1), TA_RIGHT),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
        ]))
        
        return [table]
    
    def _create_payment_information(self, invoice_dto: InvoiceDTO) -> list:
        """Create payment information section."""
        company_name = current_app.config.get('COMPANY_NAME', 'GMFlow')
        company_bank = current_app.config.get('COMPANY_BANK', '')
        company_iban = current_app.config.get('COMPANY_IBAN', '')
        company_bic = current_app.config.get('COMPANY_BIC', '')
        
        info = f"""<b>Informations de paiement:</b>

Veuillez effectuer le virement à l'ordre de {company_name}."""
        
        if company_bank:
            info += f"\nBanque: {company_bank}"
        if company_iban:
            info += f"\nIBAN: {company_iban}"
        if company_bic:
            info += f"\nBIC: {company_bic}"
        
        info += f"\n\nMerci de mentionner la référence de facture: {invoice_dto.number}"
        
        return [Paragraph(info, self.styles['Normal'])]

