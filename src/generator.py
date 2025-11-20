"""
Answer Generator for E-Commerce MiniRAG System
"""
from typing import List, Dict
from .config import OPENAI_API_KEY, LLM_MODEL, MAX_TOKENS, TEMPERATURE
import openai
import json

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
    Generate answer from retrieved contexts with proper formatting.
    Excludes technical details like guardrails and metadata.
    
    Args:
        query: User question
        contexts: Retrieved contexts from MiniRAG graph
        
    Returns:
        Generated answer
    """
    if not contexts:
        return "I couldn't find relevant information to answer your question. Please try rephrasing or contact support."
    
    # Format contexts - exclude technical details
    formatted_contexts = []
    for ctx in contexts[:3]:  # Use top 3 contexts
        title = ctx.get('title', 'Information')
        category = ctx.get('category', 'N/A')
        content = ctx.get('content', {})
        
        # Extract user-friendly content, skip guardrails and metadata
        if isinstance(content, dict):
            user_content = []
            for key, value in content.items():
                # Skip technical/administrative fields
                if key.lower() not in ['guardrails', 'metadata', 'technical', 'admin', 'internal']:
                    if isinstance(value, (list, dict)):
                        # Format lists and dicts nicely
                        if isinstance(value, list) and value:
                            user_content.append(f"{key}: {', '.join(str(v) for v in value[:5])}")
                        else:
                            user_content.append(f"{key}: {json.dumps(value, indent=2) if isinstance(value, dict) else str(value)}")
                    else:
                        user_content.append(f"{key}: {value}")
            content_str = "\n".join(user_content)
        else:
            content_str = str(content)
        
        formatted_contexts.append(f"=== {title} ===\nCategory: {category}\n{content_str}")
    
    context_str = "\n\n".join(formatted_contexts)
    
    enhanced_prompt = f"""{SYSTEM_PROMPT}

When generating answers:
- Use the context information provided
- Format information in a user-friendly way
- Exclude technical details like guardrails, metadata, and internal notes
- Be concise but comprehensive
- If the context mentions policies, explain them clearly
"""
    
    try:
        completion = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": enhanced_prompt},
                {"role": "user", "content": f"Context Information:\n{context_str}\n\nUser Question: {query}\n\nProvide a helpful, user-friendly answer based on the context:"}
            ],
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE
        )
        
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"[ERROR] Generation failed: {e}")
        return "I apologize, but I encountered an error generating your answer."
