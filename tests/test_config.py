"""
Unit tests for Configuration
"""
import unittest
import pathlib
import os
from unittest.mock import patch

import sys
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from src.config import (
    OPENAI_API_KEY,
    SUPABASE_URL,
    GRAPH_DIR,
    KNOWLEDGE_BASE_PATH,
    GRAPH_RETRIEVAL_TOP_K,
    GRAPH_TRAVERSAL_DEPTH,
    SEMANTIC_FALLBACK_ENABLED
)


class TestConfig(unittest.TestCase):
    """Test cases for Configuration"""
    
    def test_knowledge_base_path_exists(self):
        """Test that knowledge base path is defined"""
        self.assertIsNotNone(KNOWLEDGE_BASE_PATH)
        self.assertTrue(hasattr(KNOWLEDGE_BASE_PATH, 'exists'))
    
    def test_graph_dir_exists(self):
        """Test that graph directory path is defined"""
        self.assertIsNotNone(GRAPH_DIR)
        self.assertTrue(hasattr(GRAPH_DIR, 'mkdir'))
    
    def test_graph_retrieval_config(self):
        """Test graph retrieval configuration"""
        self.assertIsInstance(GRAPH_RETRIEVAL_TOP_K, int)
        self.assertGreater(GRAPH_RETRIEVAL_TOP_K, 0)
    
    def test_graph_traversal_config(self):
        """Test graph traversal configuration"""
        self.assertIsInstance(GRAPH_TRAVERSAL_DEPTH, int)
        self.assertGreater(GRAPH_TRAVERSAL_DEPTH, 0)
    
    def test_semantic_fallback_disabled(self):
        """Test that semantic fallback is disabled (true MiniRAG)"""
        self.assertFalse(SEMANTIC_FALLBACK_ENABLED)


if __name__ == '__main__':
    unittest.main()

