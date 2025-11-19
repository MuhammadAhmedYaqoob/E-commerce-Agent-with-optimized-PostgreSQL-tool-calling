"""
Unit tests for Gmail Tool
"""
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import pathlib

import sys
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from src.tools.gmail_tool import GmailTool
from src.config import EMAIL_VERIFICATION_EXPIRY


class TestGmailTool(unittest.TestCase):
    """Test cases for Gmail Tool"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.gmail_tool = GmailTool()
    
    def test_init(self):
        """Test Gmail tool initialization"""
        self.assertEqual(self.gmail_tool.smtp_server, "smtp.gmail.com")
        self.assertEqual(self.gmail_tool.smtp_port, 587)
        self.assertIsInstance(self.gmail_tool.verification_codes, dict)
    
    def test_generate_verification_code(self):
        """Test verification code generation"""
        code = self.gmail_tool._generate_verification_code()
        self.assertEqual(len(code), 6)
        self.assertTrue(code.isdigit())
    
    def test_generate_verification_code_custom_length(self):
        """Test verification code with custom length"""
        code = self.gmail_tool._generate_verification_code(length=8)
        self.assertEqual(len(code), 8)
        self.assertTrue(code.isdigit())
    
    @patch('src.tools.gmail_tool.smtplib.SMTP')
    def test_send_email_success(self, mock_smtp):
        """Test successful email sending"""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        self.gmail_tool.user = "test@example.com"
        self.gmail_tool.password = "test_password"
        
        result = self.gmail_tool._send_email("recipient@example.com", "Test", "Body")
        self.assertTrue(result)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once()
    
    def test_send_email_no_credentials(self):
        """Test email sending without credentials"""
        self.gmail_tool.user = None
        self.gmail_tool.password = None
        result = self.gmail_tool._send_email("test@example.com", "Test", "Body")
        self.assertFalse(result)
    
    def test_send_2fa_code(self):
        """Test sending 2FA code"""
        with patch.object(self.gmail_tool, '_send_email', return_value=True):
            result = self.gmail_tool.send_2fa_code("test@example.com", "verification")
            self.assertTrue(result["success"])
            self.assertIn("test@example.com", self.gmail_tool.verification_codes)
            self.assertIn("code", self.gmail_tool.verification_codes["test@example.com"])
    
    def test_verify_2fa_code_success(self):
        """Test successful 2FA verification"""
        email = "test@example.com"
        code = "123456"
        self.gmail_tool.verification_codes[email] = {
            "code": code,
            "expiry": datetime.now() + timedelta(seconds=EMAIL_VERIFICATION_EXPIRY),
            "purpose": "verification",
            "created_at": datetime.now()
        }
        
        result = self.gmail_tool.verify_2fa_code(email, code)
        self.assertTrue(result["verified"])
        self.assertNotIn(email, self.gmail_tool.verification_codes)  # Should be deleted
    
    def test_verify_2fa_code_invalid(self):
        """Test invalid 2FA code verification"""
        email = "test@example.com"
        self.gmail_tool.verification_codes[email] = {
            "code": "123456",
            "expiry": datetime.now() + timedelta(seconds=EMAIL_VERIFICATION_EXPIRY),
            "purpose": "verification",
            "created_at": datetime.now()
        }
        
        result = self.gmail_tool.verify_2fa_code(email, "wrong_code")
        self.assertFalse(result["verified"])
    
    def test_verify_2fa_code_expired(self):
        """Test expired 2FA code verification"""
        email = "test@example.com"
        self.gmail_tool.verification_codes[email] = {
            "code": "123456",
            "expiry": datetime.now() - timedelta(seconds=1),  # Expired
            "purpose": "verification",
            "created_at": datetime.now()
        }
        
        result = self.gmail_tool.verify_2fa_code(email, "123456")
        self.assertFalse(result["verified"])
        self.assertNotIn(email, self.gmail_tool.verification_codes)  # Should be deleted
    
    def test_verify_2fa_code_not_found(self):
        """Test verification when code not found"""
        result = self.gmail_tool.verify_2fa_code("nonexistent@example.com", "123456")
        self.assertFalse(result["verified"])
    
    def test_send_notification(self):
        """Test sending notification"""
        with patch.object(self.gmail_tool, '_send_email', return_value=True):
            data = {
                "order_id": "12345",
                "customer_name": "Test User",
                "status": "shipped"
            }
            result = self.gmail_tool.send_notification("test@example.com", "order_update", data)
            self.assertTrue(result["success"])
    
    def test_cleanup_expired_codes(self):
        """Test cleanup of expired codes"""
        # Add expired code
        self.gmail_tool.verification_codes["expired@example.com"] = {
            "code": "123456",
            "expiry": datetime.now() - timedelta(seconds=1),
            "purpose": "verification",
            "created_at": datetime.now()
        }
        # Add valid code
        self.gmail_tool.verification_codes["valid@example.com"] = {
            "code": "654321",
            "expiry": datetime.now() + timedelta(seconds=EMAIL_VERIFICATION_EXPIRY),
            "purpose": "verification",
            "created_at": datetime.now()
        }
        
        self.gmail_tool.cleanup_expired_codes()
        self.assertNotIn("expired@example.com", self.gmail_tool.verification_codes)
        self.assertIn("valid@example.com", self.gmail_tool.verification_codes)


if __name__ == '__main__':
    unittest.main()

