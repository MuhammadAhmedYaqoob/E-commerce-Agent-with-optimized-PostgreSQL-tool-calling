"""
MCP Client for connecting to MCP servers
Provides unified interface for PostgreSQL and Gmail MCP servers
Uses subprocess communication for MCP stdio protocol
"""
import subprocess
import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import threading
import queue
import time

class SimpleMCPClient:
    """Simple MCP client using subprocess communication"""
    
    def __init__(self, server_script: str):
        self.server_script = Path(server_script)
        self.process: Optional[subprocess.Popen] = None
        self._connected = False
    
    def connect(self):
        """Start MCP server process"""
        if self._connected:
            return
        
        python_path = sys.executable
        self.process = subprocess.Popen(
            [python_path, str(self.server_script)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0
        )
        self._connected = True
        time.sleep(0.5)  # Give server time to start
    
    def disconnect(self):
        """Stop MCP server process"""
        if self.process:
            self.process.terminate()
            self.process.wait()
            self.process = None
        self._connected = False
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the MCP server"""
        if not self._connected:
            self.connect()
        
        # Simple JSON-RPC protocol
        request = {
            "jsonrpc": "2.0",
            "id": int(time.time() * 1000),
            "method": tool_name,
            "params": arguments
        }
        
        try:
            request_json = json.dumps(request) + "\n"
            self.process.stdin.write(request_json)
            self.process.stdin.flush()
            
            # Read response
            response_line = self.process.stdout.readline()
            if response_line:
                response = json.loads(response_line.strip())
                if "result" in response:
                    return response["result"]
                elif "error" in response:
                    return {"error": response["error"].get("message", "Unknown error")}
            return {"error": "No response"}
        except Exception as e:
            return {"error": str(e)}

class PostgreSQLMCPClient:
    """MCP client for PostgreSQL operations - synchronous"""
    
    def __init__(self):
        server_path = Path(__file__).parent.parent.parent / "mcp_servers" / "postgresql_server.py"
        self.client = SimpleMCPClient(str(server_path))
        self._connected = False
    
    def _ensure_connected(self):
        """Ensure connection is established"""
        if not self._connected:
            self.client.connect()
            self._connected = True
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        self._ensure_connected()
        result = self.client.call_tool("get_user_by_email", {"email": email})
        return result if result and "error" not in result else None
    
    def get_user_orders(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get user orders"""
        self._ensure_connected()
        result = self.client.call_tool("get_user_orders", {"user_id": user_id, "limit": limit})
        return result if isinstance(result, list) else []
    
    def get_order_by_id(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get order by ID"""
        self._ensure_connected()
        result = self.client.call_tool("get_order_by_id", {"order_id": order_id})
        return result if result and "error" not in result else None
    
    def get_user_email_from_order(self, order_number: str) -> Optional[str]:
        """Get user email from order number"""
        self._ensure_connected()
        result = self.client.call_tool("get_user_email_from_order", {"order_number": order_number})
        return result.get("email") if result and "error" not in result else None
    
    def search_orders_by_status(self, status: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search orders by status"""
        self._ensure_connected()
        result = self.client.call_tool("search_orders_by_status", {"status": status, "limit": limit})
        return result if isinstance(result, list) else []
    
    def update_order_status(self, order_id: str, status: str) -> bool:
        """Update order status"""
        self._ensure_connected()
        result = self.client.call_tool("update_order_status", {"order_id": order_id, "status": status})
        return result.get("success", False) if result else False
    
    def create_user(self, email: str, name: str) -> Optional[Dict[str, Any]]:
        """Create user"""
        self._ensure_connected()
        result = self.client.call_tool("create_user", {"email": email, "name": name})
        return result if result and "error" not in result else None
    
    def close(self):
        """Close connection"""
        self.client.disconnect()
        self._connected = False

class GmailMCPClient:
    """MCP client for Gmail operations - synchronous"""
    
    def __init__(self):
        server_path = Path(__file__).parent.parent.parent / "mcp_servers" / "gmail_server.py"
        self.client = SimpleMCPClient(str(server_path))
        self._connected = False
    
    def _ensure_connected(self):
        """Ensure connection is established"""
        if not self._connected:
            self.client.connect()
            self._connected = True
    
    def send_2fa_code(self, email: str, purpose: str = "verification") -> Dict[str, Any]:
        """Send 2FA code"""
        self._ensure_connected()
        result = self.client.call_tool("send_2fa_code", {"email": email, "purpose": purpose})
        return result if result else {"success": False, "error": "Unknown error"}
    
    def verify_2fa_code(self, email: str, code: str) -> Dict[str, Any]:
        """Verify 2FA code"""
        self._ensure_connected()
        result = self.client.call_tool("verify_2fa_code", {"email": email, "code": code})
        return result if result else {"verified": False, "error": "Unknown error"}
    
    def send_notification(self, email: str, notification_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send notification"""
        self._ensure_connected()
        result = self.client.call_tool("send_notification", {
            "email": email,
            "notification_type": notification_type,
            "data": data
        })
        return result if result else {"success": False, "error": "Unknown error"}
    
    def cleanup_expired_codes(self):
        """Cleanup expired codes"""
        self._ensure_connected()
        self.client.call_tool("cleanup_expired_codes", {})
    
    def close(self):
        """Close connection"""
        self.client.disconnect()
        self._connected = False

