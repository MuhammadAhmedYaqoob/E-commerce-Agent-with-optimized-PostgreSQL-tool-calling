"""
Unit tests for Answer Generator
"""
import unittest
from unittest.mock import patch, MagicMock
import pathlib

import sys
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from src.generator import generate_answer


class TestGenerator(unittest.TestCase):
    """Test cases for Answer Generator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.sample_contexts = [
            {
                "id": "POL-001",
                "title": "Return Policy",
                "category": "customer_service",
                "content": {"return_window": "30 days"}
            }
        ]
    
    def test_generate_answer_with_contexts(self):
        """Test answer generation with valid contexts"""
        with patch('src.generator.client') as mock_client:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "Test answer"
            mock_client.chat.completions.create.return_value = mock_response
            
            result = generate_answer("What is the return policy?", self.sample_contexts)
            self.assertIsInstance(result, str)
            self.assertEqual(result, "Test answer")
    
    def test_generate_answer_no_contexts(self):
        """Test answer generation without contexts"""
        result = generate_answer("Test query", [])
        self.assertIsInstance(result, str)
        self.assertIn("couldn't find", result.lower())
    
    def test_generate_answer_api_error(self):
        """Test answer generation with API error"""
        with patch('src.generator.client') as mock_client:
            mock_client.chat.completions.create.side_effect = Exception("API Error")
            
            result = generate_answer("Test query", self.sample_contexts)
            self.assertIsInstance(result, str)
            self.assertIn("error", result.lower())


if __name__ == '__main__':
    unittest.main()

