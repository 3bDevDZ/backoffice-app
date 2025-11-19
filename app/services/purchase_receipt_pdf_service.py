"""Service for generating purchase receipt PDFs."""
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

from app.application.purchases.receipts.queries.receipt_dto import PurchaseReceiptDTO
from app.services.pdf_service import PDFService


class PurchaseReceiptPDFService(PDFService):
    """Service for generating purchase receipt PDFs using the same template as invoices and orders."""
    
    def __init__(self):
        super().__init__()  # Initialize PDFService to get styles and helpers
        self._setup_receipt_styles()
    
    def _setup_receipt_styles(self):
        """Setup custom paragraph styles specific to purchase receipts."""
        # Receipt status badge styles (similar to invoice/order status badges)
        self.styles.add(ParagraphStyle(
            name='ReceiptStatusBadge',
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
    
    def _create_receipt_status_badge(self, status: str) -> Paragraph:
        """Create a status badge for receipt status."""
        status_labels = {
            'draft': 'BROUILLON',
            'validated': 'VALIDÉ',
            'cancelled': 'ANNULÉ'
        }
        status_text = status_labels.get(status.lower(), status.upper())
        
        badge_colors = {
            'draft': {'bg': '#fef3c7', 'text': '#92400e', 'border': '#fbbf24'},
            'validated': {'bg': '#d1fae5', 'text': '#065f46', 'border': '#10b981'},
            'cancelled': {'bg': '#fee2e2', 'text': '#991b1b', 'border': '#ef4444'}
        }
        colors_dict = badge_colors.get(status.lower(), badge_colors['draft'])
        
        badge_style = ParagraphStyle(
            name='ReceiptStatusBadge',
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
    
    def generate_receipt_pdf(self, receipt_dto: PurchaseReceiptDTO) -> BytesIO:
        """
        Generate a professional PDF for a purchase receipt using the same template as invoices and orders.
        
        Args:
            receipt_dto: PurchaseReceiptDTO containing receipt information
            
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
        doc.title = f"Bon de réception {receipt_dto.number} - {receipt_dto.purchase_order_number or 'N/A'}"
        doc.author = current_app.config.get('COMPANY_NAME', 'CommerceFlow')
        doc.subject = "Bon de réception"
        
        # Build story (content)
        story = []
        
        # ========== PROFESSIONAL HEADER ==========
        company_info = get_company_info()
        
        # Header table: Left (Company) | Right (Receipt title and info)
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
                Paragraph(f"<b>BON DE RÉCEPTION</b>", ParagraphStyle(
                    name='ReceiptTitle',
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
                    f"N° Bon: <b>{receipt_dto.number}</b><br/>"
                    f"Date réception: {self._format_date(receipt_dto.receipt_date)}<br/>"
                    f"N° Commande: {receipt_dto.purchase_order_number or 'N/A'}",
                    ParagraphStyle(
                        name='ReceiptInfo',
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
        
        # Accent bar (optional colored bar) - Green for receipts
        accent_bar = Table([['']], colWidths=[170*mm], rowHeights=[4*mm])
        accent_bar.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#10b981')),  # Green for receipts
            ('LINEBELOW', (0, 0), (0, 0), 0, colors.HexColor('#10b981')),
        ]))
        story.append(accent_bar)
        story.append(Spacer(1, 20*mm))
        
        # ========== RECEIPT DETAILS SECTION WITH STATUS BADGE ==========
        status = receipt_dto.status
        status_badge = self._create_receipt_status_badge(status)
        
        # Receipt details in grid layout
        receipt_details_data = [
            ['Statut:', status_badge],
        ]
        
        if receipt_dto.received_by_name:
            receipt_details_data.append(['Reçu par:', receipt_dto.received_by_name])
        
        if receipt_dto.validated_by_name:
            receipt_details_data.append(['Validé par:', receipt_dto.validated_by_name])
        
        if receipt_dto.validated_at:
            receipt_details_data.append(['Validé le:', self._format_date(receipt_dto.validated_at)])
        
        receipt_details_table = Table(receipt_details_data, colWidths=[60*mm, 110*mm])
        receipt_details_table.setStyle(TableStyle([
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
        story.append(receipt_details_table)
        story.append(Spacer(1, 20*mm))
        
        # ========== RECEIPT LINES TABLE ==========
        if receipt_dto.lines:
            story.append(Paragraph("Lignes de réception", self.styles['CustomHeading']))
            
            # Table header
            table_data = [[
                'Produit',
                'Qté commandée',
                'Qté reçue',
                'Écart',
                'Emplacement',
                'Notes qualité'
            ]]
            
            # Table rows
            for line in receipt_dto.lines:
                product_code = line.product_code or ''
                product_name = line.product_name or 'N/A'
                
                # Format product name with code on new line in smaller font using Paragraph
                if product_code:
                    product_cell = Paragraph(
                        f"<b>{product_name}</b><br/><font size='7'>{product_code}</font>",
                        self.styles['Normal']
                    )
                else:
                    product_cell = Paragraph(f"<b>{product_name}</b>", self.styles['Normal'])
                
                # Format discrepancy
                discrepancy_str = f"{float(line.quantity_discrepancy):.3f}" if line.quantity_discrepancy != 0 else "-"
                if line.quantity_discrepancy > 0:
                    discrepancy_str = f"+{discrepancy_str}"
                
                # Location
                location_str = line.location_code or '-'
                
                # Quality notes
                quality_notes = line.quality_notes or '-'
                if len(quality_notes) > 30:
                    quality_notes = quality_notes[:27] + '...'
                
                table_data.append([
                    product_cell,
                    f"{float(line.quantity_ordered):.3f}",
                    f"{float(line.quantity_received):.3f}",
                    discrepancy_str,
                    location_str,
                    quality_notes
                ])
            
            # Create table
            receipt_table = Table(table_data, colWidths=[50*mm, 25*mm, 25*mm, 20*mm, 25*mm, 25*mm])
            receipt_table.setStyle(TableStyle([
                # Header
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),  # Green for receipts
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
            story.append(receipt_table)
            story.append(Spacer(1, 10*mm))
        
        # ========== SUMMARY SECTION ==========
        if receipt_dto.lines:
            total_ordered = sum(float(line.quantity_ordered) for line in receipt_dto.lines)
            total_received = sum(float(line.quantity_received) for line in receipt_dto.lines)
            total_discrepancy = sum(float(line.quantity_discrepancy) for line in receipt_dto.lines)
            
            summary_data = [
                ['Total quantités commandées:', f"{total_ordered:.3f}"],
                ['Total quantités reçues:', f"{total_received:.3f}"],
            ]
            
            if total_discrepancy != 0:
                discrepancy_str = f"{total_discrepancy:.3f}"
                if total_discrepancy > 0:
                    discrepancy_str = f"+{discrepancy_str}"
                summary_data.append(['Total écart:', discrepancy_str])
            
            summary_table = Table(summary_data, colWidths=[100*mm, 70*mm])
            summary_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1a1a1a')),
                ('LINEABOVE', (0, -1), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f9fafb')),
            ]))
            
            # Wrap summary in a container table to right-align it
            summary_container = Table([[summary_table]], colWidths=[170*mm])
            summary_container.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'RIGHT'),
                ('VALIGN', (0, 0), (0, 0), 'TOP'),
            ]))
            story.append(summary_container)
            story.append(Spacer(1, 15*mm))
        
        # Notes
        if receipt_dto.notes:
            story.append(Paragraph("Notes", self.styles['CustomHeading']))
            story.append(Paragraph(
                receipt_dto.notes.replace('\n', '<br/>'),
                self.styles['CustomNormal']
            ))
            story.append(Spacer(1, 10*mm))
        
        # Footer
        footer_text = "Bon de réception généré automatiquement par le système GMFlow."
        if receipt_dto.created_at:
            footer_text += f"<br/>Généré le {self._format_date(receipt_dto.created_at)}"
        story.append(Paragraph(footer_text, self.styles['CustomFooter']))
        
        # Build PDF
        doc.build(story)
        pdf_buffer.seek(0)
        
        return pdf_buffer




