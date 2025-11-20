"""
Unified Database Tool - Supports both Supabase and Local PostgreSQL
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import os

from ..config import (
    USE_SUPABASE, SUPABASE_URL, SUPABASE_KEY, SUPABASE_SERVICE_KEY,
    LOCAL_DB_HOST, LOCAL_DB_PORT, LOCAL_DB_NAME, LOCAL_DB_USER, LOCAL_DB_PASSWORD
)

# Imports (conditional loading in methods)
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

class DatabaseTool:
    """
    Unified database tool that works with both Supabase and Local PostgreSQL.
    Same interface, different backend based on configuration.
    """
    
    def __init__(self):
        self.use_supabase = USE_SUPABASE
        self.client = None
        self.conn = None
        self._initialize()
    
    def _initialize(self):
        """Initialize database connection based on configuration"""
        if self.use_supabase:
            self._initialize_supabase()
        else:
            self._initialize_local_postgres()
    
    def _initialize_supabase(self):
        """Initialize Supabase client"""
        try:
            if not SUPABASE_AVAILABLE:
                print("[WARNING] Supabase package not installed")
                return
            if SUPABASE_URL and SUPABASE_KEY:
                self.client = create_client(SUPABASE_URL, SUPABASE_KEY)
                print("[INFO] Connected to Supabase")
            else:
                print("[WARNING] Supabase credentials not configured")
        except Exception as e:
            print(f"[WARNING] Supabase initialization failed: {e}")
            print("[INFO] Falling back to mock mode")
    
    def _initialize_local_postgres(self):
        """Initialize local PostgreSQL connection"""
        try:
            if not PSYCOPG2_AVAILABLE:
                print("[WARNING] psycopg2 not installed. Install with: pip install psycopg2-binary")
                return
            self.conn = psycopg2.connect(
                host=LOCAL_DB_HOST,
                port=LOCAL_DB_PORT,
                database=LOCAL_DB_NAME,
                user=LOCAL_DB_USER,
                password=LOCAL_DB_PASSWORD
            )
            print(f"[INFO] Connected to local PostgreSQL: {LOCAL_DB_NAME}")
        except Exception as e:
            print(f"[WARNING] Local PostgreSQL connection failed: {e}")
            print("[INFO] Running in mock mode - database operations will be simulated")
            self.conn = None
    
    def _execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Execute query and return results (for local PostgreSQL only)"""
        if self.use_supabase:
            # Supabase uses its own query methods, not raw SQL
            return []
        
        if not self.conn:
            return []
        
        try:
            cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, params)
            
            if query.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
                return [dict(row) for row in results]
            else:
                self.conn.commit()
                return []
        except Exception as e:
            print(f"[ERROR] Query execution failed: {e}")
            if self.conn:
                self.conn.rollback()
            return []
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        if self.use_supabase:
            if not self.client:
                return self._mock_user(email)
            try:
                response = self.client.table("users").select("*").eq("email", email).limit(1).execute()
                if response.data:
                    return response.data[0]
                return None
            except Exception as e:
                print(f"[ERROR] Failed to get user: {e}")
                return None
        else:
            # Local PostgreSQL
            query = "SELECT * FROM users WHERE email = %s LIMIT 1"
            results = self._execute_query(query, (email,))
            return results[0] if results else None
    
    def get_user_orders(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get user orders with items"""
        if self.use_supabase:
            if not self.client:
                return self._mock_orders(user_id, limit)
            try:
                response = self.client.table("orders").select(
                    "*, order_items(*)"
                ).eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute()
                return response.data if response.data else []
            except Exception as e:
                print(f"[ERROR] Failed to get orders: {e}")
                return []
        else:
            # Local PostgreSQL - optimized query with JOIN
            query = """
                SELECT 
                    o.*,
                    json_agg(
                        json_build_object(
                            'id', oi.id,
                            'product_id', oi.product_id,
                            'variant_id', oi.variant_id,
                            'product_name', oi.product_name,
                            'variant_description', oi.variant_description,
                            'quantity', oi.quantity,
                            'unit_price', oi.unit_price,
                            'total_price', oi.total_price
                        )
                    ) as order_items
                FROM orders o
                LEFT JOIN order_items oi ON o.id = oi.order_id
                WHERE o.user_id = %s
                GROUP BY o.id
                ORDER BY o.created_at DESC
                LIMIT %s
            """
            results = self._execute_query(query, (user_id, limit))
            return results
    
    def get_user_email_from_order(self, order_number: str) -> Optional[str]:
        """Get user email from order number for verification"""
        if self.use_supabase:
            if not self.client:
                # Mock for testing
                order = self._mock_order(order_number)
                return order.get("users", {}).get("email") if order else None
            try:
                response = self.client.table("orders").select(
                    "users(email)"
                ).eq("order_number", order_number).limit(1).execute()
                if response.data and response.data[0].get("users"):
                    return response.data[0]["users"]["email"]
                return None
            except Exception as e:
                print(f"[ERROR] Failed to get user email from order: {e}")
                return None
        else:
            # Local PostgreSQL
            query = """
                SELECT u.email
                FROM orders o
                JOIN users u ON o.user_id = u.id
                WHERE o.order_number = %s
                LIMIT 1
            """
            results = self._execute_query(query, (order_number,))
            return results[0]["email"] if results else None
    
    def get_order_by_id(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get order by ID with all related data"""
        if self.use_supabase:
            if not self.client:
                return self._mock_order(order_id)
            try:
                response = self.client.table("orders").select(
                    "*, order_items(*), users(email, name)"
                ).eq("id", order_id).limit(1).execute()
                if response.data:
                    return response.data[0]
                return None
            except Exception as e:
                print(f"[ERROR] Failed to get order: {e}")
                return None
        else:
            # Local PostgreSQL - optimized query
            # Try order_number first (string), then id (UUID)
            query = """
                SELECT 
                    o.*,
                    json_agg(
                        json_build_object(
                            'id', oi.id,
                            'product_id', oi.product_id,
                            'variant_id', oi.variant_id,
                            'product_name', oi.product_name,
                            'variant_description', oi.variant_description,
                            'quantity', oi.quantity,
                            'unit_price', oi.unit_price,
                            'total_price', oi.total_price
                        )
                    ) as order_items,
                    json_build_object(
                        'email', u.email,
                        'name', u.name
                    ) as users
                FROM orders o
                LEFT JOIN order_items oi ON o.id = oi.order_id
                LEFT JOIN users u ON o.user_id = u.id
                WHERE o.order_number = %s OR (o.id::text = %s AND %s ~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
                GROUP BY o.id, u.email, u.name
                LIMIT 1
            """
            results = self._execute_query(query, (order_id, order_id, order_id))
            return results[0] if results else None
    
    def search_orders_by_status(self, status: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search orders by status"""
        if self.use_supabase:
            if not self.client:
                return self._mock_orders_by_status(status, limit)
            try:
                response = self.client.table("orders").select(
                    "*, users(email, name)"
                ).eq("status", status).order("created_at", desc=True).limit(limit).execute()
                return response.data if response.data else []
            except Exception as e:
                print(f"[ERROR] Failed to search orders: {e}")
                return []
        else:
            # Local PostgreSQL
            query = """
                SELECT 
                    o.*,
                    json_build_object(
                        'email', u.email,
                        'name', u.name
                    ) as users
                FROM orders o
                LEFT JOIN users u ON o.user_id = u.id
                WHERE o.status = %s
                ORDER BY o.created_at DESC
                LIMIT %s
            """
            results = self._execute_query(query, (status, limit))
            return results
    
    def cache_graph_entity(self, entity_id: str, entity_type: str, 
                          related_entities: Dict, metadata: Dict = None) -> bool:
        """Cache graph entity"""
        if self.use_supabase:
            if not self.client:
                return True
            try:
                data = {
                    "entity_id": entity_id,
                    "entity_type": entity_type,
                    "related_entities": json.dumps(related_entities),
                    "metadata": json.dumps(metadata or {}),
                    "last_updated": datetime.now().isoformat()
                }
                self.client.table("graph_cache").upsert(data).execute()
                return True
            except Exception as e:
                print(f"[ERROR] Failed to cache entity: {e}")
                return False
        else:
            # Local PostgreSQL
            query = """
                INSERT INTO graph_cache (entity_id, entity_type, related_entities, metadata, last_updated)
                VALUES (%s, %s, %s::jsonb, %s::jsonb, %s)
                ON CONFLICT (entity_id) 
                DO UPDATE SET 
                    entity_type = EXCLUDED.entity_type,
                    related_entities = EXCLUDED.related_entities,
                    metadata = EXCLUDED.metadata,
                    last_updated = EXCLUDED.last_updated
            """
            try:
                cursor = self.conn.cursor()
                cursor.execute(query, (
                    entity_id,
                    entity_type,
                    json.dumps(related_entities),
                    json.dumps(metadata or {}),
                    datetime.now()
                ))
                self.conn.commit()
                cursor.close()
                return True
            except Exception as e:
                print(f"[ERROR] Failed to cache entity: {e}")
                return False
    
    def get_cached_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get cached graph entity"""
        if self.use_supabase:
            if not self.client:
                return None
            try:
                response = self.client.table("graph_cache").select("*").eq(
                    "entity_id", entity_id
                ).limit(1).execute()
                if response.data:
                    entity = response.data[0]
                    entity["related_entities"] = json.loads(entity.get("related_entities", "{}"))
                    entity["metadata"] = json.loads(entity.get("metadata", "{}"))
                    return entity
                return None
            except Exception as e:
                print(f"[ERROR] Failed to get cached entity: {e}")
                return None
        else:
            # Local PostgreSQL
            query = "SELECT * FROM graph_cache WHERE entity_id = %s LIMIT 1"
            results = self._execute_query(query, (entity_id,))
            if results:
                entity = results[0]
                # Parse JSONB fields
                if isinstance(entity.get("related_entities"), str):
                    entity["related_entities"] = json.loads(entity["related_entities"])
                if isinstance(entity.get("metadata"), str):
                    entity["metadata"] = json.loads(entity["metadata"])
                return entity
            return None
    
    def create_user(self, email: str, name: str) -> Optional[Dict[str, Any]]:
        """Create new user"""
        if self.use_supabase:
            if not self.client:
                return self._mock_user(email)
            try:
                data = {
                    "email": email,
                    "name": name,
                    "created_at": datetime.now().isoformat(),
                    "verified": False
                }
                response = self.client.table("users").insert(data).execute()
                return response.data[0] if response.data else None
            except Exception as e:
                print(f"[ERROR] Failed to create user: {e}")
                return None
        else:
            # Local PostgreSQL
            query = """
                INSERT INTO users (email, name, created_at, verified)
                VALUES (%s, %s, %s, %s)
                RETURNING *
            """
            results = self._execute_query(query, (email, name, datetime.now(), False))
            return results[0] if results else None
    
    def update_order_status(self, order_id: str, status: str) -> bool:
        """Update order status"""
        if self.use_supabase:
            if not self.client:
                return True
            try:
                self.client.table("orders").update({
                    "status": status,
                    "updated_at": datetime.now().isoformat()
                }).eq("id", order_id).execute()
                return True
            except Exception as e:
                print(f"[ERROR] Failed to update order: {e}")
                return False
        else:
            # Local PostgreSQL
            query = """
                UPDATE orders 
                SET status = %s, updated_at = %s
                WHERE id = %s OR order_number = %s
            """
            try:
                cursor = self.conn.cursor()
                cursor.execute(query, (status, datetime.now(), order_id, order_id))
                self.conn.commit()
                cursor.close()
                return cursor.rowcount > 0
            except Exception as e:
                print(f"[ERROR] Failed to update order: {e}")
                return False
    
    def close(self):
        """Close database connection"""
        if not self.use_supabase and self.conn:
            self.conn.close()
    
    # Mock methods for testing
    def _mock_user(self, email: str) -> Dict:
        return {
            "id": "mock-user-id",
            "email": email,
            "name": "Mock User",
            "verified": True
        }
    
    def _mock_orders(self, user_id: str, limit: int) -> List[Dict]:
        return [
            {
                "id": f"order-{i}",
                "user_id": user_id,
                "status": ["pending", "processing", "shipped", "delivered"][i % 4],
                "total_amount": 99.99 + i * 10,
                "created_at": datetime.now().isoformat(),
                "order_items": [
                    {"product_id": f"prod-{i}", "quantity": 1, "price": 99.99}
                ]
            }
            for i in range(min(limit, 5))
        ]
    
    def _mock_order(self, order_id: str) -> Dict:
        return {
            "id": order_id,
            "user_id": "mock-user-id",
            "status": "shipped",
            "total_amount": 149.99,
            "created_at": datetime.now().isoformat(),
            "order_items": [
                {"product_id": "prod-1", "quantity": 2, "price": 74.99}
            ],
            "users": {"email": "user@example.com", "name": "Test User"}
        }
    
    def _mock_orders_by_status(self, status: str, limit: int) -> List[Dict]:
        return [
            {
                "id": f"order-{i}",
                "status": status,
                "total_amount": 99.99,
                "created_at": datetime.now().isoformat(),
                "users": {"email": f"user{i}@example.com", "name": f"User {i}"}
            }
            for i in range(min(limit, 5))
        ]

