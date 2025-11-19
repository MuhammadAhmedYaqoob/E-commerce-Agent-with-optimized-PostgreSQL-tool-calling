"""
Visualization for Experiment Results
"""
from typing import Dict, Any, List
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import json


class ResultsVisualizer:
    """
    Create visualizations for experiment results
    """
    
    def __init__(self, results_path: Path = None):
        """
        Initialize visualizer
        
        Args:
            results_path: Path to results JSON file
        """
        self.results_path = results_path
        self.results = self._load_results() if results_path else {}
    
    def _load_results(self) -> Dict[str, Any]:
        """Load results from JSON file"""
        try:
            with open(self.results_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[ERROR] Failed to load results: {e}")
            return {}
    
    def plot_comprehensive_scores(self, output_path: Path):
        """
        Plot comprehensive scores comparison
        
        Args:
            output_path: Path to save the plot
        """
        systems = []
        scores = []
        
        for system_name, data in self.results.items():
            if "evaluation" in data:
                systems.append(system_name)
                scores.append(data["evaluation"].get("comprehensive_score", 0.0))
        
        if not systems:
            print("[WARNING] No results to plot")
            return
        
        plt.figure(figsize=(10, 6))
        bars = plt.bar(systems, scores, color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
        plt.ylabel('Comprehensive Score', fontsize=12)
        plt.title('Comprehensive Score Comparison: Naive RAG vs MiniRAG SLM vs MiniRAG LLM SOTA', fontsize=14, fontweight='bold')
        plt.ylim(0, 1.0)
        plt.xticks(rotation=15, ha='right')
        plt.grid(axis='y', alpha=0.3)
        
        # Add value labels on bars
        for bar, score in zip(bars, scores):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{score:.3f}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"[INFO] Plot saved to {output_path}")
    
    def plot_metric_comparison(self, output_path: Path):
        """
        Plot detailed metric comparison
        
        Args:
            output_path: Path to save the plot
        """
        metrics = ["retrieval_accuracy", "relevance_score", "tool_usage_accuracy", 
                   "state_consistency", "memory_retention", "answer_quality"]
        
        systems = []
        metric_data = {metric: [] for metric in metrics}
        
        for system_name, data in self.results.items():
            if "evaluation" in data:
                systems.append(system_name)
                eval_data = data["evaluation"]
                for metric in metrics:
                    mean = eval_data.get("metrics", {}).get(metric, {}).get("mean", 0.0)
                    metric_data[metric].append(mean)
        
        if not systems:
            print("[WARNING] No results to plot")
            return
        
        x = np.arange(len(metrics))
        width = 0.25
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        for i, system in enumerate(systems):
            values = [metric_data[metric][i] for metric in metrics]
            offset = (i - 1) * width
            ax.bar(x + offset, values, width, label=system)
        
        ax.set_ylabel('Score', fontsize=12)
        ax.set_title('Detailed Metric Comparison Across Systems', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels([m.replace('_', ' ').title() for m in metrics], rotation=45, ha='right')
        ax.legend()
        ax.set_ylim(0, 1.0)
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"[INFO] Plot saved to {output_path}")
    
    def plot_response_times(self, output_path: Path):
        """
        Plot response time comparison
        
        Args:
            output_path: Path to save the plot
        """
        systems = []
        avg_times = []
        std_times = []
        
        for system_name, data in self.results.items():
            if "evaluation" in data:
                systems.append(system_name)
                metrics = data["evaluation"].get("metrics", {})
                response_time = metrics.get("response_time", {})
                avg_times.append(response_time.get("mean", 0.0))
                std_times.append(response_time.get("std", 0.0))
        
        if not systems:
            print("[WARNING] No results to plot")
            return
        
        plt.figure(figsize=(10, 6))
        bars = plt.bar(systems, avg_times, yerr=std_times, capsize=5, 
                      color=['#FF6B6B', '#4ECDC4', '#45B7D1'], alpha=0.8)
        plt.ylabel('Response Time (seconds)', fontsize=12)
        plt.title('Response Time Comparison', fontsize=14, fontweight='bold')
        plt.xticks(rotation=15, ha='right')
        plt.grid(axis='y', alpha=0.3)
        
        # Add value labels
        for bar, avg in zip(bars, avg_times):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{avg:.3f}s', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"[INFO] Plot saved to {output_path}")
    
    def plot_database_efficiency(self, output_path: Path):
        """
        Plot database query efficiency (for SOTA system)
        
        Args:
            output_path: Path to save the plot
        """
        sota_data = None
        for system_name, data in self.results.items():
            if "SOTA" in system_name and "evaluation" in data:
                sota_data = data["evaluation"].get("db_efficiency", {})
                break
        
        if not sota_data:
            print("[WARNING] No SOTA database efficiency data")
            return
        
        metrics = ["avg_time", "min_time", "max_time", "p95_time", "p99_time"]
        values = [sota_data.get(m, 0.0) for m in metrics]
        
        plt.figure(figsize=(10, 6))
        bars = plt.bar([m.replace('_', ' ').title() for m in metrics], values, color='#45B7D1')
        plt.ylabel('Query Time (seconds)', fontsize=12)
        plt.title('SOTA PostgreSQL Query Efficiency Metrics', fontsize=14, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y', alpha=0.3)
        
        # Add value labels
        for bar, val in zip(bars, values):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.001,
                    f'{val:.4f}s', ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"[INFO] Plot saved to {output_path}")
    
    def create_all_visualizations(self, output_dir: Path):
        """
        Create all visualizations
        
        Args:
            output_dir: Directory to save all plots
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        self.plot_comprehensive_scores(output_dir / "comprehensive_scores.png")
        self.plot_metric_comparison(output_dir / "metric_comparison.png")
        self.plot_response_times(output_dir / "response_times.png")
        self.plot_database_efficiency(output_dir / "database_efficiency.png")
        
        print(f"\n[INFO] All visualizations saved to {output_dir}")

