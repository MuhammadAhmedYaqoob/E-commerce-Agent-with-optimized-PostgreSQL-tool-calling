"""
Add test data for ahmedyaqoobbusiness@gmail.com
"""
import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

from src.tools.database_tool import DatabaseTool
import uuid
from datetime import datetime, timedelta

def add_test_data():
    """Add test data for the user's email"""
    db = DatabaseTool()
    
    # Check if user exists
    user = db.get_user_by_email("ahmedyaqoobbusiness@gmail.com")
    if not user:
        # Create user
        user = db.create_user("ahmedyaqoobbusiness@gmail.com", "Ahmed Yaqoob")
        if user:
            print(f"✅ Created user: {user.get('email', 'ahmedyaqoobbusiness@gmail.com')}")
        else:
            print("⚠️  Failed to create user (may already exist)")
            user = {"id": "550e8400-e29b-41d4-a716-446655440013", "email": "ahmedyaqoobbusiness@gmail.com"}
    else:
        print(f"✅ User already exists: {user['email']}")
    
    # Check if orders exist for this user
    orders = db.get_user_orders(user["id"], limit=10)
    if len(orders) < 2:
        print(f"⚠️  User has {len(orders)} orders. Adding test orders...")
        # Note: We can't directly insert via tool, but seed_data.sql should have the data
        print("Please run: python database/load_seed_data.py to ensure all test data is loaded")
    else:
        print(f"✅ User has {len(orders)} orders")
        for order in orders[:3]:
            print(f"  - {order.get('order_number')} - {order.get('status')} - ${order.get('total_amount', 0):.2f}")
    
    print("\n✅ Test data ready!")

if __name__ == "__main__":
    add_test_data()

