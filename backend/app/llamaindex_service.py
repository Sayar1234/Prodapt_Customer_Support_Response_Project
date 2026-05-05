"""
LlamaIndex service for RAG pipeline integration
Wraps existing retrievers and rerankers with LlamaIndex
"""

from typing import List, Dict, Any
from llama_index.core import Document
from llama_index.core.retrievers import BaseRetriever
from llama_index.core.schema import NodeWithScore

from app.bm25 import BM25Retriever
from app.hr_pinecone import HRPineconeRetriever
from app.reranker import Reranker
from app.retrieval_utils import normalize_docs, deduplicate_docs


class HybridRetriever(BaseRetriever):
    """
    Hybrid retriever combining BM25 and Pinecone
    with reranking support
    """
    
    def __init__(
        self,
        bm25_path: str = "app/sample.pdf",
        pinecone_path: str = "app/sample.pdf",
        bm25_weight: float = 0.8,
        pinecone_weight: float = 1.2,
        top_k: int = 10,
        rerank_top_n: int = 5
    ):
        """
        Initialize hybrid retriever
        
        Args:
            bm25_path: Path to PDF for BM25 indexing
            pinecone_path: Path to PDF for Pinecone indexing
            bm25_weight: Weight multiplier for BM25 scores
            pinecone_weight: Weight multiplier for Pinecone scores
            top_k: Number of results per retriever
            rerank_top_n: Number of results after reranking
        """
        super().__init__()
        self.bm25 = BM25Retriever(bm25_path)
        self.pinecone = HRPineconeRetriever(pinecone_path)
        self.reranker = Reranker()
        self.bm25_weight = bm25_weight
        self.pinecone_weight = pinecone_weight
        self.top_k = top_k
        self.rerank_top_n = rerank_top_n
    
    def _retrieve(self, query_str: str) -> List[NodeWithScore]:
        """
        Retrieve documents using hybrid approach
        
        Args:
            query_str: Query string
            
        Returns:
            List of NodeWithScore objects
        """
        # 1. Retrieve from both sources
        pinecone_results = self.pinecone.search(query_str, top_k=self.top_k)
        bm25_results = self.bm25.search(query_str, top_k=self.top_k)
        
        # 2. Normalize
        pinecone_results = normalize_docs(pinecone_results)
        bm25_results = normalize_docs(bm25_results)
        
        # 3. Apply weights
        for doc in pinecone_results:
            doc["score"] *= self.pinecone_weight
        
        for doc in bm25_results:
            doc["score"] *= self.bm25_weight
        
        # 4. Merge and deduplicate
        merged_results = pinecone_results + bm25_results
        merged_results = deduplicate_docs(merged_results)
        
        # 5. Rerank
        if merged_results:
            merged_results = self.reranker.rerank(
                query_str, 
                merged_results, 
                top_n=self.rerank_top_n
            )
        
        # 6. Convert to NodeWithScore format
        nodes_with_scores = []
        for doc in merged_results:
            node = Document(
                text=doc.get("content", ""),
                metadata={
                    "title": doc.get("title", ""),
                    "score": doc.get("score", 0.0)
                }
            )
            node_with_score = NodeWithScore(
                node=node,
                score=doc.get("score", 0.0)
            )
            nodes_with_scores.append(node_with_score)
        
        return nodes_with_scores
    
    def retrieve(self, query_str: str) -> List[NodeWithScore]:
        """Public retrieve method"""
        return self._retrieve(query_str)


# Singleton instance
_hybrid_retriever = None


def get_hybrid_retriever(
    bm25_path: str = "app/sample.pdf",
    pinecone_path: str = "app/sample.pdf"
) -> HybridRetriever:
    """Get or create singleton hybrid retriever"""
    global _hybrid_retriever
    if _hybrid_retriever is None:
        _hybrid_retriever = HybridRetriever(
            bm25_path=bm25_path,
            pinecone_path=pinecone_path
        )
    return _hybrid_retriever
