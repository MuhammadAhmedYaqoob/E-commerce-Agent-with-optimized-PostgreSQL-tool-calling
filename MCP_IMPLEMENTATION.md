# MCP (Model Context Protocol) Implementation

## Overview

This implementation introduces MCP servers for PostgreSQL and Gmail operations, providing a cleaner separation of concerns and better tool detection in the LangGraph workflow.

## Architecture

### MCP Servers

1. **PostgreSQL MCP Server** (`mcp_servers/postgresql_server.py`)
   - Handles all database operations
   - Supports both local PostgreSQL and Supabase (via DatabaseTool)
   - Endpoints:
     - `get_user_by_email`
     - `get_user_orders`
     - `get_order_by_id`
     - `get_user_email_from_order`
     - `search_orders_by_status`
     - `update_order_status`
     - `create_user`
     - `get_database_info`

2. **Gmail MCP Server** (`mcp_servers/gmail_server.py`)
   - Handles email operations
   - Endpoints:
     - `send_2fa_code`
     - `verify_2fa_code`
     - `send_notification`
     - `cleanup_expired_codes`

### MCP Clients

1. **PostgreSQLMCPClient** (`src/tools/mcp_client.py`)
   - Synchronous client for database operations
   - Automatically connects to MCP server
   - Falls back to direct DatabaseTool on errors

2. **GmailMCPClient** (`src/tools/mcp_client.py`)
   - Synchronous client for email operations
   - Automatically connects to MCP server
   - Falls back to direct GmailTool on errors

### Communication Protocol

Uses simple JSON-RPC over stdio:
- Request: `{"jsonrpc": "2.0", "id": 123, "method": "method_name", "params": {...}}`
- Response: `{"jsonrpc": "2.0", "id": 123, "result": {...}}`

## Integration

### Agent Integration

The agent (`src/agent/ecommerce_agent.py`) now uses MCP clients:
- Tools automatically use MCP when available
- Falls back to direct tools on MCP errors
- No changes needed to tool definitions

### Benefits

1. **Simpler Prompts**: No need for complex tool descriptions
2. **Better Tool Detection**: MCP provides structured tool definitions
3. **Separation of Concerns**: Database/email logic isolated in servers
4. **Maintainability**: Easier to update endpoints
5. **Testing**: Can test servers independently

## Running MCP Servers

Servers run automatically when clients connect. They use subprocess communication:
- PostgreSQL server: `python mcp_servers/postgresql_server.py`
- Gmail server: `python mcp_servers/gmail_server.py`

## Configuration

The PostgreSQL MCP server respects the `USE_SUPABASE` environment variable:
- `USE_SUPABASE=true`: Uses Supabase
- `USE_SUPABASE=false`: Uses local PostgreSQL

## Testing

### Unit Tests
```bash
pytest tests/test_mcp_servers.py -v
```

### Integration Tests
```bash
pytest tests/test_mcp_integration.py -v
```

## Error Handling

- MCP clients automatically fall back to direct tools on errors
- Logs MCP errors for debugging
- Maintains backward compatibility

## Future Enhancements

1. Add more endpoints as needed
2. Implement proper MCP protocol (currently using simplified JSON-RPC)
3. Add connection pooling for MCP servers
4. Add metrics/monitoring for MCP operations

