# Streamlit Testing Guide - MCP Integration

## Quick Start

1. **Start Streamlit**:
   ```bash
   streamlit run streamlit_app.py
   ```

2. **Initialize the Agent**:
   - Click "🤖 Initialize Agent" in the sidebar
   - Wait for "✅ Agent initialized" message

3. **Test MCP Integration**:

### Test Scenarios

#### 1. Order Tracking (Not Logged In)
```
Query: "I want to track my order"
Expected: Agent asks for order number
Then: "ORD-12345"
Expected: Agent sends verification code
Then: Enter the 6-digit code from your email
Expected: Agent shows order details
```

#### 2. Order Tracking (Logged In)
```
Email: john@example.com (or your test email)
Query: "Show me my orders"
Expected: Agent shows all orders for that user
```

#### 3. Policy Questions
```
Query: "What is your return policy?"
Expected: Agent retrieves policy via MiniRAG and formats it nicely (no guardrails)
```

#### 4. Context Preservation
```
Query: "I want to track my order"
Then: "ORD-12345"
Then: "I want to return this order"
Expected: Agent remembers ORD-12345 and initiates return
```

## What to Check

### In the Debug Panel (Agent Details)
- **Tool Calls**: Should show MCP tools being called
- **Tool Results**: Should show successful responses
- **Conversation Length**: Should increase with each turn

### MCP Server Status
- MCP servers start automatically when agent tools are called
- Check console/logs for MCP server startup messages
- If MCP fails, system falls back to direct tools (check logs)

## Troubleshooting

### If MCP servers don't start:
- Check that Python can find the server scripts
- Verify subprocess permissions
- Check console for error messages

### If tools aren't working:
- Check the debug panel for tool call information
- Verify database connection (PostgreSQL or Supabase)
- Verify Gmail credentials in .env file

### Performance:
- First MCP call may be slower (server startup)
- Subsequent calls should be fast
- If slow, check MCP server logs

## Expected Behavior

✅ **MCP Working**: Tools use MCP servers, responses are fast
✅ **Fallback Working**: If MCP fails, direct tools are used (check logs)
✅ **State Management**: Agent remembers context across queries
✅ **Error Handling**: Graceful degradation if MCP unavailable

## Test Your Email

If you want to test with your email (`ahmedyaqoobbusiness@gmail.com`):
1. Use that email in the email field
2. Try: "Show me my orders"
3. Should show orders: ORD-88888 and ORD-99999

