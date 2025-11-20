"""
Insert seed data directly into database
"""
import psycopg2
from psycopg2.extras import execute_values
import uuid
from datetime import datetime, timedelta

DB_NAME = "ecommerce_db"
DB_USER = "postgres"
DB_PASSWORD = "datalens"
DB_HOST = "localhost"
DB_PORT = 5432

def insert_seed_data():
    """Insert seed data"""
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    cursor = conn.cursor()
    
    try:
        # Check if data exists
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] > 0:
            print("[INFO] Data already exists. Skipping.")
            return True
        
        print("[INFO] Inserting seed data...")
        
        # Insert users
        users = [
            (str(uuid.uuid4()), 'john@example.com', 'John Doe', True, 'silver', 750),
            (str(uuid.uuid4()), 'sarah@example.com', 'Sarah Smith', True, 'gold', 2500),
            (str(uuid.uuid4()), 'mike@example.com', 'Mike Johnson', True, 'bronze', 300),
            (str(uuid.uuid4()), 'lisa@example.com', 'Lisa Brown', True, 'silver', 1200),
            (str(uuid.uuid4()), 'david@example.com', 'David Wilson', True, 'bronze', 200),
            (str(uuid.uuid4()), 'emily@example.com', 'Emily Davis', True, 'platinum', 6000),
            (str(uuid.uuid4()), 'james@example.com', 'James Miller', True, 'gold', 3000),
            (str(uuid.uuid4()), 'jane@example.com', 'Jane Anderson', True, 'silver', 1500),
            (str(uuid.uuid4()), 'bob@example.com', 'Bob Taylor', True, 'bronze', 100),
            (str(uuid.uuid4()), 'alice@example.com', 'Alice Martinez', True, 'gold', 2800),
            (str(uuid.uuid4()), 'charlie@example.com', 'Charlie Garcia', True, 'silver', 900),
            (str(uuid.uuid4()), 'test@example.com', 'Test User', True, 'bronze', 500),
        ]
        
        execute_values(
            cursor,
            """INSERT INTO users (id, email, name, verified, loyalty_tier, loyalty_points) 
               VALUES %s ON CONFLICT (email) DO NOTHING""",
            users
        )
        
        print(f"[OK] Inserted {len(users)} users")
        
        # Get user IDs for orders
        cursor.execute("SELECT id, email FROM users WHERE email = 'john@example.com'")
        john_id = cursor.fetchone()[0]
        
        cursor.execute("SELECT id, email FROM users WHERE email = 'sarah@example.com'")
        sarah_id = cursor.fetchone()[0]
        
        # Insert products
        products = [
            ('660e8400-e29b-41d4-a716-446655440001', 'Mens Classic Blue Shirt', 'Premium cotton shirt', 'Mens Clothing', 'Shirts', 49.99, 59.99, 'MENS-SHIRT-BLUE-001', 'active'),
            ('660e8400-e29b-41d4-a716-446655440002', 'Mens White Dress Shirt', 'Formal white dress shirt', 'Mens Clothing', 'Shirts', 59.99, 69.99, 'MENS-SHIRT-WHITE-001', 'active'),
            ('660e8400-e29b-41d4-a716-446655440003', 'Mens Blue Jeans', 'Classic fit blue denim jeans', 'Mens Clothing', 'Jeans', 79.99, 89.99, 'MENS-JEANS-BLUE-001', 'active'),
        ]
        
        execute_values(
            cursor,
            """INSERT INTO products (id, name, description, category, subcategory, price, compare_at_price, sku, status) 
               VALUES %s ON CONFLICT DO NOTHING""",
            products
        )
        
        print(f"[OK] Inserted {len(products)} products")
        
        # Insert orders
        orders = [
            ('880e8400-e29b-41d4-a716-446655440001', john_id, 'ORD-12345', 'shipped', 'captured', 'Credit Card', 49.99, 4.00, 5.99, 59.98, 'TRACK123456789', 'FedEx', datetime.now() + timedelta(days=3)),
            ('880e8400-e29b-41d4-a716-446655440002', sarah_id, 'ORD-67890', 'delivered', 'captured', 'PayPal', 89.99, 7.20, 0.00, 97.19, 'TRACK987654321', 'UPS', datetime.now() - timedelta(days=2)),
        ]
        
        execute_values(
            cursor,
            """INSERT INTO orders (id, user_id, order_number, status, payment_status, payment_method, subtotal, tax, shipping_cost, total_amount, tracking_number, carrier, estimated_delivery) 
               VALUES %s ON CONFLICT DO NOTHING""",
            orders
        )
        
        print(f"[OK] Inserted {len(orders)} orders")
        
        conn.commit()
        print("[SUCCESS] Seed data inserted successfully!")
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Failed to insert seed data: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("="*60)
    print("Inserting Seed Data")
    print("="*60)
    insert_seed_data()


