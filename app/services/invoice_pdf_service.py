"""Service for generating legal-compliant invoice PDFs (Article 289 CGI)."""
from io import BytesIO
from decimal import Decimal
from datetime import date, datetime
from typing import Optional
from flask import current_app
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT, TA_LEFT, TA_CENTER
from reportlab.pdfgen import canvas

from app.application.billing.invoices.queries.invoice_dto import InvoiceDTO
from app.services.pdf_service import PDFService


class InvoicePDFService(PDFService):
    """Service for generating legal-compliant invoice PDFs using the same template as orders."""
    
    def __init__(self):
        super().__init__()  # Initialize PDFService to get styles and helpers
        self._setup_invoice_styles()
    
    def _setup_invoice_styles(self):
        """Setup custom paragraph styles specific to invoices."""
        # Invoice status badge styles (similar to order status badges)
        self.styles.add(ParagraphStyle(
            name='InvoiceStatusBadge',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#065f46'),
            backColor=colors.HexColor('#d1fae5'),
            borderColor=colors.HexColor('#10b981'),
            borderWidth=1,
            borderPadding=3,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            leading=12
        ))
    
    def _create_invoice_status_badge(self, status: str) -> Paragraph:
        """Create a status badge for invoice status."""
        status_labels = {
            'draft': 'BROUILLON',
            'validated': 'VALIDÉE',
            'sent': 'ENVOYÉE',
            'partially_paid': 'PARTIELLEMENT PAYÉE',
            'paid': 'PAYÉE',
            'overdue': 'IMPAYÉE',
            'canceled': 'ANNULÉE'
        }
        status_text = status_labels.get(status.lower(), status.upper())
        
        badge_colors = {
            'draft': {'bg': '#fef3c7', 'text': '#92400e', 'border': '#fbbf24'},
            'validated': {'bg': '#d1fae5', 'text': '#065f46', 'border': '#10b981'},
            'sent': {'bg': '#dbeafe', 'text': '#1e40af', 'border': '#3b82f6'},
            'partially_paid': {'bg': '#fef3c7', 'text': '#92400e', 'border': '#fbbf24'},
            'paid': {'bg': '#a7f3d0', 'text': '#064e3b', 'border': '#059669'},
            'overdue': {'bg': '#fee2e2', 'text': '#991b1b', 'border': '#ef4444'},
            'canceled': {'bg': '#e5e7eb', 'text': '#4b5563', 'border': '#9ca3af'}
        }
        colors_dict = badge_colors.get(status.lower(), badge_colors['draft'])
        
        badge_style = ParagraphStyle(
            name='InvoiceStatusBadge',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor(colors_dict['text']),
            backColor=colors.HexColor(colors_dict['bg']),
            borderColor=colors.HexColor(colors_dict['border']),
            borderWidth=1,
            borderPadding=3,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            leading=12
        )
        return Paragraph(f"<b>{status_text}</b>", badge_style)
    
    def generate_invoice_pdf(self, invoice_dto: InvoiceDTO) -> BytesIO:
        """
        Generate a legal-compliant PDF invoice using the same template as orders.
        Follows Article 289 CGI requirements.
        
        Args:
            invoice_dto: InvoiceDTO containing invoice information
            
        Returns:
            BytesIO object containing the PDF data
        """
        # Import helper functions (with fallback)
        try:
            from .pdf_service_helper import get_company_info
        except ImportError:
            # Fallback implementation
            def get_company_info():
                return {
                    'name': current_app.config.get('COMPANY_NAME', 'CommerceFlow'),
                    'address': current_app.config.get('COMPANY_ADDRESS', '123 Rue de la Commerce'),
                    'postal_code': current_app.config.get('COMPANY_POSTAL_CODE', '69000'),
                    'city': current_app.config.get('COMPANY_CITY', 'Lyon'),
                    'country': current_app.config.get('COMPANY_COUNTRY', 'France'),
                    'phone': current_app.config.get('COMPANY_PHONE', '+33 4 XX XX XX XX'),
                    'email': current_app.config.get('COMPANY_EMAIL', 'contact@commerceflow.com'),
                    'website': current_app.config.get('COMPANY_WEBSITE', 'www.commerceflow.com')
                }
        
        pdf_buffer = BytesIO()
        # Professional margins: 20mm all around
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=15*mm,  # Smaller top margin for header
            bottomMargin=20*mm
        )
        
        # Set PDF metadata
        doc.title = f"Facture {invoice_dto.number} - {invoice_dto.customer_name}"
        doc.author = current_app.config.get('COMPANY_NAME', 'CommerceFlow')
        doc.subject = "Facture commerciale"
        
        # Build story (content)
        story = []
        
        # ========== PROFESSIONAL HEADER ==========
        company_info = get_company_info()
        
        # Header table: Left (Company) | Right (Invoice title and info)
        header_data = [
            [
                Paragraph(f"<b>{company_info['name']}</b>", ParagraphStyle(
                    name='CompanyName',
                    parent=self.styles['Normal'],
                    fontSize=18,
                    textColor=colors.HexColor('#1a1a1a'),
                    fontName='Helvetica-Bold',
                    leading=22
                )),
                Paragraph(f"<b>FACTURE</b>", ParagraphStyle(
                    name='InvoiceTitle',
                    parent=self.styles['Normal'],
                    fontSize=28,
                    textColor=colors.HexColor('#1a1a1a'),
                    fontName='Helvetica-Bold',
                    leading=34,
                    alignment=TA_RIGHT
                ))
            ],
            [
                '',  # Empty cell for spacing
                Paragraph(
                    f"N° Facture: <b>{invoice_dto.number}</b><br/>"
                    f"Date facturation: {self._format_date(invoice_dto.invoice_date)}<br/>"
                    f"Date échéance: {self._format_date(invoice_dto.due_date)}",
                    ParagraphStyle(
                        name='InvoiceInfo',
                        parent=self.styles['Normal'],
                        fontSize=10,
                        textColor=colors.HexColor('#4a4a4a'),
                        alignment=TA_RIGHT,
                        leading=12
                    )
                )
            ]
        ]
        
        header_table = Table(header_data, colWidths=[100*mm, 70*mm])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
        ]))
        story.append(header_table)
        
        # Accent bar (optional colored bar)
        accent_bar = Table([['']], colWidths=[170*mm], rowHeights=[4*mm])
        accent_bar.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#2563EB')),  # Blue for invoices
            ('LINEBELOW', (0, 0), (0, 0), 0, colors.HexColor('#2563EB')),
        ]))
        story.append(accent_bar)
        story.append(Spacer(1, 20*mm))
        
        # ========== TWO-COLUMN COMPANY/CLIENT INFO ==========
        company_info = get_company_info()
        
        # Build company address with legal info
        company_address_lines = [
            company_info['address'],
            f"{company_info['postal_code']} {company_info['city']}",
            company_info['country']
        ]
        # Add SIRET and VAT if available in config
        if current_app.config.get('COMPANY_SIRET'):
            company_address_lines.append(f"SIRET: {current_app.config.get('COMPANY_SIRET')}")
        if current_app.config.get('COMPANY_VAT_NUMBER'):
            company_address_lines.append(f"TVA: {current_app.config.get('COMPANY_VAT_NUMBER')}")
        company_address = '<br/>'.join([line for line in company_address_lines if line])
        
        # Build customer info with legal info (Article 289 CGI)
        customer_info_lines = [f"<b>{invoice_dto.customer_name or 'N/A'}</b>"]
        if invoice_dto.customer_code:
            customer_info_lines.append(f"Code: {invoice_dto.customer_code}")
        if invoice_dto.siret:
            customer_info_lines.append(f"SIRET: {invoice_dto.siret}")
        if invoice_dto.vat_number:
            customer_info_lines.append(f"N° TVA: {invoice_dto.vat_number}")
        customer_info = '<br/>'.join(customer_info_lines)
        
        # Two-column layout
        company_client_data = [
            [
                Paragraph("<b>FACTURÉ PAR</b>", ParagraphStyle(
                    name='SectionTitle',
                    parent=self.styles['Normal'],
                    fontSize=11,
                    textColor=colors.HexColor('#2d3748'),
                    fontName='Helvetica-Bold',
                    leading=13
                )),
                Paragraph("<b>FACTURÉ À</b>", ParagraphStyle(
                    name='SectionTitle',
                    parent=self.styles['Normal'],
                    fontSize=11,
                    textColor=colors.HexColor('#2d3748'),
                    fontName='Helvetica-Bold',
                    leading=13
                ))
            ],
            [
                Paragraph(company_info['name'], self.styles['CustomNormal']),
                Paragraph(customer_info, self.styles['CustomNormal'])
            ],
            [
                Paragraph(company_address, ParagraphStyle(
                    name='Address',
                    parent=self.styles['Normal'],
                    fontSize=9,
                    textColor=colors.HexColor('#1a1a1a'),
                    leading=11
                )),
                ''  # Customer address if available
            ],
            [
                Paragraph(f"Tél: {company_info['phone']}", ParagraphStyle(
                    name='Contact',
                    parent=self.styles['Normal'],
                    fontSize=9,
                    textColor=colors.HexColor('#6b7280'),
                    leading=11
                )),
                ''
            ],
            [
                Paragraph(f"Email: {company_info['email']}", ParagraphStyle(
                    name='Contact',
                    parent=self.styles['Normal'],
                    fontSize=9,
                    textColor=colors.HexColor('#6b7280'),
                    leading=11
                )),
                ''
            ]
        ]
        
        company_client_table = Table(company_client_data, colWidths=[80*mm, 80*mm])
        company_client_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('TOPPADDING', (0, 0), (-1, 0), 6),
            ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.HexColor('#e2e8f0')),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 3),
            ('TOPPADDING', (0, 1), (-1, -1), 3),
        ]))
        story.append(company_client_table)
        story.append(Spacer(1, 15*mm))
        
        # ========== INVOICE DETAILS SECTION WITH STATUS BADGE ==========
        status = invoice_dto.status
        status_badge = self._create_invoice_status_badge(status)
        
        # Invoice details in grid layout
        invoice_details_data = [
            ['Statut:', status_badge],
        ]
        
        if invoice_dto.order_number:
            invoice_details_data.append(['N° Commande:', invoice_dto.order_number])
        
        if invoice_dto.validated_at:
            invoice_details_data.append(['Validée le:', self._format_date(invoice_dto.validated_at)])
        
        if invoice_dto.sent_at:
            invoice_details_data.append(['Envoyée le:', self._format_date(invoice_dto.sent_at)])
        
        invoice_details_table = Table(invoice_details_data, colWidths=[60*mm, 110*mm])
        invoice_details_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('FONTSIZE', (1, 0), (1, -1), 9),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#6b7280')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#1a1a1a')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#ffffff')),
        ]))
        story.append(invoice_details_table)
        story.append(Spacer(1, 20*mm))
        
        # ========== INVOICE LINES TABLE ==========
        if invoice_dto.lines:
            story.append(Paragraph("Lignes de facture", self.styles['CustomHeading']))
            
            # Table header
            table_data = [[
                'Produit',
                'Qté',
                'Prix unit.',
                'Remise %',
                'Total HT',
                'TVA',
                'Total TTC'
            ]]
            
            # Table rows
            for line in invoice_dto.lines:
                discount_str = f"{float(line.discount_percent):.2f}%" if line.discount_percent > 0 else "-"
                product_code = line.product_code or ''
                product_name = line.product_name or 'N/A'
                
                # Add variant info if present
                if line.variant_name:
                    product_name += f" - {line.variant_name}"
                    if line.variant_code:
                        product_code = line.variant_code
                
                # Format product name with code on new line in smaller font using Paragraph
                if product_code:
                    product_cell = Paragraph(
                        f"<b>{product_name}</b><br/><font size='7'>{product_code}</font>",
                        self.styles['Normal']
                    )
                else:
                    product_cell = Paragraph(f"<b>{product_name}</b>", self.styles['Normal'])
                
                table_data.append([
                    product_cell,
                    f"{float(line.quantity):.3f}",
                    f"{float(line.unit_price):.2f} €",
                    discount_str,
                    f"{float(line.line_total_ht):.2f} €",
                    f"{float(line.tax_rate):.2f}%",
                    f"{float(line.line_total_ttc):.2f} €"
                ])
            
            # Create table
            invoice_table = Table(table_data, colWidths=[60*mm, 20*mm, 25*mm, 20*mm, 25*mm, 20*mm, 30*mm])
            invoice_table.setStyle(TableStyle([
                # Header
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563EB')),  # Blue for invoices
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),  # Numbers right-aligned
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, 0), 12),
                # Data rows
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                ('TOPPADDING', (0, 1), (-1, -1), 8),
            ]))
            story.append(invoice_table)
            story.append(Spacer(1, 10*mm))
        
        # ========== PROFESSIONAL TOTALS SECTION ==========
        subtotal = float(invoice_dto.subtotal)
        discount_amount = float(invoice_dto.discount_amount)
        tax_amount = float(invoice_dto.tax_amount)
        total = float(invoice_dto.total)
        paid_amount = float(invoice_dto.paid_amount) if invoice_dto.paid_amount else 0
        remaining_amount = float(invoice_dto.remaining_amount) if invoice_dto.remaining_amount else total
        
        totals_data = [
            ['Sous-total HT:', f"{subtotal:.2f} €"],
        ]
        
        if discount_amount > 0:
            discount_percent = float(invoice_dto.discount_percent)
            totals_data.append([f'Remise document ({discount_percent:.2f}%):', f"-{discount_amount:.2f} €"])
            totals_data.append(['Total HT:', f"{subtotal - discount_amount:.2f} €"])
        else:
            totals_data.append(['Total HT:', f"{subtotal:.2f} €"])
        
        totals_data.append(['TVA:', f"{tax_amount:.2f} €"])
        
        # Use Paragraph for bold formatting in totals
        totals_data.append([
            Paragraph('<b>TOTAL TTC:</b>', self.styles['Normal']),
            Paragraph(f'<b>{total:.2f} €</b>', self.styles['Normal'])
        ])
        
        # Payment information if applicable
        if paid_amount > 0:
            totals_data.append(['Montant payé:', f"-{paid_amount:.2f} €"])
            totals_data.append([
                Paragraph('<b>MONTANT RESTANT:</b>', self.styles['Normal']),
                Paragraph(f'<b>{remaining_amount:.2f} €</b>', self.styles['Normal'])
            ])
        
        # Professional totals box - right-aligned
        totals_table = Table(totals_data, colWidths=[100*mm, 70*mm])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -2), 10),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            ('TEXTCOLOR', (0, 0), (-1, -2), colors.HexColor('#1a1a1a')),
            ('LINEABOVE', (0, -2), (-1, -2), 0.5, colors.HexColor('#d1d5db')),
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor('#2563EB')),  # Blue accent line
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#ffffff')),  # White background
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),  # Border around box
            ('BACKGROUND', (0, 0), (-1, -2), colors.HexColor('#f9fafb')),  # Light gray background
        ]))
        
        # Wrap totals in a container table to right-align it
        totals_container = Table([[totals_table]], colWidths=[170*mm])
        totals_container.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (0, 0), 'TOP'),
        ]))
        story.append(totals_container)
        story.append(Spacer(1, 15*mm))
        
        # ========== LEGAL MENTIONS (Article 289 CGI) ==========
        if invoice_dto.legal_mention:
            story.append(Paragraph("Mentions légales", self.styles['CustomHeading']))
            story.append(Paragraph(
                invoice_dto.legal_mention.replace('\n', '<br/>'),
                ParagraphStyle(
                    name='LegalMention',
                    parent=self.styles['Normal'],
                    fontSize=8,
                    textColor=colors.HexColor('#4b5563'),
                    leading=11
                )
            ))
            story.append(Spacer(1, 10*mm))
        
        # Payment terms (Article 289 CGI requirement)
        story.append(Paragraph("Conditions de paiement", self.styles['CustomHeading']))
        payment_terms = f"Date d'échéance: {self._format_date(invoice_dto.due_date)}."
        if paid_amount > 0:
            payment_terms += f"<br/>Montant déjà payé: {paid_amount:.2f} €. Montant restant: {remaining_amount:.2f} €."
        else:
            payment_terms += "<br/>En cas de retard de paiement, une pénalité de 3 fois le taux d'intérêt légal sera appliquée, ainsi qu'une indemnité forfaitaire de 40€ pour frais de recouvrement."
        story.append(Paragraph(
            payment_terms,
            ParagraphStyle(
                name='PaymentTerms',
                parent=self.styles['Normal'],
                fontSize=9,
                textColor=colors.HexColor('#1a1a1a'),
                leading=12
            )
        ))
        story.append(Spacer(1, 10*mm))
        
        # Notes
        if invoice_dto.notes:
            story.append(Paragraph("Notes", self.styles['CustomHeading']))
            story.append(Paragraph(
                invoice_dto.notes.replace('\n', '<br/>'),
                self.styles['CustomNormal']
            ))
            story.append(Spacer(1, 10*mm))
        
        # Footer
        footer_text = "Facture générée automatiquement par le système GMFlow."
        if invoice_dto.created_at:
            footer_text += f"<br/>Générée le {self._format_date(invoice_dto.created_at)}"
        story.append(Paragraph(footer_text, self.styles['CustomFooter']))
        
        # Build PDF
        doc.build(story)
        pdf_buffer.seek(0)
        
        return pdf_buffer
