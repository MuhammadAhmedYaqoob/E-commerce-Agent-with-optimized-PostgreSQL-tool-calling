"""
Evaluator for E-Commerce MiniRAG System
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from pathlib import Path
import numpy as np

from .metrics import Metrics


class Evaluator:
    """
    Evaluator for comparing different RAG architectures
    """
    
    def __init__(self, questions_path: Optional[Path] = None):
        """
        Initialize evaluator
        
        Args:
            questions_path: Path to evaluation questions JSON file
        """
        if questions_path is None:
            questions_path = Path(__file__).parent.parent.parent / "data" / "evaluation_questions.json"
        
        self.questions_path = questions_path
        self.questions = self._load_questions()
        self.metrics = Metrics()
    
    def _load_questions(self) -> Dict[str, Any]:
        """Load evaluation questions"""
        try:
            with open(self.questions_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get("questions", {})
        except Exception as e:
            print(f"[ERROR] Failed to load questions: {e}")
            return {}
    
    def evaluate_single_query(
        self,
        query: str,
        system_response: Dict[str, Any],
        expected_tools: List[str] = None,
        expected_context: List[str] = None
    ) -> Dict[str, float]:
        """
        Evaluate a single query response
        
        Args:
            query: User query
            system_response: System response with answer, context, tools used, etc.
            expected_tools: Expected tools to be called
            expected_context: Expected context/document IDs
            
        Returns:
            Dictionary with metric scores
        """
        start_time = system_response.get("start_time", datetime.now())
        end_time = system_response.get("end_time", datetime.now())
        
        retrieved = system_response.get("context", [])
        answer = system_response.get("answer", "")
        tools_used = system_response.get("tools_used", [])
        
        metrics = {
            "retrieval_accuracy": self.metrics.calculate_retrieval_accuracy(
                retrieved, expected_context or []
            ),
            "relevance_score": self.metrics.calculate_relevance_score(retrieved, query),
            "response_time": self.metrics.calculate_response_time(start_time, end_time),
            "tool_usage_accuracy": self.metrics.calculate_tool_usage_accuracy(
                expected_tools or [], tools_used
            ),
            "answer_quality": self.metrics.calculate_answer_quality(
                answer, self._extract_expected_keywords(query)
            )
        }
        
        return metrics
    
    def evaluate_conversation(
        self,
        conversation_history: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """
        Evaluate a multi-turn conversation
        
        Args:
            conversation_history: List of conversation turns
            
        Returns:
            Dictionary with conversation metrics
        """
        metrics = {
            "state_consistency": self.metrics.calculate_state_consistency(conversation_history),
            "memory_retention": self.metrics.calculate_memory_retention(conversation_history),
            "avg_response_time": np.mean([
                self.metrics.calculate_response_time(
                    turn.get("start_time", datetime.now()),
                    turn.get("end_time", datetime.now())
                )
                for turn in conversation_history
            ]) if conversation_history else 0.0
        }
        
        return metrics
    
    def evaluate_system(
        self,
        system_name: str,
        results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Evaluate entire system performance
        
        Args:
            system_name: Name of the system being evaluated
            results: List of evaluation results
            
        Returns:
            Comprehensive evaluation results
        """
        if not results:
            return {}
        
        # Aggregate metrics
        all_metrics = {
            "retrieval_accuracy": [],
            "relevance_score": [],
            "response_time": [],
            "tool_usage_accuracy": [],
            "answer_quality": [],
            "state_consistency": [],
            "memory_retention": []
        }
        
        for result in results:
            metrics = result.get("metrics", {})
            for key in all_metrics.keys():
                if key in metrics:
                    all_metrics[key].append(metrics[key])
        
        # Calculate statistics
        evaluation_results = {
            "system_name": system_name,
            "total_queries": len(results),
            "metrics": {
                key: {
                    "mean": np.mean(values) if values else 0.0,
                    "std": np.std(values) if values else 0.0,
                    "min": min(values) if values else 0.0,
                    "max": max(values) if values else 0.0,
                    "median": np.median(values) if values else 0.0
                }
                for key, values in all_metrics.items()
            },
            "comprehensive_score": self.metrics.calculate_comprehensive_score({
                "retrieval_accuracy": np.mean(all_metrics["retrieval_accuracy"]) if all_metrics["retrieval_accuracy"] else 0.0,
                "relevance_score": np.mean(all_metrics["relevance_score"]) if all_metrics["relevance_score"] else 0.0,
                "tool_usage_accuracy": np.mean(all_metrics["tool_usage_accuracy"]) if all_metrics["tool_usage_accuracy"] else 0.0,
                "state_consistency": np.mean(all_metrics["state_consistency"]) if all_metrics["state_consistency"] else 0.0,
                "memory_retention": np.mean(all_metrics["memory_retention"]) if all_metrics["memory_retention"] else 0.0,
                "answer_quality": np.mean(all_metrics["answer_quality"]) if all_metrics["answer_quality"] else 0.0
            })
        }
        
        return evaluation_results
    
    def _extract_expected_keywords(self, query: str) -> List[str]:
        """Extract expected keywords from query"""
        # Simple keyword extraction
        important_words = [
            "return", "refund", "shipping", "delivery", "payment",
            "order", "size", "policy", "tracking", "cancel"
        ]
        
        query_lower = query.lower()
        return [word for word in important_words if word in query_lower]

