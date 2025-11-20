"""
Stateful E-Commerce Agent with Proper LangGraph Orchestration
Uses LangGraph's statefulness for memory, context, and multi-step process management
"""
from typing import TypedDict, Annotated, List, Dict, Any, Optional, Literal
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage, BaseMessage
from langchain_core.tools import tool
import operator
import logging
import json
import re
from datetime import datetime

from ..config import OPENAI_API_KEY, LLM_MODEL, MAX_ITERATIONS
from ..minirag.graph_retriever import MiniRAGRetriever
from ..tools.gmail_tool import GmailTool
from ..tools.database_tool import DatabaseTool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentState(TypedDict):
    """Enhanced state with proper memory management"""
    messages: Annotated[List[BaseMessage], operator.add]
    user_email: str
    current_order_number: Optional[str]
    current_process: Optional[str]  # 'tracking', 'return', 'refund', 'replacement', etc.
    process_state: Dict[str, Any]  # State for current process
    verified_email: Optional[str]  # Email verified via 2FA
    retrieved_context: List[Dict[str, Any]]
    conversation_summary: str  # Summary of conversation for context

class StatefulECommerceAgent:
    """
    Stateful agent with proper LangGraph orchestration.
    Maintains context, memory, and handles multi-step processes.
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=LLM_MODEL,
            temperature=0.1,
            api_key=OPENAI_API_KEY
        )
        self.retriever = MiniRAGRetriever()
        self.gmail_tool = GmailTool()
        self.database_tool = DatabaseTool()
        
        # Create memory for state persistence
        self.memory = MemorySaver()
        
        # Define tools
        self.tools = [
            self._create_retrieve_policy_tool(),
            self._create_get_order_tool(),
            self._create_get_user_email_from_order_tool(),
            self._create_send_2fa_tool(),
            self._create_verify_2fa_tool(),
            self._create_search_orders_tool(),
            self._create_initiate_return_tool(),
            self._create_cancel_process_tool(),
        ]
        
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # Build workflow
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile(checkpointer=self.memory)
    
    def _create_retrieve_policy_tool(self):
        """Retrieve policies with proper formatting"""
        def retrieve_policy(query: str) -> str:
            """Retrieve e-commerce policies. Returns formatted, user-friendly information."""
            results = self.retriever.retrieve(query, k=3)
            if results:
                # Format nicely, exclude technical details like guardrails
                formatted = []
                for r in results:
                    title = r.get('title', '')
                    content = r.get('content', {})
                    
                    # Extract main content, skip guardrails and metadata
                    if isinstance(content, dict):
                        main_content = []
                        for key, value in content.items():
                            if key.lower() not in ['guardrails', 'metadata', 'technical']:
                                if isinstance(value, (list, dict)):
                                    main_content.append(f"{key}: {json.dumps(value, indent=2)}")
                                else:
                                    main_content.append(f"{key}: {value}")
                        content_str = "\n".join(main_content)
                    else:
                        content_str = str(content)
                    
                    formatted.append(f"{title}\n{content_str}")
                
                return "\n\n".join(formatted)
            return "No relevant policy information found."
        return tool(retrieve_policy)
    
    def _create_get_order_tool(self):
        """Get order with context awareness"""
        def get_order(order_id: str = None, user_email: str = None) -> str:
            """Get order details. If order_id not provided, uses current_order_number from state."""
            order_number = order_id
            if not order_number:
                # Try to get from state (will be passed via tool context)
                logger.warning("Order ID not provided to get_order tool")
                return "Order number is required. Please provide your order number."
            
            order = self.database_tool.get_order_by_id(order_number)
            if order:
                # Format nicely
                info = f"Order Number: {order.get('order_number')}\n"
                info += f"Status: {order.get('status', 'N/A')}\n"
                info += f"Total: ${order.get('total_amount', 0):.2f}\n"
                if order.get('tracking_number'):
                    info += f"Tracking: {order.get('tracking_number')} ({order.get('carrier', 'N/A')})\n"
                if order.get('estimated_delivery'):
                    info += f"Estimated Delivery: {order.get('estimated_delivery')}\n"
                if order.get('order_items'):
                    info += "\nItems:\n"
                    for item in order.get('order_items', [])[:5]:
                        info += f"  - {item.get('product_name', 'N/A')} x{item.get('quantity', 0)}\n"
                return info
            return f"Order {order_number} not found."
        return tool(get_order)
    
    def _create_get_user_email_from_order_tool(self):
        """Get email from order"""
        def get_user_email_from_order(order_number: str) -> str:
            email = self.database_tool.get_user_email_from_order(order_number)
            if email:
                return f"Email: {email}"
            return f"Order {order_number} not found."
        return tool(get_user_email_from_order)
    
    def _create_send_2fa_tool(self):
        """Send 2FA code"""
        def send_2fa_code(email: str, purpose: str = "verification") -> str:
            result = self.gmail_tool.send_2fa_code(email, purpose)
            if result.get("success"):
                return f"Verification code sent to {email}. Code expires in 30 seconds."
            return "Failed to send verification code."
        return tool(send_2fa_code)
    
    def _create_verify_2fa_tool(self):
        """Verify 2FA code"""
        def verify_2fa_code(email: str, code: str) -> str:
            result = self.gmail_tool.verify_2fa_code(email, code)
            if result.get("verified"):
                return "Verification successful."
            return result.get("message", "Verification failed.")
        return tool(verify_2fa_code)
    
    def _create_search_orders_tool(self):
        """Search orders"""
        def search_orders(user_email: str = None, status: str = None) -> str:
            if user_email:
                user = self.database_tool.get_user_by_email(user_email)
                if user:
                    orders = self.database_tool.get_user_orders(user["id"], limit=10)
                    if orders:
                        result = f"Found {len(orders)} order(s):\n\n"
                        for i, order in enumerate(orders[:5], 1):
                            result += f"{i}. {order.get('order_number')} - {order.get('status')} - ${order.get('total_amount', 0):.2f}\n"
                        return result
                    return "No orders found."
                return f"User {user_email} not found."
            elif status:
                orders = self.database_tool.search_orders_by_status(status)
                return f"Found {len(orders)} orders with status {status}."
            return "Please provide user_email or status."
        return tool(search_orders)
    
    def _create_initiate_return_tool(self):
        """Initiate return process"""
        def initiate_return(order_number: str, reason: str = None) -> str:
            # Check if order exists
            order = self.database_tool.get_order_by_id(order_number)
            if not order:
                return f"Order {order_number} not found."
            
            # Check if order is returnable
            status = order.get('status', '').lower()
            if status in ['delivered', 'shipped']:
                return f"Return process initiated for order {order_number}. Reason: {reason or 'Not specified'}. Please provide return details."
            return f"Order {order_number} with status '{status}' may not be eligible for return."
        return tool(initiate_return)
    
    def _create_cancel_process_tool(self):
        """Cancel current process"""
        def cancel_process(process_type: str) -> str:
            return f"Process '{process_type}' cancelled. How can I help you?"
        return tool(cancel_process)
    
    def _build_workflow(self) -> StateGraph:
        """Build LangGraph workflow with proper state management"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze", self._analyze_node)
        workflow.add_node("retrieve", self._retrieve_node)
        workflow.add_node("reason", self._reason_node)
        workflow.add_node("tools", self._tools_node)
        workflow.add_node("generate", self._generate_node)
        
        # Set entry point
        workflow.set_entry_point("analyze")
        
        # Define edges
        workflow.add_edge("analyze", "retrieve")
        workflow.add_edge("retrieve", "reason")
        workflow.add_conditional_edges(
            "reason",
            self._should_use_tools,
            {
                "tools": "tools",
                "generate": "generate",
            }
        )
        workflow.add_edge("tools", "reason")
        workflow.add_edge("generate", END)
        
        return workflow
    
    def _analyze_node(self, state: AgentState) -> AgentState:
        """Analyze query and extract context"""
        query = state.get("messages", [])[-1].content if state.get("messages") else ""
        user_email = state.get("user_email", "")
        
        # Extract order number if present
        order_match = re.search(r'ORD[-_]?\d+', query.upper())
        if order_match:
            state["current_order_number"] = order_match.group(0).replace('_', '-')
        
        # Detect process type
        query_lower = query.lower()
        if any(kw in query_lower for kw in ["return", "refund", "replace"]):
            if "return" in query_lower:
                state["current_process"] = "return"
            elif "refund" in query_lower:
                state["current_process"] = "refund"
            elif "replace" in query_lower:
                state["current_process"] = "replacement"
        elif any(kw in query_lower for kw in ["track", "where is", "order status"]):
            state["current_process"] = "tracking"
        
        # Check for process cancellation
        if any(kw in query_lower for kw in ["cancel", "don't want", "changed mind", "never mind"]):
            if state.get("current_process"):
                state["current_process"] = None
                state["process_state"] = {}
        
        return state
    
    def _retrieve_node(self, state: AgentState) -> AgentState:
        """Retrieve relevant context"""
        query = state.get("messages", [])[-1].content if state.get("messages") else ""
        retrieved = self.retriever.retrieve(query, k=3)
        state["retrieved_context"] = retrieved
        return state
    
    def _reason_node(self, state: AgentState) -> AgentState:
        """Reasoning with full context"""
        messages = state.get("messages", [])
        user_email = state.get("user_email", "")
        current_order = state.get("current_order_number")
        current_process = state.get("current_process")
        process_state = state.get("process_state", {})
        verified_email = state.get("verified_email")
        
        # Build context-aware system prompt
        system_parts = [
            "You are an intelligent e-commerce assistant with access to tools.",
            "You maintain conversation context and remember previous interactions.",
            "",
            f"User Status: {'Logged in' if user_email else 'Not logged in'}",
            f"Current Order: {current_order or 'None'}",
            f"Current Process: {current_process or 'None'}",
            f"Verified Email: {verified_email or 'None'}",
        ]
        
        if current_process and process_state:
            system_parts.append(f"Process State: {json.dumps(process_state, indent=2)}")
        
        system_parts.extend([
            "",
            "IMPORTANT RULES:",
            "1. Remember order numbers and context from previous messages",
            "2. If user mentions 'my order' and you have current_order_number, use it",
            "3. For returns/refunds, remember the order number from tracking",
            "4. If user changes mind mid-process, acknowledge and adapt",
            "5. Use tools to perform actions, don't just provide information",
            "6. Format RAG results nicely, exclude technical details like guardrails",
        ])
        
        system_msg = SystemMessage(content="\n".join(system_parts))
        
        # Prepare messages
        reasoning_messages = [system_msg] + messages[-10:]  # Last 10 for context
        
        # Get LLM response
        response = self.llm_with_tools.invoke(reasoning_messages)
        state["messages"].append(response)
        
        return state
    
    def _should_use_tools(self, state: AgentState) -> Literal["tools", "generate"]:
        """Decide if tools should be used"""
        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return "generate"
    
    def _tools_node(self, state: AgentState) -> AgentState:
        """Execute tools using ToolNode"""
        from langgraph.prebuilt import ToolNode
        tool_node = ToolNode(self.tools)
        return tool_node.invoke(state)
    
    def _generate_node(self, state: AgentState) -> AgentState:
        """Generate final answer"""
        messages = state.get("messages", [])
        
        # Get last AI message (might already have good response)
        last_ai = None
        for msg in reversed(messages):
            if isinstance(msg, AIMessage) and not (hasattr(msg, "tool_calls") and msg.tool_calls):
                last_ai = msg
                break
        
        # If we have tool results, format them nicely
        tool_results = []
        for msg in messages[-10:]:
            if isinstance(msg, ToolMessage):
                tool_results.append(msg.content)
        
        if tool_results and last_ai:
            # LLM already has context from tool results, use its response
            state["messages"].append(AIMessage(content=last_ai.content))
        elif last_ai and last_ai.content:
            # Use existing response
            state["messages"].append(AIMessage(content=last_ai.content))
        else:
            # Generate new response
            response = self.llm.invoke(messages[-5:])
            state["messages"].append(response)
        
        return state
    
    def process_query(
        self,
        query: str,
        user_email: str = None,
        thread_id: str = "default"
    ) -> Dict[str, Any]:
        """Process query with state persistence"""
        config = {"configurable": {"thread_id": thread_id}}
        
        # Get current state
        current_state = self.app.get_state(config)
        existing_state = current_state.values if current_state.values else {}
        
        # Add new user message
        new_message = HumanMessage(content=query)
        
        # Initial state - preserve existing state
        initial_state: AgentState = {
            "messages": [new_message],
            "user_email": user_email or existing_state.get("user_email", ""),
            "current_order_number": existing_state.get("current_order_number"),
            "current_process": existing_state.get("current_process"),
            "process_state": existing_state.get("process_state", {}),
            "verified_email": existing_state.get("verified_email"),
            "retrieved_context": [],
            "conversation_summary": existing_state.get("conversation_summary", ""),
        }
        
        # Run workflow with checkpointing
        final_state = None
        try:
            for iteration in range(MAX_ITERATIONS):
                final_state = self.app.invoke(initial_state, config)
                
                # Check if we should continue
                messages = final_state.get("messages", [])
                last_msg = messages[-1] if messages else None
                
                # If last message is final AI response without tool calls, we're done
                if isinstance(last_msg, AIMessage) and not (hasattr(last_msg, "tool_calls") and last_msg.tool_calls):
                    if last_msg.content and len(last_msg.content) > 10:
                        break
                
                # Update initial_state for next iteration
                initial_state = final_state
                
        except Exception as e:
            logger.error(f"Workflow error: {e}", exc_info=True)
            final_state = initial_state
        
        # Extract answer
        messages = final_state.get("messages", []) if final_state else []
        answer = "I apologize, but I couldn't process your request."
        
        # Get last AI message
        for msg in reversed(messages):
            if isinstance(msg, AIMessage) and msg.content:
                if not (hasattr(msg, "tool_calls") and msg.tool_calls):
                    answer = msg.content
                    break
        
        return {
            "answer": answer,
            "state": {
                "current_order_number": final_state.get("current_order_number") if final_state else None,
                "current_process": final_state.get("current_process") if final_state else None,
                "verified_email": final_state.get("verified_email") if final_state else None,
            }
        }

