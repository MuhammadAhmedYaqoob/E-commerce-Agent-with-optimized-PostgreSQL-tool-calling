"""
Initialize Local PostgreSQL Database
Creates database and runs schema + seed data
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from pathlib import Path
import sys

# Database configuration
DB_NAME = "ecommerce_db"
DB_USER = "postgres"  # Default PostgreSQL user
DB_PASSWORD = "datalens"  # Your password
DB_HOST = "localhost"
DB_PORT = 5432

def create_database():
    """Create database if it doesn't exist"""
    try:
        # Connect to PostgreSQL server (default postgres database)
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database="postgres"  # Connect to default database first
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
        exists = cursor.fetchone()
        
        if not exists:
            print(f"[INFO] Creating database '{DB_NAME}'...")
            cursor.execute(f'CREATE DATABASE {DB_NAME}')
            print(f"[INFO] Database '{DB_NAME}' created successfully")
        else:
            print(f"[INFO] Database '{DB_NAME}' already exists")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to create database: {e}")
        return False

def run_sql_file(conn, file_path: Path):
    """Run SQL file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            sql = f.read()
        
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        cursor.close()
        print(f"[INFO] Executed {file_path.name}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to execute {file_path.name}: {e}")
        return False

def initialize_database():
    """Initialize database with schema and seed data"""
    # Create database
    if not create_database():
        return False
    
    # Connect to the new database
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        
        # Get SQL files
        db_dir = Path(__file__).parent
        schema_file = db_dir / "schema.sql"
        seed_file = db_dir / "seed_data.sql"
        
        # Run schema
        if schema_file.exists():
            print(f"\n[INFO] Running schema...")
            if not run_sql_file(conn, schema_file):
                conn.close()
                return False
        else:
            print(f"[ERROR] Schema file not found: {schema_file}")
            conn.close()
            return False
        
        # Run seed data
        if seed_file.exists():
            print(f"\n[INFO] Running seed data...")
            if not run_sql_file(conn, seed_file):
                conn.close()
                return False
        else:
            print(f"[WARNING] Seed data file not found: {seed_file}")
        
        conn.close()
        print(f"\n[INFO] Database initialization complete!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to initialize database: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("E-Commerce Database Initialization")
    print("="*60)
    
    success = initialize_database()
    
    if success:
        print("\n[SUCCESS] Database ready for use!")
        print(f"Database: {DB_NAME}")
        print(f"Host: {DB_HOST}:{DB_PORT}")
        print(f"User: {DB_USER}")
    else:
        print("\n[ERROR] Database initialization failed!")
        sys.exit(1)

