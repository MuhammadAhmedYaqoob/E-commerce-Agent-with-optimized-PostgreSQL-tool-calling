"""
FastAPI Backend for E-Commerce MiniRAG Agentic System
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn

from ..config import API_TITLE, API_VERSION
from ..agent.ecommerce_agent import ECommerceAgent
from ..minirag.graph_builder import MiniRAGGraphBuilder

app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description="Agentic E-Commerce Assistant using MiniRAG Architecture"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agent
agent = ECommerceAgent()

# Request/Response models
class QueryRequest(BaseModel):
    query: str
    user_email: Optional[str] = None

class QueryResponse(BaseModel):
    answer: str
    context: List[Dict[str, Any]]
    steps: str
    iterations: int
    tool_usage: int

class BuildGraphRequest(BaseModel):
    force_rebuild: bool = False

class BuildGraphResponse(BaseModel):
    success: bool
    message: str
    nodes: int
    edges: int

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "E-Commerce MiniRAG Agentic API",
        "version": API_VERSION,
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "agent": "ready"}

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process user query through agentic workflow.
    
    This endpoint:
    1. Retrieves information from MiniRAG graph
    2. Uses agentic reasoning to determine actions
    3. Calls tools (Gmail, Supabase) as needed
    4. Generates final answer
    """
    try:
        result = agent.process_query(
            query=request.query,
            user_email=request.user_email
        )
        return QueryResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/build-graph", response_model=BuildGraphResponse)
async def build_graph(request: BuildGraphRequest = BuildGraphRequest()):
    """
    Build or rebuild the MiniRAG knowledge graph.
    This is the PRIMARY indexing mechanism.
    """
    try:
        builder = MiniRAGGraphBuilder()
        graph_path = builder.build_graph()
        
        if graph_path:
            graph = builder.get_graph()
            return BuildGraphResponse(
                success=True,
                message="Graph built successfully",
                nodes=graph.number_of_nodes(),
                edges=graph.number_of_edges()
            )
        else:
            return BuildGraphResponse(
                success=False,
                message="Failed to build graph",
                nodes=0,
                edges=0
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/graph/stats")
async def get_graph_stats():
    """Get graph statistics"""
    from ..minirag.graph_retriever import MiniRAGRetriever
    retriever = MiniRAGRetriever()
    graph = retriever.graph
    
    if graph:
        return {
            "nodes": graph.number_of_nodes(),
            "edges": graph.number_of_edges(),
            "policy_nodes": len([n for n, a in graph.nodes(data=True) if a.get("type") == "policy"]),
            "entity_nodes": len([n for n, a in graph.nodes(data=True) if a.get("type") == "entity"])
        }
    return {"error": "Graph not loaded"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

