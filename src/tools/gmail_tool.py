"""
Gmail Tool for 2FA and Notifications
"""
import smtplib
import random
import string
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Optional
from datetime import datetime, timedelta
from ..config import GMAIL_USER, GMAIL_APP_PASSWORD, EMAIL_VERIFICATION_EXPIRY

class GmailTool:
    """
    Gmail tool for sending 2FA codes and notifications.
    Implements secure email verification and customer communication.
    """
    
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.user = GMAIL_USER
        self.password = GMAIL_APP_PASSWORD
        self.verification_codes: Dict[str, Dict] = {}  # Store codes temporarily
        
    def _generate_verification_code(self, length: int = 6) -> str:
        """Generate a random verification code"""
        return ''.join(random.choices(string.digits, k=length))
    
    def _send_email(self, to_email: str, subject: str, body: str, is_html: bool = False) -> bool:
        """Send email via SMTP"""
        try:
            if not self.user or not self.password:
                print("[WARNING] Gmail credentials not configured")
                return False
                
            msg = MIMEMultipart()
            msg['From'] = self.user
            msg['To'] = to_email
            msg['Subject'] = subject
            
            if is_html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.user, self.password)
                server.send_message(msg)
            
            return True
        except Exception as e:
            print(f"[ERROR] Failed to send email: {e}")
            return False
    
    def send_2fa_code(self, email: str, purpose: str = "verification") -> Dict[str, any]:
        """
        Send 2FA verification code to user email.
        
        Args:
            email: Recipient email address
            purpose: Purpose of verification (verification, login, transaction)
            
        Returns:
            Dict with success status and code info
        """
        code = self._generate_verification_code()
        expiry_time = datetime.now() + timedelta(seconds=EMAIL_VERIFICATION_EXPIRY)
        
        # Store code with expiry
        self.verification_codes[email] = {
            "code": code,
            "expiry": expiry_time,
            "purpose": purpose,
            "created_at": datetime.now()
        }
        
        expiry_text = f"{EMAIL_VERIFICATION_EXPIRY} seconds" if EMAIL_VERIFICATION_EXPIRY < 60 else f"{EMAIL_VERIFICATION_EXPIRY // 60} minutes"
        subject = f"Your Verification Code - {purpose.title()}"
        body = f"""
        Hello,
        
        Your verification code is: {code}
        
        This code will expire in {expiry_text}.
        
        If you didn't request this code, please ignore this email.
        
        Best regards,
        E-Commerce Support Team
        """
        
        success = self._send_email(email, subject, body)
        
        return {
            "success": success,
            "code_sent": success,
            "expiry_seconds": EMAIL_VERIFICATION_EXPIRY,
            "expiry_text": expiry_text,
            "message": "Verification code sent successfully" if success else "Failed to send code"
        }
    
    def verify_2fa_code(self, email: str, code: str) -> Dict[str, any]:
        """
        Verify 2FA code for user.
        
        Args:
            email: User email
            code: Verification code to check
            
        Returns:
            Dict with verification result
        """
        if email not in self.verification_codes:
            return {
                "verified": False,
                "message": "No verification code found for this email"
            }
        
        stored_data = self.verification_codes[email]
        
        # Check expiry
        if datetime.now() > stored_data["expiry"]:
            del self.verification_codes[email]
            return {
                "verified": False,
                "message": "Verification code has expired"
            }
        
        # Verify code
        if stored_data["code"] == code:
            del self.verification_codes[email]  # One-time use
            return {
                "verified": True,
                "message": "Code verified successfully"
            }
        else:
            return {
                "verified": False,
                "message": "Invalid verification code"
            }
    
    def send_notification(self, email: str, notification_type: str, data: Dict) -> Dict[str, any]:
        """
        Send notification email to user.
        
        Args:
            email: Recipient email
            notification_type: Type of notification (order_update, shipping, payment, etc.)
            data: Notification data
            
        Returns:
            Dict with send status
        """
        templates = {
            "order_update": {
                "subject": f"Order Update - Order #{data.get('order_id', 'N/A')}",
                "body": f"""
                Hello {data.get('customer_name', 'Customer')},
                
                Your order #{data.get('order_id')} status has been updated to: {data.get('status', 'N/A')}
                
                {data.get('message', '')}
                
                Track your order: {data.get('tracking_url', 'N/A')}
                
                Best regards,
                E-Commerce Team
                """
            },
            "shipping": {
                "subject": f"Your Order Has Shipped - Order #{data.get('order_id', 'N/A')}",
                "body": f"""
                Hello {data.get('customer_name', 'Customer')},
                
                Great news! Your order #{data.get('order_id')} has been shipped.
                
                Tracking Number: {data.get('tracking_number', 'N/A')}
                Carrier: {data.get('carrier', 'N/A')}
                Estimated Delivery: {data.get('estimated_delivery', 'N/A')}
                
                Track your shipment: {data.get('tracking_url', 'N/A')}
                
                Best regards,
                E-Commerce Team
                """
            },
            "payment": {
                "subject": f"Payment Confirmation - Order #{data.get('order_id', 'N/A')}",
                "body": f"""
                Hello {data.get('customer_name', 'Customer')},
                
                Your payment for order #{data.get('order_id')} has been confirmed.
                
                Amount: ${data.get('amount', '0.00')}
                Payment Method: {data.get('payment_method', 'N/A')}
                Transaction ID: {data.get('transaction_id', 'N/A')}
                
                Thank you for your purchase!
                
                Best regards,
                E-Commerce Team
                """
            },
            "custom": {
                "subject": data.get("subject", "Notification from E-Commerce"),
                "body": data.get("body", "")
            }
        }
        
        template = templates.get(notification_type, templates["custom"])
        success = self._send_email(email, template["subject"], template["body"])
        
        return {
            "success": success,
            "notification_type": notification_type,
            "message": "Notification sent successfully" if success else "Failed to send notification"
        }
    
    def cleanup_expired_codes(self):
        """Remove expired verification codes"""
        current_time = datetime.now()
        expired_emails = [
            email for email, data in self.verification_codes.items()
            if current_time > data["expiry"]
        ]
        for email in expired_emails:
            del self.verification_codes[email]

