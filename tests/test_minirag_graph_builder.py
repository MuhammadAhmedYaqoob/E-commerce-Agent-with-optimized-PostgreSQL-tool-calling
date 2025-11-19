"""
Unit tests for MiniRAG Graph Builder
"""
import unittest
import json
import tempfile
import pathlib
from unittest import mock
from unittest.mock import patch, MagicMock
import networkx as nx

import sys
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from src.minirag.graph_builder import MiniRAGGraphBuilder
from src.config import KNOWLEDGE_BASE_PATH


class TestMiniRAGGraphBuilder(unittest.TestCase):
    """Test cases for MiniRAG Graph Builder"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.builder = MiniRAGGraphBuilder()
        self.sample_kb = {
            "metadata": {"version": "1.0"},
            "policies": {
                "test_policy": {
                    "id": "POL-TEST",
                    "title": "Test Policy",
                    "category": "test",
                    "content": {"description": "Test content"}
                }
            },
            "entities": {
                "product_categories": ["Electronics", "Clothing"]
            },
            "relationships": {
                "policy_connections": [
                    {"from": "test_policy", "to": "test_policy", "relation": "related", "strength": 0.8}
                ]
            }
        }
    
    def test_init(self):
        """Test graph builder initialization"""
        self.assertIsNotNone(self.builder.graph)
        self.assertEqual(self.builder.graph.name, "ecommerce_minirag_graph")
        self.assertIsInstance(self.builder.graph, nx.MultiDiGraph)
    
    def test_load_knowledge_base_success(self):
        """Test successful knowledge base loading"""
        with patch('builtins.open', mock.mock_open(read_data=json.dumps(self.sample_kb))):
            with patch('pathlib.Path.exists', return_value=True):
                result = self.builder.load_knowledge_base()
                self.assertIsNotNone(result)
                self.assertIn("policies", result)
    
    def test_load_knowledge_base_failure(self):
        """Test knowledge base loading failure"""
        with patch('builtins.open', side_effect=FileNotFoundError("File not found")):
            result = self.builder.load_knowledge_base()
            self.assertEqual(result, {})
    
    def test_build_graph_with_valid_kb(self):
        """Test graph building with valid knowledge base"""
        self.builder.knowledge_base = self.sample_kb
        
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('src.minirag.graph_builder.GRAPH_DIR', pathlib.Path(tmpdir)):
                graph_path = self.builder.build_graph()
                self.assertIsNotNone(graph_path)
                self.assertTrue(pathlib.Path(graph_path).exists())
    
    def test_build_graph_no_kb(self):
        """Test graph building without knowledge base"""
        self.builder.knowledge_base = None
        result = self.builder.build_graph()
        self.assertIsNone(result)
    
    def test_resolve_entity_node(self):
        """Test entity node resolution"""
        self.builder.knowledge_base = self.sample_kb
        result = self.builder._resolve_entity_node("Electronics")
        self.assertIsNotNone(result)
        self.assertIn("entity", result)
    
    def test_extract_keywords(self):
        """Test keyword extraction from node"""
        self.builder.graph.add_node("test_node", type="policy", title="Test Policy", content={"key": "value"})
        keywords = self.builder._extract_keywords("test_node")
        self.assertIsInstance(keywords, set)
        self.assertIn("test", keywords)
    
    def test_calculate_similarity(self):
        """Test Jaccard similarity calculation"""
        set_a = {"test", "policy", "content"}
        set_b = {"test", "policy", "data"}
        similarity = self.builder._calculate_similarity(set_a, set_b)
        self.assertGreater(similarity, 0)
        self.assertLessEqual(similarity, 1.0)
    
    def test_calculate_similarity_empty(self):
        """Test similarity with empty sets"""
        similarity = self.builder._calculate_similarity(set(), set())
        self.assertEqual(similarity, 0.0)
    
    def test_get_graph(self):
        """Test getting the graph"""
        graph = self.builder.get_graph()
        self.assertIsInstance(graph, nx.MultiDiGraph)


if __name__ == '__main__':
    unittest.main()

