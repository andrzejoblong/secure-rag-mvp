"""
Hybrid search combining BM25 (keyword-based) and semantic (embedding-based) search.

BM25 is excellent for:
- Exact matches (invoice numbers, IDs)
- Technical terms and specifications
- Keyword-based queries

Semantic search is excellent for:
- Understanding intent and meaning
- Handling synonyms and paraphrases
- Context-aware retrieval

Hybrid approach combines both for best results.
"""

from rank_bm25 import BM25Okapi
from typing import List, Dict, Tuple
import numpy as np


class HybridSearcher:
    """
    Combines BM25 and semantic search for improved retrieval.
    """
    
    def __init__(self, chunks: List[Dict], bm25_weight: float = 0.3, semantic_weight: float = 0.7):
        """
        Initialize hybrid searcher.
        
        Args:
            chunks: List of chunk dictionaries with 'id', 'text', and other metadata
            bm25_weight: Weight for BM25 scores (default 0.3)
            semantic_weight: Weight for semantic scores (default 0.7)
        """
        self.chunks = chunks
        self.bm25_weight = bm25_weight
        self.semantic_weight = semantic_weight
        
        # Prepare BM25 corpus (tokenized texts)
        self.corpus = [self._tokenize(chunk['text']) for chunk in chunks]
        self.bm25 = BM25Okapi(self.corpus)
        
    def _tokenize(self, text: str) -> List[str]:
        """
        Simple tokenization: lowercase, split by whitespace and basic punctuation.
        """
        # Convert to lowercase and split
        tokens = text.lower().split()
        # Remove basic punctuation from ends
        tokens = [t.strip('.,!?;:()[]{}') for t in tokens]
        return [t for t in tokens if t]  # Remove empty strings
    
    def search(
        self, 
        query: str, 
        semantic_scores: List[float], 
        top_k: int = 10
    ) -> List[Tuple[int, float]]:
        """
        Perform hybrid search.
        
        Args:
            query: Search query string
            semantic_scores: Pre-computed semantic similarity scores for all chunks
            top_k: Number of top results to return
            
        Returns:
            List of (chunk_index, combined_score) tuples, sorted by score descending
        """
        # Get BM25 scores
        query_tokens = self._tokenize(query)
        bm25_scores = self.bm25.get_scores(query_tokens)
        
        # Normalize scores to [0, 1] range
        bm25_scores_norm = self._normalize_scores(bm25_scores)
        semantic_scores_norm = self._normalize_scores(semantic_scores)
        
        # Combine scores
        combined_scores = (
            self.bm25_weight * bm25_scores_norm + 
            self.semantic_weight * semantic_scores_norm
        )
        
        # Get top-k indices
        top_indices = np.argsort(combined_scores)[::-1][:top_k]
        
        # Return as list of (index, score) tuples
        results = [(int(idx), float(combined_scores[idx])) for idx in top_indices]
        return results
    
    def _normalize_scores(self, scores: List[float]) -> np.ndarray:
        """
        Normalize scores to [0, 1] range using min-max normalization.
        Handles edge case where all scores are the same.
        """
        scores_array = np.array(scores)
        min_score = scores_array.min()
        max_score = scores_array.max()
        
        if max_score == min_score:
            # All scores are the same, return array of 0.5
            return np.full_like(scores_array, 0.5)
        
        normalized = (scores_array - min_score) / (max_score - min_score)
        return normalized


def create_hybrid_searcher(chunks: List[Dict]) -> HybridSearcher:
    """
    Factory function to create a HybridSearcher instance.
    
    Args:
        chunks: List of chunk dictionaries
        
    Returns:
        Configured HybridSearcher instance
    """
    return HybridSearcher(chunks, bm25_weight=0.3, semantic_weight=0.7)
