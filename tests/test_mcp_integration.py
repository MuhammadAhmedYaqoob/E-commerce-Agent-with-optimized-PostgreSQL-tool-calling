"""
Functional tests for MCP integration with LangGraph
"""
import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent.ecommerce_agent import ECommerceAgent
import time

class TestMCPIntegration:
    """Test MCP integration with agent"""
    
    @pytest.fixture(scope="class")
    def agent(self):
        """Create agent with MCP clients"""
        agent = ECommerceAgent()
        yield agent
    
    def test_order_tracking_with_mcp(self, agent):
        """Test order tracking using MCP"""
        result = agent.process_query(
            query="I want to track my order ORD-12345",
            user_email=None,
            thread_id="test_mcp_1"
        )
        assert "order" in result["answer"].lower() or "tracking" in result["answer"].lower()
    
    def test_user_email_from_order_mcp(self, agent):
        """Test getting user email from order via MCP"""
        result = agent.process_query(
            query="What email is associated with order ORD-12345?",
            user_email=None,
            thread_id="test_mcp_2"
        )
        # Should either get email or ask for verification
        assert len(result["answer"]) > 0
    
    def test_2fa_flow_with_mcp(self, agent):
        """Test 2FA flow using MCP"""
        # Step 1: Request order tracking
        result1 = agent.process_query(
            query="I want to track my order",
            user_email=None,
            thread_id="test_mcp_3"
        )
        assert "order number" in result1["answer"].lower()
        
        # Step 2: Provide order number
        result2 = agent.process_query(
            query="ORD-12345",
            user_email=None,
            thread_id="test_mcp_3"
        )
        # Should send verification code
        assert "verification" in result2["answer"].lower() or "code" in result2["answer"].lower()
    
    def test_search_orders_with_mcp(self, agent):
        """Test searching orders via MCP"""
        result = agent.process_query(
            query="Show me my orders",
            user_email="john@example.com",
            thread_id="test_mcp_4"
        )
        assert "order" in result["answer"].lower()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

