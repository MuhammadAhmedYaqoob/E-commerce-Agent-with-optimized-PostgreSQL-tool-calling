"""
System Initialization and Verification Script
Verifies configuration, builds graph, tests connections, and runs quick test
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import (
    OPENAI_API_KEY, USE_SUPABASE, LOCAL_DB_NAME, LOCAL_DB_HOST,
    DATA_DIR, GRAPH_DIR, POLICIES_PATH, ENTITIES_PATH
)
from src.minirag.graph_builder import MiniRAGGraphBuilder
from src.tools.database_tool import DatabaseTool
from src.agent.ecommerce_agent import ECommerceAgent

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def check_configuration():
    """Verify configuration"""
    print_header("[1/4] Configuration Check")
    
    issues = []
    
    # Check OpenAI API key
    if OPENAI_API_KEY:
        print("[OK] OpenAI API key configured")
    else:
        print("[ERROR] OpenAI API key NOT found")
        issues.append("OPENAI_API_KEY")
    
    # Check database configuration
    if USE_SUPABASE:
        print("[OK] Using Supabase (cloud database)")
    else:
        print(f"[OK] Using Local PostgreSQL: {LOCAL_DB_NAME}")
        print(f"      Host: {LOCAL_DB_HOST}")
    
    # Check knowledge base files
    print("\nKnowledge Base Files:")
    files_to_check = [
        ("Policies", POLICIES_PATH),
        ("Entities", ENTITIES_PATH),
    ]
    
    all_files_exist = True
    for name, path in files_to_check:
        if path.exists():
            print(f"   [OK] {name}: {path.name}")
        else:
            print(f"   [ERROR] {name}: {path.name} NOT FOUND")
            all_files_exist = False
            issues.append(f"{name} file")
    
    if issues:
        print(f"\n[WARNING] Issues found: {', '.join(issues)}")
        return False
    
    print("\n[OK] All configuration checks passed!")
    return True

def test_database():
    """Test database connection"""
    print_header("[2/4] Database Connection Test")
    
    try:
        db = DatabaseTool()
        
        # Test user lookup
        test_email = "john@example.com"
        user = db.get_user_by_email(test_email)
        
        if user:
            print(f"[OK] Database connected successfully")
            print(f"      Test query: Found user '{user.get('name', 'N/A')}' ({test_email})")
            
            # Test order lookup
            order = db.get_order_by_id("ORD-12345")
            if order:
                print(f"      Test query: Found order '{order.get('order_number', 'N/A')}'")
            
            return True
        else:
            print(f"[WARNING] Database connected but test user not found")
            print(f"          Run: python database/init_database.py")
            return False
            
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        print(f"         Make sure PostgreSQL is running and database is initialized")
        return False

def build_graph():
    """Build MiniRAG graph"""
    print_header("[3/4] Building MiniRAG Graph")
    
    try:
        # Ensure graph directory exists
        GRAPH_DIR.mkdir(parents=True, exist_ok=True)
        
        print("Building graph from knowledge base...")
        builder = MiniRAGGraphBuilder()
        graph_path = builder.build_graph()
        
        if graph_path and graph_path.exists():
            graph = builder.get_graph()
            print(f"\n[OK] Graph built successfully!")
            print(f"     Nodes: {graph.number_of_nodes()}")
            print(f"     Edges: {graph.number_of_edges()}")
            print(f"     Saved to: {graph_path}")
            return True
        else:
            print("[ERROR] Graph build failed")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error building graph: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_agent():
    """Test agent with a simple query"""
    print_header("[4/4] Agent Test")
    
    try:
        print("Initializing agent...")
        agent = ECommerceAgent()
        
        test_query = "What is your return policy?"
        print(f"\nTest query: '{test_query}'")
        print("Processing...")
        
        result = agent.process_query(query=test_query, user_email="test@example.com")
        
        if result and result.get("answer"):
            print(f"\n[OK] Agent test successful!")
            print(f"\nAnswer preview:")
            answer = result["answer"]
            preview = answer[:200] + "..." if len(answer) > 200 else answer
            print(f"      {preview}")
            print(f"\nMetadata:")
            print(f"      Iterations: {result.get('iterations', 0)}")
            print(f"      Tools used: {result.get('tool_usage', 0)}")
            return True
        else:
            print("[WARNING] Agent responded but answer is empty")
            return False
            
    except Exception as e:
        print(f"[ERROR] Agent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main initialization flow"""
    print("\n" + "="*60)
    print("  E-Commerce MiniRAG System Initialization")
    print("="*60)
    
    results = {
        "configuration": False,
        "database": False,
        "graph": False,
        "agent": False
    }
    
    # Step 1: Check configuration
    results["configuration"] = check_configuration()
    if not results["configuration"]:
        print("\n[WARNING] Configuration issues found. Please fix before continuing.")
        return
    
    # Step 2: Test database
    results["database"] = test_database()
    if not results["database"]:
        print("\n[WARNING] Database not ready. Run: python database/init_database.py")
    
    # Step 3: Build graph
    results["graph"] = build_graph()
    if not results["graph"]:
        print("\n[WARNING] Graph build failed. Check knowledge base files.")
    
    # Step 4: Test agent (only if graph is built)
    if results["graph"]:
        results["agent"] = test_agent()
    else:
        print("\n[SKIP] Skipping agent test (graph not built)")
    
    # Final summary
    print_header("Initialization Summary")
    
    status_icons = {
        True: "[OK]",
        False: "[ERROR]"
    }
    
    for component, status in results.items():
        icon = status_icons[status]
        print(f"{icon} {component.capitalize()}: {'Ready' if status else 'Not Ready'}")
    
    all_ready = all(results.values())
    
    if all_ready:
        print("\n[SUCCESS] System is fully initialized and ready!")
        print("\nNext steps:")
        print("   1. Test with Streamlit: streamlit run streamlit_app.py")
        print("   2. Run evaluation: python run_evaluation.py")
        print("   3. Use API: python -m uvicorn src.api.main:app --reload")
    else:
        print("\n[WARNING] Some components need attention. Please fix issues above.")
        print("\nCommon fixes:")
        if not results["database"]:
            print("   - Database: python database/init_database.py")
        if not results["graph"]:
            print("   - Graph: Check knowledge base files in data/ folder")
        if not results["agent"]:
            print("   - Agent: Ensure graph is built and OpenAI key is valid")

if __name__ == "__main__":
    main()

