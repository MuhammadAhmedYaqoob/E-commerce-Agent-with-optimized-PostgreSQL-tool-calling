"""
Quick script to verify database has seed data
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.tools.database_tool import DatabaseTool

def verify_database():
    """Verify database has seed data"""
    print("="*60)
    print("Verifying Database Seed Data")
    print("="*60)
    
    db_tool = DatabaseTool()
    
    # Check users
    test_user = db_tool.get_user_by_email("john@example.com")
    if test_user:
        print(f"✅ Found test user: {test_user.get('name')} ({test_user.get('email')})")
    else:
        print("❌ Test user not found. Please run database/load_seed_data.py")
        return False
    
    # Check orders
    test_order = db_tool.get_order_by_id("ORD-12345")
    if test_order:
        print(f"✅ Found test order: {test_order.get('order_number')} - Status: {test_order.get('status')}")
        
        # Check if we can get user email from order
        user_email = db_tool.get_user_email_from_order("ORD-12345")
        if user_email:
            print(f"✅ Can retrieve user email from order: {user_email}")
        else:
            print("❌ Cannot retrieve user email from order")
            return False
    else:
        print("❌ Test order not found. Please run database/load_seed_data.py")
        return False
    
    # List some orders
    orders = db_tool.search_orders_by_status("shipped", limit=5)
    print(f"✅ Found {len(orders)} shipped orders")
    
    print("\n" + "="*60)
    print("✅ Database verification successful!")
    print("="*60)
    return True

if __name__ == "__main__":
    success = verify_database()
    sys.exit(0 if success else 1)

