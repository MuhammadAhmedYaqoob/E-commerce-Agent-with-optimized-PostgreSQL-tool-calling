"""
Streamlit UI for E-Commerce MiniRAG Agentic System
"""
import streamlit as st
from src.agent.ecommerce_agent import ECommerceAgent
from src.minirag.graph_builder import MiniRAGGraphBuilder
from src.config import KNOWLEDGE_BASE_PATH
import json

st.set_page_config(
    page_title="E-Commerce MiniRAG Agent",
    page_icon="🛒",
    layout="wide"
)

# Initialize session state
if "agent" not in st.session_state:
    st.session_state.agent = None
if "graph_built" not in st.session_state:
    st.session_state.graph_built = False

# Sidebar
with st.sidebar:
    st.header("🛒 E-Commerce MiniRAG System")
    st.markdown("---")
    
    st.subheader("📊 System Status")
    
    # Check knowledge base
    if KNOWLEDGE_BASE_PATH.exists():
        st.success("✅ Knowledge base loaded")
        with open(KNOWLEDGE_BASE_PATH, 'r') as f:
            kb = json.load(f)
            st.info(f"Policies: {len(kb.get('policies', {}))}")
    else:
        st.error("❌ Knowledge base not found")
    
    st.markdown("---")
    
    st.subheader("🔧 Configuration")
    
    # Build graph button
    if st.button("🔨 Build MiniRAG Graph", type="primary"):
        with st.spinner("Building graph (PRIMARY index)..."):
            try:
                builder = MiniRAGGraphBuilder()
                graph_path = builder.build_graph()
                if graph_path:
                    st.session_state.graph_built = True
                    graph = builder.get_graph()
                    st.success(f"✅ Graph built: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")
                else:
                    st.error("❌ Failed to build graph")
            except Exception as e:
                st.error(f"Error: {e}")
    
    # Initialize agent button
    if st.button("🤖 Initialize Agent"):
        with st.spinner("Initializing agentic system..."):
            try:
                st.session_state.agent = ECommerceAgent()
                st.success("✅ Agent initialized")
            except Exception as e:
                st.error(f"Error: {e}")
    
    st.markdown("---")
    
    st.subheader("ℹ️ About")
    st.markdown("""
    **MiniRAG Architecture:**
    - Graph-first retrieval (PRIMARY)
    - LangGraph orchestration
    - Agentic tool calling
    - Gmail & Supabase tools
    """)

# Main interface
def main():
    st.title("🛒 E-Commerce Agentic Assistant")
    st.markdown("""
    Powered by **MiniRAG Architecture** with LangGraph orchestration.
    Ask questions about policies, orders, shipping, returns, and more.
    """)
    
    # Check if agent is initialized
    if st.session_state.agent is None:
        st.warning("⚠️ Please initialize the agent from the sidebar first.")
        return
    
    # User input section
    col1, col2 = st.columns([3, 1])
    
    with col1:
        user_email = st.text_input(
            "📧 Your Email (optional, for personalized responses)",
            placeholder="user@example.com"
        )
    
    with col2:
        k = st.slider("Results", min_value=1, max_value=10, value=5)
    
    query = st.text_area(
        "💬 Ask your question",
        placeholder="e.g., What is your return policy? How long does shipping take?",
        height=100
    )
    
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        submit_button = st.button("🚀 Query", type="primary")
    with col2:
        clear_button = st.button("🗑️ Clear")
    
    if clear_button:
        st.rerun()
    
    # Process query
    if submit_button and query:
        with st.spinner("🤔 Agent is thinking..."):
            try:
                result = st.session_state.agent.process_query(
                    query=query,
                    user_email=user_email if user_email else None
                )
                
                # Display answer
                st.markdown("### 💡 Answer")
                st.markdown(result["answer"])
                
                # Display metadata
                with st.expander("🔍 Agent Details", expanded=False):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Iterations", result["iterations"])
                    with col2:
                        st.metric("Tools Used", result["tool_usage"])
                    with col3:
                        st.metric("Context Retrieved", len(result["context"]))
                    
                    st.write("**Step:**", result["steps"])
                
                # Display retrieved context
                if result["context"]:
                    with st.expander("📚 Retrieved Context (MiniRAG Graph)", expanded=False):
                        for i, ctx in enumerate(result["context"][:3], 1):
                            st.markdown(f"#### Context {i}: {ctx.get('title', 'N/A')}")
                            st.write(f"**Category:** {ctx.get('category', 'N/A')}")
                            st.write(f"**Score:** {ctx.get('score', 0):.3f}")
                            st.write(f"**Method:** {ctx.get('retrieval_method', 'N/A')}")
                            st.json(ctx.get('content', {}))
                            st.markdown("---")
                
            except Exception as e:
                st.error(f"❌ Error: {e}")
                st.exception(e)
    
    # Example queries
    st.markdown("---")
    st.subheader("💡 Example Queries")
    
    examples = [
        "What is your return and refund policy?",
        "How long does standard shipping take?",
        "What payment methods do you accept?",
        "What is your privacy policy?",
        "How does the loyalty program work?",
        "What are the shipping costs?",
        "Can I track my order?",
        "What is your dispute resolution process?"
    ]
    
    cols = st.columns(4)
    for i, example in enumerate(examples):
        with cols[i % 4]:
            if st.button(example, key=f"example_{i}"):
                st.session_state.example_query = example
                st.rerun()
    
    if "example_query" in st.session_state:
        query = st.session_state.example_query
        del st.session_state.example_query

if __name__ == "__main__":
    main()
