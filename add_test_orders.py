"""
Add test orders for ahmedyaqoobbusiness@gmail.com
"""
import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import psycopg2
from datetime import datetime, timedelta

DB_NAME = "ecommerce_db"
DB_USER = "postgres"
DB_PASSWORD = "datalens"
DB_HOST = "localhost"
DB_PORT = 5432

def add_test_orders():
    """Add test orders for the user"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()
        
        # Get user ID
        cursor.execute("SELECT id FROM users WHERE email = 'ahmedyaqoobbusiness@gmail.com'")
        user_row = cursor.fetchone()
        if not user_row:
            print("ERROR: User not found")
            return
        user_id = user_row[0]
        print(f"Found user ID: {user_id}")
        
        # Check if orders exist
        cursor.execute("SELECT COUNT(*) FROM orders WHERE user_id = %s", (user_id,))
        order_count = cursor.fetchone()[0]
        print(f"Current orders: {order_count}")
        
        if order_count == 0:
            # Add orders
            orders = [
                {
                    'id': '880e8400-e29b-41d4-a716-446655440010',
                    'order_number': 'ORD-88888',
                    'status': 'shipped',
                    'total': 172.98,
                    'tracking': 'TRACK999888777',
                    'carrier': 'FedEx',
                    'delivery': datetime.now() + timedelta(days=2)
                },
                {
                    'id': '880e8400-e29b-41d4-a716-446655440011',
                    'order_number': 'ORD-99999',
                    'status': 'delivered',
                    'total': 97.19,
                    'tracking': 'TRACK111222333',
                    'carrier': 'UPS',
                    'delivery': datetime.now() - timedelta(days=3)
                }
            ]
            
            for order in orders:
                cursor.execute("""
                    INSERT INTO orders (id, user_id, order_number, status, payment_status, 
                                      payment_method, subtotal, tax, shipping_cost, total_amount,
                                      tracking_number, carrier, estimated_delivery)
                    VALUES (%s, %s, %s, %s, 'captured', 'Credit Card', 
                            %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                """, (
                    order['id'], user_id, order['order_number'], order['status'],
                    order['total'] * 0.85, order['total'] * 0.08, order['total'] * 0.07,
                    order['total'], order['tracking'], order['carrier'], order['delivery']
                ))
                print(f"Added order: {order['order_number']}")
            
            conn.commit()
            print("Orders added successfully!")
        else:
            print("Orders already exist")
        
        # Verify
        cursor.execute("SELECT order_number, status FROM orders WHERE user_id = %s", (user_id,))
        orders = cursor.fetchall()
        print(f"\nUser orders:")
        for order_num, status in orders:
            print(f"  - {order_num}: {status}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    add_test_orders()

