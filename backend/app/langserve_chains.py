"""
LangServe chains for exposing RAG endpoints
Wraps the support response generation logic as callable chains
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import JsonOutputParser

from app.llamaindex_service import get_hybrid_retriever
from app.prompts import strict_prompt, friendly_prompt, fallback_prompt
from app.openrouter import call_openrouter
from app.query_rewriter import rewrite_query
from app.logger import log_request
from app.retrieval_utils import build_context


# ==================== Input/Output Models ====================

class QueryRequest(BaseModel):
    """Input model for query processing"""
    query: str = Field(..., description="User query")
    mode: str = Field(default="friendly", description="Response mode: strict or friendly")


class DocumentReference(BaseModel):
    """Reference to a document"""
    id: str
    title: str
    content: str
    score: float
    preview: str


class QueryResponse(BaseModel):
    """Response model for query processing"""
    response: str = Field(..., description="Generated response")
    documents: List[DocumentReference] = Field(
        default_factory=list, 
        description="Retrieved documents"
    )
    query_rewritten: str = Field(
        default="", 
        description="Rewritten query if applicable"
    )


# ==================== Chain Components ====================

def retrieve_documents(query_input: Dict[str, Any]) -> Dict[str, Any]:
    """Retrieve documents using hybrid retriever"""
    query = query_input.get("query", "")
    retriever = get_hybrid_retriever()
    
    results = retriever.retrieve(query)
    
    # Convert to dict format
    docs = []
    for i, node_with_score in enumerate(results):
        doc_dict = {
            "id": f"doc-{i}",
            "title": node_with_score.node.metadata.get("title", ""),
            "content": node_with_score.node.text,
            "score": node_with_score.score,
            "preview": node_with_score.node.text[:180] + "..."
        }
        docs.append(doc_dict)
    
    return {
        **query_input,
        "documents": docs,
        "original_query": query
    }


def generate_response(chain_input: Dict[str, Any]) -> Dict[str, Any]:
    """Generate response using LLM"""
    query = chain_input.get("query", "")
    mode = chain_input.get("mode", "friendly")
    documents = chain_input.get("documents", [])
    
    # Determine if we have good results
    if not documents or (documents and documents[0].get("score", 0) < 0.15):
        prompt = fallback_prompt()
        temperature = 0.2
        max_tokens = 80
    else:
        # Build context from documents
        docs_text = build_context(documents)
        
        if mode == "strict":
            prompt = strict_prompt(docs_text, query)
            temperature = 0.2
        else:
            prompt = friendly_prompt(docs_text, query)
            temperature = 0.7
        
        max_tokens = 250
    
    # Call LLM
    response = call_openrouter(
        prompt=prompt,
        temperature=temperature,
        max_tokens=max_tokens
    )
    
    return {
        **chain_input,
        "response": response,
        "prompt": prompt,
        "temperature": temperature,
        "max_tokens": max_tokens
    }


def format_output(chain_output: Dict[str, Any]) -> QueryResponse:
    """Format output to QueryResponse model"""
    documents = [
        DocumentReference(**doc) 
        for doc in chain_output.get("documents", [])
    ]
    
    return QueryResponse(
        response=chain_output.get("response", ""),
        documents=documents,
        query_rewritten=chain_output.get("original_query", "")
    )


def rewrite_input_query(query_input: Dict[str, Any]) -> Dict[str, Any]:
    """Rewrite query for better retrieval"""
    original_query = query_input.get("query", "").strip()
    rewritten = rewrite_query(original_query)
    
    return {
        **query_input,
        "query": rewritten,
        "original_query": original_query
    }


# ==================== Main Chain ====================

def build_rag_chain():
    """
    Build the complete RAG chain
    
    Returns:
        A runnable chain that processes queries
    """
    chain = (
        RunnableLambda(lambda x: x if isinstance(x, dict) else {"query": x, "mode": "friendly"})
        | RunnableLambda(rewrite_input_query)
        | RunnableLambda(retrieve_documents)
        | RunnableLambda(generate_response)
        | RunnableLambda(format_output)
    )
    
    return chain


# ==================== Specialized Chains ====================

def build_retrieval_chain():
    """Build chain that only retrieves documents"""
    chain = (
        RunnableLambda(lambda x: x if isinstance(x, dict) else {"query": x, "mode": "friendly"})
        | RunnableLambda(retrieve_documents)
    )
    return chain


def build_rewriting_chain():
    """Build chain that only rewrites queries"""
    chain = RunnableLambda(rewrite_input_query)
    return chain


# Export chain instances
rag_chain = build_rag_chain()
retrieval_chain = build_retrieval_chain()
rewriting_chain = build_rewriting_chain()
