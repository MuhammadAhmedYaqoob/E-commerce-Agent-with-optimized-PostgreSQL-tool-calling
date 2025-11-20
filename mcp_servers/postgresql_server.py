"""
MCP Server for PostgreSQL Database Operations
Supports both local PostgreSQL and Supabase based on configuration
Uses simple JSON-RPC over stdio
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import (
    USE_SUPABASE, SUPABASE_URL, SUPABASE_KEY,
    LOCAL_DB_HOST, LOCAL_DB_PORT, LOCAL_DB_NAME, LOCAL_DB_USER, LOCAL_DB_PASSWORD
)
from src.tools.database_tool import DatabaseTool
from mcp_servers.simple_rpc_server import SimpleRPCServer

# Initialize database tool
db_tool = DatabaseTool()

# Define handlers
def get_user_by_email(email: str):
    """Get user by email"""
    user = db_tool.get_user_by_email(email)
    return user if user else {"error": "User not found"}

def get_user_orders(user_id: str, limit: int = 10):
    """Get user orders"""
    return db_tool.get_user_orders(user_id, limit)

def get_order_by_id(order_id: str):
    """Get order by ID"""
    order = db_tool.get_order_by_id(order_id)
    return order if order else {"error": "Order not found"}

def get_user_email_from_order(order_number: str):
    """Get user email from order"""
    email = db_tool.get_user_email_from_order(order_number)
    return {"email": email} if email else {"error": "Order not found"}

def search_orders_by_status(status: str, limit: int = 20):
    """Search orders by status"""
    return db_tool.search_orders_by_status(status, limit)

def update_order_status(order_id: str, status: str):
    """Update order status"""
    success = db_tool.update_order_status(order_id, status)
    return {"success": success}

def create_user(email: str, name: str):
    """Create user"""
    user = db_tool.create_user(email, name)
    return user if user else {"error": "Failed to create user"}

def get_database_info():
    """Get database info"""
    return {
        "use_supabase": USE_SUPABASE,
        "database_type": "Supabase" if USE_SUPABASE else "Local PostgreSQL",
        "host": LOCAL_DB_HOST if not USE_SUPABASE else SUPABASE_URL,
        "database": LOCAL_DB_NAME if not USE_SUPABASE else "Supabase"
    }

# Create server with handlers
handlers = {
    "get_user_by_email": get_user_by_email,
    "get_user_orders": get_user_orders,
    "get_order_by_id": get_order_by_id,
    "get_user_email_from_order": get_user_email_from_order,
    "search_orders_by_status": search_orders_by_status,
    "update_order_status": update_order_status,
    "create_user": create_user,
    "get_database_info": get_database_info
}

if __name__ == "__main__":
    server = SimpleRPCServer(handlers)
    server.run()

