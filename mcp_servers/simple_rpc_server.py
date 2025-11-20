"""
Simple RPC Server for MCP-style communication
Uses JSON-RPC over stdio for simplicity and reliability
"""
import sys
import json
from typing import Any, Dict

class SimpleRPCServer:
    """Simple RPC server using JSON-RPC over stdio"""
    
    def __init__(self, handlers: Dict[str, callable]):
        self.handlers = handlers
    
    def run(self):
        """Run the server, reading from stdin and writing to stdout"""
        while True:
            try:
                # Read request from stdin
                line = sys.stdin.readline()
                if not line:
                    break
                
                request = json.loads(line.strip())
                
                # Handle request
                response = self._handle_request(request)
                
                # Write response to stdout
                print(json.dumps(response), flush=True)
            
            except json.JSONDecodeError:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": "Parse error"}
                }
                print(json.dumps(error_response), flush=True)
            
            except Exception as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id") if 'request' in locals() else None,
                    "error": {"code": -32603, "message": str(e)}
                }
                print(json.dumps(error_response), flush=True)
    
    def _handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a JSON-RPC request"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        if method in self.handlers:
            try:
                result = self.handlers[method](**params)
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": result
                }
            except Exception as e:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32603, "message": str(e)}
                }
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"}
            }

