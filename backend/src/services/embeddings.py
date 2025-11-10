"""Embedding service using Alibaba-NLP/gme-Qwen2-VL-7B-Instruct model."""

from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating embeddings using gme-Qwen2-VL-7B-Instruct model."""
    
    def __init__(self, model_name: str = "Alibaba-NLP/gme-Qwen2-VL-2B-Instruct"):
        """Initialize the embedding service with the specified model.
        
        Args:
            model_name: Name of the embedding model to use
        """
        logger.info(f"Initializing embedding service with model: {model_name}")
        self.model = SentenceTransformer(model_name, trust_remote_code=True)
        logger.info("Embedding service initialized successfully")
    
    def encode(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            numpy array of embeddings with shape (len(texts), embedding_dim)
        """
        if not texts:
            logger.warning("Empty text list provided for encoding")
            return np.array([])
        
        logger.info(f"Encoding {len(texts)} text chunks")
        embeddings = self.model.encode(texts)
        logger.info(f"Generated embeddings with shape: {embeddings.shape}")
        return embeddings
    
    def encode_batch(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for a batch of texts (alias for encode).
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            numpy array of embeddings with shape (len(texts), embedding_dim)
        """
        return self.encode(texts)
    
    def encode_single(self, text: str) -> np.ndarray:
        """Generate embedding for a single text.
        
        Args:
            text: Text string to embed
            
        Returns:
            numpy array of embedding
        """
        return self.encode([text])[0]
    
    def similarity(self, embeddings1: np.ndarray, embeddings2: np.ndarray) -> np.ndarray:
        """Calculate similarity matrix between two sets of embeddings.
        
        Args:
            embeddings1: First set of embeddings
            embeddings2: Second set of embeddings
            
        Returns:
            Similarity matrix
        """
        return self.model.similarity(embeddings1, embeddings2)


# Global instance
_embedding_service: EmbeddingService = None


def get_embedding_service() -> EmbeddingService:
    """Get or create the global embedding service instance.
    
    Returns:
        EmbeddingService instance
    """
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service