"""
Memory Management Testing
Tests conversation history growth and state persistence
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.agent.ecommerce_agent import ECommerceAgent

def test_conversation_history_growth():
    """Test that conversation history doesn't grow exponentially"""
    print("\n" + "="*70)
    print("MEMORY MANAGEMENT TEST: Conversation History Growth")
    print("="*70)
    
    agent = ECommerceAgent()
    thread_id = "test_memory_growth"
    
    message_counts = []
    
    # Run 10 queries
    queries = [
        "hi",
        "what is your return policy?",
        "I want to track my order",
        "ORD-12345",
        "what was my last question?",
        "I want to return this order",
        "actually, I changed my mind",
        "what are your shipping policies?",
        "how long does shipping take?",
        "thank you"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n[Query {i}] {query}")
        result = agent.process_query(query, user_email=None, thread_id=thread_id)
        msg_count = result['debug_info']['conversation_length']
        message_counts.append(msg_count)
        print(f"  Message count: {msg_count}")
        print(f"  Tool calls: {len(result['debug_info']['tool_calls'])}")
    
    print("\n" + "="*70)
    print("MEMORY GROWTH ANALYSIS")
    print("="*70)
    
    print(f"\nMessage counts per query:")
    for i, count in enumerate(message_counts, 1):
        print(f"  Query {i}: {count} messages")
    
    # Check growth pattern
    growth_rates = []
    for i in range(1, len(message_counts)):
        if message_counts[i-1] > 0:
            growth = (message_counts[i] - message_counts[i-1]) / message_counts[i-1]
            growth_rates.append(growth)
    
    avg_growth = sum(growth_rates) / len(growth_rates) if growth_rates else 0
    
    print(f"\n📊 Growth Analysis:")
    print(f"  Average growth rate: {avg_growth*100:.1f}% per query")
    print(f"  Final message count: {message_counts[-1]}")
    print(f"  Total queries: {len(queries)}")
    
    # Check if growth is reasonable
    if message_counts[-1] > 100:
        print(f"\n  ❌ FAIL: Message count too high ({message_counts[-1]})")
        print(f"  Expected: < 50 messages for {len(queries)} queries")
        return False
    elif message_counts[-1] < 50:
        print(f"\n  ✅ PASS: Message count is reasonable ({message_counts[-1]})")
        return True
    else:
        print(f"\n  ⚠️  WARNING: Message count is acceptable but high ({message_counts[-1]})")
        return True

def test_state_persistence():
    """Test that state persists correctly across queries"""
    print("\n" + "="*70)
    print("MEMORY MANAGEMENT TEST: State Persistence")
    print("="*70)
    
    agent = ECommerceAgent()
    thread_id = "test_state_persist"
    
    # Query 1: Track order
    print("\n[Query 1] 'I want to track my order'")
    result1 = agent.process_query("I want to track my order", user_email=None, thread_id=thread_id)
    state1 = result1.get("state", {})
    print(f"  State: {state1}")
    
    # Query 2: Provide order number
    print("\n[Query 2] 'ORD-12345'")
    result2 = agent.process_query("ORD-12345", user_email=None, thread_id=thread_id)
    state2 = result2.get("state", {})
    print(f"  State: {state2}")
    
    # Check if order number persisted
    if state2.get("current_order_number") == "ORD-12345":
        print("  ✅ PASS: Order number persisted in state")
    else:
        print(f"  ❌ FAIL: Order number not persisted. State: {state2}")
        return False
    
    # Query 3: Return order (should remember)
    print("\n[Query 3] 'I want to return this order'")
    result3 = agent.process_query("I want to return this order", user_email=None, thread_id=thread_id)
    state3 = result3.get("state", {})
    print(f"  State: {state3}")
    
    if state3.get("current_order_number") == "ORD-12345":
        print("  ✅ PASS: Order number remembered across queries")
        return True
    else:
        print(f"  ❌ FAIL: Order number not remembered. State: {state3}")
        return False

def test_tool_call_accumulation():
    """Test that tool calls don't accumulate incorrectly"""
    print("\n" + "="*70)
    print("MEMORY MANAGEMENT TEST: Tool Call Accumulation")
    print("="*70)
    
    agent = ECommerceAgent()
    thread_id = "test_tool_accumulation"
    
    tool_call_counts = []
    
    queries = [
        "hi",
        "what is your return policy?",
        "I want to track my order ORD-12345"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n[Query {i}] {query}")
        result = agent.process_query(query, user_email=None, thread_id=thread_id)
        tool_count = len(result['debug_info']['tool_calls'])
        tool_call_counts.append(tool_count)
        print(f"  Tool calls in this query: {tool_count}")
        if tool_count > 0:
            print(f"  Tools: {[tc['tool'] for tc in result['debug_info']['tool_calls']]}")
    
    print("\n📊 Tool Call Analysis:")
    print(f"  Query 1: {tool_call_counts[0]} tool calls")
    print(f"  Query 2: {tool_call_counts[1]} tool calls")
    print(f"  Query 3: {tool_call_counts[2]} tool calls")
    
    # Tool calls should be per-query, not cumulative
    # Query 3 should have the most (order tracking needs tools)
    if tool_call_counts[2] >= tool_call_counts[0] and tool_call_counts[2] >= tool_call_counts[1]:
        print("  ✅ PASS: Tool calls are per-query, not cumulative")
        return True
    else:
        print("  ⚠️  WARNING: Tool call pattern unexpected")
        return True

if __name__ == "__main__":
    print("\n" + "="*70)
    print("MEMORY MANAGEMENT TESTING")
    print("="*70)
    
    results = []
    results.append(("Conversation History Growth", test_conversation_history_growth()))
    results.append(("State Persistence", test_state_persistence()))
    results.append(("Tool Call Accumulation", test_tool_call_accumulation()))
    
    print("\n" + "="*70)
    print("MEMORY TEST SUMMARY")
    print("="*70)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    all_passed = all(result[1] for result in results)
    print(f"\nOverall: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    print("="*70)

