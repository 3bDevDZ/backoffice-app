"""PDF generation service using ReportLab and xhtml2pdf."""
from io import BytesIO
from pathlib import Path
from typing import Optional
from flask import render_template_string, current_app
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT, TA_LEFT, TA_CENTER
from reportlab.pdfgen import canvas
from datetime import datetime, date


class PDFService:
    """Service for generating PDF documents using ReportLab."""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles."""
        # Title style - Professional header
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=30,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=10,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold',
            leading=36
        ))
        
        # Heading style - Section titles
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#2d3748'),
            spaceAfter=6,
            spaceBefore=15,
            fontName='Helvetica-Bold'
        ))
        
        # Normal text
        self.styles.add(ParagraphStyle(
            name='CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=3,
            textColor=colors.HexColor('#1a1a1a')
        ))
        
        # Small text for product codes
        self.styles.add(ParagraphStyle(
            name='CustomSmall',
            parent=self.styles['Normal'],
            fontSize=7,
            spaceAfter=2,
            textColor=colors.HexColor('#6b7280')
        ))
        
        # Footer style
        self.styles.add(ParagraphStyle(
            name='CustomFooter',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#9ca3af'),
            alignment=TA_CENTER,
            spaceBefore=10
        ))
    
    def generate_quote_pdf(self, quote_data: dict, template_path: Optional[str] = None) -> BytesIO:
        """
        Generate a PDF for a quote using ReportLab.
        
        Args:
            quote_data: Dictionary containing quote information
            template_path: Not used with ReportLab (kept for compatibility)
            
        Returns:
            BytesIO object containing the PDF data
        """
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )
        
        # Build story (content)
        story = []
        
        # Header
        story.append(Paragraph("DEVIS", self.styles['CustomTitle']))
        story.append(Spacer(1, 10*mm))
        
        # Quote info table
        quote_info_data = [
            ['N° Devis:', quote_data.get('number', 'N/A')],
            ['Version:', str(quote_data.get('version', 1))],
            ['Date:', self._format_date(quote_data.get('created_at'))],
            ['Statut:', quote_data.get('status', 'draft').upper()],
        ]
        
        quote_info_table = Table(quote_info_data, colWidths=[60*mm, 100*mm])
        quote_info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(quote_info_table)
        story.append(Spacer(1, 10*mm))
        
        # Customer section
        customer = quote_data.get('customer', {})
        story.append(Paragraph("Client", self.styles['CustomHeading']))
        story.append(Paragraph(f"<b>{customer.get('name', 'N/A')}</b>", self.styles['CustomNormal']))
        if customer.get('code'):
            story.append(Paragraph(f"Code: {customer.get('code')}", self.styles['CustomNormal']))
        story.append(Spacer(1, 10*mm))
        
        # Quote lines table
        lines = quote_data.get('lines', [])
        if lines:
            story.append(Paragraph("Lignes de devis", self.styles['CustomHeading']))
            
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
            for line in lines:
                discount_str = f"{line.get('discount_percent', 0):.2f}%" if line.get('discount_percent', 0) > 0 else "-"
                table_data.append([
                    f"{line.get('product_name', 'N/A')}<br/><small>{line.get('product_code', '')}</small>",
                    f"{line.get('quantity', 0):.3f}",
                    f"{line.get('unit_price', 0):.2f} €",
                    discount_str,
                    f"{line.get('line_total_ht', 0):.2f} €",
                    f"{line.get('tax_rate', 20):.2f}%",
                    f"{line.get('line_total_ttc', 0):.2f} €"
                ])
            
            # Create table
            quote_table = Table(table_data, colWidths=[60*mm, 20*mm, 25*mm, 20*mm, 25*mm, 20*mm, 30*mm])
            quote_table.setStyle(TableStyle([
                # Header
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4CAF50')),
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
            story.append(quote_table)
            story.append(Spacer(1, 10*mm))
        
        # Totals section
        story.append(Paragraph("Totaux", self.styles['CustomHeading']))
        
        subtotal = quote_data.get('subtotal', 0)
        discount_amount = quote_data.get('discount_amount', 0)
        tax_amount = quote_data.get('tax_amount', 0)
        total = quote_data.get('total', 0)
        
        totals_data = [
            ['Sous-total HT:', f"{subtotal:.2f} €"],
        ]
        
        if discount_amount > 0:
            discount_percent = quote_data.get('discount_percent', 0)
            totals_data.append([f'Remise document ({discount_percent:.2f}%):', f"-{discount_amount:.2f} €"])
            totals_data.append(['Total HT:', f"{subtotal - discount_amount:.2f} €"])
        else:
            totals_data.append(['Total HT:', f"{subtotal:.2f} €"])
        
        totals_data.append(['TVA:', f"{tax_amount:.2f} €"])
        totals_data.append(['<b>TOTAL TTC:</b>', f"<b>{total:.2f} €</b>"])
        
        totals_table = Table(totals_data, colWidths=[120*mm, 60*mm])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -2), 'Helvetica'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            ('LINEABOVE', (0, -2), (-1, -2), 1, colors.grey),
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.black),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f0f0f0')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(totals_table)
        story.append(Spacer(1, 10*mm))
        
        # Validity
        valid_until = quote_data.get('valid_until')
        if valid_until:
            valid_date = self._format_date(valid_until)
            story.append(Paragraph(
                f"<b>Validité du devis:</b> jusqu'au {valid_date}",
                ParagraphStyle(
                    name='Validity',
                    parent=self.styles['Normal'],
                    fontSize=10,
                    backColor=colors.HexColor('#fff3cd'),
                    borderColor=colors.HexColor('#ffc107'),
                    borderWidth=1,
                    borderPadding=10,
                    alignment=TA_CENTER
                )
            ))
            story.append(Spacer(1, 10*mm))
        
        # Notes
        notes = quote_data.get('notes')
        if notes:
            story.append(Paragraph("Notes", self.styles['CustomHeading']))
            story.append(Paragraph(
                notes.replace('\n', '<br/>'),
                ParagraphStyle(
                    name='Notes',
                    parent=self.styles['Normal'],
                    fontSize=10,
                    backColor=colors.HexColor('#f9f9f9'),
                    borderColor=colors.HexColor('#4CAF50'),
                    borderWidth=0,
                    borderPadding=15,
                    leftIndent=0
                )
            ))
            story.append(Spacer(1, 10*mm))
        
        # Footer
        story.append(Spacer(1, 20*mm))
        story.append(Paragraph(
            "<i>Ce devis est généré automatiquement par le système GMFlow.</i>",
            ParagraphStyle(
                name='Footer',
                parent=self.styles['Normal'],
                fontSize=8,
                textColor=colors.grey,
                alignment=TA_CENTER
            )
        ))
        
        # Build PDF
        doc.build(story)
        pdf_buffer.seek(0)
        
        return pdf_buffer
    
    def generate_order_pdf(self, order_data: dict, template_path: Optional[str] = None) -> BytesIO:
        """
        Generate a professional PDF for an order using ReportLab.
        Follows the design specification in docs/PDF_DESIGN_SPECIFICATION.md
        
        Args:
            order_data: Dictionary containing order information
            template_path: Not used with ReportLab (kept for compatibility)
            
        Returns:
            BytesIO object containing the PDF data
        """
        # Import helper functions (with fallback)
        try:
            from .pdf_service_helper import get_company_info, create_status_badge
        except ImportError:
            # Fallback implementations
            def get_company_info():
                return {
                    'name': 'CommerceFlow',
                    'address': '123 Rue de la Commerce',
                    'postal_code': '69000',
                    'city': 'Lyon',
                    'country': 'France',
                    'phone': '+33 4 XX XX XX XX',
                    'email': 'contact@commerceflow.com',
                    'website': 'www.commerceflow.com'
                }
            
            def create_status_badge(status, styles):
                status_labels = {
                    'draft': 'BROUILLON',
                    'confirmed': 'CONFIRMÉ',
                    'ready': 'PRÊT',
                    'shipped': 'EXPÉDIÉ',
                    'delivered': 'LIVRÉ',
                    'canceled': 'ANNULÉ'
                }
                status_text = status_labels.get(status.lower(), status.upper())
                
                badge_colors = {
                    'draft': {'bg': '#fef3c7', 'text': '#92400e', 'border': '#fbbf24'},
                    'confirmed': {'bg': '#d1fae5', 'text': '#065f46', 'border': '#10b981'},
                    'ready': {'bg': '#dbeafe', 'text': '#1e40af', 'border': '#3b82f6'},
                    'shipped': {'bg': '#ede9fe', 'text': '#5b21b6', 'border': '#8b5cf6'},
                    'delivered': {'bg': '#a7f3d0', 'text': '#064e3b', 'border': '#059669'},
                    'canceled': {'bg': '#fee2e2', 'text': '#991b1b', 'border': '#ef4444'}
                }
                colors_dict = badge_colors.get(status.lower(), badge_colors['draft'])
                
                badge_style = ParagraphStyle(
                    name='StatusBadge',
                    parent=styles['Normal'],
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
        doc.title = f"Commande {order_data.get('number', 'N/A')} - {order_data.get('customer_name', 'N/A')}"
        doc.author = "CommerceFlow"
        doc.subject = "Commande commerciale"
        
        # Build story (content)
        story = []
        
        # ========== PROFESSIONAL HEADER ==========
        # Header with company name/title and order number/date
        company_info = get_company_info()
        
        # Header table: Left (Title) | Right (Order info)
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
                Paragraph(f"<b>COMMANDE</b>", ParagraphStyle(
                    name='OrderTitle',
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
                    f"N° Commande: <b>{order_data.get('number', 'N/A')}</b><br/>"
                    f"Date: {self._format_date(order_data.get('created_at'))}",
                    ParagraphStyle(
                        name='OrderInfo',
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
            ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#4CAF50')),
            ('LINEBELOW', (0, 0), (0, 0), 0, colors.HexColor('#4CAF50')),
        ]))
        story.append(accent_bar)
        story.append(Spacer(1, 20*mm))
        
        # ========== TWO-COLUMN COMPANY/CLIENT INFO ==========
        company_info = get_company_info()
        customer = order_data.get('customer', {})
        if isinstance(customer, dict):
            customer_name = customer.get('name', order_data.get('customer_name', 'N/A'))
            customer_code = customer.get('code', order_data.get('customer_code'))
        else:
            customer_name = order_data.get('customer_name', 'N/A')
            customer_code = order_data.get('customer_code')
        
        # Build company address
        company_address_lines = [
            company_info['address'],
            f"{company_info['postal_code']} {company_info['city']}",
            company_info['country']
        ]
        company_address = '<br/>'.join([line for line in company_address_lines if line])
        
        # Build customer info
        customer_info_lines = [f"<b>{customer_name}</b>"]
        if customer_code:
            customer_info_lines.append(f"Code: {customer_code}")
        customer_info = '<br/>'.join(customer_info_lines)
        
        # Two-column layout
        company_client_data = [
            [
                Paragraph("<b>EXPÉDITEUR</b>", ParagraphStyle(
                    name='SectionTitle',
                    parent=self.styles['Normal'],
                    fontSize=11,
                    textColor=colors.HexColor('#2d3748'),
                    fontName='Helvetica-Bold',
                    leading=13
                )),
                Paragraph("<b>DESTINATAIRE</b>", ParagraphStyle(
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
        
        # ========== ORDER DETAILS SECTION WITH STATUS BADGE ==========
        status = order_data.get('status', 'draft')
        status_badge = create_status_badge(status, self.styles)
        
        # Order details in grid layout
        order_details_data = [
            ['Statut:', status_badge],
            ['N° Devis:', order_data.get('quote_number', '-') if order_data.get('quote_number') else '-']
        ]
        
        if order_data.get('confirmed_at'):
            order_details_data.append(['Confirmé le:', self._format_date(order_data.get('confirmed_at'))])
        
        if order_data.get('delivery_date_requested'):
            order_details_data.append(['Date livraison demandée:', self._format_date(order_data.get('delivery_date_requested'))])
        
        if order_data.get('delivery_date_promised'):
            order_details_data.append(['Date livraison promise:', self._format_date(order_data.get('delivery_date_promised'))])
        
        order_details_table = Table(order_details_data, colWidths=[60*mm, 110*mm])
        order_details_table.setStyle(TableStyle([
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
        story.append(order_details_table)
        story.append(Spacer(1, 20*mm))
        
        # Order lines table
        lines = order_data.get('lines', [])
        if lines:
            story.append(Paragraph("Lignes de commande", self.styles['CustomHeading']))
            
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
            for line in lines:
                discount_str = f"{line.get('discount_percent', 0):.2f}%" if line.get('discount_percent', 0) > 0 else "-"
                product_code = line.get('product_code', '')
                product_name = line.get('product_name', 'N/A')
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
                    f"{line.get('quantity', 0):.3f}",
                    f"{line.get('unit_price', 0):.2f} €",
                    discount_str,
                    f"{line.get('line_total_ht', 0):.2f} €",
                    f"{line.get('tax_rate', 20):.2f}%",
                    f"{line.get('line_total_ttc', 0):.2f} €"
                ])
            
            # Create table
            order_table = Table(table_data, colWidths=[60*mm, 20*mm, 25*mm, 20*mm, 25*mm, 20*mm, 30*mm])
            order_table.setStyle(TableStyle([
                # Header
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4CAF50')),
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
            story.append(order_table)
            story.append(Spacer(1, 10*mm))
        
        # ========== PROFESSIONAL TOTALS SECTION ==========
        subtotal = order_data.get('subtotal', 0)
        discount_amount = order_data.get('discount_amount', 0)
        tax_amount = order_data.get('tax_amount', 0)
        total = order_data.get('total', 0)
        
        totals_data = [
            ['Sous-total HT:', f"{subtotal:.2f} €"],
        ]
        
        if discount_amount > 0:
            discount_percent = order_data.get('discount_percent', 0)
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
        
        # Delivery instructions
        delivery_instructions = order_data.get('delivery_instructions')
        if delivery_instructions:
            story.append(Paragraph("Instructions de livraison", self.styles['CustomHeading']))
            story.append(Paragraph(
                delivery_instructions.replace('\n', '<br/>'),
                ParagraphStyle(
                    name='Instructions',
                    parent=self.styles['Normal'],
                    fontSize=10,
                    backColor=colors.HexColor('#fff3cd'),
                    borderColor=colors.HexColor('#ffc107'),
                    borderWidth=1,
                    borderPadding=10,
                    leftIndent=0
                )
            ))
            story.append(Spacer(1, 10*mm))
        
        # Notes
        notes = order_data.get('notes')
        if notes:
            story.append(Paragraph("Notes", self.styles['CustomHeading']))
            story.append(Paragraph(
                notes.replace('\n', '<br/>'),
                ParagraphStyle(
                    name='Notes',
                    parent=self.styles['Normal'],
                    fontSize=10,
                    backColor=colors.HexColor('#f9f9f9'),
                    borderColor=colors.HexColor('#4CAF50'),
                    borderWidth=0,
                    borderPadding=15,
                    leftIndent=0
                )
            ))
            story.append(Spacer(1, 10*mm))
        
        # ========== PROFESSIONAL FOOTER ==========
        story.append(Spacer(1, 20*mm))
        
        # Footer separator line
        footer_line = Table([['']], colWidths=[170*mm], rowHeights=[0.5*mm])
        footer_line.setStyle(TableStyle([
            ('LINEBELOW', (0, 0), (0, 0), 0.5, colors.HexColor('#e5e7eb')),
        ]))
        story.append(footer_line)
        story.append(Spacer(1, 8*mm))
        
        # Footer content
        company_info = get_company_info()
        footer_content = [
            f"<b>{company_info['name']}</b> - Système de Gestion Commercial",
            f"{company_info['website']} | {company_info['email']}",
            "Ce document est généré automatiquement."
        ]
        
        for line in footer_content:
            story.append(Paragraph(
                line,
                self.styles['CustomFooter']
            ))
        
        # Build PDF with watermark support for drafts
        status = order_data.get('status', 'draft')
        
        # Create custom canvas class for watermark (if draft)
        class WatermarkCanvas(canvas.Canvas):
            def __init__(self, *args, **kwargs):
                self.is_draft = kwargs.pop('is_draft', False)
                canvas.Canvas.__init__(self, *args, **kwargs)
            
            def showPage(self):
                canvas.Canvas.showPage(self)
                if self.is_draft:
                    # Draw watermark on each page
                    self.saveState()
                    self.translate(A4[0] / 2, A4[1] / 2)
                    self.rotate(45)
                    self.setFont('Helvetica-Bold', 72)
                    self.setFillColor(colors.HexColor('#f3f4f6'), alpha=0.1)
                    self.drawCentredString(0, 0, 'BROUILLON')
                    self.restoreState()
        
        # Build PDF
        if status.lower() == 'draft':
            # Use custom canvas for watermark
            doc.build(story, canvasmaker=lambda *args, **kwargs: WatermarkCanvas(*args, is_draft=True, **kwargs))
        else:
            # Normal build without watermark
            doc.build(story)
        
        pdf_buffer.seek(0)
        
        return pdf_buffer
    
    def _format_date(self, date_value):
        """Format date for display."""
        if not date_value:
            return 'N/A'
        
        if isinstance(date_value, str):
            try:
                # Try ISO format
                if 'T' in date_value:
                    date_value = datetime.fromisoformat(date_value.replace('Z', '+00:00'))
                else:
                    date_value = date.fromisoformat(date_value)
            except:
                return date_value
        
        if isinstance(date_value, datetime):
            return date_value.strftime('%d/%m/%Y')
        elif isinstance(date_value, date):
            return date_value.strftime('%d/%m/%Y')
        
        return str(date_value)
    
    def generate_pdf_from_html(self, html_content: str, stylesheet: Optional[str] = None) -> BytesIO:
        """
        Generate a PDF from HTML content using xhtml2pdf as fallback.
        
        Args:
            html_content: HTML string to convert to PDF
            stylesheet: Optional CSS string for styling (limited support)
            
        Returns:
            BytesIO object containing the PDF data
        """
        try:
            from xhtml2pdf import pisa
            
            pdf_buffer = BytesIO()
            
            # Convert HTML to PDF
            pisa_status = pisa.CreatePDF(
                html_content,
                dest=pdf_buffer,
                encoding='utf-8'
            )
            
            if pisa_status.err:
                raise Exception(f"Error generating PDF: {pisa_status.err}")
            
            pdf_buffer.seek(0)
            return pdf_buffer
            
        except ImportError:
            # Fallback to ReportLab if xhtml2pdf not available
            raise ImportError("xhtml2pdf not installed. Install with: pip install xhtml2pdf")
    
    def generate_delivery_note_pdf(self, order_data: dict, template_path: Optional[str] = None) -> BytesIO:
        """
        Generate a delivery note (bon de livraison) PDF for an order.
        
        Args:
            order_data: Dictionary containing order information with delivery details
            template_path: Not used with ReportLab (kept for compatibility)
            
        Returns:
            BytesIO object containing the PDF data
        """
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )
        
        # Build story (content)
        story = []
        
        # Header
        story.append(Paragraph("BON DE LIVRAISON", self.styles['CustomTitle']))
        story.append(Spacer(1, 10*mm))
        
        # Delivery note number (generate if not provided)
        delivery_note_number = order_data.get('delivery_note_number', f"BL-{datetime.now().year}-{datetime.now().strftime('%m%d%H%M')}")
        
        # Order info table
        order_info_data = [
            ['N° Bon de Livraison:', delivery_note_number],
            ['N° Commande:', order_data.get('number', 'N/A')],
            ['Date de livraison:', self._format_date(order_data.get('delivery_date_actual') or order_data.get('delivery_date_promised'))],
            ['Statut:', order_data.get('status', 'draft').upper()],
        ]
        
        order_info_table = Table(order_info_data, colWidths=[60*mm, 100*mm])
        order_info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(order_info_table)
        story.append(Spacer(1, 10*mm))
        
        # Customer and delivery address section
        customer = order_data.get('customer', {})
        delivery_address = order_data.get('delivery_address', {})
        
        story.append(Paragraph("Client", self.styles['CustomHeading']))
        story.append(Paragraph(f"<b>{customer.get('name', 'N/A')}</b>", self.styles['CustomNormal']))
        if customer.get('code'):
            story.append(Paragraph(f"Code: {customer.get('code')}", self.styles['CustomNormal']))
        story.append(Spacer(1, 5*mm))
        
        if delivery_address:
            story.append(Paragraph("Adresse de livraison", self.styles['CustomHeading']))
            address_lines = []
            if delivery_address.get('street'):
                address_lines.append(delivery_address.get('street'))
            if delivery_address.get('postal_code') or delivery_address.get('city'):
                city_line = f"{delivery_address.get('postal_code', '')} {delivery_address.get('city', '')}".strip()
                if city_line:
                    address_lines.append(city_line)
            if delivery_address.get('country'):
                address_lines.append(delivery_address.get('country'))
            
            for line in address_lines:
                story.append(Paragraph(line, self.styles['CustomNormal']))
        
        story.append(Spacer(1, 10*mm))
        
        # Delivery lines table
        lines = order_data.get('lines', [])
        stock_reservations = order_data.get('stock_reservations', [])
        
        if lines:
            story.append(Paragraph("Articles livrés", self.styles['CustomHeading']))
            
            # Table header
            table_data = [[
                'Produit',
                'Qté commandée',
                'Qté livrée',
                'Emplacement',
                'Unité'
            ]]
            
            # Group reservations by order line
            reservations_by_line = {}
            for reservation in stock_reservations:
                line_id = reservation.get('order_line_id')
                if line_id not in reservations_by_line:
                    reservations_by_line[line_id] = []
                reservations_by_line[line_id].append(reservation)
            
            # Table rows
            for line in lines:
                line_id = line.get('id')
                quantity_ordered = line.get('quantity', 0)
                quantity_delivered = line.get('quantity_delivered', quantity_ordered)  # Default to full delivery
                
                # Get locations from reservations
                locations = []
                if line_id in reservations_by_line:
                    for reservation in reservations_by_line[line_id]:
                        stock_item = reservation.get('stock_item', {})
                        location = stock_item.get('location', {})
                        if location:
                            locations.append(f"{location.get('code', 'N/A')} ({reservation.get('quantity', 0)})")
                
                location_str = ', '.join(locations) if locations else 'N/A'
                
                table_data.append([
                    f"{line.get('product_name', 'N/A')}<br/><small>{line.get('product_code', '')}</small>",
                    f"{quantity_ordered:.3f}",
                    f"{quantity_delivered:.3f}",
                    location_str,
                    'U'
                ])
            
            # Create table
            delivery_table = Table(table_data, colWidths=[70*mm, 30*mm, 30*mm, 50*mm, 20*mm])
            delivery_table.setStyle(TableStyle([
                # Header
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2196F3')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (2, -1), 'RIGHT'),  # Quantities right-aligned
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
            story.append(delivery_table)
            story.append(Spacer(1, 10*mm))
        
        # Delivery instructions
        delivery_instructions = order_data.get('delivery_instructions')
        if delivery_instructions:
            story.append(Paragraph("Instructions de livraison", self.styles['CustomHeading']))
            story.append(Paragraph(
                delivery_instructions.replace('\n', '<br/>'),
                ParagraphStyle(
                    name='Instructions',
                    parent=self.styles['Normal'],
                    fontSize=10,
                    backColor=colors.HexColor('#fff3cd'),
                    borderColor=colors.HexColor('#ffc107'),
                    borderWidth=1,
                    borderPadding=10,
                    leftIndent=0
                )
            ))
            story.append(Spacer(1, 10*mm))
        
        # Signature section
        story.append(Spacer(1, 20*mm))
        signature_table = Table([
            ['', ''],
            ['Signature client', 'Signature transporteur']
        ], colWidths=[80*mm, 80*mm])
        signature_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, 1), 9),
            ('LINEABOVE', (0, 0), (-1, 0), 1, colors.black),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 30),
            ('TOPPADDING', (0, 1), (-1, 1), 10),
        ]))
        story.append(signature_table)
        story.append(Spacer(1, 10*mm))
        
        # Footer
        story.append(Spacer(1, 10*mm))
        story.append(Paragraph(
            "<i>Ce bon de livraison est généré automatiquement par le système GMFlow.</i>",
            ParagraphStyle(
                name='Footer',
                parent=self.styles['Normal'],
                fontSize=8,
                textColor=colors.grey,
                alignment=TA_CENTER
            )
        ))
        
        # Build PDF
        doc.build(story)
        pdf_buffer.seek(0)
        
        return pdf_buffer


# Singleton instance
pdf_service = PDFService()
