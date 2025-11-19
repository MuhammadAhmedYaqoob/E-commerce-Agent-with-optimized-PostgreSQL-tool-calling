"""
E-Commerce Agentic AI System using LangGraph
Implements full agentic behavior with tool calling and orchestration.
"""
from typing import TypedDict, Annotated, List, Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
import operator

from ..config import OPENAI_API_KEY, LLM_MODEL, AGENT_SYSTEM_PROMPT, MAX_ITERATIONS
from ..minirag.graph_retriever import MiniRAGRetriever
from ..tools.gmail_tool import GmailTool
from ..tools.supabase_tool import SupabaseTool
from ..generator import generate_answer

class AgentState(TypedDict):
    """State for the agentic workflow"""
    messages: Annotated[List, operator.add]
    query: str
    retrieved_context: List[Dict[str, Any]]
    user_email: str
    current_step: str
    tool_results: Dict[str, Any]
    iteration_count: int

class ECommerceAgent:
    """
    Agentic E-Commerce Assistant using LangGraph orchestration.
    Implements autonomous decision-making, tool usage, and multi-step reasoning.
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=LLM_MODEL,
            temperature=0.1,
            api_key=OPENAI_API_KEY
        )
        self.retriever = MiniRAGRetriever()
        self.gmail_tool = GmailTool()
        self.supabase_tool = SupabaseTool()
        
        # Define tools
        self.tools = [
            self._create_retrieve_policy_tool(),
            self._create_get_order_tool(),
            self._create_send_notification_tool(),
            self._create_send_2fa_tool(),
            self._create_verify_2fa_tool(),
            self._create_search_orders_tool()
        ]
        
        # Bind tools to LLM
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # Build agent graph
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile()
    
    def _create_retrieve_policy_tool(self):
        """Tool for retrieving policies from MiniRAG graph"""
        def retrieve_policy(query: str) -> str:
            """Retrieve e-commerce policies and information from knowledge graph.
            
            Args:
                query: User question about policies, returns, shipping, etc.
                
            Returns:
                Retrieved policy information
            """
            results = self.retriever.retrieve(query, k=3)
            if results:
                context = "\n\n".join([
                    f"Policy: {r.get('title', 'N/A')}\n"
                    f"Category: {r.get('category', 'N/A')}\n"
                    f"Content: {str(r.get('content', {}))}"
                    for r in results
                ])
                return context
            return "No relevant policy information found."
        
        return tool(retrieve_policy)
    
    def _create_get_order_tool(self):
        """Tool for getting order information from database"""
        def get_order(order_id: str, user_email: str = None) -> str:
            """Get order details from database.
            
            Args:
                order_id: Order ID to retrieve
                user_email: Optional user email for verification
                
            Returns:
                Order information as JSON string
            """
            order = self.supabase_tool.get_order_by_id(order_id)
            if order:
                return f"Order found: {order}"
            return f"Order {order_id} not found."
        
        return tool(get_order)
    
    def _create_send_notification_tool(self):
        """Tool for sending email notifications"""
        def send_notification(email: str, notification_type: str, data: str) -> str:
            """Send notification email to user.
            
            Args:
                email: Recipient email
                notification_type: Type (order_update, shipping, payment)
                data: Notification data as JSON string
                
            Returns:
                Success status
            """
            import json
            data_dict = json.loads(data) if isinstance(data, str) else data
            result = self.gmail_tool.send_notification(email, notification_type, data_dict)
            return f"Notification sent: {result.get('success', False)}"
        
        return tool(send_notification)
    
    def _create_send_2fa_tool(self):
        """Tool for sending 2FA codes"""
        def send_2fa_code(email: str, purpose: str = "verification") -> str:
            """Send 2FA verification code to user email.
            
            Args:
                email: User email address
                purpose: Purpose of verification
                
            Returns:
                Status message
            """
            result = self.gmail_tool.send_2fa_code(email, purpose)
            return result.get("message", "Failed to send code")
        
        return tool(send_2fa_code)
    
    def _create_verify_2fa_tool(self):
        """Tool for verifying 2FA codes"""
        def verify_2fa_code(email: str, code: str) -> str:
            """Verify 2FA code for user.
            
            Args:
                email: User email
                code: Verification code
                
            Returns:
                Verification result
            """
            result = self.gmail_tool.verify_2fa_code(email, code)
            return result.get("message", "Verification failed")
        
        return tool(verify_2fa_code)
    
    def _create_search_orders_tool(self):
        """Tool for searching orders"""
        def search_orders(status: str = None, user_email: str = None) -> str:
            """Search orders by status or user.
            
            Args:
                status: Order status filter
                user_email: User email to filter orders
                
            Returns:
                List of orders
            """
            if user_email:
                user = self.supabase_tool.get_user_by_email(user_email)
                if user:
                    orders = self.supabase_tool.get_user_orders(user["id"], limit=10)
                    return f"Found {len(orders)} orders for user"
            elif status:
                orders = self.supabase_tool.search_orders_by_status(status)
                return f"Found {len(orders)} orders with status {status}"
            return "Please provide status or user_email"
        
        return tool(search_orders)
    
    def _build_workflow(self) -> StateGraph:
        """Build LangGraph workflow for agentic behavior"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("retrieve", self._retrieve_node)
        workflow.add_node("reason", self._reason_node)
        workflow.add_node("tools", ToolNode(self.tools))
        workflow.add_node("generate", self._generate_node)
        workflow.add_node("notify", self._notify_node)
        
        # Define edges
        workflow.set_entry_point("retrieve")
        
        workflow.add_edge("retrieve", "reason")
        workflow.add_conditional_edges(
            "reason",
            self._should_use_tools,
            {
                "tools": "tools",
                "generate": "generate",
                "notify": "notify"
            }
        )
        workflow.add_edge("tools", "reason")
        workflow.add_edge("generate", END)
        workflow.add_edge("notify", END)
        
        return workflow
    
    def _retrieve_node(self, state: AgentState) -> AgentState:
        """Retrieve relevant information from MiniRAG graph"""
        query = state.get("query", "")
        retrieved = self.retriever.retrieve(query, k=5)
        
        state["retrieved_context"] = retrieved
        state["current_step"] = "retrieved"
        state["messages"].append(AIMessage(
            content=f"Retrieved {len(retrieved)} relevant policies from knowledge graph."
        ))
        
        return state
    
    def _reason_node(self, state: AgentState) -> AgentState:
        """Agent reasoning step - decide on next action"""
        messages = state.get("messages", [])
        query = state.get("query", "")
        context = state.get("retrieved_context", [])
        
        # Build context string
        context_str = "\n\n".join([
            f"Policy: {r.get('title', 'N/A')}\n{r.get('content', {})}"
            for r in context[:3]
        ])
        
        # System message with context
        system_msg = f"{AGENT_SYSTEM_PROMPT}\n\nRetrieved Context:\n{context_str}"
        
        # Prepare messages
        reasoning_messages = [
            SystemMessage(content=system_msg),
            HumanMessage(content=query)
        ] + messages[-3:]  # Last few messages for context
        
        # Get LLM response with tool calling
        response = self.llm_with_tools.invoke(reasoning_messages)
        
        state["messages"].append(response)
        state["current_step"] = "reasoned"
        state["iteration_count"] = state.get("iteration_count", 0) + 1
        
        return state
    
    def _should_use_tools(self, state: AgentState) -> str:
        """Decide whether to use tools or generate final answer"""
        last_message = state["messages"][-1]
        
        # Check if LLM wants to use tools
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        
        # Check if notification is needed
        query_lower = state.get("query", "").lower()
        if any(keyword in query_lower for keyword in ["notify", "send email", "update"]):
            return "notify"
        
        # Otherwise generate answer
        return "generate"
    
    def _generate_node(self, state: AgentState) -> AgentState:
        """Generate final answer"""
        query = state.get("query", "")
        context = state.get("retrieved_context", [])
        
        answer = generate_answer(query, context)
        
        state["messages"].append(AIMessage(content=answer))
        state["current_step"] = "completed"
        
        return state
    
    def _notify_node(self, state: AgentState) -> AgentState:
        """Handle notification actions"""
        user_email = state.get("user_email", "")
        query = state.get("query", "")
        
        # Extract notification intent from query
        if "order" in query.lower() and user_email:
            # Send order update notification
            notification_data = {
                "customer_name": "Customer",
                "order_id": "extracted_from_query",
                "status": "updated",
                "message": "Your order status has been updated."
            }
            self.gmail_tool.send_notification(
                user_email,
                "order_update",
                notification_data
            )
        
        state["messages"].append(AIMessage(
            content="Notification sent successfully."
        ))
        state["current_step"] = "notified"
        
        return state
    
    def process_query(self, query: str, user_email: str = None) -> Dict[str, Any]:
        """
        Process user query through agentic workflow.
        
        Args:
            query: User question
            user_email: Optional user email for personalized responses
            
        Returns:
            Agent response with answer and metadata
        """
        initial_state: AgentState = {
            "messages": [HumanMessage(content=query)],
            "query": query,
            "retrieved_context": [],
            "user_email": user_email or "",
            "current_step": "started",
            "tool_results": {},
            "iteration_count": 0
        }
        
        # Run workflow with iteration limit
        final_state = initial_state
        try:
            for _ in range(MAX_ITERATIONS):
                final_state = self.app.invoke(final_state)
                if final_state.get("current_step") in ["completed", "notified"]:
                    break
        except Exception as e:
            print(f"[ERROR] Agent workflow error: {e}")
        
        # Extract final answer
        final_messages = final_state.get("messages", [])
        answer = final_messages[-1].content if final_messages else "I apologize, but I couldn't process your request."
        
        return {
            "answer": answer,
            "context": final_state.get("retrieved_context", []),
            "steps": final_state.get("current_step", ""),
            "iterations": final_state.get("iteration_count", 0),
            "tool_usage": len([m for m in final_messages if hasattr(m, "tool_calls")])
        }

