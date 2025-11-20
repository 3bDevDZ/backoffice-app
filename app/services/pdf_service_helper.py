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
    """Get company information for PDF header from database settings."""
    try:
        from app.application.common.mediator import mediator
        from app.application.settings.queries.queries import GetCompanySettingsQuery
        
        company_settings = mediator.dispatch(GetCompanySettingsQuery())
        
        return {
            'name': company_settings.name or 'CommerceFlow',
            'address': company_settings.address or '',
            'postal_code': company_settings.postal_code or '',
            'city': company_settings.city or '',
            'country': company_settings.country or 'France',
            'phone': company_settings.phone or '',
            'email': company_settings.email or '',
            'website': company_settings.website or ''
        }
    except Exception:
        # Fallback to defaults if settings not available
        return {
            'name': 'CommerceFlow',
            'address': '',
            'postal_code': '',
            'city': '',
            'country': 'France',
            'phone': '',
            'email': '',
            'website': ''
        }
