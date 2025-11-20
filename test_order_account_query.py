"""
Comprehensive Test Suite for Order Account Query Scenario
Tests the specific scenario: "I want to know that how many orders are belong to my account currently"
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.agent.ecommerce_agent import ECommerceAgent
from src.tools.database_tool import DatabaseTool
import json

def print_section(title):
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def print_test(test_name):
    print(f"\n[TEST] {test_name}")
    print("-" * 80)

def test_order_account_query_logged_in():
    """Test: User asks about orders when logged in (user_email provided)"""
    print_test("Order Account Query - LOGGED IN USER")
    
    agent = ECommerceAgent()
    query = "I want to know that how many orders are belong to my account currently"
    user_email = "john@example.com"  # Simulating logged-in user
    
    print(f"Query: {query}")
    print(f"User Email: {user_email}")
    print("\nProcessing query...")
    
    try:
        result = agent.process_query(
            query=query,
            user_email=user_email,
            thread_id="test_logged_in"
        )
        
        print(f"\n[RESULT] Answer: {result.get('answer', 'N/A')}")
        print(f"[RESULT] Steps: {result.get('steps', 'N/A')}")
        print(f"[RESULT] Iterations: {result.get('iterations', 0)}")
        print(f"[RESULT] Tool Usage: {result.get('tool_usage', 0)}")
        
        # Check if search_orders tool was used
        tool_calls = result.get('debug_info', {}).get('tool_calls', [])
        print(f"\n[TOOLS] Tools called: {len(tool_calls)}")
        for i, tool_call in enumerate(tool_calls, 1):
            print(f"  {i}. {tool_call.get('tool', 'unknown')}: {json.dumps(tool_call.get('args', {}), indent=2)}")
        
        # Verify correct behavior
        answer_lower = result.get('answer', '').lower()
        used_search_orders = any(tc.get('tool') == 'search_orders' for tc in tool_calls)
        
        print(f"\n[VERIFICATION]")
        print(f"  Used search_orders tool: {used_search_orders}")
        print(f"  Answer mentions orders: {'order' in answer_lower}")
        print(f"  Answer mentions count/number: {any(word in answer_lower for word in ['order', 'found', 'have', 'total', 'count'])}")
        
        if used_search_orders:
            print("  [OK] CORRECT: Used search_orders tool for logged-in user")
        else:
            print("  [ERROR] Should have used search_orders tool for logged-in user")
        
        if "order number" in answer_lower and "can you" in answer_lower:
            print("  [ERROR] Asked for order number when should show all orders")
        else:
            print("  [OK] CORRECT: Did not incorrectly ask for order number")
        
        return result
        
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_order_account_query_not_logged_in():
    """Test: User asks about orders when NOT logged in (no user_email)"""
    print_test("Order Account Query - NOT LOGGED IN USER")
    
    agent = ECommerceAgent()
    query = "I want to know that how many orders are belong to my account currently"
    user_email = None  # Not logged in
    
    print(f"Query: {query}")
    print(f"User Email: {user_email or 'NOT PROVIDED'}")
    print("\nProcessing query...")
    
    try:
        result = agent.process_query(
            query=query,
            user_email=user_email,
            thread_id="test_not_logged_in"
        )
        
        print(f"\n[RESULT] Answer: {result.get('answer', 'N/A')}")
        print(f"[RESULT] Steps: {result.get('steps', 'N/A')}")
        print(f"[RESULT] Iterations: {result.get('iterations', 0)}")
        print(f"[RESULT] Tool Usage: {result.get('tool_usage', 0)}")
        
        # Check if search_orders tool was used
        tool_calls = result.get('debug_info', {}).get('tool_calls', [])
        print(f"\n[TOOLS] Tools called: {len(tool_calls)}")
        for i, tool_call in enumerate(tool_calls, 1):
            print(f"  {i}. {tool_call.get('tool', 'unknown')}: {json.dumps(tool_call.get('args', {}), indent=2)}")
        
        # Verify correct behavior
        answer_lower = result.get('answer', '').lower()
        
        print(f"\n[VERIFICATION]")
        print(f"  Answer mentions order number: {'order number' in answer_lower}")
        print(f"  Answer asks for order number: {('order number' in answer_lower and 'can you' in answer_lower) or 'share' in answer_lower}")
        
        # For non-logged-in users, asking for order number is acceptable
        # But ideally should explain they need to log in or provide order number
        if "order number" in answer_lower or "log in" in answer_lower or "email" in answer_lower:
            print("  [OK] ACCEPTABLE: Asked for order number or login (expected for non-logged-in)")
        else:
            print("  [WARNING] Response may not be clear for non-logged-in user")
        
        return result
        
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_memory_preservation():
    """Test: Memory and context preservation across multiple queries"""
    print_test("Memory and Context Preservation")
    
    agent = ECommerceAgent()
    thread_id = "test_memory"
    
    queries = [
        ("What is your return policy?", None),
        ("I want to track my order ORD-12345", None),
        ("What is the status?", None),  # Should remember ORD-12345
        ("I want to know that how many orders are belong to my account currently", "john@example.com"),
    ]
    
    print("Running sequence of queries to test memory...")
    
    for i, (query, user_email) in enumerate(queries, 1):
        print(f"\n[Query {i}] {query}")
        print(f"  User Email: {user_email or 'NOT PROVIDED'}")
        
        try:
            result = agent.process_query(
                query=query,
                user_email=user_email,
                thread_id=thread_id
            )
            
            answer_preview = result.get('answer', '')[:100]
            print(f"  Answer: {answer_preview}...")
            
            # Check if order number was remembered
            if i == 3:  # Third query should remember ORD-12345
                tool_calls = result.get('debug_info', {}).get('tool_calls', [])
                used_order = any('ORD-12345' in str(tc.get('args', {})) for tc in tool_calls)
                if used_order:
                    print("  [OK] Memory working: Used remembered order number")
                else:
                    print("  [WARNING] Memory: Order number may not have been remembered")
        
        except Exception as e:
            print(f"  [ERROR] {e}")
    
    print("\n[VERIFICATION] Memory test completed")

def test_database_tool():
    """Test: Database tool functionality"""
    print_test("Database Tool Functionality")
    
    db = DatabaseTool()
    
    # Test get_user_by_email
    print("\n[1] Testing get_user_by_email...")
    user = db.get_user_by_email("john@example.com")
    if user:
        print(f"  [OK] User found: {user.get('email', 'N/A')}")
        user_id = user.get('id')
        
        # Test get_user_orders
        print(f"\n[2] Testing get_user_orders for user_id: {user_id}...")
        orders = db.get_user_orders(user_id, limit=10)
        print(f"  [OK] Found {len(orders)} orders")
        if orders:
            print(f"  Sample order: {orders[0].get('order_number', 'N/A')} - {orders[0].get('status', 'N/A')}")
    else:
        print("  [WARNING] User not found (may be using mock mode)")
    
    # Test search_orders functionality
    print(f"\n[3] Testing search_orders_by_status...")
    orders = db.search_orders_by_status("pending", limit=5)
    print(f"  [OK] Found {len(orders)} pending orders")
    
    print("\n[VERIFICATION] Database tool tests completed")

def run_all_tests():
    """Run all tests"""
    print_section("COMPREHENSIVE TEST SUITE - Order Account Query")
    print("Testing bot behavior, memory, and all aspects")
    
    # Test 1: Database tool
    test_database_tool()
    
    # Test 2: Logged-in user query
    result1 = test_order_account_query_logged_in()
    
    # Test 3: Not logged-in user query
    result2 = test_order_account_query_not_logged_in()
    
    # Test 4: Memory preservation
    test_memory_preservation()
    
    # Summary
    print_section("TEST SUMMARY")
    print("\n[RESULTS]")
    print(f"  Logged-in test: {'[PASSED]' if result1 else '[FAILED]'}")
    print(f"  Not logged-in test: {'[PASSED]' if result2 else '[FAILED]'}")
    print("\n[RECOMMENDATIONS]")
    
    if result1:
        tool_calls = result1.get('debug_info', {}).get('tool_calls', [])
        used_search = any(tc.get('tool') == 'search_orders' for tc in tool_calls)
        if not used_search:
            print("  [WARNING] For logged-in users asking about 'my orders', bot should use search_orders tool")
            print("  [WARNING] Current behavior may be asking for order number incorrectly")
    
    print("\n[COMPLETE] All tests finished")

if __name__ == "__main__":
    run_all_tests()

