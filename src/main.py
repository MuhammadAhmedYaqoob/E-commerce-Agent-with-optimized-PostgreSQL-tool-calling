"""
CLI Entry Point for E-Commerce MiniRAG System
"""
import argparse
from .minirag.graph_builder import MiniRAGGraphBuilder
from .agent.ecommerce_agent import ECommerceAgent

def cli():
    """Command-line interface"""
    parser = argparse.ArgumentParser("E-Commerce MiniRAG Agentic System")
    parser.add_argument("--build-graph", action="store_true", help="Build MiniRAG graph")
    parser.add_argument("--query", type=str, help="Ask a question")
    parser.add_argument("--email", type=str, help="User email (optional)")
    args = parser.parse_args()
    
    if args.build_graph:
        print("🔄 Building MiniRAG graph (PRIMARY index)...")
        builder = MiniRAGGraphBuilder()
        graph_path = builder.build_graph()
        if graph_path:
            graph = builder.get_graph()
            print(f"✅ Graph built: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")
        else:
            print("❌ Failed to build graph")
    
    if args.query:
        print(f"🔎 Processing query: {args.query}")
        agent = ECommerceAgent()
        result = agent.process_query(query=args.query, user_email=args.email)
        
        print("\n💡 Answer:")
        print(result["answer"])
        print(f"\n📊 Metadata: {result['iterations']} iterations, {result['tool_usage']} tools used")

if __name__ == "__main__":
    cli()
