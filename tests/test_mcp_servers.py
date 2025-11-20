"""
Unit tests for MCP servers
"""
import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools.mcp_client import PostgreSQLMCPClient, GmailMCPClient
import time

class TestPostgreSQLMCP:
    """Test PostgreSQL MCP client"""
    
    @pytest.fixture(scope="class")
    def client(self):
        """Create MCP client"""
        client = PostgreSQLMCPClient()
        yield client
        client.close()
    
    def test_get_user_by_email(self, client):
        """Test getting user by email"""
        user = client.get_user_by_email("john@example.com")
        assert user is not None
        assert user.get("email") == "john@example.com"
    
    def test_get_order_by_id(self, client):
        """Test getting order by ID"""
        order = client.get_order_by_id("ORD-12345")
        assert order is not None
        assert order.get("order_number") == "ORD-12345"
    
    def test_get_user_email_from_order(self, client):
        """Test getting email from order"""
        email = client.get_user_email_from_order("ORD-12345")
        assert email is not None
        assert "@" in email
    
    def test_get_user_orders(self, client):
        """Test getting user orders"""
        user = client.get_user_by_email("john@example.com")
        assert user is not None
        orders = client.get_user_orders(user["id"], limit=5)
        assert isinstance(orders, list)
    
    def test_search_orders_by_status(self, client):
        """Test searching orders by status"""
        orders = client.search_orders_by_status("shipped", limit=5)
        assert isinstance(orders, list)

class TestGmailMCP:
    """Test Gmail MCP client"""
    
    @pytest.fixture(scope="class")
    def client(self):
        """Create MCP client"""
        client = GmailMCPClient()
        yield client
        client.close()
    
    def test_send_2fa_code(self, client):
        """Test sending 2FA code"""
        result = client.send_2fa_code("test@example.com", "verification")
        assert "success" in result or "error" in result
    
    def test_verify_2fa_code(self, client):
        """Test verifying 2FA code"""
        # First send a code
        send_result = client.send_2fa_code("test@example.com", "verification")
        if send_result.get("success"):
            # Get the code from the tool (in real scenario, user would get it from email)
            # For testing, we'll use a wrong code
            result = client.verify_2fa_code("test@example.com", "000000")
            assert "verified" in result

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

