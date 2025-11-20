"""
Load seed data into existing database
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from pathlib import Path
import sys

# Database configuration
DB_NAME = "ecommerce_db"
DB_USER = "postgres"
DB_PASSWORD = "datalens"
DB_HOST = "localhost"
DB_PORT = 5432

def load_seed_data():
    """Load seed data into database"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        
        cursor = conn.cursor()
        
        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        if user_count > 0:
            print(f"[INFO] Database already has {user_count} users. Skipping seed data.")
            cursor.close()
            conn.close()
            return True
        
        # Read and execute seed data
        seed_file = Path(__file__).parent / "seed_data.sql"
        
        if not seed_file.exists():
            print(f"[ERROR] Seed data file not found: {seed_file}")
            return False
        
        with open(seed_file, 'r', encoding='utf-8') as f:
            sql = f.read()
        
        # Execute in parts to handle errors gracefully
        statements = sql.split(';')
        
        for statement in statements:
            statement = statement.strip()
            if statement and not statement.startswith('--'):
                try:
                    cursor.execute(statement)
                except Exception as e:
                    # Ignore errors for existing data
                    if 'already exists' not in str(e) and 'duplicate' not in str(e).lower():
                        print(f"[WARNING] Statement failed: {e}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("[SUCCESS] Seed data loaded successfully!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to load seed data: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("Loading Seed Data")
    print("="*60)
    
    success = load_seed_data()
    
    if not success:
        sys.exit(1)


