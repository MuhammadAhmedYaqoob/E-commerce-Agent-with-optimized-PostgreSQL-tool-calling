"""
Configuration file for E-Commerce MiniRAG Agentic System
"""
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
if not OPENAI_API_KEY:
    print("[WARNING] OpenAI API key not found. Set OPENAI_API_KEY in your .env file.")

# Supabase Configuration
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")

# Gmail Configuration
GMAIL_USER = os.environ.get("GMAIL_USER", "")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")

# Directory structure
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
GRAPH_DIR = DATA_DIR / "graphs"
KNOWLEDGE_BASE_PATH = DATA_DIR / "ecommerce_knowledge_base.json"

# OpenAI Models
OPENAI_EMBED_MODEL = "text-embedding-3-small"
EMBED_DIM = 1536
LLM_MODEL = "gpt-4o-mini"  # Using mini model for efficiency
MAX_TOKENS = 2048
TEMPERATURE = 0.1

# Agent Configuration
AGENT_NAME = "E-Commerce Assistant"
AGENT_SYSTEM_PROMPT = """You are an intelligent e-commerce assistant powered by MiniRAG architecture.
You help customers with:
- Product inquiries and recommendations
- Order status and tracking
- Return and refund policies
- Shipping and delivery information
- Payment and security questions
- Account management and support

You have access to:
1. Knowledge graph for efficient retrieval
2. PostgreSQL database for order/user data
3. Gmail for sending notifications and 2FA codes

Always be helpful, accurate, and follow the e-commerce policies precisely."""

# Graph Configuration
GRAPH_RETRIEVAL_TOP_K = 5
GRAPH_TRAVERSAL_DEPTH = 3
SEMANTIC_FALLBACK_ENABLED = False  # True MiniRAG: graph-first only

# Database Configuration
DB_POOL_SIZE = 10
DB_MAX_OVERFLOW = 20

# Gmail Configuration
EMAIL_VERIFICATION_EXPIRY = 300  # 5 minutes for 2FA codes
NOTIFICATION_ENABLED = True

# FastAPI Configuration
API_HOST = "0.0.0.0"
API_PORT = 8000
API_TITLE = "E-Commerce MiniRAG Agentic API"
API_VERSION = "1.0.0"

# LangGraph Configuration
MAX_ITERATIONS = 50
MEMORY_ENABLED = True
