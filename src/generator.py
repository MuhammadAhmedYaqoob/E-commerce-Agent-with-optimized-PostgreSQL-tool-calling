"""
Answer Generator for E-Commerce MiniRAG System
"""
from typing import List, Dict
from .config import OPENAI_API_KEY, LLM_MODEL, MAX_TOKENS, TEMPERATURE
import openai

client = openai.OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """You are an intelligent e-commerce assistant powered by MiniRAG architecture.
You help customers with product inquiries, order status, policies, and support.

Guidelines:
1. Provide accurate, helpful answers based on retrieved context
2. Be concise but comprehensive
3. If information is not available, say so clearly
4. For policy questions, cite specific policy details
5. Always be professional and customer-friendly
"""

def generate_answer(query: str, contexts: List[Dict]) -> str:
    """
    Generate answer from retrieved contexts.
    
    Args:
        query: User question
        contexts: Retrieved contexts from MiniRAG graph
        
    Returns:
        Generated answer
    """
    if not contexts:
        return "I couldn't find relevant information to answer your question. Please try rephrasing or contact support."
    
    # Format contexts
    context_str = "\n\n".join([
        f"=== {ctx.get('title', 'Information')} ===\n"
        f"Category: {ctx.get('category', 'N/A')}\n"
        f"Content: {str(ctx.get('content', {}))}\n"
        for ctx in contexts[:3]  # Use top 3 contexts
    ])
    
    try:
        completion = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Context:\n{context_str}\n\nQuestion: {query}\n\nAnswer:"}
            ],
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE
        )
        
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"[ERROR] Generation failed: {e}")
        return "I apologize, but I encountered an error generating your answer."
