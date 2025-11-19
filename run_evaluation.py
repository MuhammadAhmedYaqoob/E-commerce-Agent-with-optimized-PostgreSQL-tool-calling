"""
Main script to run evaluation experiments
"""
import json
from pathlib import Path
from src.config import EVALUATION_QUESTIONS_PATH, EVALUATION_OUTPUT_DIR, EVALUATION_PLOTS_DIR
from src.evaluation.experiments import ExperimentRunner
from src.evaluation.visualization import ResultsVisualizer

def load_questions() -> list:
    """Load all evaluation questions"""
    try:
        with open(EVALUATION_QUESTIONS_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Flatten all question categories into single list
        all_questions = []
        questions_dict = data.get("questions", {})
        
        for category, questions in questions_dict.items():
            for question in questions:
                question["category"] = category
                all_questions.append(question)
        
        return all_questions
    except Exception as e:
        print(f"[ERROR] Failed to load questions: {e}")
        return []

def main():
    """Run evaluation experiments"""
    print("="*80)
    print("E-Commerce MiniRAG Evaluation Framework")
    print("="*80)
    
    # Load questions
    print("\n[INFO] Loading evaluation questions...")
    questions = load_questions()
    print(f"[INFO] Loaded {len(questions)} questions")
    
    # Initialize experiment runner
    runner = ExperimentRunner(EVALUATION_QUESTIONS_PATH)
    
    # Create mock systems (replace with actual system instances)
    # For now, these are placeholders - you'll need to implement actual systems
    naive_rag_system = None  # Replace with Naive RAG system
    minirag_slm_system = None  # Replace with MiniRAG SLM system
    minirag_llm_sota_system = None  # Replace with MiniRAG LLM SOTA system
    
    print("\n[INFO] Starting experiments...")
    print("[NOTE] Using simulated responses. Replace with actual system calls.")
    
    # Run experiments
    results = runner.run_all_experiments(
        naive_rag_system=naive_rag_system,
        minirag_slm_system=minirag_slm_system,
        minirag_llm_sota_system=minirag_llm_sota_system,
        questions=questions
    )
    
    # Save results
    EVALUATION_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    results_path = EVALUATION_OUTPUT_DIR / "evaluation_results.json"
    runner.save_results(results_path)
    
    # Create visualizations
    print("\n[INFO] Creating visualizations...")
    visualizer = ResultsVisualizer(results_path)
    EVALUATION_PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    visualizer.create_all_visualizations(EVALUATION_PLOTS_DIR)
    
    # Print summary
    print("\n" + "="*80)
    print("EVALUATION SUMMARY")
    print("="*80)
    
    if "comparison" in results:
        comp = results["comparison"]
        print("\nComprehensive Scores:")
        for system, score in comp.get("comprehensive_scores", {}).items():
            print(f"  {system}: {score:.4f}")
        
        print("\nImprovements:")
        improvements = comp.get("improvements", {})
        for comparison, data in improvements.items():
            print(f"  {comparison}:")
            print(f"    Score Improvement: {data.get('score_improvement', 0):.4f}")
            print(f"    Percentage: {data.get('percentage', 0):.2f}%")
    
    print(f"\n[INFO] Results saved to {EVALUATION_OUTPUT_DIR}")
    print("[INFO] Plots saved to {EVALUATION_PLOTS_DIR}")

if __name__ == "__main__":
    main()

