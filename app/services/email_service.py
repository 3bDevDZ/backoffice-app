"""Email sending service using SMTP."""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional
from flask import current_app
from io import BytesIO


class EmailService:
    """Service for sending emails via SMTP."""
    
    def __init__(self):
        self.smtp_server = None
        self.smtp_port = None
        self.use_tls = None
        self.use_ssl = None
        self.username = None
        self.password = None
        self.default_sender = None
    
    def _get_config(self):
        """Get SMTP configuration from Flask app config."""
        self.smtp_server = current_app.config.get('MAIL_SERVER')
        self.smtp_port = current_app.config.get('MAIL_PORT', 587)
        self.use_tls = current_app.config.get('MAIL_USE_TLS', True)
        self.use_ssl = current_app.config.get('MAIL_USE_SSL', False)
        self.username = current_app.config.get('MAIL_USERNAME')
        self.password = current_app.config.get('MAIL_PASSWORD')
        self.default_sender = current_app.config.get('MAIL_DEFAULT_SENDER')
    
    def send_email(
        self,
        to: str | List[str],
        subject: str,
        body_text: str,
        body_html: Optional[str] = None,
        attachments: Optional[List[dict]] = None,
        from_email: Optional[str] = None
    ) -> bool:
        """
        Send an email via SMTP.
        
        Args:
            to: Recipient email address(es)
            subject: Email subject
            body_text: Plain text body
            body_html: Optional HTML body
            attachments: Optional list of attachments (dict with 'filename' and 'content' BytesIO)
            from_email: Optional sender email (defaults to MAIL_DEFAULT_SENDER)
            
        Returns:
            True if email sent successfully, False otherwise
        """
        self._get_config()
        
        if not self.smtp_server:
            raise ValueError("SMTP server not configured. Set MAIL_SERVER in config.")
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = from_email or self.default_sender
        
        # Handle multiple recipients
        if isinstance(to, list):
            msg['To'] = ', '.join(to)
            recipients = to
        else:
            msg['To'] = to
            recipients = [to]
        
        # Add text and HTML parts
        msg.attach(MIMEText(body_text, 'plain', 'utf-8'))
        if body_html:
            msg.attach(MIMEText(body_html, 'html', 'utf-8'))
        
        # Add attachments
        if attachments:
            for attachment in attachments:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment['content'].read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {attachment["filename"]}'
                )
                msg.attach(part)
        
        # Send email
        try:
            if self.use_ssl:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            
            if self.use_tls and not self.use_ssl:
                server.starttls()
            
            if self.username and self.password:
                server.login(self.username, self.password)
            
            server.sendmail(msg['From'], recipients, msg.as_string())
            server.quit()
            
            return True
        except Exception as e:
            current_app.logger.error(f"Failed to send email: {e}")
            raise
    
    def send_quote_email(
        self,
        to: str | List[str],
        quote_number: str,
        quote_pdf: BytesIO,
        customer_name: Optional[str] = None,
        locale: str = 'fr'
    ) -> bool:
        """
        Send a quote email with PDF attachment.
        
        Args:
            to: Recipient email address(es)
            quote_number: Quote number
            quote_pdf: PDF file as BytesIO
            customer_name: Optional customer name for personalization
            locale: Locale for email content ('fr' or 'ar')
            
        Returns:
            True if email sent successfully, False otherwise
        """
        # Email content based on locale
        if locale == 'ar':
            subject = f"عرض سعر - {quote_number}"
            body_text = f"""
عزيزي/عزيزتي {customer_name or 'العميل'}،

نشكرك على اهتمامك بخدماتنا.

يرجى الاطلاع على عرض السعر المرفق رقم {quote_number}.

نأمل أن نسمع منك قريباً.

مع أطيب التحيات،
فريق المبيعات
"""
            body_html = f"""
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; direction: rtl; }}
        .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .footer {{ background-color: #f1f1f1; padding: 10px; text-align: center; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>عرض سعر</h1>
    </div>
    <div class="content">
        <p>عزيزي/عزيزتي {customer_name or 'العميل'}،</p>
        <p>نشكرك على اهتمامك بخدماتنا.</p>
        <p>يرجى الاطلاع على عرض السعر المرفق رقم <strong>{quote_number}</strong>.</p>
        <p>نأمل أن نسمع منك قريباً.</p>
    </div>
    <div class="footer">
        <p>مع أطيب التحيات،<br>فريق المبيعات</p>
    </div>
</body>
</html>
"""
        else:  # French (default)
            subject = f"Devis - {quote_number}"
            body_text = f"""
Bonjour {customer_name or 'Monsieur/Madame'},

Nous vous remercions de l'intérêt que vous portez à nos services.

Veuillez trouver ci-joint notre devis n° {quote_number}.

Nous espérons avoir de vos nouvelles prochainement.

Cordialement,
L'équipe commerciale
"""
            body_html = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; }}
        .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .footer {{ background-color: #f1f1f1; padding: 10px; text-align: center; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Devis</h1>
    </div>
    <div class="content">
        <p>Bonjour {customer_name or 'Monsieur/Madame'},</p>
        <p>Nous vous remercions de l'intérêt que vous portez à nos services.</p>
        <p>Veuillez trouver ci-joint notre devis n° <strong>{quote_number}</strong>.</p>
        <p>Nous espérons avoir de vos nouvelles prochainement.</p>
    </div>
    <div class="footer">
        <p>Cordialement,<br>L'équipe commerciale</p>
    </div>
</body>
</html>
"""
        
        # Reset PDF buffer position
        quote_pdf.seek(0)
        
        return self.send_email(
            to=to,
            subject=subject,
            body_text=body_text,
            body_html=body_html,
            attachments=[{
                'filename': f'Devis_{quote_number}.pdf',
                'content': quote_pdf
            }]
        )


# Singleton instance
email_service = EmailService()

