"""
Evaluation Metrics for RAG Systems
"""
from typing import List, Dict, Any
import numpy as np
from datetime import datetime


class Metrics:
    """
    Evaluation metrics for comparing RAG systems:
    - Naive RAG with normal PostgreSQL
    - MiniRAG with SLM with normal PostgreSQL
    - MiniRAG with LLM with SOTA optimized PostgreSQL
    """
    
    @staticmethod
    def calculate_retrieval_accuracy(retrieved: List[Dict], expected: List[str]) -> float:
        """
        Calculate retrieval accuracy (precision@k)
        
        Args:
            retrieved: List of retrieved documents with IDs
            expected: List of expected document IDs
            
        Returns:
            Accuracy score (0-1)
        """
        if not retrieved or not expected:
            return 0.0
        
        retrieved_ids = [r.get("id", "") for r in retrieved]
        matches = sum(1 for rid in retrieved_ids if rid in expected)
        
        return matches / len(retrieved) if retrieved else 0.0
    
    @staticmethod
    def calculate_relevance_score(retrieved: List[Dict], query: str) -> float:
        """
        Calculate relevance score based on content matching
        
        Args:
            retrieved: List of retrieved documents
            query: Original query
            
        Returns:
            Relevance score (0-1)
        """
        if not retrieved:
            return 0.0
        
        query_words = set(query.lower().split())
        scores = []
        
        for doc in retrieved:
            content = str(doc.get("content", "")).lower()
            title = str(doc.get("title", "")).lower()
            
            content_words = set(content.split())
            title_words = set(title.split())
            
            # Calculate overlap
            content_overlap = len(query_words & content_words) / len(query_words) if query_words else 0
            title_overlap = len(query_words & title_words) / len(query_words) if query_words else 0
            
            # Weighted score (title more important)
            score = (title_overlap * 0.6) + (content_overlap * 0.4)
            scores.append(score)
        
        return np.mean(scores) if scores else 0.0
    
    @staticmethod
    def calculate_response_time(start_time: datetime, end_time: datetime) -> float:
        """
        Calculate response time in seconds
        
        Args:
            start_time: Query start time
            end_time: Response end time
            
        Returns:
            Response time in seconds
        """
        delta = end_time - start_time
        return delta.total_seconds()
    
    @staticmethod
    def calculate_tool_usage_accuracy(expected_tools: List[str], actual_tools: List[str]) -> float:
        """
        Calculate tool usage accuracy
        
        Args:
            expected_tools: Expected tools to be called
            actual_tools: Actually called tools
            
        Returns:
            Accuracy score (0-1)
        """
        if not expected_tools:
            return 1.0 if not actual_tools else 0.5
        
        expected_set = set(expected_tools)
        actual_set = set(actual_tools)
        
        # Precision: how many expected tools were called
        precision = len(expected_set & actual_set) / len(actual_set) if actual_set else 0.0
        
        # Recall: how many expected tools were actually called
        recall = len(expected_set & actual_set) / len(expected_set) if expected_set else 0.0
        
        # F1 score
        if precision + recall == 0:
            return 0.0
        return 2 * (precision * recall) / (precision + recall)
    
    @staticmethod
    def calculate_state_consistency(conversation_history: List[Dict]) -> float:
        """
        Calculate state consistency across conversation
        
        Args:
            conversation_history: List of conversation turns with state
            
        Returns:
            Consistency score (0-1)
        """
        if len(conversation_history) < 2:
            return 1.0
        
        consistency_scores = []
        
        for i in range(1, len(conversation_history)):
            prev_state = conversation_history[i-1].get("state", {})
            curr_state = conversation_history[i].get("state", {})
            
            # Check if relevant state is maintained
            relevant_keys = ["user_email", "product_query", "order_id", "size_preference"]
            
            maintained = sum(
                1 for key in relevant_keys
                if key in prev_state and key in curr_state and prev_state[key] == curr_state[key]
            )
            
            score = maintained / len(relevant_keys) if relevant_keys else 1.0
            consistency_scores.append(score)
        
        return np.mean(consistency_scores) if consistency_scores else 1.0
    
    @staticmethod
    def calculate_memory_retention(conversation_history: List[Dict]) -> float:
        """
        Calculate memory retention across conversation
        
        Args:
            conversation_history: List of conversation turns
            
        Returns:
            Memory retention score (0-1)
        """
        if len(conversation_history) < 2:
            return 1.0
        
        retention_scores = []
        
        for i in range(1, len(conversation_history)):
            prev_context = conversation_history[i-1].get("context", {})
            curr_context = conversation_history[i].get("context", {})
            
            # Check if previous context is referenced
            prev_entities = set(prev_context.get("entities", []))
            curr_entities = set(curr_context.get("entities", []))
            
            if prev_entities:
                overlap = len(prev_entities & curr_entities) / len(prev_entities)
                retention_scores.append(overlap)
        
        return np.mean(retention_scores) if retention_scores else 1.0
    
    @staticmethod
    def calculate_answer_quality(answer: str, expected_keywords: List[str]) -> float:
        """
        Calculate answer quality based on expected keywords
        
        Args:
            answer: Generated answer
            expected_keywords: Expected keywords in answer
            
        Returns:
            Quality score (0-1)
        """
        if not answer or not expected_keywords:
            return 0.0
        
        answer_lower = answer.lower()
        found_keywords = sum(1 for keyword in expected_keywords if keyword.lower() in answer_lower)
        
        return found_keywords / len(expected_keywords) if expected_keywords else 0.0
    
    @staticmethod
    def calculate_comprehensive_score(results: Dict[str, Any]) -> float:
        """
        Calculate comprehensive score from all metrics
        
        Args:
            results: Dictionary with all metric scores
            
        Returns:
            Overall score (0-1)
        """
        weights = {
            "retrieval_accuracy": 0.25,
            "relevance_score": 0.20,
            "tool_usage_accuracy": 0.15,
            "state_consistency": 0.15,
            "memory_retention": 0.15,
            "answer_quality": 0.10
        }
        
        score = 0.0
        for metric, weight in weights.items():
            value = results.get(metric, 0.0)
            score += value * weight
        
        return min(score, 1.0)
    
    @staticmethod
    def calculate_database_query_efficiency(query_times: List[float]) -> Dict[str, float]:
        """
        Calculate database query efficiency metrics
        
        Args:
            query_times: List of query execution times in seconds
            
        Returns:
            Dictionary with efficiency metrics
        """
        if not query_times:
            return {
                "avg_time": 0.0,
                "min_time": 0.0,
                "max_time": 0.0,
                "p95_time": 0.0,
                "p99_time": 0.0
            }
        
        sorted_times = sorted(query_times)
        n = len(sorted_times)
        
        return {
            "avg_time": np.mean(query_times),
            "min_time": min(query_times),
            "max_time": max(query_times),
            "p95_time": sorted_times[int(n * 0.95)] if n > 0 else 0.0,
            "p99_time": sorted_times[int(n * 0.99)] if n > 0 else 0.0
        }

