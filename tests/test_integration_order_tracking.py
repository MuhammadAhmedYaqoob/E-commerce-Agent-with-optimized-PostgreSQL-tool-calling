"""
Integration Tests for Complete Order Tracking Flow
"""
import pytest
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent.ecommerce_agent import ECommerceAgent
from src.tools.database_tool import DatabaseTool
from src.tools.gmail_tool import GmailTool

class TestIntegrationOrderTracking:
    """Integration tests for complete order tracking scenarios"""
    
    @pytest.fixture
    def agent(self):
        return ECommerceAgent()
    
    @pytest.fixture
    def db_tool(self):
        return DatabaseTool()
    
    @pytest.fixture
    def gmail_tool(self):
        return GmailTool()
    
    def test_complete_flow_not_logged_in_with_order_number(self, agent, gmail_tool):
        """Integration Test 1: Complete flow - Not logged in, order number provided"""
        print("\n" + "="*60)
        print("Integration Test 1: Not Logged In + Order Number")
        print("="*60)
        
        # User provides order number directly
        query = "track my order ORD-12345"
        start_time = time.time()
        
        result = agent.process_query(query=query, user_email=None)
        
        elapsed = time.time() - start_time
        print(f"\n⏱️  Response time: {elapsed:.2f}s")
        
        debug_info = result.get("debug_info", {})
        tool_calls = debug_info.get("tool_calls", [])
        tool_names = [tc["tool"] for tc in tool_calls]
        
        print(f"\n📊 Tool calls made: {tool_names}")
        print(f"📝 Answer: {result['answer'][:200]}...")
        
        # Should call get_user_email_from_order
        assert "get_user_email_from_order" in tool_names, "Should get email from order"
        
        # If email found, should send verification code
        if "get_user_email_from_order" in tool_names:
            # Check tool results to see if email was found
            tool_results = debug_info.get("tool_results", [])
            email_found = any("email found" in str(tr.get("result", "")).lower() for tr in tool_results)
            
            if email_found:
                # Should send verification code
                assert "send_2fa_code" in tool_names, "Should send verification code after finding email"
                print("✅ Flow: Order → Email → Verification Code Sent")
            else:
                print("⚠️  Email not found, skipping verification")
        
        assert elapsed < 10.0, "Should complete in reasonable time"
        print("\n✅ Integration Test 1 PASSED")
    
    def test_complete_flow_not_logged_in_no_order_number(self, agent):
        """Integration Test 2: Complete flow - Not logged in, no order number"""
        print("\n" + "="*60)
        print("Integration Test 2: Not Logged In + No Order Number")
        print("="*60)
        
        query = "I want to track my order"
        start_time = time.time()
        
        result = agent.process_query(query=query, user_email=None)
        
        elapsed = time.time() - start_time
        print(f"\n⏱️  Response time: {elapsed:.2f}s")
        print(f"📝 Answer: {result['answer']}")
        
        # Should ask for order number
        answer_lower = result["answer"].lower()
        assert "order number" in answer_lower or "share" in answer_lower, "Should ask for order number"
        
        assert elapsed < 5.0, "Should respond quickly"
        print("\n✅ Integration Test 2 PASSED")
    
    def test_complete_flow_logged_in(self, agent):
        """Integration Test 3: Complete flow - Logged in user"""
        print("\n" + "="*60)
        print("Integration Test 3: Logged In User")
        print("="*60)
        
        query = "track my order ORD-12345"
        start_time = time.time()
        
        result = agent.process_query(query=query, user_email="john@example.com")
        
        elapsed = time.time() - start_time
        print(f"\n⏱️  Response time: {elapsed:.2f}s")
        
        debug_info = result.get("debug_info", {})
        tool_calls = debug_info.get("tool_calls", [])
        tool_names = [tc["tool"] for tc in tool_calls]
        
        print(f"📊 Tool calls made: {tool_names}")
        print(f"📝 Answer: {result['answer'][:200]}...")
        
        # Should NOT use verification tools
        assert "get_user_email_from_order" not in tool_names, "Logged-in users skip email lookup"
        assert "send_2fa_code" not in tool_names, "Logged-in users skip verification"
        
        # Should directly get order
        assert "get_order" in tool_names, "Should directly get order"
        
        assert elapsed < 10.0, "Should complete quickly"
        print("\n✅ Integration Test 3 PASSED")
    
    def test_multi_turn_conversation(self, agent, gmail_tool):
        """Integration Test 4: Multi-turn conversation flow"""
        print("\n" + "="*60)
        print("Integration Test 4: Multi-Turn Conversation")
        print("="*60)
        
        conversation_history = []
        
        # Turn 1: User asks to track order
        print("\n🔄 Turn 1: User asks to track order")
        result1 = agent.process_query(
            query="I want to track my order",
            user_email=None,
            conversation_history=conversation_history
        )
        conversation_history.append(("user", "I want to track my order"))
        conversation_history.append(("assistant", result1["answer"]))
        print(f"Assistant: {result1['answer']}")
        
        # Turn 2: User provides order number
        print("\n🔄 Turn 2: User provides order number")
        result2 = agent.process_query(
            query="ORD-12345",
            user_email=None,
            conversation_history=conversation_history
        )
        conversation_history.append(("user", "ORD-12345"))
        conversation_history.append(("assistant", result2["answer"]))
        print(f"Assistant: {result2['answer'][:200]}...")
        
        debug_info = result2.get("debug_info", {})
        tool_calls = debug_info.get("tool_calls", [])
        tool_names = [tc["tool"] for tc in tool_calls]
        print(f"📊 Tools used: {tool_names}")
        
        # Should have used tools in turn 2
        assert len(tool_calls) > 0, "Should use tools when order number provided"
        
        # Turn 3: User provides verification code (if code was sent)
        if "send_2fa_code" in tool_names:
            print("\n🔄 Turn 3: User provides verification code")
            # Get the code from gmail_tool's storage
            tool_results = debug_info.get("tool_results", [])
            email_result = next((tr for tr in tool_results if tr["tool"] == "get_user_email_from_order"), None)
            
            if email_result and "john@example.com" in str(email_result.get("result", "")):
                # Find the code
                if "john@example.com" in gmail_tool.verification_codes:
                    code = gmail_tool.verification_codes["john@example.com"]["code"]
                    print(f"📧 Using verification code: {code}")
                    
                    result3 = agent.process_query(
                        query=f"verification code: {code}",
                        user_email=None,
                        conversation_history=conversation_history
                    )
                    print(f"Assistant: {result3['answer'][:200]}...")
                    
                    debug_info3 = result3.get("debug_info", {})
                    tool_calls3 = debug_info3.get("tool_calls", [])
                    tool_names3 = [tc["tool"] for tc in tool_calls3]
                    
                    # Should verify code and get order
                    assert "verify_2fa_code" in tool_names3, "Should verify code"
                    assert "get_order" in tool_names3, "Should get order after verification"
                    print("✅ Verification successful, order retrieved")
        
        print("\n✅ Integration Test 4 PASSED")
    
    def test_performance_benchmark(self, agent):
        """Integration Test 5: Performance benchmark"""
        print("\n" + "="*60)
        print("Integration Test 5: Performance Benchmark")
        print("="*60)
        
        queries = [
            ("hi", None),
            ("I want to track my order", None),
            ("ORD-12345", None),
            ("track order ORD-12345", "john@example.com"),
        ]
        
        times = []
        for query, email in queries:
            start = time.time()
            result = agent.process_query(query=query, user_email=email)
            elapsed = time.time() - start
            times.append(elapsed)
            print(f"Query: '{query}' - {elapsed:.2f}s")
        
        avg_time = sum(times) / len(times)
        max_time = max(times)
        
        print(f"\n📊 Average response time: {avg_time:.2f}s")
        print(f"📊 Max response time: {max_time:.2f}s")
        
        assert avg_time < 5.0, f"Average response time should be < 5s (got {avg_time:.2f}s)"
        assert max_time < 15.0, f"Max response time should be < 15s (got {max_time:.2f}s)"
        
        print("\n✅ Integration Test 5 PASSED")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

