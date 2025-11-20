"""
E-Commerce Agentic AI System using LangGraph
Implements full agentic behavior with tool calling and orchestration.
"""
from typing import TypedDict, Annotated, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
import operator
import logging
import re
import json

from ..config import OPENAI_API_KEY, LLM_MODEL, AGENT_SYSTEM_PROMPT, MAX_ITERATIONS
from ..minirag.graph_retriever import MiniRAGRetriever
from ..tools.gmail_tool import GmailTool
from ..tools.database_tool import DatabaseTool
from ..tools.mcp_client import PostgreSQLMCPClient, GmailMCPClient
from ..generator import generate_answer
from .planning import PlanningModule

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentState(TypedDict):
    """State for the agentic workflow with proper memory management"""
    messages: Annotated[List, operator.add]
    query: str
    retrieved_context: List[Dict[str, Any]]
    user_email: str
    current_step: str
    tool_results: Dict[str, Any]
    iteration_count: int
    # Enhanced state for context preservation
    current_order_number: Optional[str]
    current_process: Optional[str]  # 'tracking', 'return', 'refund', 'replacement'
    process_state: Dict[str, Any]
    verified_email: Optional[str]
    conversation_context: Dict[str, Any]  # Store important context

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
        # Use MCP clients instead of direct tools
        self.postgresql_mcp = PostgreSQLMCPClient()
        self.gmail_mcp = GmailMCPClient()
        # Keep direct tools as fallback
        self.gmail_tool = GmailTool()
        self.database_tool = DatabaseTool()  # Unified database tool (Supabase or Local PostgreSQL)
        self.planning_module = PlanningModule()  # Explicit planning
        
        # Define tools
        self.tools = [
            self._create_retrieve_policy_tool(),
            self._create_get_order_tool(),
            self._create_get_user_email_from_order_tool(),
            self._create_send_notification_tool(),
            self._create_send_2fa_tool(),
            self._create_verify_2fa_tool(),
            self._create_search_orders_tool()
        ]
        
        # Bind tools to LLM
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # Build agent graph with custom tool node for debugging
        self.workflow = self._build_workflow()
        
        # Use memory for state persistence across conversations
        self.memory = MemorySaver()
        self.app = self.workflow.compile(checkpointer=self.memory)
        
        # Store debug info
        self.debug_info = []
    
    def _create_retrieve_policy_tool(self):
        """Tool for retrieving policies from MiniRAG graph with proper formatting"""
        def retrieve_policy(query: str) -> str:
            """Retrieve e-commerce policies and information from knowledge graph.
            Returns user-friendly formatted information, excluding technical details like guardrails.
            
            Args:
                query: User question about policies, returns, shipping, etc.
                
            Returns:
                Formatted policy information (excludes guardrails and metadata)
            """
            results = self.retriever.retrieve(query, k=3)
            if results:
                formatted = []
                for r in results:
                    title = r.get('title', 'N/A')
                    category = r.get('category', 'N/A')
                    content = r.get('content', {})
                    
                    # Format content, exclude technical details
                    if isinstance(content, dict):
                        user_content = []
                        for key, value in content.items():
                            # Skip technical/administrative fields
                            if key.lower() not in ['guardrails', 'metadata', 'technical', 'admin', 'internal']:
                                if isinstance(value, (list, dict)):
                                    if isinstance(value, list) and value:
                                        user_content.append(f"{key}: {', '.join(str(v) for v in value[:5])}")
                                    else:
                                        user_content.append(f"{key}: {json.dumps(value, indent=2) if isinstance(value, dict) else str(value)}")
                                else:
                                    user_content.append(f"{key}: {value}")
                        content_str = "\n".join(user_content)
                    else:
                        content_str = str(content)
                    
                    formatted.append(f"=== {title} ===\nCategory: {category}\n{content_str}")
                
                return "\n\n".join(formatted)
            return "No relevant policy information found."
        
        return tool(retrieve_policy)
    
    def _create_get_order_tool(self):
        """Tool for getting order information from database"""
        def get_order(order_id: str = None, user_email: str = None) -> str:
            """Get order details from database.
            If order_id not provided, will use current_order_number from conversation context.
            
            Args:
                order_id: Order ID or order number to retrieve (optional if in context)
                user_email: Optional user email for verification
                
            Returns:
                Formatted order information
            """
            # If order_id not provided, try to get from state (passed via tool context)
            if not order_id:
                logger.warning("[TOOL] get_order: order_id not provided")
                return "Order number is required. Please provide your order number."
            
            logger.info(f"[TOOL] get_order called via MCP with: order_id={order_id}, user_email={user_email}")
            try:
                order = self.postgresql_mcp.get_order_by_id(order_id)
            except Exception as e:
                logger.error(f"[TOOL] MCP error: {e}, falling back to direct tool")
                order = self.database_tool.get_order_by_id(order_id)
            if order and "error" not in order:
                logger.info(f"[TOOL] ✅ Order found: {order.get('order_number')} - Status: {order.get('status')}")
                # Format order information nicely
                order_info = f"Order Number: {order.get('order_number', 'N/A')}\n"
                order_info += f"Status: {order.get('status', 'N/A')}\n"
                order_info += f"Total Amount: ${order.get('total_amount', 0):.2f}\n"
                if order.get('tracking_number'):
                    order_info += f"Tracking Number: {order.get('tracking_number')}\n"
                if order.get('carrier'):
                    order_info += f"Carrier: {order.get('carrier')}\n"
                if order.get('estimated_delivery'):
                    order_info += f"Estimated Delivery: {order.get('estimated_delivery')}\n"
                if order.get('order_items'):
                    order_info += "\nItems:\n"
                    for item in order.get('order_items', [])[:10]:  # Limit to 10 items
                        order_info += f"  - {item.get('product_name', 'N/A')} x{item.get('quantity', 0)} @ ${item.get('unit_price', 0):.2f}\n"
                return order_info
            logger.warning(f"[TOOL] ❌ Order {order_id} not found")
            return f"Order {order_id} not found."
        
        return tool(get_order)
    
    def _create_get_user_email_from_order_tool(self):
        """Tool for getting user email from order number via MCP"""
        def get_user_email_from_order(order_number: str) -> str:
            """Get user email address associated with an order number using MCP client.
            This is used for sending verification codes to non-logged-in users.
            
            Args:
                order_number: Order number (e.g., 'ORD-12345')
                
            Returns:
                User email address or error message
            """
            logger.info(f"[TOOL] get_user_email_from_order called via MCP with: {order_number}")
            try:
                email = self.postgresql_mcp.get_user_email_from_order(order_number)
            except Exception as e:
                logger.error(f"[TOOL] MCP error: {e}, falling back to direct tool")
                email = self.database_tool.get_user_email_from_order(order_number)
            
            if email:
                logger.info(f"[TOOL] ✅ Found email: {email}")
                return f"User email found: {email}"
            logger.warning(f"[TOOL] ❌ Order {order_number} not found")
            return f"Order {order_number} not found or has no associated user."
        
        return tool(get_user_email_from_order)
    
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
        """Tool for sending 2FA codes via MCP"""
        def send_2fa_code(email: str, purpose: str = "verification") -> str:
            """Send 2FA verification code to user email using MCP client.
            
            Args:
                email: User email address
                purpose: Purpose of verification
                
            Returns:
                Status message
            """
            logger.info(f"[TOOL] send_2fa_code called via MCP with: email={email}, purpose={purpose}")
            try:
                result = self.gmail_mcp.send_2fa_code(email, purpose)
            except Exception as e:
                logger.error(f"[TOOL] MCP error: {e}, falling back to direct tool")
                result = self.gmail_tool.send_2fa_code(email, purpose)
            logger.info(f"[TOOL] send_2fa_code result: {result.get('message', 'Unknown')}")
            return result.get("message", "Failed to send code")
        
        return tool(send_2fa_code)
    
    def _create_verify_2fa_tool(self):
        """Tool for verifying 2FA codes via MCP"""
        def verify_2fa_code(email: str, code: str) -> str:
            """Verify 2FA code for user using MCP client.
            
            Args:
                email: User email
                code: Verification code
                
            Returns:
                Verification result
            """
            logger.info(f"[TOOL] verify_2fa_code called via MCP with: email={email}, code={'*' * len(code)}")
            try:
                result = self.gmail_mcp.verify_2fa_code(email, code)
            except Exception as e:
                logger.error(f"[TOOL] MCP error: {e}, falling back to direct tool")
                result = self.gmail_tool.verify_2fa_code(email, code)
            verified = result.get("verified", False)
            logger.info(f"[TOOL] verify_2fa_code result: {'✅ VERIFIED' if verified else '❌ FAILED'} - {result.get('message', 'Unknown')}")
            return result.get("message", "Verification failed")
        
        return tool(verify_2fa_code)
    
    def _create_search_orders_tool(self):
        """Tool for searching orders"""
        def search_orders(status: str = None, user_email: str = None) -> str:
            """Search orders by status or user.
            
            Args:
                status: Order status filter
                user_email: User email to filter orders (REQUIRED if no status)
                
            Returns:
                List of orders with details
            """
            logger.info(f"[TOOL] search_orders called with: status={status}, user_email={user_email}")
            
            if user_email:
                user = self.database_tool.get_user_by_email(user_email)
                if user:
                    orders = self.database_tool.get_user_orders(user["id"], limit=10)
                    if orders:
                        result = f"Found {len(orders)} order(s) for {user_email}:\n\n"
                        for i, order in enumerate(orders[:5], 1):  # Show first 5
                            result += f"{i}. Order {order.get('order_number', 'N/A')} - Status: {order.get('status', 'N/A')} - Total: ${order.get('total_amount', 0):.2f}\n"
                        if len(orders) > 5:
                            result += f"\n... and {len(orders) - 5} more orders"
                        logger.info(f"[TOOL] ✅ Found {len(orders)} orders for user")
                        return result
                    else:
                        logger.info(f"[TOOL] ⚠️ No orders found for user")
                        return f"No orders found for {user_email}"
                else:
                    logger.warning(f"[TOOL] ❌ User not found: {user_email}")
                    return f"User {user_email} not found in database"
            elif status:
                orders = self.database_tool.search_orders_by_status(status)
                result = f"Found {len(orders)} order(s) with status '{status}':\n\n"
                for i, order in enumerate(orders[:5], 1):
                    result += f"{i}. Order {order.get('order_number', 'N/A')} - Total: ${order.get('total_amount', 0):.2f}\n"
                logger.info(f"[TOOL] ✅ Found {len(orders)} orders with status {status}")
                return result
            else:
                logger.warning(f"[TOOL] ❌ No status or user_email provided")
                return "Please provide either status or user_email parameter"
        
        return tool(search_orders)
    
    def _build_workflow(self) -> StateGraph:
        """Build LangGraph workflow for agentic behavior"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("retrieve", self._retrieve_node)
        workflow.add_node("reason", self._reason_node)
        workflow.add_node("tools", self._tools_node)  # Custom tool node with debugging
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
        user_email = state.get("user_email", "")
        
        # Extract order number from query if present
        order_match = re.search(r'ORD[-_]?\d+', query.upper())
        if order_match:
            state["current_order_number"] = order_match.group(0).replace('_', '-')
            logger.info(f"[RETRIEVE] Extracted order number: {state['current_order_number']}")
        
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
        if any(kw in query_lower for kw in ["cancel", "don't want", "changed mind", "never mind", "leave it"]):
            if state.get("current_process"):
                logger.info(f"[RETRIEVE] Process cancellation detected. Clearing process: {state['current_process']}")
                state["current_process"] = None
                state["process_state"] = {}
        
        logger.info(f"[RETRIEVE] Query: {query}")
        logger.info(f"[RETRIEVE] User email: {user_email or 'NOT PROVIDED (not logged in)'}")
        logger.info(f"[RETRIEVE] Current order: {state.get('current_order_number', 'None')}")
        logger.info(f"[RETRIEVE] Current process: {state.get('current_process', 'None')}")
        
        retrieved = self.retriever.retrieve(query, k=5)
        
        logger.info(f"[RETRIEVE] Retrieved {len(retrieved)} context items")
        
        state["retrieved_context"] = retrieved
        state["current_step"] = "retrieved"
        
        return state
    
    def _reason_node(self, state: AgentState) -> AgentState:
        """Agent reasoning step - decide on next action with explicit planning"""
        messages = state.get("messages", [])
        query = state.get("query", "")
        context = state.get("retrieved_context", [])
        user_email = state.get("user_email", "")
        
        logger.info(f"[REASON] Starting reasoning for query: {query}")
        logger.info(f"[REASON] User logged in: {bool(user_email)}")
        logger.info(f"[REASON] Conversation history length: {len(messages)}")
        
        # Explicit planning with scratchpad
        previous_state = {
            "retrieved_context": context,
            "user_email": user_email,
            "tool_results": state.get("tool_results", {})
        }
        
        # Get tool names
        available_tools = []
        for tool in self.tools:
            if hasattr(tool, 'name'):
                available_tools.append(tool.name)
            elif hasattr(tool, 'func'):
                available_tools.append(tool.func.__name__)
            else:
                available_tools.append(str(tool))
        
        logger.info(f"[REASON] Available tools: {available_tools}")
        
        plan = self.planning_module.plan_action_sequence(
            query=query,
            context=context,
            available_tools=available_tools,
            previous_state=previous_state
        )
        
        logger.info(f"[REASON] Plan: {plan}")
        
        # Add planning reasoning to scratchpad
        self.planning_module.scratchpad.add_reasoning_step(
            step="Query analysis",
            reasoning=f"Analyzed query: {query[:50]}...",
            confidence=1.0 - plan.get("uncertainty", 0.0)
        )
        
        # Build context string (formatted nicely, exclude guardrails)
        context_parts = []
        for r in context[:3]:
            title = r.get('title', 'N/A')
            content = r.get('content', {})
            if isinstance(content, dict):
                # Filter out technical details
                user_content = {k: v for k, v in content.items() 
                              if k.lower() not in ['guardrails', 'metadata', 'technical', 'admin']}
                context_parts.append(f"Policy: {title}\n{json.dumps(user_content, indent=2)}")
            else:
                context_parts.append(f"Policy: {title}\n{content}")
        context_str = "\n\n".join(context_parts)
        
        # Include planning information in system message
        planning_info = f"\n\nPlanning:\nPrimary Action: {plan['primary_action']}\nUncertainty: {plan.get('uncertainty', 0.0):.2f}"
        
        # Get state context
        remembered_order = state.get("current_order_number")
        current_process = state.get("current_process")
        verified_email = state.get("verified_email")
        process_state = state.get("process_state", {})
        
        # Build state context info
        state_context = []
        if remembered_order:
            state_context.append(f"REMEMBERED ORDER: {remembered_order} - Use this when user says 'my order' or 'the order'")
        if current_process:
            state_context.append(f"CURRENT PROCESS: {current_process}")
        if verified_email:
            state_context.append(f"VERIFIED EMAIL: {verified_email} - User has been verified")
        if process_state:
            state_context.append(f"PROCESS STATE: {json.dumps(process_state, indent=2)}")
        
        state_context_str = "\n".join(state_context) if state_context else "No previous context"
        
        # System message with context and planning
        system_msg = f"{AGENT_SYSTEM_PROMPT}\n\n=== CONVERSATION STATE ===\n{state_context_str}\n\n=== RETRIEVED CONTEXT ===\n{context_str}{planning_info}"
        
        # Check if query contains order number pattern
        import re
        order_pattern = r'ORD[-_]?\d+'
        order_match = re.search(order_pattern, query.upper())
        
        # Build context-aware prompt
        context_notes = []
        
        # Use remembered order number if available and user refers to "my order"
        if remembered_order and any(phrase in query.lower() for phrase in ["my order", "the order", "this order", "that order"]):
            context_notes.append(f"[CRITICAL CONTEXT: User is referring to order {remembered_order} from previous conversation. USE THIS ORDER NUMBER.]")
            order_number = remembered_order
        elif order_match:
            order_number = order_match.group(0).replace('_', '-')
            logger.info(f"[REASON] 🔍 Detected order number in query: {order_number}")
        else:
            order_number = remembered_order  # Use remembered if no new one
        
        # Check if this is an order tracking request
        is_order_tracking = any(keyword in query.lower() for keyword in [
            "track", "order", "where is my order", "order status", "order number"
        ])
        
        # Check if user is asking about ALL their orders (not a specific order)
        is_all_orders_query = any(phrase in query.lower() for phrase in [
            "my orders", "orders in my account", "how many orders", "list my orders",
            "orders belong to my account", "all my orders", "my account orders"
        ])
        
        if is_all_orders_query and user_email:
            context_notes.append(f"[CRITICAL: User IS LOGGED IN ({user_email}) and asking about ALL their orders. You MUST immediately use search_orders tool with user_email='{user_email}'. DO NOT ask for order number - they want to see ALL orders.]")
        elif is_order_tracking:
            if user_email:
                context_notes.append(f"[CRITICAL: User IS LOGGED IN ({user_email}). For order tracking, you MUST use get_order or search_orders tool directly. DO NOT use verification tools.]")
            else:
                context_notes.append("[CRITICAL: User is NOT LOGGED IN. For order tracking, you MUST use tools in this exact sequence: 1) get_user_email_from_order, 2) send_2fa_code, 3) wait for user to provide code, 4) verify_2fa_code, 5) get_order. DO NOT just ask them to visit the website.]")
        
        if order_number:
            logger.info(f"[REASON] 🔍 Using order number: {order_number}")
            if not user_email and not verified_email:
                # Need verification
                context_notes.append(f"[ACTION REQUIRED: Order number {order_number} available. You MUST immediately call get_user_email_from_order tool with order_number='{order_number}'. Do not ask for confirmation.]")
            elif verified_email or user_email:
                # Already verified or logged in
                context_notes.append(f"[ACTION REQUIRED: Order number {order_number} available. You MUST immediately call get_order tool with order_id='{order_number}'. Do not ask for confirmation.]")
        
        # Handle return/refund requests with remembered order
        if any(kw in query.lower() for kw in ["return", "refund", "replace"]) and order_number:
            context_notes.append(f"[ACTION: User wants to {current_process or 'process'} order {order_number}. Remember this order number for the return process.]")
        
        # Handle verification code input
        code_match = re.search(r'\b\d{6}\b', query)
        if code_match and not user_email:
            code = code_match.group(0)
            # Get email from previous tool results or state
            email_to_verify = verified_email or state.get("conversation_context", {}).get("pending_verification_email")
            if email_to_verify:
                context_notes.append(f"[ACTION REQUIRED: User provided verification code {code}. You MUST call verify_2fa_code tool with email='{email_to_verify}' and code='{code}'.]")
            else:
                context_notes.append("[WARNING: Verification code provided but email not found in context. Check previous tool results for email.]")
        
        if context_notes:
            query_with_context = f"{query}\n\n" + "\n".join(context_notes)
        else:
            query_with_context = query
        
        # Prepare messages - filter to ensure ToolMessages are properly paired
        # OpenAI requires ToolMessages to come immediately after AIMessage with tool_calls
        # AND each ToolMessage must have a tool_call_id matching a tool_call in the AIMessage
        # CRITICAL: Only include AIMessage with tool_calls if ALL tool_call_ids have matching ToolMessages
        filtered_messages = []
        i = 0
        while i < len(messages):
            msg = messages[i]
            # If it's an AIMessage with tool_calls, check if all tool_calls have responses
            if isinstance(msg, AIMessage) and hasattr(msg, 'tool_calls') and msg.tool_calls:
                # Get all tool_call_ids from this AIMessage
                tool_call_ids = {tc.get('id') for tc in msg.tool_calls if tc.get('id')}
                # Check if all tool_call_ids have matching ToolMessages immediately following
                matched_tool_call_ids = set()
                j = i + 1
                while j < len(messages) and isinstance(messages[j], ToolMessage):
                    tool_msg = messages[j]
                    if hasattr(tool_msg, 'tool_call_id') and tool_msg.tool_call_id in tool_call_ids:
                        matched_tool_call_ids.add(tool_msg.tool_call_id)
                    j += 1
                
                # Only include if ALL tool_call_ids have matching ToolMessages
                if matched_tool_call_ids == tool_call_ids and len(tool_call_ids) > 0:
                    filtered_messages.append(msg)
                    i += 1
                    # Include all matching ToolMessages
                    while i < len(messages) and isinstance(messages[i], ToolMessage):
                        tool_msg = messages[i]
                        if hasattr(tool_msg, 'tool_call_id') and tool_msg.tool_call_id in tool_call_ids:
                            filtered_messages.append(tool_msg)
                            i += 1
                        else:
                            break
                else:
                    # Not all tool_calls have responses - skip this AIMessage and its ToolMessages
                    i += 1
                    while i < len(messages) and isinstance(messages[i], ToolMessage):
                        i += 1
            # If it's a HumanMessage or AIMessage without tool_calls, include it
            elif isinstance(msg, (HumanMessage, AIMessage)) and not (hasattr(msg, 'tool_calls') and msg.tool_calls):
                filtered_messages.append(msg)
                i += 1
            # Skip standalone ToolMessages (they should have been paired above)
            else:
                i += 1
        
        # Take last few messages for context (but ensure proper pairing)
        context_messages = filtered_messages[-5:] if len(filtered_messages) > 5 else filtered_messages
        
        # Prepare messages
        # Limit context messages to prevent token bloat
        # Only use last 10 messages for context (recent conversation)
        limited_context = context_messages[-10:] if len(context_messages) > 10 else context_messages
        
        reasoning_messages = [
            SystemMessage(content=system_msg),
            HumanMessage(content=query_with_context)
        ] + limited_context
        
        logger.info(f"[REASON] Using {len(limited_context)} context messages (limited from {len(context_messages)})")
        
        logger.info(f"[REASON] Sending {len(reasoning_messages)} messages to LLM")
        logger.info(f"[REASON] System prompt length: {len(system_msg)} chars")
        logger.info(f"[REASON] Context messages: {[type(m).__name__ for m in context_messages]}")
        
        # Get LLM response with tool calling
        response = self.llm_with_tools.invoke(reasoning_messages)
        
        # Debug LLM response
        logger.info(f"[REASON] LLM response type: {type(response)}")
        logger.info(f"[REASON] LLM response content: {response.content[:200] if hasattr(response, 'content') else 'N/A'}")
        
        if hasattr(response, 'tool_calls') and response.tool_calls:
            logger.info(f"[REASON] ✅ LLM wants to call {len(response.tool_calls)} tool(s):")
            for i, tool_call in enumerate(response.tool_calls):
                logger.info(f"[REASON]   Tool {i+1}: {tool_call.get('name', 'unknown')} with args: {tool_call.get('args', {})}")
        else:
            logger.warning(f"[REASON] ⚠️ LLM did NOT call any tools. Response: {response.content[:200] if hasattr(response, 'content') else 'N/A'}")
        
        state["messages"].append(response)
        state["current_step"] = "reasoned"
        state["iteration_count"] = state.get("iteration_count", 0) + 1
        state["planning_scratchpad"] = self.planning_module.get_scratchpad().to_dict()
        state["action_plan"] = plan
        
        return state
    
    def _should_use_tools(self, state: AgentState) -> str:
        """Decide whether to use tools or generate final answer"""
        last_message = state["messages"][-1]
        query = state.get("query", "")
        user_email = state.get("user_email", "")
        
        logger.info(f"[DECISION] Checking if tools should be used for query: {query}")
        
        # Check if LLM wants to use tools
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            logger.info(f"[DECISION] ✅ Routing to TOOLS node - LLM requested {len(last_message.tool_calls)} tool call(s)")
            return "tools"
        
        # Special case: If LLM already gave a good response (asking for order number), use it directly
        if isinstance(last_message, AIMessage) and last_message.content:
            content_lower = last_message.content.lower()
            # If LLM is asking for order number, that's a complete response - don't regenerate
            if ("order number" in content_lower or "share your order" in content_lower) and "can you" in content_lower:
                logger.info(f"[DECISION] ✅ LLM already provided good response (asking for order number). Using it directly.")
                # Mark as completed so we use this response
                state["current_step"] = "completed"
                return "generate"  # Will use the existing response
        
        # Special case: If this is an order tracking request with order number and user not logged in,
        # we should force tool usage even if LLM didn't call tools
        query_lower = query.lower()
        is_order_tracking = any(keyword in query_lower for keyword in ["track", "order"])
        has_order_number = "ORD-" in query.upper() or "order number" in query_lower
        
        if is_order_tracking and has_order_number and not user_email:
            logger.warning(f"[DECISION] ⚠️ Order tracking detected but no tools called. This is an error - should use tools!")
            logger.error(f"[DECISION] ❌ CRITICAL: Order tracking request without tool calls!")
        
        # Check if notification is needed
        if any(keyword in query_lower for keyword in ["notify", "send email", "update"]):
            logger.info(f"[DECISION] ✅ Routing to NOTIFY node")
            return "notify"
        
        # Otherwise generate answer
        logger.warning(f"[DECISION] ⚠️ Routing to GENERATE node - No tool calls detected")
        logger.warning(f"[DECISION] Last message: {last_message.content[:200] if hasattr(last_message, 'content') else str(last_message)}")
        return "generate"
    
    def _generate_node(self, state: AgentState) -> AgentState:
        """Generate final answer"""
        query = state.get("query", "")
        context = state.get("retrieved_context", [])
        user_email = state.get("user_email", "")
        messages = state.get("messages", [])
        
        logger.warning(f"[GENERATE] Generating answer without tools for query: {query}")
        logger.warning(f"[GENERATE] User logged in: {bool(user_email)}")
        
        # Check if LLM already provided a good response in REASON node
        # Look for the last AIMessage that's not from tool calls
        last_ai_message = None
        for msg in reversed(messages):
            if isinstance(msg, AIMessage) and not (hasattr(msg, "tool_calls") and msg.tool_calls):
                last_ai_message = msg
                break
        
        # If we have a good response from REASON node (like asking for order number), use it
        if last_ai_message and last_ai_message.content:
            content_lower = last_ai_message.content.lower()
            # If it's asking for order number or already has a complete response, use it
            if ("order number" in content_lower and "can you" in content_lower) or len(last_ai_message.content) > 50:
                logger.info(f"[GENERATE] Using existing LLM response from REASON node")
                # Don't add another message, just mark as completed
                state["current_step"] = "completed"
                return state
        
        # Check if we have tool results in recent messages that should be used
        tool_results_text = ""
        for msg in reversed(messages[-10:]):  # Check last 10 messages
            if isinstance(msg, ToolMessage):
                tool_results_text += f"\nTool Result: {msg.content}\n"
        
        # If we have tool results, include them in the answer generation
        if tool_results_text:
            logger.info(f"[GENERATE] Found tool results, including in answer generation")
            query_with_results = f"{query}\n\nTool Results:\n{tool_results_text}"
            answer = generate_answer(query_with_results, context)
        else:
            answer = generate_answer(query, context)
        
        logger.info(f"[GENERATE] Generated answer: {answer[:200]}...")
        
        state["messages"].append(AIMessage(content=answer))
        state["current_step"] = "completed"
        
        return state
    
    def _tools_node(self, state: AgentState) -> AgentState:
        """Custom tool node with debugging and state updates"""
        last_message = state["messages"][-1]
        
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            logger.info(f"[TOOLS] Executing {len(last_message.tool_calls)} tool call(s)")
            
            for tool_call in last_message.tool_calls:
                tool_name = tool_call.get("name", "unknown")
                tool_args = tool_call.get("args", {})
                logger.info(f"[TOOLS] Calling tool: {tool_name}")
                logger.info(f"[TOOLS] Tool arguments: {tool_args}")
                
                # Inject state context into tool calls
                if tool_name == "get_order" and not tool_args.get("order_id"):
                    if state.get("current_order_number"):
                        tool_args["order_id"] = state["current_order_number"]
                        logger.info(f"[TOOLS] Injected order number from state: {state['current_order_number']}")
        
        # Use the standard ToolNode
        tool_node = ToolNode(self.tools)
        result_state = tool_node.invoke(state)
        
        # Update state based on tool results
        for msg in result_state.get("messages", []):
            if isinstance(msg, ToolMessage):
                logger.info(f"[TOOLS] Tool result from {msg.name}: {msg.content[:200]}...")
                
                # Extract email from get_user_email_from_order result
                if msg.name == "get_user_email_from_order" and "email found" in msg.content.lower():
                    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', msg.content)
                    if email_match:
                        result_state["conversation_context"] = result_state.get("conversation_context", {})
                        result_state["conversation_context"]["pending_verification_email"] = email_match.group(0)
                        logger.info(f"[TOOLS] Stored email for verification: {email_match.group(0)}")
                
                # Update verified_email on successful verification
                if msg.name == "verify_2fa_code" and "successful" in msg.content.lower():
                    # Get email from conversation context
                    pending_email = result_state.get("conversation_context", {}).get("pending_verification_email")
                    if pending_email:
                        result_state["verified_email"] = pending_email
                        logger.info(f"[TOOLS] Email verified: {pending_email}")
        
        return result_state
    
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
    
    def process_query(
        self, 
        query: str, 
        user_email: str = None, 
        conversation_history: List = None,
        thread_id: str = "default"
    ) -> Dict[str, Any]:
        """
        Process user query through agentic workflow.
        
        Args:
            query: User question
            user_email: Optional user email for personalized responses
            conversation_history: Optional list of previous messages in format [(role, content), ...]
            
        Returns:
            Agent response with answer and metadata
        """
        # Use checkpointing for state persistence
        config = {"configurable": {"thread_id": thread_id}}
        
        # Get existing state if any
        try:
            existing_state = self.app.get_state(config)
            existing_values = existing_state.values if existing_state.values else {}
            existing_messages = existing_state.values.get("messages", []) if existing_state.values else []
        except:
            existing_values = {}
            existing_messages = []
        
        # Limit existing messages to last 20 to prevent bloat
        # Only keep recent messages for context
        if len(existing_messages) > 20:
            existing_messages = existing_messages[-20:]
            logger.warning(f"[WORKFLOW] Truncated message history from {len(existing_state.values.get('messages', []))} to 20 messages")
        
        # Build messages - use existing messages from checkpoint OR conversation_history, not both
        messages = []
        
        # If we have existing messages from checkpoint, use those (they're already in the right format)
        if existing_messages:
            messages = existing_messages.copy()
            logger.info(f"[WORKFLOW] Using {len(messages)} messages from checkpoint")
        # Otherwise, build from conversation_history if provided
        elif conversation_history:
            for role, content in conversation_history[-10:]:  # Only last 10 from history
                if role == "user":
                    messages.append(HumanMessage(content=content))
                elif role == "assistant":
                    messages.append(AIMessage(content=content))
            logger.info(f"[WORKFLOW] Built {len(messages)} messages from conversation_history")
        
        # Add current query
        messages.append(HumanMessage(content=query))
        
        # Limit messages to prevent bloat - only keep recent conversation
        if len(messages) > 30:
            logger.warning(f"[WORKFLOW] ⚠️ Too many messages ({len(messages)}), truncating to last 30")
            # Keep system messages and last 30
            system_msgs = [m for m in messages if isinstance(m, SystemMessage)]
            other_msgs = [m for m in messages if not isinstance(m, SystemMessage)]
            messages = system_msgs + other_msgs[-30:]
        
        # Preserve state across queries
        initial_state: AgentState = {
            "messages": messages,
            "query": query,
            "retrieved_context": [],
            "user_email": user_email or existing_values.get("user_email", ""),
            "current_step": "started",
            "tool_results": {},
            "iteration_count": 0,
            "current_order_number": existing_values.get("current_order_number"),
            "current_process": existing_values.get("current_process"),
            "process_state": existing_values.get("process_state", {}),
            "verified_email": existing_values.get("verified_email"),
            "conversation_context": existing_values.get("conversation_context", {}),
        }
        
        # Run workflow with checkpointing
        final_state = initial_state
        logger.info(f"[WORKFLOW] Starting workflow with query: {query}")
        logger.info(f"[WORKFLOW] User email: {user_email or 'NOT PROVIDED'}")
        logger.info(f"[WORKFLOW] Thread ID: {thread_id}")
        logger.info(f"[WORKFLOW] Max iterations: {MAX_ITERATIONS}")
        
        try:
            for iteration in range(MAX_ITERATIONS):
                logger.info(f"[WORKFLOW] === Iteration {iteration + 1}/{MAX_ITERATIONS} ===")
                logger.info(f"[WORKFLOW] Current step: {final_state.get('current_step', 'unknown')}")
                
                # Invoke with checkpointing
                final_state = self.app.invoke(final_state, config)
                
                # Check message count and truncate if too large
                messages = final_state.get("messages", [])
                if len(messages) > 50:
                    logger.warning(f"[WORKFLOW] ⚠️ Message count too high ({len(messages)}), truncating to last 30")
                    # Keep system message if present, then last 30 messages
                    system_msgs = [m for m in messages if isinstance(m, SystemMessage)]
                    other_msgs = [m for m in messages if not isinstance(m, SystemMessage)]
                    final_state["messages"] = system_msgs + other_msgs[-30:]
                    messages = final_state["messages"]
                
                # Check for loops
                recent_tool_calls = []
                for msg in messages[-10:]:
                    if hasattr(msg, "tool_calls") and msg.tool_calls:
                        for tc in msg.tool_calls:
                            recent_tool_calls.append(tc.get("name", "unknown"))
                
                # Detect loops - check if same tool called multiple times with same args
                if len(recent_tool_calls) >= 2:
                    last_two = recent_tool_calls[-2:]
                    if len(set(last_two)) == 1:
                        # Same tool called twice - check if it's with same arguments
                        tool_name = last_two[0]
                        recent_tool_msgs = [msg for msg in messages[-10:] if hasattr(msg, "tool_calls") and msg.tool_calls]
                        if len(recent_tool_msgs) >= 2:
                            last_two_tool_msgs = recent_tool_msgs[-2:]
                            # Check if same tool with same args
                            same_args = True
                            for msg in last_two_tool_msgs:
                                for tc in msg.tool_calls:
                                    if tc.get("name") == tool_name:
                                        # Compare args (simplified - just check if both have same keys)
                                        break
                            
                            # If same tool called twice consecutively, it's likely a loop
                            logger.warning(f"[WORKFLOW] ⚠️ Same tool '{tool_name}' called twice. Checking for loop...")
                            # Check if we have a response after the tool calls
                            has_response_after_tools = False
                            for msg in reversed(messages[-5:]):
                                if isinstance(msg, AIMessage) and msg.content and not (hasattr(msg, "tool_calls") and msg.tool_calls):
                                    if len(msg.content) > 20:
                                        has_response_after_tools = True
                                        break
                            
                            if not has_response_after_tools:
                                logger.error(f"[WORKFLOW] ❌ LOOP DETECTED: Tool '{tool_name}' called repeatedly without progress. Breaking.")
                                # Force completion with last response or error message
                                final_state["current_step"] = "completed"
                                break
                
                current_step = final_state.get("current_step", "unknown")
                logger.info(f"[WORKFLOW] After iteration {iteration + 1}, step: {current_step}")
                
                # Check if we have a complete answer and can stop
                messages = final_state.get("messages", [])
                last_ai_msg = None
                for msg in reversed(messages):
                    if isinstance(msg, AIMessage) and msg.content:
                        if not (hasattr(msg, "tool_calls") and msg.tool_calls):
                            last_ai_msg = msg
                            break
                
                # If we have tool results and a response, we can complete
                has_tool_results = any(isinstance(m, ToolMessage) for m in messages[-5:])
                
                # Check if we've already completed
                if current_step in ["completed", "notified"]:
                    logger.info(f"[WORKFLOW] ✅ Workflow completed at step: {current_step}")
                    break
                
                # If we have tool results AND a response, complete immediately
                # This prevents loops where tool is called repeatedly
                if has_tool_results and last_ai_msg:
                    # Check if the response is meaningful (not just "thinking" or empty)
                    content = last_ai_msg.content.strip()
                    if len(content) > 15 and not content.lower().startswith("i'm") and "thinking" not in content.lower():
                        logger.info(f"[WORKFLOW] ✅ Have tool results and meaningful response. Completing to prevent loop.")
                        final_state["current_step"] = "completed"
                        break
                
                # Additional check: if we've had tool results in last 2 iterations and have a response, complete
                recent_tool_results = [m for m in messages[-10:] if isinstance(m, ToolMessage)]
                if len(recent_tool_results) >= 1 and last_ai_msg and len(last_ai_msg.content) > 15:
                    # We've had at least one tool result and a response - that's enough
                    logger.info(f"[WORKFLOW] ✅ Have tool results from previous iteration and response. Completing.")
                    final_state["current_step"] = "completed"
                    break
                
                if current_step in ["completed", "notified"]:
                    logger.info(f"[WORKFLOW] ✅ Workflow completed at step: {current_step}")
                    break
                    
                # Log tool results if any
                tool_results = final_state.get("tool_results", {})
                if tool_results:
                    logger.info(f"[WORKFLOW] Tool results: {tool_results}")
                    
        except Exception as e:
            logger.error(f"[WORKFLOW] ❌ Agent workflow error: {e}", exc_info=True)
            print(f"[ERROR] Agent workflow error: {e}")
        
        # Extract final answer
        final_messages = final_state.get("messages", []) if final_state else []
        
        # Limit final messages for processing
        if len(final_messages) > 50:
            logger.warning(f"[WORKFLOW] Final message count too high ({len(final_messages)}), using last 30 for processing")
            final_messages = final_messages[-30:]
        
        answer = "I apologize, but I couldn't process your request."
        
        # Get last AI message (check recent messages first)
        for msg in reversed(final_messages[-20:]):  # Check last 20 messages only
            if isinstance(msg, AIMessage) and msg.content:
                if not (hasattr(msg, "tool_calls") and msg.tool_calls):
                    answer = msg.content
                    break
        
        # Collect debug info (only from recent messages to avoid bloat)
        tool_calls_made = []
        tool_results_received = []
        recent_messages = final_messages[-30:] if len(final_messages) > 30 else final_messages
        for msg in recent_messages:
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for tc in msg.tool_calls:
                    tool_calls_made.append({
                        "tool": tc.get("name", "unknown"),
                        "args": tc.get("args", {})
                    })
            if isinstance(msg, ToolMessage):
                tool_results_received.append({
                    "tool": msg.name,
                    "result": msg.content[:200]
                })
        
        logger.info(f"[WORKFLOW] Final answer: {answer[:200]}...")
        logger.info(f"[WORKFLOW] Tool calls made: {len(tool_calls_made)}")
        logger.info(f"[WORKFLOW] Tool results received: {len(tool_results_received)}")
        logger.info(f"[WORKFLOW] Final message count: {len(final_messages)}")
        
        # Clean up final state messages before checkpoint saves (limit to 30)
        if len(final_state.get("messages", [])) > 30:
            final_messages_clean = final_state["messages"]
            system_msgs = [m for m in final_messages_clean if isinstance(m, SystemMessage)]
            other_msgs = [m for m in final_messages_clean if not isinstance(m, SystemMessage)]
            final_state["messages"] = system_msgs + other_msgs[-30:]
            logger.info(f"[WORKFLOW] Cleaned up messages before checkpoint: {len(final_messages_clean)} -> {len(final_state['messages'])}")
        
        return {
            "answer": answer,
            "context": final_state.get("retrieved_context", []),
            "steps": final_state.get("current_step", ""),
            "iterations": final_state.get("iteration_count", 0),
            "tool_usage": len([m for m in final_messages if hasattr(m, "tool_calls")]),
            "debug_info": {
                "tool_calls": tool_calls_made,
                "tool_results": tool_results_received,
                "conversation_length": len(final_messages),
                "user_logged_in": bool(user_email)
            }
        }

