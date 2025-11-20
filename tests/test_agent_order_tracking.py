"""
Comprehensive Unit and Functional Tests for Order Tracking Agent
"""
import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent.ecommerce_agent import ECommerceAgent
from src.tools.database_tool import DatabaseTool
from src.tools.gmail_tool import GmailTool
import time

class TestOrderTracking:
    """Test suite for order tracking functionality"""
    
    @pytest.fixture
    def agent(self):
        """Initialize agent for testing"""
        return ECommerceAgent()
    
    @pytest.fixture
    def db_tool(self):
        """Initialize database tool"""
        return DatabaseTool()
    
    @pytest.fixture
    def gmail_tool(self):
        """Initialize Gmail tool"""
        return GmailTool()
    
    def test_database_has_seed_data(self, db_tool):
        """Test 1: Verify database has seed data"""
        # Test user exists
        user = db_tool.get_user_by_email("john@example.com")
        assert user is not None, "Test user john@example.com should exist"
        assert user["email"] == "john@example.com"
        
        # Test order exists
        order = db_tool.get_order_by_id("ORD-12345")
        assert order is not None, "Test order ORD-12345 should exist"
        assert order["order_number"] == "ORD-12345"
        
        # Test can get email from order
        email = db_tool.get_user_email_from_order("ORD-12345")
        assert email is not None, "Should be able to get email from order"
        assert email == "john@example.com"
    
    def test_get_user_email_from_order_tool(self, agent):
        """Test 2: Test get_user_email_from_order tool"""
        # This should work without user being logged in
        result = agent.process_query(
            query="ORD-12345",
            user_email=None  # Not logged in
        )
        
        # Check if tool was called
        debug_info = result.get("debug_info", {})
        tool_calls = debug_info.get("tool_calls", [])
        
        # Should call get_user_email_from_order
        tool_names = [tc["tool"] for tc in tool_calls]
        assert "get_user_email_from_order" in tool_names, "Should call get_user_email_from_order tool"
    
    def test_order_tracking_flow_not_logged_in(self, agent):
        """Test 3: Full order tracking flow for non-logged-in user"""
        # Step 1: User asks to track order (no order number)
        result1 = agent.process_query(
            query="I want to track my order",
            user_email=None
        )
        
        answer1 = result1["answer"].lower()
        assert "order number" in answer1 or "share" in answer1, "Should ask for order number"
        
        # Step 2: User provides order number
        result2 = agent.process_query(
            query="ORD-12345",
            user_email=None,
            conversation_history=[("user", "I want to track my order"), ("assistant", result1["answer"])]
        )
        
        debug_info = result2.get("debug_info", {})
        tool_calls = debug_info.get("tool_calls", [])
        tool_names = [tc["tool"] for tc in tool_calls]
        
        # Should call get_user_email_from_order
        assert "get_user_email_from_order" in tool_names, "Should call get_user_email_from_order"
    
    def test_order_tracking_flow_logged_in(self, agent):
        """Test 4: Order tracking for logged-in user (should skip verification)"""
        result = agent.process_query(
            query="track my order ORD-12345",
            user_email="john@example.com"  # Logged in
        )
        
        debug_info = result.get("debug_info", {})
        tool_calls = debug_info.get("tool_calls", [])
        tool_names = [tc["tool"] for tc in tool_calls]
        
        # Should NOT call verification tools
        assert "get_user_email_from_order" not in tool_names, "Logged-in users should not need email lookup"
        assert "send_2fa_code" not in tool_names, "Logged-in users should not need verification"
        
        # Should directly call get_order
        assert "get_order" in tool_names, "Should directly get order for logged-in users"
    
    def test_gmail_tool_send_code(self, gmail_tool):
        """Test 5: Gmail tool can send verification code"""
        result = gmail_tool.send_2fa_code("john@example.com", "order_verification")
        
        assert result["success"] is True, "Should successfully send code"
        assert "code_sent" in result
        assert result.get("expiry_seconds") == 30, "Code should expire in 30 seconds"
    
    def test_gmail_tool_verify_code(self, gmail_tool):
        """Test 6: Gmail tool can verify code"""
        # Send code first
        send_result = gmail_tool.send_2fa_code("test@example.com", "test")
        assert send_result["success"] is True
        
        # Get the code from the tool's internal storage
        # Note: This is a bit hacky, but we need to test verification
        stored_codes = gmail_tool.verification_codes
        if "test@example.com" in stored_codes:
            code = stored_codes["test@example.com"]["code"]
            
            # Verify code
            verify_result = gmail_tool.verify_2fa_code("test@example.com", code)
            assert verify_result["verified"] is True, "Should verify correct code"
            
            # Test wrong code
            wrong_result = gmail_tool.verify_2fa_code("test@example.com", "000000")
            assert wrong_result["verified"] is False, "Should reject wrong code"
    
    def test_order_number_detection(self, agent):
        """Test 7: Agent detects order numbers in queries"""
        queries_with_orders = [
            "ORD-12345",
            "track order ORD-12345",
            "order number ORD-12345",
            "ORD12345"
        ]
        
        for query in queries_with_orders:
            result = agent.process_query(query=query, user_email=None)
            # Should detect order number and proceed with tools
            debug_info = result.get("debug_info", {})
            # At minimum, should not give generic response
            assert "order" in result["answer"].lower() or len(debug_info.get("tool_calls", [])) > 0
    
    def test_performance_order_lookup(self, db_tool):
        """Test 8: Performance - Order lookup speed"""
        start = time.time()
        for _ in range(10):
            order = db_tool.get_order_by_id("ORD-12345")
            assert order is not None
        elapsed = time.time() - start
        
        avg_time = elapsed / 10
        assert avg_time < 0.1, f"Order lookup should be fast (avg: {avg_time:.3f}s, max: 0.1s)"
        print(f"✅ Average order lookup time: {avg_time:.3f}s")
    
    def test_performance_email_lookup(self, db_tool):
        """Test 9: Performance - Email lookup from order"""
        start = time.time()
        for _ in range(10):
            email = db_tool.get_user_email_from_order("ORD-12345")
            assert email is not None
        elapsed = time.time() - start
        
        avg_time = elapsed / 10
        assert avg_time < 0.1, f"Email lookup should be fast (avg: {avg_time:.3f}s, max: 0.1s)"
        print(f"✅ Average email lookup time: {avg_time:.3f}s")
    
    def test_agent_response_time(self, agent):
        """Test 10: Performance - Agent response time"""
        start = time.time()
        result = agent.process_query("hi", user_email=None)
        elapsed = time.time() - start
        
        assert elapsed < 5.0, f"Agent should respond quickly (took: {elapsed:.2f}s, max: 5s)"
        assert result["answer"] is not None
        print(f"✅ Agent response time: {elapsed:.2f}s")
    
    def test_conversation_context_preservation(self, agent):
        """Test 11: Conversation context is preserved"""
        # First message
        result1 = agent.process_query("I want to track my order", user_email=None)
        
        # Second message with context
        result2 = agent.process_query(
            "ORD-12345",
            user_email=None,
            conversation_history=[("user", "I want to track my order"), ("assistant", result1["answer"])]
        )
        
        # Should use context from previous message
        assert len(result2.get("debug_info", {}).get("tool_calls", [])) > 0 or "order" in result2["answer"].lower()
    
    def test_error_handling_invalid_order(self, agent):
        """Test 12: Error handling for invalid order number"""
        result = agent.process_query(
            query="ORD-99999",  # Non-existent order
            user_email=None
        )
        
        # Should handle gracefully
        answer = result["answer"].lower()
        assert "not found" in answer or "couldn't find" in answer or "invalid" in answer

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

