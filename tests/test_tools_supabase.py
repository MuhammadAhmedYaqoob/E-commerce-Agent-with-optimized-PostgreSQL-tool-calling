"""
Unit tests for Supabase Tool
"""
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
import pathlib

import sys
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from src.tools.supabase_tool import SupabaseTool


class TestSupabaseTool(unittest.TestCase):
    """Test cases for Supabase Tool"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.supabase_tool = SupabaseTool()
    
    def test_init(self):
        """Test Supabase tool initialization"""
        self.assertIsNotNone(self.supabase_tool.schema)
        self.assertIn("users", self.supabase_tool.schema)
        self.assertIn("orders", self.supabase_tool.schema)
    
    def test_get_user_by_email_mock(self):
        """Test getting user by email in mock mode"""
        result = self.supabase_tool.get_user_by_email("test@example.com")
        self.assertIsNotNone(result)
        self.assertEqual(result["email"], "test@example.com")
        self.assertIn("id", result)
    
    def test_get_user_orders_mock(self):
        """Test getting user orders in mock mode"""
        result = self.supabase_tool.get_user_orders("user-id-123", limit=5)
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertIn("id", result[0])
        self.assertIn("status", result[0])
    
    def test_get_order_by_id_mock(self):
        """Test getting order by ID in mock mode"""
        result = self.supabase_tool.get_order_by_id("order-123")
        self.assertIsNotNone(result)
        self.assertEqual(result["id"], "order-123")
        self.assertIn("order_items", result)
    
    def test_search_orders_by_status_mock(self):
        """Test searching orders by status in mock mode"""
        result = self.supabase_tool.search_orders_by_status("shipped", limit=10)
        self.assertIsInstance(result, list)
        if result:
            self.assertEqual(result[0]["status"], "shipped")
    
    def test_cache_graph_entity_mock(self):
        """Test caching graph entity in mock mode"""
        result = self.supabase_tool.cache_graph_entity(
            "entity-123",
            "policy",
            {"related": ["entity-456"]},
            {"metadata": "test"}
        )
        self.assertTrue(result)
    
    def test_create_user_mock(self):
        """Test creating user in mock mode"""
        result = self.supabase_tool.create_user("newuser@example.com", "New User")
        self.assertIsNotNone(result)
        self.assertEqual(result["email"], "newuser@example.com")
    
    def test_update_order_status_mock(self):
        """Test updating order status in mock mode"""
        result = self.supabase_tool.update_order_status("order-123", "delivered")
        self.assertTrue(result)
    
    def test_mock_user(self):
        """Test mock user generation"""
        result = self.supabase_tool._mock_user("test@example.com")
        self.assertEqual(result["email"], "test@example.com")
        self.assertIn("id", result)
        self.assertIn("verified", result)
    
    def test_mock_orders(self):
        """Test mock orders generation"""
        result = self.supabase_tool._mock_orders("user-id", limit=3)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["user_id"], "user-id")
    
    def test_mock_order(self):
        """Test mock order generation"""
        result = self.supabase_tool._mock_order("order-123")
        self.assertEqual(result["id"], "order-123")
        self.assertIn("order_items", result)
    
    def test_mock_orders_by_status(self):
        """Test mock orders by status generation"""
        result = self.supabase_tool._mock_orders_by_status("pending", limit=5)
        self.assertEqual(len(result), 5)
        self.assertEqual(result[0]["status"], "pending")


if __name__ == '__main__':
    unittest.main()

