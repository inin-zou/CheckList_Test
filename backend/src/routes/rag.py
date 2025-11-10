from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any
import logging

from src.services.vector_db import WeaviateService
from src.services.embeddings import EmbeddingService
from src.services.llm import LLMService
from src.dependencies import get_weaviate_service, get_embedding_service, get_llm_service

logger = logging.getLogger(__name__)

router = APIRouter()


class RAGQueryRequest(BaseModel):
    question: str
    top_k: int = 5


class RAGResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]


@router.post("/ask")
async def query_rag(
    request: RAGQueryRequest,
    embedding_service: EmbeddingService = Depends(get_embedding_service),
    vector_db: WeaviateService = Depends(get_weaviate_service),
    llm_service: LLMService = Depends(get_llm_service),
) -> RAGResponse:
    """Query the RAG system with a question.
    
    Args:
        request: The RAG query request containing the question and optional parameters
        embedding_service: Service for generating embeddings
        vector_db: Weaviate vector database service
        llm_service: LLM service for generating answers
        
    Returns:
        RAGResponse containing the answer and source documents
    """
    try:
        logger.info(f"Processing RAG query: {request.question}")
        
        # 1. Generate embedding for the question
        question_embedding = embedding_service.encode([request.question])[0]
        logger.info(f"Generated question embedding with dimension: {len(question_embedding)}")
        
        # 2. Search vector database for relevant documents
        search_results = vector_db.search(
            query_vector=question_embedding,
            limit=request.top_k,
            collection_type="user"  # Search in user documents
        )
        logger.info(f"Found {len(search_results)} relevant documents")
        
        if not search_results:
            return RAGResponse(
                answer="I couldn't find any relevant documents to answer your question. Please make sure you have uploaded some documents first.",
                sources=[]
            )
        
        # 3. Prepare context from retrieved documents
        context_parts = []
        sources = []
        
        for idx, result in enumerate(search_results, 1):
            context_parts.append(f"[Document {idx}] {result['filename']}:\n{result['content']}")
            sources.append({
                "filename": result["filename"],
                "content": result["content"][:300] + "..." if len(result["content"]) > 300 else result["content"],
                "chunk_index": result.get("chunk_index", 0),
                "distance": result.get("distance", 0.0)
            })
        
        context = "\n\n".join(context_parts)
        
        # 4. Generate answer using LLM with retrieved context
        prompt = f"""Based on the following documents, please answer the question. If the documents don't contain enough information to answer the question, say so.

Documents:
{context}

Question: {request.question}

Please provide a clear and concise answer based on the information in the documents above."""
        
        answer = await llm_service.generate_response(prompt)
        logger.info(f"Generated answer with length: {len(answer)}")
        
        return RAGResponse(
            answer=answer,
            sources=sources
        )
    except Exception as e:
        logger.error(f"Error in RAG query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rebuild-index")
async def rebuild_index():
    """Rebuild the vector database index"""
    # TODO: Implement index rebuild logic
    return {"message": "Index rebuild started"}