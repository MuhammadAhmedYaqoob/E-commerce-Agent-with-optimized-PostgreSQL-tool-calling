"""
Quick Simple Test - No Unicode Issues
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.agent.ecommerce_agent import ECommerceAgent

def main():
    print("\n" + "="*70)
    print("QUICK AGENT TEST")
    print("="*70)
    
    agent = ECommerceAgent()
    thread_id = "quick_test_1"
    
    # Test 1: Simple query
    print("\n[Test 1] Query: 'hi'")
    result1 = agent.process_query("hi", user_email=None, thread_id=thread_id)
    print(f"Response: {result1['answer'][:100]}...")
    print(f"Messages: {result1['debug_info']['conversation_length']}")
    print(f"Tool calls: {len(result1['debug_info']['tool_calls'])}")
    
    # Test 2: Order tracking
    print("\n[Test 2] Query: 'I want to track my order'")
    result2 = agent.process_query("I want to track my order", user_email=None, thread_id=thread_id)
    print(f"Response: {result2['answer'][:100]}...")
    print(f"Messages: {result2['debug_info']['conversation_length']}")
    print(f"Tool calls: {len(result2['debug_info']['tool_calls'])}")
    
    # Test 3: Order number
    print("\n[Test 3] Query: 'ORD-12345'")
    result3 = agent.process_query("ORD-12345", user_email=None, thread_id=thread_id)
    print(f"Response: {result3['answer'][:150]}...")
    print(f"Messages: {result3['debug_info']['conversation_length']}")
    print(f"Tool calls: {len(result3['debug_info']['tool_calls'])}")
    
    # Memory check
    print("\n" + "="*70)
    print("MEMORY CHECK")
    print("="*70)
    msg_counts = [
        result1['debug_info']['conversation_length'],
        result2['debug_info']['conversation_length'],
        result3['debug_info']['conversation_length']
    ]
    print(f"Query 1: {msg_counts[0]} messages")
    print(f"Query 2: {msg_counts[1]} messages")
    print(f"Query 3: {msg_counts[2]} messages")
    
    if msg_counts[2] < 50:
        print("\nPASS: Memory growth is reasonable")
    else:
        print(f"\nWARNING: Memory growth is high ({msg_counts[2]} messages)")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()

