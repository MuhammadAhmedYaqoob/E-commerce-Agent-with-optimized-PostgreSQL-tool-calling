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
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "waiting_for_input" not in st.session_state:
    st.session_state.waiting_for_input = None  # 'order_number', 'verification_code', or None
if "pending_order_number" not in st.session_state:
    st.session_state.pending_order_number = None

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
    
    # Display conversation history
    if st.session_state.conversation_history:
        st.markdown("### 💬 Conversation History")
        for i, (role, message) in enumerate(st.session_state.conversation_history):
            if role == "user":
                st.markdown(f"**You:** {message}")
            else:
                st.markdown(f"**Assistant:** {message}")
        st.markdown("---")
    
    # User input section
    col1, col2 = st.columns([3, 1])
    
    with col1:
        user_email = st.text_input(
            "📧 Your Email (optional, leave empty if not logged in)",
            placeholder="user@example.com",
            value="" if st.session_state.waiting_for_input else st.session_state.get("user_email", "")
        )
    
    with col2:
        k = st.slider("Results", min_value=1, max_value=10, value=5)
    
    # Handle different input states
    if st.session_state.waiting_for_input == "order_number":
        query = st.text_input(
            "📦 Please enter your order number:",
            placeholder="e.g., ORD-12345",
            key="order_number_input"
        )
        submit_button = st.button("✅ Submit Order Number", type="primary")
    elif st.session_state.waiting_for_input == "verification_code":
        query = st.text_input(
            "🔐 Please enter the 6-digit verification code sent to your email:",
            placeholder="123456",
            key="verification_code_input",
            max_chars=6
        )
        submit_button = st.button("✅ Verify Code", type="primary")
        if st.button("🔄 Resend Code"):
            # Resend verification code
            if st.session_state.pending_order_number:
                with st.spinner("Resending verification code..."):
                    try:
                        # Get user email from order
                        user_email_from_order = st.session_state.agent.database_tool.get_user_email_from_order(
                            st.session_state.pending_order_number
                        )
                        if user_email_from_order:
                            result = st.session_state.agent.gmail_tool.send_2fa_code(
                                user_email_from_order, 
                                "order_verification"
                            )
                            if result.get("success"):
                                st.success("✅ Verification code resent! Check your email.")
                                st.rerun()
                    except Exception as e:
                        st.error(f"Error resending code: {e}")
    else:
        query = st.text_area(
            "💬 Ask your question",
            placeholder="e.g., What is your return policy? I want to track my order",
            height=100
        )
        submit_button = st.button("🚀 Query", type="primary")
    
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if not st.session_state.waiting_for_input:
            clear_button = st.button("🗑️ Clear")
        else:
            clear_button = st.button("❌ Cancel")
    
    if clear_button:
        st.session_state.conversation_history = []
        st.session_state.waiting_for_input = None
        st.session_state.pending_order_number = None
        st.rerun()
    
    # Process query
    if submit_button and query:
        # Add user message to history
        st.session_state.conversation_history.append(("user", query))
        
        with st.spinner("🤔 Agent is thinking..."):
            try:
                # Determine if user is logged in
                is_logged_in = bool(user_email and user_email.strip())
                
                # Build full query context if we're in a verification flow
                full_query = query
                if st.session_state.waiting_for_input == "order_number":
                    # User provided order number, add context
                    full_query = f"Order number: {query}"
                    st.session_state.pending_order_number = query
                elif st.session_state.waiting_for_input == "verification_code":
                    # User provided verification code
                    full_query = f"Verification code: {query}"
                
                # Use thread_id based on user email for state persistence
                thread_id = user_email if user_email else "anonymous"
                
                result = st.session_state.agent.process_query(
                    query=full_query,
                    user_email=user_email if is_logged_in else None,
                    conversation_history=st.session_state.conversation_history[:-1],  # Exclude current message
                    thread_id=thread_id
                )
                
                # Add assistant response to history
                st.session_state.conversation_history.append(("assistant", result["answer"]))
                
                # Check if agent is asking for order number
                answer_lower = result["answer"].lower()
                if ("order number" in answer_lower or "share your order" in answer_lower) and ("can you" in answer_lower or "please" in answer_lower):
                    st.session_state.waiting_for_input = "order_number"
                # Check if agent sent verification code
                elif "verification code" in answer_lower and ("sent" in answer_lower or "sent to" in answer_lower):
                    st.session_state.waiting_for_input = "verification_code"
                # Check if verification was successful and order was retrieved
                elif ("order number:" in answer_lower or "order found" in answer_lower or "status:" in answer_lower) and st.session_state.waiting_for_input == "verification_code":
                    # Verification successful, reset state
                    st.session_state.waiting_for_input = None
                    st.session_state.pending_order_number = None
                # Check if order was found directly (user provided order number in initial query)
                elif ("order number:" in answer_lower or "order found" in answer_lower) and not st.session_state.waiting_for_input:
                    # Order retrieved, no need to wait for input
                    st.session_state.waiting_for_input = None
                else:
                    # Reset waiting state if we got a final answer (unless we're explicitly waiting)
                    if "enter" not in answer_lower and "please" not in answer_lower:
                        st.session_state.waiting_for_input = None
                
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
                    
                    # Display debug info if available
                    if "debug_info" in result:
                        debug = result["debug_info"]
                        st.markdown("---")
                        st.markdown("### 🐛 Debug Information")
                        st.write(f"**User Logged In:** {debug.get('user_logged_in', False)}")
                        st.write(f"**Conversation Length:** {debug.get('conversation_length', 0)} messages")
                        
                        if debug.get("tool_calls"):
                            st.markdown("#### Tool Calls Made:")
                            for i, tc in enumerate(debug["tool_calls"], 1):
                                st.write(f"{i}. **{tc['tool']}** with args: `{tc['args']}`")
                        else:
                            st.warning("⚠️ No tool calls were made!")
                        
                        if debug.get("tool_results"):
                            st.markdown("#### Tool Results:")
                            for i, tr in enumerate(debug["tool_results"], 1):
                                st.write(f"{i}. **{tr['tool']}**: {tr['result']}")
                
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
                
                # Rerun to show updated UI
                st.rerun()
                
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
