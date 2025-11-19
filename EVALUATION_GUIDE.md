# Evaluation Framework Guide

## Overview

This evaluation framework compares three RAG architectures:
1. **Naive RAG** with normal PostgreSQL
2. **MiniRAG with SLM** with normal PostgreSQL  
3. **MiniRAG with LLM** with SOTA optimized PostgreSQL

## Structure

### Data Files (Multi-Purpose JSON)

```
data/
├── policies.json          # All e-commerce policies
├── entities.json          # Product categories, sizes, statuses
├── relationships.json     # Graph relationships
├── guardrails.json        # System guardrails
└── evaluation_questions.json  # 100 test questions
```

### Evaluation Questions (100 Total)

**Categories:**
- **State/Memory Tests (20)**: Test agent state persistence and memory
- **Tool Calling Tests (10)**: Test tool usage accuracy
- **Policy Queries (20)**: Test policy retrieval
- **Product Queries (15)**: Test product information queries
- **Order Queries (10)**: Test order management
- **Complex Multi-Tool (10)**: Test multiple tool usage
- **Edge Cases (10)**: Test edge case handling
- **Conversation Flow (5)**: Test multi-turn conversations

## Evaluation Metrics

### 1. Retrieval Accuracy
- Precision@K: How many retrieved documents are relevant
- Measures: Graph retrieval quality

### 2. Relevance Score
- Content matching: How well retrieved content matches query
- Measures: Semantic relevance

### 3. Response Time
- Query to answer time
- Measures: System efficiency

### 4. Tool Usage Accuracy
- Precision/Recall: Expected vs actual tool calls
- Measures: Agent decision-making

### 5. State Consistency
- State maintained across conversation turns
- Measures: Agent state management

### 6. Memory Retention
- Context maintained across turns
- Measures: Agent memory

### 7. Answer Quality
- Keyword coverage in answers
- Measures: Response quality

### 8. Database Efficiency (SOTA only)
- Query execution times
- Measures: PostgreSQL optimization

## Running Evaluation

### Step 1: Prepare Systems

You need to implement three systems:

```python
# 1. Naive RAG System
class NaiveRAGSystem:
    def query(self, question):
        # Semantic search + PostgreSQL
        pass

# 2. MiniRAG SLM System
class MiniRAGSLMSystem:
    def query(self, question):
        # Graph retrieval + SLM + PostgreSQL
        pass

# 3. MiniRAG LLM SOTA System (Your system)
class MiniRAGLLMSOTASystem:
    def query(self, question):
        # Graph retrieval + LLM + SOTA PostgreSQL
        pass
```

### Step 2: Run Evaluation

```bash
python run_evaluation.py
```

### Step 3: View Results

Results are saved to:
- `evaluation_results/evaluation_results.json` - Detailed results
- `evaluation_results/plots/` - Visualization graphs

## Expected Outputs

### 1. Comprehensive Scores Plot
Shows overall performance comparison

### 2. Metric Comparison Plot
Shows detailed metric breakdown

### 3. Response Times Plot
Shows performance comparison

### 4. Database Efficiency Plot
Shows SOTA PostgreSQL optimization benefits

## Question Format

Each question includes:
- `id`: Unique identifier
- `question`: The query text
- `category`: Question category
- `expected_tools`: Tools that should be called
- `expected_context`: Expected document IDs
- `context_required`: For follow-up questions

## State and Memory Testing

Questions Q001-Q020 test:
- State persistence across turns
- Memory of previous context
- Tool usage in context
- Multi-turn conversations

Example:
```
Q001: "I'm looking for a men's blue shirt in size Large"
Q002: "What about the same shirt in Medium?"  # Should remember product
```

## Tool Calling Testing

Questions Q021-Q030 test:
- Correct tool selection
- Tool sequence
- Multi-tool operations

## Implementation Notes

1. **Replace Simulated Responses**: Update `_simulate_*_response` methods in `experiments.py` with actual system calls

2. **Add Database Timing**: Track database query times in SOTA system

3. **State Tracking**: Ensure state is tracked for multi-turn questions

4. **Tool Logging**: Log all tool calls for accuracy measurement

## Research Paper Contribution

This evaluation framework demonstrates:
- Comprehensive comparison methodology
- Multiple evaluation metrics
- State and memory testing
- Tool usage evaluation
- Database optimization impact

## Next Steps

1. Implement actual system interfaces
2. Run full evaluation
3. Analyze results
4. Generate graphs
5. Write research paper section

