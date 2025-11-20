"""
Comprehensive Test Suite - All Scenarios
Tests the complete agentic behavior with state management
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.agent.ecommerce_agent import ECommerceAgent
import time

def test_scenario(name, queries, user_email=None, expected_behaviors=None):
    """Test a complete scenario"""
    print(f"\n{'='*70}")
    print(f"SCENARIO: {name}")
    print(f"{'='*70}")
    
    agent = ECommerceAgent()
    thread_id = user_email if user_email else "test_anonymous"
    
    results = []
    for i, query in enumerate(queries, 1):
        print(f"\n[Turn {i}] User: {query}")
        print("-" * 70)
        
        start = time.time()
        result = agent.process_query(
            query=query,
            user_email=user_email,
            thread_id=thread_id
        )
        elapsed = time.time() - start
        
        answer = result["answer"]
        state = result.get("state", {})
        tool_calls = result.get("debug_info", {}).get("tool_calls", [])
        
        print(f"Assistant: {answer[:300]}...")
        print(f"Time: {elapsed:.2f}s | Tools: {len(tool_calls)}")
        if state.get("current_order_number"):
            print(f"State - Order: {state['current_order_number']}, Process: {state.get('current_process')}")
        
        results.append({
            "query": query,
            "answer": answer,
            "state": state,
            "tools": tool_calls,
            "time": elapsed
        })
        
        # Check expected behaviors
        if expected_behaviors and i <= len(expected_behaviors):
            expected = expected_behaviors[i-1]
            if expected:
                check_passed = any(expected.lower() in answer.lower() for expected in expected) if isinstance(expected, list) else expected.lower() in answer.lower()
                status = "PASS" if check_passed else "FAIL"
                print(f"[{status}] Expected: {expected}")
    
    return results

def main():
    print("="*70)
    print("COMPREHENSIVE AGENT TEST SUITE")
    print("="*70)
    
    # Scenario 1: Order Tracking - Not Logged In
    print("\n\n" + "="*70)
    test_scenario(
        "Order Tracking - Not Logged In",
        [
            "I want to track my order",
            "ORD-12345",
            "477763"  # Verification code
        ],
        user_email=None,
        expected_behaviors=[
            ["order number", "share"],
            ["verification code", "sent"],
            ["order", "status"]  # Should show order after verification
        ]
    )
    
    # Scenario 2: Order Tracking - Logged In
    print("\n\n" + "="*70)
    test_scenario(
        "Order Tracking - Logged In",
        [
            "I want to track my order",
            "ORD-12345"
        ],
        user_email="john@example.com",
        expected_behaviors=[
            ["order"],  # Should show orders or ask for order number
            ["order", "status"]  # Should show order details
        ]
    )
    
    # Scenario 3: Context Preservation - Return After Tracking
    print("\n\n" + "="*70)
    test_scenario(
        "Context Preservation - Return After Tracking",
        [
            "I want to track my order",
            "ORD-12345",
            "I want to return this order"  # Should remember ORD-12345
        ],
        user_email="john@example.com",
        expected_behaviors=[
            ["order"],
            ["order", "status"],
            ["return", "ORD-12345"]  # Should remember the order
        ]
    )
    
    # Scenario 4: Process Cancellation
    print("\n\n" + "="*70)
    test_scenario(
        "Process Cancellation",
        [
            "I want to return my order ORD-12345",
            "Actually, I changed my mind, I don't want to return it"
        ],
        user_email="john@example.com",
        expected_behaviors=[
            ["return"],
            ["changed", "mind", "cancel"]  # Should acknowledge cancellation
        ]
    )
    
    # Scenario 5: Policy Questions
    print("\n\n" + "="*70)
    test_scenario(
        "Policy Questions",
        [
            "What are your return policies?",
            "What was my last question?"
        ],
        user_email=None,
        expected_behaviors=[
            ["return", "policy", "30 days"],  # Should not include guardrails
            ["return", "policy"]  # Should remember
        ]
    )
    
    print("\n\n" + "="*70)
    print("TEST SUITE COMPLETE")
    print("="*70)

if __name__ == "__main__":
    main()

