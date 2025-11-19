"""
Experiment Runner for Comparing RAG Systems
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from pathlib import Path
import numpy as np

from .evaluator import Evaluator
from .metrics import Metrics


class ExperimentRunner:
    """
    Run experiments comparing:
    1. Naive RAG with normal PostgreSQL
    2. MiniRAG with SLM with normal PostgreSQL
    3. MiniRAG with LLM with SOTA optimized PostgreSQL
    """
    
    def __init__(self, questions_path: Optional[Path] = None):
        """
        Initialize experiment runner
        
        Args:
            questions_path: Path to evaluation questions
        """
        self.evaluator = Evaluator(questions_path)
        self.metrics = Metrics()
        self.results = {}
    
    def run_naive_rag_experiment(
        self,
        system,
        questions: List[Dict[str, Any]],
        system_name: str = "Naive RAG + Normal PostgreSQL"
    ) -> Dict[str, Any]:
        """
        Run experiment with Naive RAG system
        
        Args:
            system: Naive RAG system instance
            questions: List of questions to test
            system_name: Name of the system
            
        Returns:
            Evaluation results
        """
        print(f"\n[EXPERIMENT] Running {system_name}...")
        
        results = []
        for i, question_data in enumerate(questions, 1):
            query = question_data.get("question", "")
            expected_tools = question_data.get("expected_tools", [])
            expected_context = question_data.get("expected_context", [])
            
            print(f"  Processing question {i}/{len(questions)}: {query[:50]}...")
            
            start_time = datetime.now()
            
            # Simulate system response (replace with actual system call)
            response = self._simulate_naive_rag_response(system, query)
            
            end_time = datetime.now()
            
            response["start_time"] = start_time
            response["end_time"] = end_time
            
            # Evaluate
            metrics = self.evaluator.evaluate_single_query(
                query, response, expected_tools, expected_context
            )
            
            results.append({
                "question_id": question_data.get("id", f"Q{i}"),
                "query": query,
                "response": response,
                "metrics": metrics
            })
        
        # Aggregate results
        evaluation = self.evaluator.evaluate_system(system_name, results)
        self.results[system_name] = {
            "evaluation": evaluation,
            "detailed_results": results
        }
        
        return evaluation
    
    def run_minirag_slm_experiment(
        self,
        system,
        questions: List[Dict[str, Any]],
        system_name: str = "MiniRAG + SLM + Normal PostgreSQL"
    ) -> Dict[str, Any]:
        """
        Run experiment with MiniRAG + SLM system
        
        Args:
            system: MiniRAG SLM system instance
            questions: List of questions to test
            system_name: Name of the system
            
        Returns:
            Evaluation results
        """
        print(f"\n[EXPERIMENT] Running {system_name}...")
        
        results = []
        for i, question_data in enumerate(questions, 1):
            query = question_data.get("question", "")
            expected_tools = question_data.get("expected_tools", [])
            expected_context = question_data.get("expected_context", [])
            
            print(f"  Processing question {i}/{len(questions)}: {query[:50]}...")
            
            start_time = datetime.now()
            
            # Simulate system response (replace with actual system call)
            response = self._simulate_minirag_slm_response(system, query)
            
            end_time = datetime.now()
            
            response["start_time"] = start_time
            response["end_time"] = end_time
            
            # Evaluate
            metrics = self.evaluator.evaluate_single_query(
                query, response, expected_tools, expected_context
            )
            
            results.append({
                "question_id": question_data.get("id", f"Q{i}"),
                "query": query,
                "response": response,
                "metrics": metrics
            })
        
        # Aggregate results
        evaluation = self.evaluator.evaluate_system(system_name, results)
        self.results[system_name] = {
            "evaluation": evaluation,
            "detailed_results": results
        }
        
        return evaluation
    
    def run_minirag_llm_sota_experiment(
        self,
        system,
        questions: List[Dict[str, Any]],
        system_name: str = "MiniRAG + LLM + SOTA PostgreSQL"
    ) -> Dict[str, Any]:
        """
        Run experiment with MiniRAG + LLM + SOTA PostgreSQL system
        
        Args:
            system: MiniRAG LLM SOTA system instance
            questions: List of questions to test
            system_name: Name of the system
            
        Returns:
            Evaluation results
        """
        print(f"\n[EXPERIMENT] Running {system_name}...")
        
        results = []
        db_query_times = []
        
        for i, question_data in enumerate(questions, 1):
            query = question_data.get("question", "")
            expected_tools = question_data.get("expected_tools", [])
            expected_context = question_data.get("expected_context", [])
            
            print(f"  Processing question {i}/{len(questions)}: {query[:50]}...")
            
            start_time = datetime.now()
            
            # Simulate system response (replace with actual system call)
            response = self._simulate_minirag_llm_sota_response(system, query)
            
            end_time = datetime.now()
            
            response["start_time"] = start_time
            response["end_time"] = end_time
            
            # Track database query times
            if "db_query_time" in response:
                db_query_times.append(response["db_query_time"])
            
            # Evaluate
            metrics = self.evaluator.evaluate_single_query(
                query, response, expected_tools, expected_context
            )
            
            results.append({
                "question_id": question_data.get("id", f"Q{i}"),
                "query": query,
                "response": response,
                "metrics": metrics
            })
        
        # Aggregate results
        evaluation = self.evaluator.evaluate_system(system_name, results)
        
        # Add database efficiency metrics
        if db_query_times:
            evaluation["db_efficiency"] = self.metrics.calculate_database_query_efficiency(db_query_times)
        
        self.results[system_name] = {
            "evaluation": evaluation,
            "detailed_results": results
        }
        
        return evaluation
    
    def run_all_experiments(
        self,
        naive_rag_system,
        minirag_slm_system,
        minirag_llm_sota_system,
        questions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Run all experiments and compare results
        
        Args:
            naive_rag_system: Naive RAG system
            minirag_slm_system: MiniRAG SLM system
            minirag_llm_sota_system: MiniRAG LLM SOTA system
            questions: List of questions to test
            
        Returns:
            Comparison results
        """
        print("\n" + "="*80)
        print("RUNNING COMPREHENSIVE EXPERIMENTS")
        print("="*80)
        
        # Run all experiments
        naive_results = self.run_naive_rag_experiment(naive_rag_system, questions)
        slm_results = self.run_minirag_slm_experiment(minirag_slm_system, questions)
        sota_results = self.run_minirag_llm_sota_experiment(minirag_llm_sota_system, questions)
        
        # Compare results
        comparison = self._compare_results(naive_results, slm_results, sota_results)
        
        return {
            "naive_rag": naive_results,
            "minirag_slm": slm_results,
            "minirag_llm_sota": sota_results,
            "comparison": comparison,
            "all_results": self.results
        }
    
    def _compare_results(
        self,
        naive: Dict[str, Any],
        slm: Dict[str, Any],
        sota: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compare results from all three systems"""
        comparison = {
            "comprehensive_scores": {
                "naive_rag": naive.get("comprehensive_score", 0.0),
                "minirag_slm": slm.get("comprehensive_score", 0.0),
                "minirag_llm_sota": sota.get("comprehensive_score", 0.0)
            },
            "improvements": {
                "slm_vs_naive": {
                    "score_improvement": slm.get("comprehensive_score", 0.0) - naive.get("comprehensive_score", 0.0),
                    "percentage": ((slm.get("comprehensive_score", 0.0) / naive.get("comprehensive_score", 0.0) - 1) * 100) if naive.get("comprehensive_score", 0.0) > 0 else 0.0
                },
                "sota_vs_naive": {
                    "score_improvement": sota.get("comprehensive_score", 0.0) - naive.get("comprehensive_score", 0.0),
                    "percentage": ((sota.get("comprehensive_score", 0.0) / naive.get("comprehensive_score", 0.0) - 1) * 100) if naive.get("comprehensive_score", 0.0) > 0 else 0.0
                },
                "sota_vs_slm": {
                    "score_improvement": sota.get("comprehensive_score", 0.0) - slm.get("comprehensive_score", 0.0),
                    "percentage": ((sota.get("comprehensive_score", 0.0) / slm.get("comprehensive_score", 0.0) - 1) * 100) if slm.get("comprehensive_score", 0.0) > 0 else 0.0
                }
            }
        }
        
        return comparison
    
    def _simulate_naive_rag_response(self, system, query: str) -> Dict[str, Any]:
        """Simulate Naive RAG response (replace with actual system call)"""
        # This is a placeholder - replace with actual system call
        return {
            "answer": f"Naive RAG response to: {query}",
            "context": [],
            "tools_used": [],
            "response_time": 0.5
        }
    
    def _simulate_minirag_slm_response(self, system, query: str) -> Dict[str, Any]:
        """Simulate MiniRAG SLM response (replace with actual system call)"""
        # This is a placeholder - replace with actual system call
        return {
            "answer": f"MiniRAG SLM response to: {query}",
            "context": [],
            "tools_used": [],
            "response_time": 0.4
        }
    
    def _simulate_minirag_llm_sota_response(self, system, query: str) -> Dict[str, Any]:
        """Simulate MiniRAG LLM SOTA response (replace with actual system call)"""
        # This is a placeholder - replace with actual system call
        return {
            "answer": f"MiniRAG LLM SOTA response to: {query}",
            "context": [],
            "tools_used": [],
            "response_time": 0.3,
            "db_query_time": 0.05  # SOTA optimized
        }
    
    def save_results(self, output_path: Path):
        """Save experiment results to JSON file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"\n[INFO] Results saved to {output_path}")

