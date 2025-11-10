from functools import lru_cache
from src.services.vector_db import WeaviateService
from src.services.embeddings import EmbeddingService
from src.services.llm import LLMService
from src.services.claude import ClaudeService


@lru_cache()
def get_weaviate_service() -> WeaviateService:
    """Get or create a singleton WeaviateService instance."""
    return WeaviateService()


@lru_cache()
def get_embedding_service() -> EmbeddingService:
    """Get or create a singleton EmbeddingService instance."""
    return EmbeddingService()


@lru_cache()
def get_llm_service() -> LLMService:
    """Get or create a singleton LLMService instance."""
    return LLMService()


@lru_cache()
def get_claude_service() -> ClaudeService:
    """Get or create a singleton ClaudeService instance."""
    return ClaudeService()
