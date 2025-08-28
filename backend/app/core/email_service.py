"""
Email service for sending notifications and automated communications.
Supports multiple email providers and templates.
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import asyncio
from pathlib import Path
import json
import structlog

from .config import settings
from .monitoring import logger

class EmailService:
    """Service for sending emails with templates and attachments."""
    
    def __init__(self):
        self.smtp_server = getattr(settings, 'smtp_server', 'smtp.gmail.com')
        self.smtp_port = getattr(settings, 'smtp_port', 587)
        self.smtp_username = getattr(settings, 'smtp_username', '')
        self.smtp_password = getattr(settings, 'smtp_password', '')
        self.from_email = getattr(settings, 'from_email', 'noreply@celebrantportal.com')
        self.from_name = getattr(settings, 'from_name', 'Melbourne Celebrant Portal')
        
        # Email templates
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, str]:
        """Load email templates from files."""
        templates = {}
        template_dir = Path(__file__).parent.parent / "templates" / "emails"
        
        if template_dir.exists():
            for template_file in template_dir.glob("*.html"):
                template_name = template_file.stem
                with open(template_file, 'r', encoding='utf-8') as f:
                    templates[template_name] = f.read()
        
        return templates
    
    def _get_template(self, template_name: str) -> str:
        """Get email template by name."""
        return self.templates.get(template_name, "")
    
    def _render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render email template with context variables."""
        template = self._get_template(template_name)
        
        # Simple template rendering (replace placeholders)
        for key, value in context.items():
            placeholder = f"{{{{{key}}}}}"
            template = template.replace(placeholder, str(value))
        
        return template
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ) -> bool:
        """
        Send an email asynchronously.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email content
            text_content: Plain text email content (optional)
            attachments: List of attachment dictionaries
            cc: CC recipients
            bcc: BCC recipients
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email
            
            if cc:
                message["Cc"] = ", ".join(cc)
            
            # Add HTML content
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
            
            # Add text content if provided
            if text_content:
                text_part = MIMEText(text_content, "plain")
                message.attach(text_part)
            
            # Add attachments
            if attachments:
                for attachment in attachments:
                    self._add_attachment(message, attachment)
            
            # Send email
            await self._send_message(message, cc, bcc)
            
            logger.info("Email sent successfully", to_email=to_email, subject=subject)
            return True
            
        except Exception as e:
            logger.error("Failed to send email", to_email=to_email, subject=subject, error=str(e))
            return False
    
    def _add_attachment(self, message: MIMEMultipart, attachment: Dict[str, Any]):
        """Add attachment to email message."""
        try:
            filename = attachment.get("filename", "attachment")
            content = attachment.get("content")
            content_type = attachment.get("content_type", "application/octet-stream")
            
            if content:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(content)
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename= {filename}"
                )
                message.attach(part)
                
        except Exception as e:
            logger.error("Failed to add attachment", filename=attachment.get("filename"), error=str(e))
    
    async def _send_message(self, message: MIMEMultipart, cc: Optional[List[str]], bcc: Optional[List[str]]):
        """Send email message via SMTP."""
        # Prepare recipients
        recipients = [message["To"]]
        if cc:
            recipients.extend(cc)
        if bcc:
            recipients.extend(bcc)
        
        # Send via SMTP
        context = ssl.create_default_context()
        
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls(context=context)
            server.login(self.smtp_username, self.smtp_password)
            server.sendmail(self.from_email, recipients, message.as_string())
    
    async def send_welcome_email(self, user_email: str, user_name: str) -> bool:
        """Send welcome email to new users."""
        context = {
            "user_name": user_name,
            "login_url": f"{getattr(settings, 'frontend_url', 'http://localhost:3000')}/login",
            "support_email": getattr(settings, 'support_email', 'support@celebrantportal.com'),
            "current_date": datetime.now().strftime("%B %d, %Y")
        }
        
        html_content = self._render_template("welcome", context)
        text_content = f"""
        Welcome to Melbourne Celebrant Portal, {user_name}!
        
        Thank you for joining our platform. You can now log in and start managing your couples and ceremonies.
        
        Login URL: {context['login_url']}
        Support: {context['support_email']}
        
        Best regards,
        The Melbourne Celebrant Portal Team
        """
        
        return await self.send_email(
            to_email=user_email,
            subject="Welcome to Melbourne Celebrant Portal",
            html_content=html_content,
            text_content=text_content
        )
    
    async def send_invoice_reminder(self, user_email: str, user_name: str, invoice_data: Dict[str, Any]) -> bool:
        """Send invoice reminder email."""
        context = {
            "user_name": user_name,
            "invoice_number": invoice_data.get("invoice_number"),
            "amount": str(invoice_data.get("amount")),
            "due_date": invoice_data.get("due_date"),
            "couple_names": invoice_data.get("couple_names"),
            "invoice_url": f"{getattr(settings, 'frontend_url', 'http://localhost:3000')}/invoices/{invoice_data.get('id')}",
            "current_date": datetime.now().strftime("%B %d, %Y")
        }
        
        html_content = self._render_template("invoice_reminder", context)
        text_content = f"""
        Invoice Reminder
        
        Dear {user_name},
        
        This is a reminder that invoice {invoice_data.get('invoice_number')} for {invoice_data.get('couple_names')} is due on {invoice_data.get('due_date')}.
        
        Amount: ${invoice_data.get('amount')}
        Due Date: {invoice_data.get('due_date')}
        
        View Invoice: {context['invoice_url']}
        
        Best regards,
        Melbourne Celebrant Portal
        """
        
        return await self.send_email(
            to_email=user_email,
            subject=f"Invoice Reminder: {invoice_data.get('invoice_number')}",
            html_content=html_content,
            text_content=text_content
        )
    
    async def send_ceremony_reminder(self, user_email: str, user_name: str, ceremony_data: Dict[str, Any]) -> bool:
        """Send ceremony reminder email."""
        context = {
            "user_name": user_name,
            "ceremony_title": ceremony_data.get("title"),
            "ceremony_date": ceremony_data.get("ceremony_date"),
            "couple_names": ceremony_data.get("couple_names"),
            "venue": ceremony_data.get("venue"),
            "ceremony_url": f"{getattr(settings, 'frontend_url', 'http://localhost:3000')}/ceremonies/{ceremony_data.get('id')}",
            "current_date": datetime.now().strftime("%B %d, %Y")
        }
        
        html_content = self._render_template("ceremony_reminder", context)
        text_content = f"""
        Ceremony Reminder
        
        Dear {user_name},
        
        This is a reminder about the upcoming ceremony: {ceremony_data.get('title')}
        
        Couple: {ceremony_data.get('couple_names')}
        Date: {ceremony_data.get('ceremony_date')}
        Venue: {ceremony_data.get('venue')}
        
        View Ceremony: {context['ceremony_url']}
        
        Best regards,
        Melbourne Celebrant Portal
        """
        
        return await self.send_email(
            to_email=user_email,
            subject=f"Ceremony Reminder: {ceremony_data.get('title')}",
            html_content=html_content,
            text_content=text_content
        )
    
    async def send_password_reset(self, user_email: str, reset_token: str) -> bool:
        """Send password reset email."""
        reset_url = f"{getattr(settings, 'frontend_url', 'http://localhost:3000')}/reset-password?token={reset_token}"
        
        context = {
            "reset_url": reset_url,
            "expiry_hours": 24,
            "current_date": datetime.now().strftime("%B %d, %Y")
        }
        
        html_content = self._render_template("password_reset", context)
        text_content = f"""
        Password Reset Request
        
        You have requested to reset your password for Melbourne Celebrant Portal.
        
        Click the following link to reset your password:
        {reset_url}
        
        This link will expire in 24 hours.
        
        If you didn't request this reset, please ignore this email.
        
        Best regards,
        Melbourne Celebrant Portal
        """
        
        return await self.send_email(
            to_email=user_email,
            subject="Password Reset Request - Melbourne Celebrant Portal",
            html_content=html_content,
            text_content=text_content
        )
    
    async def send_payment_confirmation(self, user_email: str, user_name: str, payment_data: Dict[str, Any]) -> bool:
        """Send payment confirmation email."""
        context = {
            "user_name": user_name,
            "invoice_number": payment_data.get("invoice_number"),
            "amount": str(payment_data.get("amount")),
            "payment_date": payment_data.get("payment_date"),
            "couple_names": payment_data.get("couple_names"),
            "current_date": datetime.now().strftime("%B %d, %Y")
        }
        
        html_content = self._render_template("payment_confirmation", context)
        text_content = f"""
        Payment Confirmation
        
        Dear {user_name},
        
        Thank you for your payment of ${payment_data.get('amount')} for invoice {payment_data.get('invoice_number')}.
        
        Payment Details:
        - Invoice: {payment_data.get('invoice_number')}
        - Amount: ${payment_data.get('amount')}
        - Date: {payment_data.get('payment_date')}
        - Couple: {payment_data.get('couple_names')}
        
        Best regards,
        Melbourne Celebrant Portal
        """
        
        return await self.send_email(
            to_email=user_email,
            subject=f"Payment Confirmation - {payment_data.get('invoice_number')}",
            html_content=html_content,
            text_content=text_content
        )

# Global email service instance
email_service = EmailService()
