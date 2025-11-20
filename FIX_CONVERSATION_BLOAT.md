# Fix: Conversation History Bloat

## Problem Identified

From the logs, I found:
- **Conversation history exploding**: 76,066 → 152,136 messages
- **Tool calls accumulating**: 24 → 400
- **State persistence issue**: Messages being duplicated/repeated

## Root Causes

1. **Checkpointing storing ALL messages**: MemorySaver persists every message forever
2. **No message limit**: Messages accumulate without cleanup
3. **Duplicate history**: Both checkpoint AND conversation_history being used
4. **Context bloat**: All messages sent to LLM every time

## Fixes Applied

### 1. Limit Checkpoint Messages
- Only keep last 20 messages from checkpoint
- Truncate if more than 20 exist

### 2. Prevent Duplication
- Use checkpoint messages OR conversation_history, not both
- Prefer checkpoint (it's already in correct format)

### 3. Limit Context to LLM
- Only send last 10 messages as context
- Prevents token bloat

### 4. Message Count Monitoring
- Truncate messages if count > 50
- Keep system messages + last 30

### 5. Debug Info Limiting
- Only collect tool calls from recent messages
- Prevents debug info bloat

## Expected Results

- Conversation history: ~20-30 messages max
- Tool calls: Only from current query
- Performance: Much faster
- Memory: Stable, no growth

## Testing

After restarting Streamlit, conversation history should stay manageable.

