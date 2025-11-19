"""
Unit tests for MiniRAG Graph Retriever
"""
import unittest
import pathlib
import networkx as nx
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from src.minirag.graph_retriever import MiniRAGRetriever


class TestMiniRAGRetriever(unittest.TestCase):
    """Test cases for MiniRAG Graph Retriever"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.retriever = MiniRAGRetriever()
        # Create a mock graph
        self.mock_graph = nx.MultiDiGraph()
        self.mock_graph.add_node(
            "policy::return_refund",
            type="policy",
            title="Return and Refund Policy",
            category="customer_service",
            content={"return_window": "30 days"},
            metadata={"id": "POL-001"}
        )
        self.mock_graph.add_node(
            "entity::product_categories::Electronics",
            type="entity",
            entity_type="product_categories",
            name="Electronics"
        )
        self.mock_graph.add_edge(
            "entity::product_categories::Electronics",
            "policy::return_refund",
            relation="governed_by",
            strength=0.9
        )
    
    def test_init(self):
        """Test retriever initialization"""
        self.assertIsNotNone(self.retriever.graph)
    
    def test_retrieve_empty_graph(self):
        """Test retrieval with empty graph"""
        self.retriever.graph = nx.MultiDiGraph()
        result = self.retriever.retrieve("test query")
        self.assertEqual(result, [])
    
    def test_extract_query_entities(self):
        """Test query entity extraction"""
        self.retriever.graph = self.mock_graph
        entities = self.retriever._extract_query_entities("return policy for electronics")
        self.assertIsInstance(entities, set)
        self.assertIn("return", entities)
    
    def test_find_matching_nodes(self):
        """Test finding matching nodes"""
        self.retriever.graph = self.mock_graph
        entities = {"return", "refund"}
        candidates = self.retriever._find_matching_nodes("return policy", entities)
        self.assertIsInstance(candidates, list)
        self.assertGreater(len(candidates), 0)
    
    def test_traverse_graph(self):
        """Test graph traversal"""
        self.retriever.graph = self.mock_graph
        seed_nodes = [("policy::return_refund", 1.0)]
        expanded = self.retriever._traverse_graph(seed_nodes, depth=2)
        self.assertIsInstance(expanded, dict)
        self.assertIn("policy::return_refund", expanded)
    
    def test_score_nodes(self):
        """Test node scoring"""
        self.retriever.graph = self.mock_graph
        nodes = {"policy::return_refund": 1.0}
        scored = self.retriever._score_nodes(nodes, "test query", set())
        self.assertIsInstance(scored, list)
        self.assertGreater(len(scored), 0)
    
    def test_extract_content(self):
        """Test content extraction"""
        self.retriever.graph = self.mock_graph
        scored_nodes = [
            ("policy::return_refund", 1.0, self.mock_graph.nodes["policy::return_refund"])
        ]
        results = self.retriever._extract_content(scored_nodes, k=5)
        self.assertIsInstance(results, list)
        if results:
            self.assertIn("title", results[0])
            self.assertIn("content", results[0])
    
    def test_extract_content_keywords(self):
        """Test content keyword extraction"""
        content_dict = {"key": "value", "list": ["item1", "item2"]}
        keywords = self.retriever._extract_content_keywords(content_dict)
        self.assertIsInstance(keywords, set)
        self.assertIn("value", keywords)
    
    def test_retrieve_with_valid_graph(self):
        """Test full retrieval with valid graph"""
        self.retriever.graph = self.mock_graph
        results = self.retriever.retrieve("return policy", k=5)
        self.assertIsInstance(results, list)


if __name__ == '__main__':
    unittest.main()

