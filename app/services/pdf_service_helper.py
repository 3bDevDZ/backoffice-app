"""Helper functions for PDF generation."""
from typing import Dict
from reportlab.lib import colors
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER


def get_status_badge_style(status: str) -> Dict:
    """Get badge style colors for order status."""
    status_styles = {
        'draft': {
            'bg_color': colors.HexColor('#fef3c7'),
            'text_color': colors.HexColor('#92400e'),
            'border_color': colors.HexColor('#fbbf24')
        },
        'confirmed': {
            'bg_color': colors.HexColor('#d1fae5'),
            'text_color': colors.HexColor('#065f46'),
            'border_color': colors.HexColor('#10b981')
        },
        'ready': {
            'bg_color': colors.HexColor('#dbeafe'),
            'text_color': colors.HexColor('#1e40af'),
            'border_color': colors.HexColor('#3b82f6')
        },
        'shipped': {
            'bg_color': colors.HexColor('#ede9fe'),
            'text_color': colors.HexColor('#5b21b6'),
            'border_color': colors.HexColor('#8b5cf6')
        },
        'delivered': {
            'bg_color': colors.HexColor('#a7f3d0'),
            'text_color': colors.HexColor('#064e3b'),
            'border_color': colors.HexColor('#059669')
        },
        'canceled': {
            'bg_color': colors.HexColor('#fee2e2'),
            'text_color': colors.HexColor('#991b1b'),
            'border_color': colors.HexColor('#ef4444')
        }
    }
    return status_styles.get(status.lower(), status_styles['draft'])


def create_status_badge(status: str, styles) -> Paragraph:
    """Create a status badge paragraph for PDF."""
    badge_style = get_status_badge_style(status)
    status_text = status.upper()
    
    # Map status to French labels
    status_labels = {
        'draft': 'BROUILLON',
        'confirmed': 'CONFIRMÉ',
        'ready': 'PRÊT',
        'shipped': 'EXPÉDIÉ',
        'delivered': 'LIVRÉ',
        'canceled': 'ANNULÉ'
    }
    status_text = status_labels.get(status.lower(), status_text)
    
    badge_para_style = ParagraphStyle(
        name='StatusBadge',
        parent=styles['Normal'],
        fontSize=9,
        textColor=badge_style['text_color'],
        backColor=badge_style['bg_color'],
        borderColor=badge_style['border_color'],
        borderWidth=1,
        borderPadding=3,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        leading=12
    )
    
    return Paragraph(f"<b>{status_text}</b>", badge_para_style)


def get_company_info() -> Dict[str, str]:
    """Get company information for PDF header.
    
    TODO: Move this to config or database for production use.
    """
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
