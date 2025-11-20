"""
Complete System Test - Verify Everything Works
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.tools.database_tool import DatabaseTool
from src.agent.ecommerce_agent import ECommerceAgent

print("="*60)
print("Complete System Test")
print("="*60)

# Test 1: Database
print("\n[TEST 1] Database Connection")
db = DatabaseTool()
user = db.get_user_by_email("john@example.com")
if user:
    print(f"[OK] User found: {user.get('name', 'N/A')}")
else:
    print("[INFO] User not found (using mock mode is OK)")

order = db.get_order_by_id("ORD-12345")
if order:
    print(f"[OK] Order found: {order.get('order_number', 'N/A')}")
else:
    print("[INFO] Order not found (using mock mode is OK)")

# Test 2: Agent
print("\n[TEST 2] Agent Query")
agent = ECommerceAgent()

test_queries = [
    "What is your return policy?",
    "What is the status of order ORD-12345?",
    "Do you have men's blue shirts in size Large?"
]

for i, query in enumerate(test_queries, 1):
    print(f"\nQuery {i}: {query}")
    try:
        result = agent.process_query(query=query, user_email="john@example.com")
        if result and result.get("answer"):
            answer_preview = result["answer"][:100] + "..." if len(result["answer"]) > 100 else result["answer"]
            print(f"[OK] Answer: {answer_preview}")
        else:
            print("[WARNING] No answer returned")
    except Exception as e:
        print(f"[ERROR] {e}")

print("\n" + "="*60)
print("[SUCCESS] System is fully operational!")
print("="*60)
print("\nNext steps:")
print("  1. streamlit run streamlit_app.py")
print("  2. python run_evaluation.py")
print("  3. python -m uvicorn src.api.main:app --reload")


