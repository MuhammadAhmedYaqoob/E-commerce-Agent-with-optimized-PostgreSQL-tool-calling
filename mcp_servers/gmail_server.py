"""
MCP Server for Gmail Operations
Handles 2FA codes and email notifications
Uses simple JSON-RPC over stdio
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools.gmail_tool import GmailTool
from mcp_servers.simple_rpc_server import SimpleRPCServer

# Initialize Gmail tool
gmail_tool = GmailTool()

# Define handlers
def send_2fa_code(email: str, purpose: str = "verification"):
    """Send 2FA code"""
    return gmail_tool.send_2fa_code(email, purpose)

def verify_2fa_code(email: str, code: str):
    """Verify 2FA code"""
    return gmail_tool.verify_2fa_code(email, code)

def send_notification(email: str, notification_type: str, data: dict):
    """Send notification"""
    return gmail_tool.send_notification(email, notification_type, data)

def cleanup_expired_codes():
    """Cleanup expired codes"""
    gmail_tool.cleanup_expired_codes()
    return {"success": True, "message": "Expired codes cleaned up"}

# Create server with handlers
handlers = {
    "send_2fa_code": send_2fa_code,
    "verify_2fa_code": verify_2fa_code,
    "send_notification": send_notification,
    "cleanup_expired_codes": cleanup_expired_codes
}

if __name__ == "__main__":
    server = SimpleRPCServer(handlers)
    server.run()

