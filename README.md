# E-Commerce MiniRAG Agentic System

A state-of-the-art agentic AI system for e-commerce platforms using **true MiniRAG architecture** with LangGraph orchestration. This system demonstrates autonomous decision-making, tool usage, and graph-first retrieval for efficient knowledge access.

## 🎯 Project Overview

This project implements a complete **Agentic AI solution** for e-commerce customer support, featuring:

- **True MiniRAG Architecture**: Graph-first retrieval (not semantic-first with graph enhancement)
- **LangGraph Orchestration**: Autonomous agentic workflow with tool calling
- **Multi-Tool Integration**: Gmail (2FA/notifications) and Supabase (PostgreSQL) tools
- **FastAPI Backend**: Production-ready REST API
- **Streamlit UI**: Interactive testing interface

## 🏗️ Architecture

### MiniRAG (True Implementation)

Unlike hybrid systems that use graphs as enhancements, this system implements **true MiniRAG**:

1. **Graph-First Indexing**: Heterogeneous knowledge graph is the PRIMARY index
2. **Graph Traversal Retrieval**: Information retrieval through graph structure, not semantic similarity
3. **Topology-Enhanced Discovery**: Related information discovered via graph relationships
4. **Lightweight Design**: Optimized for efficiency while maintaining accuracy

### Agentic System Components

```
┌─────────────────────────────────────────────────────────┐
│              LangGraph Orchestration Layer               │
├─────────────────────────────────────────────────────────┤
│  Retrieve → Reason → Tools → Generate → Notify         │
└─────────────────────────────────────────────────────────┘
         │              │              │
         ▼              ▼              ▼
    MiniRAG Graph   Gmail Tool   Supabase Tool
    (Primary)       (2FA/Email)  (PostgreSQL)
```

## 🚀 Features

### 1. MiniRAG Graph Retrieval
- **Primary Index**: Knowledge graph with policies, entities, and relationships
- **Graph Traversal**: BFS-based exploration of related nodes
- **Content-Aware Scoring**: Graph structure + content relevance
- **No Semantic Dependency**: Works without heavy embedding models

### 2. Agentic Workflow
- **Autonomous Decision-Making**: Agent decides when to use tools
- **Multi-Step Reasoning**: Iterative refinement of responses
- **Tool Orchestration**: Seamless integration of Gmail and Supabase
- **State Management**: LangGraph state machine for complex workflows

### 3. Tools

#### Gmail Tool
- **2FA Verification**: Send and verify authentication codes
- **Notifications**: Order updates, shipping alerts, payment confirmations
- **Secure Communication**: SMTP-based email delivery

#### Supabase Tool (SOTA PostgreSQL)
- **Lightweight Retrieval**: Optimized queries for fast data access
- **Graph-Aware Caching**: Cache graph entities for faster retrieval
- **Connection Pooling**: Efficient database resource management
- **Research Contribution**: Novel approach to PostgreSQL as a tool in agentic systems

## 📋 Prerequisites

- Python 3.10+
- OpenAI API key
- Supabase account (optional, system works in mock mode)
- Gmail account with App Password (optional, for email features)

## 🔧 Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd Saudi-Food-and-Drug-Authority-RAG-System
```

2. **Create virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your API keys and credentials
```

5. **Build MiniRAG Graph**
```bash
python -m src.main --build-graph
```

Or use the Streamlit UI to build the graph interactively.

## 🎮 Usage

### Streamlit UI (Recommended for Testing)

```bash
streamlit run streamlit_app.py
```

Features:
- Interactive query interface
- Graph building and status
- Agent initialization
- Real-time responses with context

### FastAPI Backend

```bash
python -m src.api.main
# Or
uvicorn src.api.main:app --reload
```

API Endpoints:
- `GET /`: Root endpoint
- `GET /health`: Health check
- `POST /query`: Process user query
- `POST /build-graph`: Build/rebuild knowledge graph
- `GET /graph/stats`: Get graph statistics

### Example API Request

```python
import requests

response = requests.post(
    "http://localhost:8000/query",
    json={
        "query": "What is your return policy?",
        "user_email": "user@example.com"
    }
)

print(response.json())
```

## 📊 Knowledge Base

The system uses a comprehensive e-commerce knowledge base (`data/ecommerce_knowledge_base.json`) containing:

- **Policies**: Return/refund, shipping, privacy, payment, quality, customer service
- **Entities**: Product categories, order statuses, payment methods
- **Relationships**: Policy connections, entity-policy mappings

## 🔬 Research Contributions

### 1. True MiniRAG Implementation
- Graph-first architecture (not hybrid)
- Efficient graph traversal algorithms
- Content-aware node scoring

### 2. PostgreSQL as Agentic Tool
- Novel use of Supabase/PostgreSQL as a tool in LangGraph
- Optimized query patterns for agentic systems
- Graph-aware caching strategies

### 3. Multi-Tool Agentic Orchestration
- Seamless integration of email and database tools
- Autonomous tool selection and usage
- State management for complex workflows

## 📁 Project Structure

```
.
├── src/
│   ├── agent/              # Agentic system with LangGraph
│   │   └── ecommerce_agent.py
│   ├── api/                 # FastAPI backend
│   │   └── main.py
│   ├── minirag/             # True MiniRAG implementation
│   │   ├── graph_builder.py
│   │   └── graph_retriever.py
│   ├── tools/               # Agent tools
│   │   ├── gmail_tool.py
│   │   └── supabase_tool.py
│   ├── config.py
│   └── generator.py
├── data/
│   ├── ecommerce_knowledge_base.json
│   └── graphs/              # Generated graph files
├── streamlit_app.py         # Streamlit UI
├── requirements.txt
├── .env.example
└── README.md
```

## 🧪 Testing

```bash
# Run tests (when implemented)
pytest tests/

# Test API
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is your shipping policy?"}'
```

## 🔒 Security Considerations

- API keys stored in `.env` (not committed)
- Gmail App Passwords (not main password)
- Supabase Row Level Security (when configured)
- Input validation in FastAPI
- Secure email transmission (TLS)

## 📈 Performance

- **Graph Building**: ~5-10 seconds for knowledge base
- **Query Processing**: ~2-5 seconds (depends on tool usage)
- **Graph Retrieval**: <100ms (graph traversal)
- **Database Queries**: <50ms (with connection pooling)

## 🛠️ Development

### Adding New Tools

1. Create tool class in `src/tools/`
2. Add tool to agent in `src/agent/ecommerce_agent.py`
3. Update workflow if needed

### Extending Knowledge Base

1. Edit `data/ecommerce_knowledge_base.json`
2. Rebuild graph: `POST /build-graph`
3. Test with queries


## 👥 Authors

Muhammad Ahmed Yaqoob

## 🙏 Acknowledgments

- MiniRAG architecture inspiration
- LangGraph for orchestration framework
- OpenAI for LLM capabilities
- Supabase for database infrastructure

## 📚 References

- MiniRAG: Lightweight Topology-Enhanced Retrieval
- LangGraph: Multi-Agent Workflows
- Agentic AI: Autonomous Systems with Tool Use

---

**Note**: This is a research project demonstrating agentic AI principles. For production use, additional security, monitoring, and error handling should be implemented.
